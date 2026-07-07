Wire up per-machine Stop hooks in `~/.claude/settings.json` — auto-sync memory and auto-push project repos. Idempotent; run once per machine.

## Step 0 — Preconditions

```bash
# With 4orman-tools (preferred):
4orman-tools gh-user
# Fallback:
gh auth status                 # git pushes need auth
git --version
```

If `authenticated` is false (or fallback exits non-zero), tell the user to run `gh auth login` first and stop.

## Step 1 — Read existing settings

Read `~/.claude/settings.json`. If it doesn't exist, treat it as `{}`. **Preserve everything already there** (theme, permissions, other hooks) — you are merging, not replacing.

## Step 2 — Ensure these two Stop hooks exist (idempotent)

The two hooks (identified by `statusMessage`). If a `Stop` hook with the same `statusMessage` already exists, leave it; only add the missing ones.

**Hook A — "Syncing memory…"** (auto-commit + push the memory repo when it changed):
```
d="$HOME/.claude/projects/$(printf '%s' \"$HOME\" | sed 's#/#-#g')/memory"; if [ -d \"$d/.git\" ]; then cd \"$d\" && git add -A 2>/dev/null; git diff --cached --quiet 2>/dev/null || { git commit -qm \"Memory auto-sync $(date +%FT%T)\" 2>/dev/null; git push -q 2>/dev/null || { git pull --rebase -q 2>/dev/null && git push -q 2>/dev/null || git rebase --abort 2>/dev/null; }; }; fi; exit 0
```

**Hook B — "Pushing project commits…"** (push any `~/4orman` project repo with a remote + unpushed commits):
```
for p in \"$HOME/4orman\"/*/; do [ -d \"$p/.git\" ] || continue; git -C \"$p\" rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1 || continue; [ -n \"$(git -C \"$p\" log @{u}..HEAD --oneline 2>/dev/null)\" ] || continue; git -C \"$p\" push -q 2>/dev/null || { git -C \"$p\" pull --rebase -q 2>/dev/null && git -C \"$p\" push -q 2>/dev/null || git -C \"$p\" rebase --abort 2>/dev/null; }; done; exit 0
```

Merge them under `.hooks.Stop` so the result looks like (alongside any existing settings):
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "<Hook A>", "timeout": 30, "statusMessage": "Syncing memory…" },
          { "type": "command", "command": "<Hook B>", "timeout": 45, "statusMessage": "Pushing project commits…" }
        ]
      }
    ]
  }
}
```

Write the merged file.

## Step 3 — Validate

```bash
# With 4orman-tools (preferred — checks both hooks by statusMessage in one call):
4orman-tools validate-hooks
# Fallback:
jq -e '.hooks.Stop[].hooks[] | select(.type=="command") | .command' ~/.claude/settings.json
```
Both `memorySync` and `autoPush` true (or fallback exit 0 + prints both commands) = correct. If `validate-hooks` returns false for either, or the fallback errors, the JSON is malformed — fix it (a broken settings.json silently disables ALL settings from that file).

Then run each stored command once to confirm it executes clean:
```bash
jq -r '.hooks.Stop[0].hooks[].command' ~/.claude/settings.json | while IFS= read -r c; do echo '{}' | bash -c "$c"; echo "exit $?"; done
```

## Step 4 — Activate + report

Hooks edited mid-session don't fire until Claude Code re-reads settings. Tell the user:
> Automation installed. Open `/hooks` once (or restart Claude Code) to activate it this session — it's automatic in all new sessions.

## Rules

- Never duplicate a hook already present; never clobber unrelated settings.
- Paths must use `$HOME`, never hardcoded usernames.
- Warn the user that auto-push publishes every commit — note this for public repos.
