Delete disposable cache entries with a preview and explicit confirmation before clearing.

## Step 1 — Preview

Show what will be deleted:

```bash
4orman-tools metrics
```

Report the current `cacheEntries` count and `estimatedTokenSavings`. Then list what the cache contains:

```bash
ls ~/.cache/4orman-tools/ 2>/dev/null | head -20
```

Show: "This will delete N cache entries (SHA256 hash files). These are outlines, parse summaries, and build artifacts — they regenerate automatically on next use. Permanent Truth (~/.4orman/) is not touched."

## Step 2 — Confirm

Ask: "Clear the disposable cache? [y/N]"

If anything other than y: abort with "Cache left intact."

## Step 3 — Clear

```bash
find ~/.cache/4orman-tools -type f -delete 2>/dev/null
```

Report: "Done — disposable cache cleared. Next session rebuilds entries on demand."

## What is NOT deleted

- `~/.4orman/ledger.json` — Permanent Truth
- `~/.4orman/session-snapshot.json` — Permanent Truth
- `~/.4orman/profile.json` — Permanent Truth
- `~/.4orman/state/` — Permanent Truth
- `~/.4orman/pending-promotions.json` — Permanent Truth
