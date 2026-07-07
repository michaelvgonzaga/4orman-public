Fully automated private release. Shows a single plan, gets one confirmation, then runs all steps without further pauses. GitHub release only — no Homebrew formula update.

## Step 1 — Gather info

Get project path (ask if unclear). Then:

```bash
4orman-tools release-info <project-path>
4orman-tools repo-info <project-path>
```

Use `suggestedNext` as the version. Check `isDirty` — abort if dirty.

## Step 2 — One-time plan

Show exactly this before doing anything:

```
Auto private release plan for <name> v<version>:

  1. Tag v<version> and push to github.com/<owner>/<repo>
  2. Create private GitHub release with auto-generated notes

Proceed? [y/N]
```

Wait for the user to type y. If anything else, abort.

## Step 3 — Execute (no further pauses)

Run all steps from `/release` Steps 2–8. Do not ask for confirmation between steps. Show each step as it runs with a one-line status.

## Step 4 — Summary

Print:
```
✓ v<version> released (private)

  GitHub: https://github.com/<owner>/<repo>/releases/tag/v<version>
```
