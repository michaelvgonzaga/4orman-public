# Zig JSON-Contract CLI Subcommand

**Works well for:** Any native CLI whose job is to replace an LLM's inline shell reasoning with a single structured call — dev-tooling binaries, CI helper tools, local automation daemons
**Confidence:** High — the pattern behind every `4orman-tools` subcommand; validated across 40+ subcommands and a full merge/regression cycle

## The pattern

Every subcommand is a pure function: `(args, stdin?) -> JSON on stdout, exit 0` or `error on stderr, exit 1`. Never both. Never partial JSON.

```zig
pub const WidgetResult = struct {
    ready: bool,
    findings: []const Finding,
    confidence: f32 = 1.0,
    self_healed: bool = false,
};

pub fn computeWidget(gpa: Allocator, io: Io, path: []const u8) !WidgetResult {
    // 1. resolve/validate input
    // 2. do the work, collecting partial results even on recoverable error
    // 3. return a fully-formed struct — never an empty or half-built one
}
```

`main.zig` owns argv parsing and `std.json.Stringify` of the result. `root.zig` owns every `compute*` function and is unit-testable without a process boundary.

### Key rules

1. **One JSON shape per subcommand, versioned by addition only.** Adding a field is safe; renaming or removing one is a breaking change — treat it like a public API, because a caller (human or LLM) has already learned the old shape.

2. **Struct fields carry the contract, not prose.** `confidence: f32` and `self_healed: bool` on every result let the caller decide whether to trust the output without parsing free text. A degraded-but-real result beats an error when partial data is still useful.

3. **Path arguments always go through one absolute-path resolver before any `*Absolute` filesystem API.** Relative paths (including `.`) into an API that expects an absolute path are undefined behavior in some runtimes, not a clean error — resolve once, at the top of the function, before any I/O.

4. **Own every string you put in a result struct.** If a struct field borrows a pointer into a buffer the caller frees before reading the result (e.g. a `defer`-freed intermediate array), the output corrupts silently — no crash, just garbage bytes in the JSON. Dupe into the allocator the result actually owns.

5. **Test at two layers.** `zig test` exercises `compute*` functions directly — fast, no process spawn, but never touches `main()`. A separate `zig build run` / `zig run` smoke pass is required to catch anything only reachable through the real entry point (stdout/stdin wiring, arg parsing, allocator setup) — `zig test` alone gives false confidence that the binary works.

6. **Degrade before you escalate.** Retry recoverable failures (network, transient I/O) with backoff; if a partial result is still useful, return it with `confidence < 1.0` rather than failing the whole call. Only exit non-zero when there is truly nothing usable to return.

7. **Scope destructive filesystem checks to what the caller actually controls.** A raw recursive directory walk and a `git ls-files`-scoped walk answer different questions — "everything on disk" vs. "everything this repo would actually publish." Picking the wrong one produces false positives (flagging git-ignored content) or false negatives (missing untracked secrets). Decide which question the subcommand is answering before writing the walk.

## When to use it

- An LLM agent currently spends tokens re-deriving structured facts from raw shell/file output (git status, build errors, dependency lists) on every session
- The same shell pipeline gets hand-written more than once — a sign it's cheap to make deterministic and expensive to keep re-reasoning about
- Output needs to be trusted programmatically (branching logic downstream), not just displayed to a human

## When NOT to use it

- The task is genuinely one-off or exploratory — building a typed contract for something used once is pure overhead
- The answer requires judgment a static function can't encode (the LLM should reason, not a subcommand fake it)
- Output is for a human terminal session only, with no downstream parser — plain text is fine and cheaper to write

## Results

- 40+ subcommands built on this contract in `4orman-tools`; two real bugs caught during the same session by following rules 4 and 5 above (a use-after-free from an un-duped struct field, and a scope-mismatch from reusing a raw walk where a `git ls-files`-scoped one was needed) — both were silent-wrong-output bugs, not crashes, confirming rule 4's premise.
