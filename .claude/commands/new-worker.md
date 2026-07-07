Create a new language worker in `_workers/` — a single-file, stdlib-only script that Zig invokes via `4orman-tools worker-run` and returns structured JSON.

## Step 1 — Capability check

```bash
4orman-tools capability-check <what you need>
```

If `available: true` — a native Zig subcommand already covers it. Use that instead.

## Step 2 — Spec the worker

Answer before writing a line:
1. **What is the single responsibility?** (one sentence — if it takes two sentences, split it into two workers)
2. **What language?**
   - Python 3 — web, ML, data processing, scripting (always available, best stdlib)
   - Node.js — browser APIs, JS ecosystem integration
   - Go — concurrent I/O, compiled performance
   - Rust — memory-safe high-performance (compile-then-run via cargo)
   - Bash — shell composition (last resort)
3. **What goes in? (stdin JSON schema)**
4. **What comes out? (stdout JSON schema)**
5. **Resource limits?** (max pages, max bytes, timeout, rate limit)

No external dependencies. If a dep is truly required, document exactly why and gate it with a graceful error if absent.

## Step 3 — Scaffold

Create `_workers/<category>/<name>.<ext>` following the senior-quality standards in `_workers/README.md`:
- Module docstring with full I/O contract
- `{"success": false, "error": "..."}` on any failure — never crash
- Rate limiting for network workers
- Robots.txt compliance for web crawlers
- Hard caps on memory, time, and output size
- Idempotent — same input → same output, no side effects

## Step 4 — Test

```bash
echo '{"<required_field>": "<value>"}' | 4orman-tools worker-run <lang> _workers/<category>/<name>.<ext>
<lang> --version
```

Verify: `success: true`, correct output shape, no raw text in JSON values. Note today's date and the runtime version — that's the known-good baseline for Step 5.

## Step 5 — Register

Add a row to the `_workers/README.md` catalog table, including the `Verified` date + runtime version from Step 4 — this is what you diff against later when a stack upgrade might have broken it:
```
| `<category>/<name>.<ext>` | <Lang> | `worker-run <lang> _workers/<category>/<name>.<ext> '<json>'` | <one-line purpose> | <YYYY-MM-DD> (<lang> <version>) — `success: true`, `confidence: <n>` |
```

## Step 6 — Promote check

Run `4orman-tools capability-promote "<what this worker does>"`. If score ≥ 70, the core logic is a Zig promotion candidate — note it but don't block on it now.

---

## Language worker capability matrix

| Need | Best choice | Why |
|------|-------------|-----|
| Web crawl / scrape | Python | `urllib` + `html.parser` stdlib — robust, handles encoding |
| Structured data transform | Python | `json` + `csv` stdlib — sufficient for 99% of ETL |
| Concurrent HTTP | Go | goroutines + `net/http` — outperforms Python 10× for parallel fetches |
| Browser JS execution | Node.js | Only language with a real browser-compatible JS runtime |
| High-perf binary processing | Rust | Zero-cost abstractions — for byte-level work that Python can't sustain |
| Shell composition | Bash | Only when the whole task is piping existing CLIs together |
| Numerical / ML | Python | `statistics` stdlib covers most needs; numpy if truly needed (document it) |
