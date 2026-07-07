Composite production readiness check — build, tests, quality gate, secrets, and env — before any deploy or promote.

## Step 1 — Resolve path

If inside a project directory (has `spec.md` and `CLAUDE.md`), use it. Otherwise ask.

## Step 2 — Run prod-ready check

```bash
4orman-tools prod-ready <abs-path>
```

## Step 3 — Surface verdict

Parse the JSON and report:

**Header:** "`READY`" or "`NOT READY`"

**If blockers exist:**
```
BLOCKER  [<source>]  <message>
```
"Fix all blockers before deploying."

**If warnings exist:**
```
WARNING  [<source>]  <message>
```
"Warnings do not block deploy but should be reviewed."

**If `ready: true` and no warnings:** "All checks passed — clear to deploy."

## Rules

- A single blocker means `ready: false` — do not proceed to deploy.
- Blockers from `quality-gate` (Critical/High build or test failures) and `secret-scan` (hardcoded secrets) are non-negotiable.
- Warnings from `env-inspect` (missing deps) or `quality-gate` (Medium findings) are advisory.
- Do not suggest fixes unless asked — surface the verdict and let the user decide next steps.
