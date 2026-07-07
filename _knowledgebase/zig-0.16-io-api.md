# Zig 0.16: std.Io API — Files, Dirs, Processes, and Environment

**Source:** Direct experiment building an internal Zig project against Zig 0.16.0_1 on macOS arm64
**Last verified:** 2026-07-04
**Confidence:** High — all items below were compile-tested and run-tested

## What we know

### Directory handles must be closed manually

`std.Io.Dir.openDirAbsolute(io, path, .{ .iterate = true })` returns a `Dir` value that must be explicitly closed. There is no RAII wrapper.

```zig
const dir = try std.Io.Dir.openDirAbsolute(io, path, .{ .iterate = true });
defer dir.close(io);  // required — omitting this leaks the fd
```

The same applies to `std.Io.Dir.cwd()` — it does not need closing (it's a sentinel), but any `openDir*` result does.

### Child process Term variants are lowercase

`std.process.Child.Term` union tags are lowercase in 0.16:

```zig
const term = try child.wait(io);
return switch (term) {
    .exited => |code| code,   // correct
    // .Exited => ...         // compile error — does not exist
    else => 1,
};
```

### std.process.run — capturing stdout/stderr

`std.process.run` spawns a child, waits for it, and returns owned slices:

```zig
const result = try std.process.run(gpa, io, .{
    .argv = &[_][]const u8{ "rg", "--version" },
    .stdout_limit = std.Io.Limit.limited(512),  // NOT .{ .bytes = 512 }
    .stderr_limit = std.Io.Limit.limited(256),
});
defer gpa.free(result.stdout);
defer gpa.free(result.stderr);
// result.term is Child.Term
```

`std.Io.Limit` is an enum, not a struct. Use `std.Io.Limit.limited(n)` or `.unlimited`.

### Environment variables via init.environ_map

In `pub fn main(init: std.process.Init)`, the process environment is available as `init.environ_map` (type `*std.process.Environ.Map`):

```zig
const home = init.environ_map.get("HOME") orelse "/tmp";
```

`std.posix.getenv` does not exist in Zig 0.16. `std.c.getenv` is the C shim and works but requires a sentinel pointer — use `init.environ_map.get` instead.

### ArrayList is unmanaged — always pass allocator explicitly

`std.ArrayList(T)` in 0.16 has no `.init(allocator)`. Initialize with `.empty` and pass the allocator to every mutation:

```zig
var list: std.ArrayList([]const u8) = .empty;
defer list.deinit(gpa);
try list.append(gpa, item);
```

### Spawning subprocesses

```zig
var child = try std.process.spawn(io, .{
    .argv = argv_slice,
    .environ_map = null,   // null = inherit parent env
    .stdin = .inherit,
    .stdout = .inherit,
    .stderr = .inherit,
});
const term = try child.wait(io);
```

`StdIo` variants: `.inherit`, `.pipe`, `.ignore`, `.close`, `.file`.
Pass `environ_map = null` to inherit; pass `*const Environ.Map` to replace.

### Injecting env vars without cloning the Map

Use `/usr/bin/env KEY=VALUE script args` to inject env vars into a subprocess without needing to clone the parent environment map:

```zig
try argv.append(gpa, "/usr/bin/env");
for (extra_env) |kv| try argv.append(gpa, kv);  // "KEY=VALUE"
try argv.append(gpa, script_path);
```

### Getting current Unix time

`std.time.timestamp()` does not exist in Zig 0.16. Use `Io.Timestamp`:

```zig
const now_ns = std.Io.Timestamp.now(io, .real).nanoseconds;  // i96 nanoseconds
const now_secs = @as(i64, @intCast(@divTrunc(now_ns, 1_000_000_000)));
```

`std.Io.Clock` variants: `.real` (wall clock / Unix epoch), `.monotonic`, `.boottime`, `.tai`.

### git --format with literal strings

`git log --format=SOMEWORD` fails with "invalid --pretty format: SOMEWORD" in git 2.54+ unless the string contains a `%` specifier. Use the `format:` prefix for literal strings:

```
git log --format=format:SOMEWORD   # works — outputs "SOMEWORD" per commit
git log --format=SOMEWORD          # fails — git rejects plain words as format specs
```

Equivalent to `--pretty=format:SOMEWORD`.

### Detecting git repos — worktrees use a file, not a directory

`openDirAbsolute` on `<path>/.git` fails silently in git worktrees because `.git` is a plain text file there (containing `gitdir: /path/to/real/.git`), not a directory. Any repo check that relies on opening `.git` as a directory will return false for worktrees.

Correct approach — use git itself:

```zig
const result = try std.process.run(gpa, io, .{
    .argv = &[_][]const u8{ "git", "-C", repo_path, "rev-parse", "--git-dir" },
    .stdout_limit = std.Io.Limit.limited(256),
    .stderr_limit = std.Io.Limit.limited(256),
});
defer gpa.free(result.stdout);
defer gpa.free(result.stderr);
const is_repo = switch (result.term) { .exited => |c| c == 0, else => false };
```

This returns exit 0 for normal repos, worktrees, submodules, and bare repos with a working tree.

### GeneralPurposeAllocator was renamed to DebugAllocator

`std.heap.GeneralPurposeAllocator` does not exist in 0.16 — compiles fine with `zig test` (which never touches `main()`) but fails with `zig run`/`zig build run`, so it's easy to ship undetected if you only run the test suite:

```zig
var gpa_state: std.heap.DebugAllocator(.{}) = .init;   // not GeneralPurposeAllocator(.{}){}
defer _ = gpa_state.deinit();
const gpa = gpa_state.allocator();
```

### Stdout/stderr in `main()` are `std.Io.File`, not `std.fs.File`

`std.fs.File.stdout()` does not exist. Use `std.Io.File`, and note the writer method is `writerStreaming` (not `.writer`) and takes `io` explicitly — `main` must take `std.process.Init` to get it:

```zig
pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var buf: [4096]u8 = undefined;
    var w = std.Io.File.stdout().writerStreaming(io, &buf);
    try w.interface.print("hello {d}\n", .{42});
    try w.interface.flush();
}
```

## What we're not sure about

- Whether `std.process.Environ.Map.clone` exists and works as documented — it was planned but not exercised in that project (switched to `/usr/bin/env` trick instead)
- Behavior of `StdIo.pipe` on macOS — not tested

## How this affects our work

- Always add `defer dir.close(io)` immediately after any `openDir*` call in a `catch` block that succeeds
- Use `.exited` (lowercase) when matching `Child.Term`
- Use `std.Io.Limit.limited(n)` not struct literal syntax for run options
- Use `init.environ_map.get(key)` for env var access in main
- Initialize all ArrayList values with `.empty`, never `.init(allocator)`
- Use `std.Io.Timestamp.now(io, .real)` for current Unix time; `.nanoseconds / 1e9` for seconds
- Always prefix literal git `--format` strings with `format:` (e.g. `--format=format:MARKER`)
- Use `std.heap.DebugAllocator(.{})` with `.init`, not `GeneralPurposeAllocator` — and run `zig run`/`zig build run` at least once, not just `zig test`, since `main()`-only code paths aren't exercised by the test runner
- Use `std.Io.File.stdout()`/`.stderr()` + `.writerStreaming(io, buf)`, not `std.fs.File`
