Find a project, file, or repo — wherever it lives — bring it into 4ORMan, scan it, and iterate to production-ready.

---

## Phase 1 — Find it

The user may give you a name, a description, a partial path, or nothing at all. If the user gave a URL (GitHub, GitLab, etc.), skip the search — that's the source.

Search `~`, common dirs (`~/Desktop`, `~/Downloads`, `~/Documents`, `~/Projects`), and `/private/tmp`. On macOS, `/tmp` is a symlink to `/private/tmp` — search both.

Present matches with path, type, and recency. Ask which one (or accept a path/URL directly). Wait for confirmation.

---

## Phase 2 — Check if already absorbed

Check `ls <4orman-root>/` and `_projects.md` for an existing match. If found, tell the user and stop.

---

## Phase 3 — Absorb

Ask the user two questions (one at a time):

1. **Name:** "What should this project be called inside 4ORMan? (lowercase, no spaces — e.g. `shopify-theme`)"
2. **Visibility:** "Public or private?"
   - **Public project** — pushed to a public GitHub repo, anyone can see it
   - **Private project** — pushed to a private GitHub repo, only you
   - **Public plugin** — extends 4ORMan, listed in `plugins.public.yml`, anyone can install via `/setup`
   - **Private plugin** — extends your 4ORMan privately, listed in `plugins.local.yml`

Then copy the source. Use `rsync` to exclude dependency dirs and any existing `.git` history — the absorbed project gets a fresh git history inside 4ORMan:

```bash
rsync -a \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='.next' \
  --exclude='vendor' \
  --exclude='*.zip' \
  <source-path>/ <4orman-root>/<name>/
```

If source is a git repo URL:
```bash
git clone --depth=1 <url> <4orman-root>/<name>
rm -rf <4orman-root>/<name>/.git
```

If source is a single file, create a minimal structure:
```bash
mkdir -p <4orman-root>/<name>/src
cp <source-path> <4orman-root>/<name>/src/
```

**On any failure during copy:** immediately remove the partial directory and tell the user what failed — do not leave a broken state.
```bash
rm -rf <4orman-root>/<name>
```

Check git version; if 2.28+: `git init -b main`, else `git init` + `git symbolic-ref HEAD refs/heads/main`. Then: `git add . && git commit -m "Initial import"`.

If the user chose **public or private project**, apply the `github-repo` skill (`_skills/github-repo.md`) to create the GitHub repo and wire up the remote now.

**If public plugin:** copy into `.claude/commands/` (if it's a runnable command) or `_skills/` (if it's a playbook/pattern). Ask if unclear.

---

## Phase 4 — Deep scan

Get a structural overview first:

```bash
# With 4orman-tools (preferred):
4orman-tools scan <4orman-root>/<name>
# Fallback: ls -la <4orman-root>/<name>
```

The JSON gives you: `framework` (tech stack), `keyFiles` (manifest/config files present), `depCount` (dependency scale), `dirMap` (directory tree), `entryPoint` (detected main file), `files` (flat file inventory sorted largest-first, capped at 500), `fileCount` (total). Use `entryPoint` and the top entries in `files` to decide which files to read first — do not `find` or `ls` when the scan result is available.

Read everything. Do not skim.

Go through all files in the project and build a complete picture:

**What it is**
- What does this do? One sentence.
- What problem does it solve?
- Who is it for?
- What tech stack / language / framework?

**What works**
- List what's functional and solid.

**What's broken**
- Errors, bugs, missing error handling, hardcoded values that will fail in prod.

**What's missing**
- No README? No tests? No env config? No deploy setup? Missing features the user probably needs?

**What's weak**
- Code quality issues, security risks, performance problems, bad patterns.

**Production gap**
- What specifically needs to happen before this is production-ready?

Write a `spec.md` based on what you find using the standard 4ORMan spec template (`_templates/spec_output.md`). The milestones should map to closing the production gap.

Write a `CLAUDE.md` based on `_templates/project_claude.md`.

Show the user the scan summary and spec draft. Ask: **"Does this look right? Any corrections before I start fixing?"**

Wait for sign-off before Phase 5.

---

## Phase 5 — Iterate to production

Work through the spec milestones in order. For each task:

1. Fix it
2. Run `/verify-output` — self-review + independent critic
3. Fix what the critic flags
4. Mark the task complete in spec.md
5. Report to the user: what was fixed, what's next

After each milestone, report: what was fixed, what's remaining, and ask: "Continue? (yes / adjust scope / stop here)"

---

## Phase 6 — Production gate

When all milestones are done, run a final `/verify-output` against the full M3 "Done when..." criteria from spec.md.

If it passes: update `_projects.md` status to `active` and report the project path and spec path. If it fails: loop back to Phase 5.

---

## Rules

- If a GitHub repo can't be cloned (private, auth required), tell the user and ask them to clone manually first.
- Roll back the partial directory on any copy or git init failure.
