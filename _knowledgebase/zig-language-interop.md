# Zig: Language Interop Policy

**Source:** Architectural decision from 4orman-tools design session
**Last verified:** 2026-06-30
**Confidence:** High — derived from actual 4orman-tools implementation and Wave 1-4 roadmap analysis

## What we know

### Zig handles natively (no workers needed through Wave 3)
- File I/O, directory walks, string matching, JSON output, SHA256 hashing
- Subprocess spawning to existing CLI tools (`git`, `gh`, `go test`, `cargo test`, `npx jest`, etc.)
- Cache read/write (L5 disk cache)
- Pattern-based parsing (error parsing, stack traces, YAML/TOML/JSON field extraction)
- All Wave 1 subcommands: `run-tests`, `build`, `env-inspect`, `symbol-find`, `secret-scan`
- All Wave 2 subcommands: `git-cache`, `project-state`, `delta-context`, `shell-run`
- All Wave 3 subcommands: `quality-gate`, `validate-schema`, `prod-ready`

### When another language is uniquely justified

| Language | Unique capability | No Zig/CLI equivalent? |
|----------|-------------------|------------------------|
| Python | numpy, pandas, ML inference, ONNX, requests (complex HTTP auth) | Yes — no Zig equivalents |
| Python | AST analysis for Python source | Only `ast.parse()` gives full fidelity |
| Node | JS/TS AST parsing via `typescript` API | Only TypeScript compiler gives type info |
| Node | npm/yarn lockfile deep analysis | Partial CLI support; full analysis needs the API |
| Go, Rust | Nothing unique for this use case | All their strengths have CLI surfaces |

### What does NOT justify a language worker
- Running shell commands → Zig subprocess
- Parsing JSON/YAML/TOML → Zig has parsers
- Reading files → Zig I/O
- Calling git/gh → Zig subprocess to system binaries
- Simple string matching / regex → Zig string matching (no regex engine in stdlib, but pattern matching covers 95% of cases)

## The decision tree

```
Task requires a library (not a CLI)?
  YES → Is there a Zig equivalent or stdlib solution?
          YES → use Zig
          NO  → Is there a CLI tool that exposes the same capability?
                  YES → Zig subprocesses the CLI
                  NO  → use a language worker (Python/Node subprocess, NOT embedded)
  NO  → use Zig (subprocess to existing CLIs as needed)
```

## Architecture rule: workers are subprocesses, never build dependencies

Zig does NOT link against Python, Node, or any other language runtime. Workers are:
- Separate executables invoked via `std.process.Child`
- Return JSON to stdout (same contract as 4orman-tools subcommands)
- Only instantiated when the task genuinely requires their ecosystem

This is Module 10 (Language Worker Manager), Wave 4. Not relevant until Wave 4.

## Current bottleneck reality

The performance bottleneck is git subprocess spawning (~20ms/call), NOT Zig compute. The M3 Pro CPU cores are idle during most operations. Adding more Zig compute code has zero marginal cost compared to one additional git call.

## What we're not sure about

- Whether `symbol-find` for TypeScript files will need the TypeScript compiler API (Node worker) or whether grep-based pattern matching is good enough for the definition lookup use case. Decision deferred to implementation.
- Whether `context-rank` will need semantic embeddings (Python + embedding model) once the basic hit-count approach hits a quality ceiling. Current approach (hit count + name bonus) is sufficient for Wave 1.

## How this affects our work

- Wave 1-3 implementation: stay pure Zig. If a task seems to require another language, first check if a CLI tool exposes the same capability.
- Wave 4 workers: only add a language when its *library* (not CLI) is the unique requirement. Document the specific library and why no CLI/Zig alternative exists before writing any worker code.
- No bloat: a worker that just calls a subprocess is worse than Zig calling the same subprocess directly. Workers add value only when they use language-native libraries.
