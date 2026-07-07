# knowledge-sync

Push or restore Pinned Knowledge State to/from the private `foreman-knowledge` repo.

Run **push** after any session where CLAUDE.md, ROADMAP.md, or _skills/README.md changes.
Run **restore** on a new machine before the first session.

---

## Push (update remote from local)

```bash
WSROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
KREPO=/tmp/foreman-knowledge-sync

# Clone or pull
if [ -d "$KREPO/.git" ]; then
  git -C "$KREPO" pull --ff-only
else
  GH_USER=$(gh api user --jq .login 2>/dev/null)
  git clone "git@github.com:${GH_USER}/foreman-knowledge.git" "$KREPO"
fi

# Re-extract pinned values — abort on cache miss (hit: false means source must be read first)
_ks_push_entry() {
  local src="$1" key="$2" dest="$3"
  local raw; raw=$(4orman-tools cache-fetch "$src" "$key" 2>/dev/null)
  local hit; hit=$(echo "$raw" | jq -r '.hit')
  if [ "$hit" != "true" ]; then
    echo "ERROR: cache miss for $src/$key — run cache-store from source before pushing" >&2
    return 1
  fi
  echo "$raw" | jq '.value' > "$dest"
}
_ks_push_entry "$WSROOT/CLAUDE.md" guardrails "$KREPO/pinned/claude-md-guardrails.json" || exit 1
_ks_push_entry "$WSROOT/ROADMAP.md" state     "$KREPO/pinned/roadmap-state.json"        || exit 1
_ks_push_entry "$WSROOT/_skills/README.md" outline "$KREPO/pinned/skills-readme-outline.json" || exit 1

# Update meta version
FTVER=$(4orman-tools doctor 2>/dev/null | jq -r '.tools[] | select(.name=="4orman-tools") | .version' || echo "unknown")
jq --arg v "$FTVER" '.foreman_tools_version = $v' "$KREPO/meta.json" > "$KREPO/meta.json.tmp" && mv "$KREPO/meta.json.tmp" "$KREPO/meta.json"

# Commit and push if anything changed
cd "$KREPO"
git add -A
git diff --cached --quiet || git commit -m "Update pinned knowledge — $(date +%Y-%m-%d)"
git push origin main
```

## Restore (warm local cache from remote on a new machine)

```bash
WSROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
KREPO=/tmp/foreman-knowledge-restore
GH_USER=$(gh api user --jq .login 2>/dev/null)
git clone "git@github.com:${GH_USER}/foreman-knowledge.git" "$KREPO"

cat "$KREPO/pinned/claude-md-guardrails.json"  | 4orman-tools cache-store "$WSROOT/CLAUDE.md" guardrails
cat "$KREPO/pinned/roadmap-state.json"          | 4orman-tools cache-store "$WSROOT/ROADMAP.md" state
cat "$KREPO/pinned/skills-readme-outline.json"  | 4orman-tools cache-store "$WSROOT/_skills/README.md" outline

echo "Pinned knowledge restored — next session starts warm."
```

---

## Rules

- `pinned/` files are JSON blobs — the exact value stored by `cache-store`. They are NOT the source files.
- `~/.4orman/ledger.json` is **never** pushed here — it is append-only and device-local.
- Push only after a confirmed source file change, not on every session.
- If a `cache-fetch` returns `hit: false` for a pinned key, rebuild from source first, then push.
- The remote is authoritative for new machines; the local cache is authoritative within the current session.
