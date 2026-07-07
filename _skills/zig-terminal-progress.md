# Zig Terminal Progress (spinner / reveal), Zero Dependencies

**Works well for:** Any native Zig CLI that has a step taking more than ~300ms and runs attached to an interactive terminal — the gap between "nothing happened" and "it's working"
**Confidence:** High — compiled and run-tested against Zig 0.16.0 on macOS arm64 (2026-07-04); not yet exercised on Linux/Windows terminals

## The pattern

A spinner is a carriage return (`\r`) plus a cycling frame, written and flushed on every tick. No ANSI library, no external dependency — `\r` alone is enough to overwrite the current line in every terminal that matters.

```zig
const std = @import("std");

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var errbuf: [256]u8 = undefined;
    var errw = std.Io.File.stderr().writerStreaming(io, &errbuf);

    // Gate on isatty — never animate into a pipe, log file, or CI capture.
    const interactive = (std.Io.File.stderr().isTty(io) catch false);

    const frames = [_][]const u8{ "-", "\\", "|", "/" };
    var i: usize = 0;
    while (i < 8) : (i += 1) {
        if (interactive) {
            try errw.interface.print("\r  {s} working...", .{frames[i % frames.len]});
            try errw.interface.flush();
        }
        std.Io.sleep(io, std.Io.Duration.fromMilliseconds(50), .awake) catch {};
    }
    if (interactive) {
        try errw.interface.print("\r  done.            \n", .{});
        try errw.interface.flush();
    }
}
```

### Key rules

1. **Write progress to stderr, never stdout.** Any tool with a JSON-on-stdout contract (see [zig-json-cli-subcommand.md](zig-json-cli-subcommand.md)) corrupts its own output if a spinner byte lands on stdout. This is not optional — it's the same separation the JSON-contract pattern already requires.

2. **Gate on `isTty`, every time.** `std.Io.File.stderr().isTty(io)` returns `false` when stderr is piped, redirected to a file, or captured by CI. Animating into a non-terminal destination produces a file full of `\r` garbage — check once at the top and skip all progress output (not just suppress the newline) when `false`.

3. **`\r` alone beats ANSI escape codes for the minimal case.** Clearing to end-of-line (`\x1b[K`) avoids leftover characters when the new frame is shorter than the old one — pad the final "done" message with trailing spaces instead if you want to stay escape-code-free, as above.

4. **Use `std.Io.sleep(io, duration, clock)`, not `std.time.sleep`.** Zig 0.16 threads a `Clock` variant through the `Io` interface — `.awake` is the equivalent of "monotonic, excludes system-suspend time" (there is no `.monotonic` member in this version). `std.Io.Duration.fromMilliseconds(n)` builds the duration.

5. **Progressive line-reveal (multiple lines appearing one at a time) needs no spinner at all** — just sequential `print` + `flush` + a short `sleep` between lines, gated by the same `isTty` check. This is the simpler sibling of the spinner: no `\r`, no frame cycling, just paced output.

## When to use it

- A subcommand does real work (file scan, network retry, subprocess chain) that can visibly run past ~300ms
- The tool is invoked interactively at least some of the time (not purely from another program's pipe)

## When NOT to use it

- The operation is reliably fast (<300ms) — a spinner that flashes once and disappears is noise
- The tool's only consumer is another program or a JSON-on-stdout contract with no human ever watching stderr live
- You need real TUI features (scrollback-safe multi-line dashboards, mouse input, resize handling) — that's a different problem needing a real terminal library, not this pattern

## Results

- Verified: compiles and runs clean under `zig run` on Zig 0.16.0 (aarch64-macos); `isTty` correctly reported `false` when output was piped through `od`, confirming the gate suppresses animation into non-terminal destinations as designed.
