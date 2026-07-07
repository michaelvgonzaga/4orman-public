# Release Notes

**Works well for:** Auto-generating release notes for 4ORMan itself or any project inside 4ORMan, based on git commits since the last tag
**Confidence:** High

## The pattern

### Step 1 — Get commits since last release

```bash
# With 4orman-tools (preferred — latestTag + pre-categorized commits in two calls):
4orman-tools release-info <repo-path>          # get latestTag → use as PREV
4orman-tools commits <repo-path> <latestTag>   # pre-categorized JSON array
# Fallback:
PREV=$(git -C <repo-path> describe --tags --abbrev=0 <new-tag>^ 2>/dev/null || echo "")
git -C <repo-path> log ${PREV:+"$PREV"..}"<new-tag>" --oneline
```

### Step 2 — Categorize commits

Group commits into buckets based on message patterns:

| Bucket | Keywords to look for |
|--------|---------------------|
| New features | `add`, `new`, `create`, `introduce`, `implement` |
| Fixes | `fix`, `bug`, `error`, `broken`, `correct`, `resolve` |
| Improvements | `update`, `improve`, `enhance`, `refactor`, `optimize` |
| Removals | `remove`, `delete`, `drop`, `deprecate` |
| Docs | `readme`, `docs`, `document`, `comment` |
| Other | anything that doesn't fit above |

### Step 3 — Write the notes

Use this structure:

```markdown
## What's new in v<version>

### ✨ New
- <feature> — <one line description>

### 🛠 Fixed
- <fix> — <one line description>

### 📈 Improved
- <improvement> — <one line description>

### 🗑 Removed
- <removal> — <one line description>

### 📝 Docs
- <doc change>
```

Skip any section that has no entries. Never include the Co-Authored-By lines from commit messages.

For projects, focus on what the user can now do differently, not what files changed.

### Step 4 — One-liner title

Write a short title (under 60 chars) that captures the most important thing in this release:

- Good: `v1.2.0 — Public/private model, 4orman-ai rename`
- Bad: `v1.2.0 — Various updates and fixes`

## When to use it

- **Automatically after every project commit** — wired into `CLAUDE.md` guardrails (framework and project template); checks if unreleased commits have accumulated and surfaces a reminder to run `/release`. Does not generate notes unprompted — just flags that a release may be due.
- Automatically during `/release` (Step 3) and `/brew-release` (Step 7) — generates the release body and CHANGELOG entry
- When the user asks "write release notes", "what changed since last release", or "generate changelog"
- When completing a project milestone and wanting to document progress
- For 4ORMan itself: if a command or skill file changed, name it specifically.

## When NOT to use it

- When there are no commits since the last tag (nothing to document)
- When the user has already written release notes manually — don't overwrite them

## Rules

Never invent changes not in the commits. If a commit message is too vague to categorize, file it under Other rather than guessing.
