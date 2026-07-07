Manual private release — pauses for explicit confirmation before each push and tag. GitHub release only, no Homebrew formula update. Use this when you want to review each step before it runs.

## Step 1 — Gather info

Get project path (ask if unclear). Then:

```bash
4orman-tools release-info <project-path>
4orman-tools repo-info <project-path>
```

Show `suggestedNext` and ask the user to confirm or override the version.

Check `isDirty` — show dirty files and ask: "Commit these first, or release from current state?" Abort if they choose to commit first.

## Step 2 — CHANGELOG preview

Generate release notes using the `release-notes` skill. Show the draft notes and ask: "Any changes before I continue?"

Apply edits if requested.

## Step 3 — Tag (confirm before running)

Show: `Will run: git tag v<version> && git push origin v<version>` — ask "OK?" before running.

## Step 4 — GitHub release (confirm before running)

Show the release title and notes. Ask "Publish this release?" before running `4orman-tools gh-release`.

## Step 5 — Summary

Print:
```
✓ v<version> released (private)

  GitHub: https://github.com/<owner>/<repo>/releases/tag/v<version>
```
