# 4ORMan Workers

Language-specific workers invoked by `4orman-tools worker-run`. Each worker:
- Reads config from **argv[1] as JSON** (when invoked via `worker-run`); falls back to stdin for direct testing
- Writes result to **stdout as JSON**
- Writes errors to **stderr** (never stdout)
- Exits 0 on success, 1 on hard failure
- Uses **stdlib only** — no pip install, no npm install, no go mod tidy

Claude invokes via:
```bash
4orman-tools worker-run python _workers/web/crawl.py '{"url":"https://example.com","max_depth":1}'
```

Zig receives `{ lang, exit_code, stdout, stderr, duration_ms }` — Claude reads JSON, never raw text.

---

## Directory Structure

```
_workers/
├── web/          ← HTTP, crawl, fetch, parse
│   └── crawl.py
├── sys/          ← process, disk, network analysis
└── code/         ← AST, deps, complexity, linting
```

---

## Worker Standards (Senior Quality + Self-Healing)

Every worker must:

1. **Single responsibility** — one task, one file, no shared state
2. **Typed I/O contract** — declare `OUTPUT_SCHEMA = Schema({...})` at module top; document every field in the docstring
3. **Self-heal before escalating** — retry network ops 3× with exponential backoff; partial results are valid with `confidence < 1.0`; never crash with a raw exception
4. **Structured output always** — `{"success": false, "error": "..."}` on failure; `schema_violations` if output diverges from contract; `self_healed: true` if recovery was needed
5. **Confidence score** — every output includes `confidence` (0.0–1.0): ratio of completed work to attempted work. Claude acts on results with `confidence >= 0.8`; investigates below that.
6. **Resource limits** — cap memory, time, and output size explicitly in constants at the top of the file
7. **No external deps** — stdlib only; if a dep is truly required, document why and gate with a graceful error if absent
8. **Rate limiting** — any network worker adds configurable `delay_ms` between requests
9. **Robots.txt** — any web crawler respects robots.txt and identifies itself with a UA string
10. **Idempotent** — same input → same output; no side effects

### Protocol library

Use `_lib/protocol.py` for all workers:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _lib.protocol import Schema, read_input, write_output, retry

OUTPUT_SCHEMA = Schema({"success": bool, "data": list, "duration_ms": int})

if __name__ == "__main__":
    cfg = read_input(required=["url"])
    result = do_work(cfg)
    write_output(result, OUTPUT_SCHEMA)  # validates schema, prints JSON
```

`retry(fn, max_attempts=3, base_delay_ms=500)` — exponential backoff: 0ms → 500ms → 1000ms  
`Schema.validate(result)` — returns `(valid, violations, confidence)`  
`write_output` — adds `schema_violations` if invalid; never silently wrong

---

## Adding a New Worker

Use `/new-worker`. It will:
1. Check if `4orman-tools capability-check` already covers the need
2. Spec the worker (inputs, outputs, constraints, language choice)
3. Scaffold the file with the standard header
4. Test it via `4orman-tools worker-run`
5. Register it here

---

## Worker Catalog

`Verified` = last date this worker was actually run and confirmed `success: true`, plus the runtime version it ran under. When you upgrade a language runtime, diff against this to see exactly what was last known-good and when — don't assume a worker still works just because the file hasn't changed.

| Worker | Lang | Invocation | Purpose | Verified |
|--------|------|-----------|---------|----------|
| `_lib/protocol.py` | Python 3 | *(library — import, do not invoke directly)* | Self-healing protocol: `Schema`, `read_input`, `write_output`, `retry` | — (library, not run directly) |
| `web/crawl.py` | Python 3 | `worker-run python _workers/web/crawl.py '<json>'` | Depth-limited BFS crawler — robots.txt, rate limiting, retry, confidence scoring | 2026-07-04 (Python 3.14.6) — `success: true`, `confidence: 1.0` |
