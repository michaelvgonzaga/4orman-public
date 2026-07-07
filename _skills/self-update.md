# Self-Update

**Works well for:** Keeping 4ORMan current by checking for upstream changes on every session start or on demand
**Confidence:** High

## The pattern

At the start of every session (or when the user asks), silently check if 4ORMan is behind its remote.

### With 4orman-tools (preferred)

If `4orman-tools` is in PATH, use it — one call, no shell reasoning:

```bash
git -C <4orman-root> fetch origin main --quiet
4orman-tools status <4orman-root>
```

Read the JSON: if `upToDate` is `true`, say nothing and continue. If `false`, surface the update prompt below using `behindBy` for the commit count.

### Without 4orman-tools (fallback)

```bash
# 1. Fetch without merging
git -C <4orman-root> fetch origin main --quiet

# 2. Compare local vs remote
LOCAL=$(git -C <4orman-root> rev-parse HEAD)
REMOTE=$(git -C <4orman-root> rev-parse origin/main)
```

**If equal** — up to date, say nothing and continue.

**If different** — surface before starting work.

## Update prompt (when behind)

Fill in the commit list and file count before showing:

```bash
# With 4orman-tools (preferred):
4orman-tools changes-preview <4orman-root>
# Fallback:
git -C <4orman-root> log HEAD..origin/main --oneline
git -C <4orman-root> diff --name-only HEAD..origin/main | wc -l
```

Then surface:

```
⚠ 4ORMan update available.

Changes incoming:
  <one line per commit from changes-preview .commits[].message, or git log --oneline output>

Files affected: <changes-preview .filesChanged, or wc -l output>

Update now? (yes / no — I'll remind you again next session if no)
```

If yes — check for local uncommitted changes first:

```bash
git -C <4orman-root> status --porcelain
```

If clean, pull:

```bash
git -C <4orman-root> pull origin main --ff-only
```

If dirty — tell the user which files are modified and stop. Do not pull over uncommitted changes.

If `--ff-only` fails (diverged) — stop, show the user the divergence, do not force anything.

## When to use it

- **Automatically at the start of every session** — wired into `CLAUDE.md` guardrails, no manual trigger needed
- Whenever the user says "check for updates", "is 4orman current", "update 4orman", or similar
- Before running `/new-project` or `/absorb` — stale commands can produce outdated behavior

## When NOT to use it

- When the user is mid-task and explicitly says not to interrupt
- In offline environments with no git remote access — skip silently if `git fetch` times out
