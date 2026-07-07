Sync Claude Code memory to a private GitHub repo (`foreman-memory`) to make it portable across machines. Argument: `backup` (default) or `restore`.

## Step 0 — Locate this session's memory directory

Memory is stored per working directory, encoded by replacing `/` with `-`:

```bash
# With 4orman-tools (preferred):
GH_INFO="$(4orman-tools gh-user)"     # {"authenticated": bool, "login": "string"}
# Fallback:
gh auth status        # must be authenticated
OWNER="$(gh api user -q .login)"

MEM="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
echo "memory dir: $MEM"
```

If `authenticated` is false (or fallback exits non-zero): tell the user to run `gh auth login` and stop.

(When launched via `4orman-ai`, `pwd` is the 4ORMan workspace, so this resolves to that session's memory.)

## backup — push local memory up

```bash
mkdir -p "$MEM" && cd "$MEM"
[ -d .git ] || { git init -q -b main; printf '.DS_Store\n' > .gitignore; }
# Create the private repo on first run if it doesn't exist, and wire the remote.
git remote get-url origin >/dev/null 2>&1 || \
  gh repo create "$OWNER/foreman-memory" --private --source=. --remote=origin 2>/dev/null || \
  git remote add origin "https://github.com/$OWNER/foreman-memory.git"
git add -A
git commit -q -m "Memory sync $(date +%Y-%m-%d)" || echo "nothing to commit"
git push -q -u origin main
```

Report what was pushed (changed files). The repo is **private** — confirm that before pushing if it had to be created.

## restore — pull memory down onto this machine

```bash
mkdir -p "$(dirname "$MEM")"
if [ -d "$MEM/.git" ]; then
  cd "$MEM"
  git fetch origin --quiet
  git pull --ff-only            # skip + warn if dirty or diverged; never clobber local memory
elif [ -d "$MEM" ] && [ -n "$(ls -A "$MEM" 2>/dev/null)" ]; then
  echo "⚠ $MEM already has files but isn't a clone — back them up, then re-run, or merge by hand."
else
  git clone "https://github.com/$OWNER/foreman-memory.git" "$MEM"
fi
```

After a restore, tell the user memory is now available and will load in the next session.

## Rules

- The memory repo MUST be private — it can contain personal/work context. Never make it public.
- Never put secrets (keys, tokens, passwords) in memory files; this command pushes them to GitHub.
- restore is fast-forward only — never overwrite or force-merge local memory; if it conflicts, surface it and stop.
