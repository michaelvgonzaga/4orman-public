Delete all disposable cache entries automatically. No confirmation — runs immediately and reports what was cleared.

## What gets deleted

Disposable cache only — entries in `~/.cache/4orman-tools/`. These are outlines, parse summaries, and build artifacts that regenerate on next access. Nothing in `~/.4orman/` is touched (Permanent Truth and Pinned Knowledge are never deleted).

## Execution

```bash
# Count before
before=$(4orman-tools metrics 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('cacheEntries',0))" 2>/dev/null || echo "?")

# Clear disposable cache
find ~/.cache/4orman-tools -type f -delete 2>/dev/null

# Count after
after=$(4orman-tools metrics 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('cacheEntries',0))" 2>/dev/null || echo "0")
```

Report: "Disposable cache cleared — $before entries removed. Permanent Truth and Pinned Knowledge untouched."

## What is NOT deleted

- `~/.4orman/ledger.json` — Permanent Truth
- `~/.4orman/session-snapshot.json` — Permanent Truth
- `~/.4orman/profile.json` — Permanent Truth
- `~/.4orman/state/` — Permanent Truth
- `~/.4orman/pending-promotions.json` — Permanent Truth
- Pinned knowledge cache entries (these regenerate from source on next access if invalidated)
