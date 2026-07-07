Cut a GitHub release — update CHANGELOG.md, tag, push, create a GitHub release. For Homebrew formula distribution, use `/brew-release`.

## Step 1 — Gather info

Ask the user (one at a time if unclear):

1. **Project repo path** — the local path to the project being released. If you are already inside a project directory (has a `spec.md` and `CLAUDE.md`), use it without asking.
2. **Version number** — get release pre-flight data:

```bash
# With 4orman-tools (preferred — latestTag, suggestedNext, commitsSince, isDirty in one call):
4orman-tools release-info <path>
# Fallback:
git -C <path> describe --tags --abbrev=0 2>/dev/null
```

Use `suggestedNext` as the default. If no tags exist, suggest `v1.0.0`. Show the suggestion and let the user confirm or override.

Do not proceed until you have both.

## Step 2 — Pre-flight checks

Run and stop on any failure:
- **Dirty repo** — use `isDirty` from `4orman-tools release-info` (if used in Step 1), or `git -C <project-path> status --porcelain`
- **Tag already exists** — `4orman-tools tag-exists <project-path> <version>` (preferred), or `git -C <project-path> tag | grep "^v<version>$"`
- `git -C <project-path> remote get-url origin` — no remote

## Step 3 — Generate release notes

Get commits since the previous tag. If `4orman-tools` is in PATH, use it — the output is pre-categorized JSON:

```bash
PREV=$(git -C <project-path> describe --tags --abbrev=0 2>/dev/null || echo "")
# With 4orman-tools (preferred):
4orman-tools commits <project-path> $PREV
# Fallback:
git -C <project-path> log "$PREV"..HEAD --oneline
```

Categorize into New / Fixed / Improved / Removed / Docs. Skip internal tracking commits (M1/M2/M3 milestones, gate results, Co-Authored-By lines). Focus on what the user can now do differently.

## Step 4 — Preview and confirm

Show the proposed version, repo, and release notes. Ask for explicit confirmation. Apply any edits before continuing.

## Step 5 — Update CHANGELOG.md

Check whether `CHANGELOG.md` exists in the project root:

```bash
ls <project-path>/CHANGELOG.md
```

**If it exists:** Prepend the new entry after the `# Changelog` header (before the previous `## [x.y.z]` entry).

**If it does not exist:** Create it with this header, then the new entry:

```markdown
# Changelog

All notable changes to this project are documented here.

## [<version>] — <date>

### ✨ New
...

### 🛠 Fixed
...
```

Use today's date. Only include sections that have entries — skip empty ones.

## Step 6 — Commit CHANGELOG.md

```bash
git -C <project-path> add CHANGELOG.md
git -C <project-path> commit -m "Release v<version>"
```

## Step 7 — Tag and push

```bash
git -C <project-path> tag v<version>
git -C <project-path> push origin main
git -C <project-path> push origin v<version>
```

## Step 8 — Create GitHub release

Get owner/repo (needed for `gh release create --repo`):

```bash
# With 4orman-tools (preferred — parses SSH and HTTPS automatically):
4orman-tools repo-info <project-path>
# Fallback:
git -C <project-path> remote get-url origin
# SSH:   git@github.com:owner/repo.git  → owner/repo
# HTTPS: https://github.com/owner/repo.git → owner/repo
```

Then create the release. Write the confirmed notes to a temp file first, then:

```bash
# With 4orman-tools (preferred — avoids heredoc/quote escaping):
# Write notes to $NOTES_FILE, then:
4orman-tools gh-release <owner> <repo> v<version> "v<version> — <summary>" $NOTES_FILE
# Fallback:
gh release create v<version> \
  --repo <owner>/<repo> \
  --title "v<version> — <one-line summary from release notes>" \
  --notes-file $NOTES_FILE
```

## Step 9 — Summary

Print:

```
Released v<version>

  GitHub release: https://github.com/<owner>/<repo>/releases/tag/v<version>
  CHANGELOG.md updated and committed

To install / update:
  git clone https://github.com/<owner>/<repo>.git   ← fresh install
  git pull                                            ← update existing clone
```

## Rules

- Never release a dirty repo — always check first.
- Never skip the user preview in Step 4 — they must confirm before any tag or push.
- Never invent release notes — only categorize what is in the commits.
- If any step fails, stop and report the exact error. Do not continue past a failure.
- For Homebrew formula distribution (tap + SHA256 + formula update), use `/brew-release` instead.
