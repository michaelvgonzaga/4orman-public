Run the full quality gate — build + tests — and get a severity-bucketed verdict before promoting or merging.

## Step 1 — Resolve path

If inside a project directory (has `spec.md` and `CLAUDE.md`), use it. Otherwise ask.

## Step 2 — Run quality gate

```bash
4orman-tools quality-gate <abs-path>
```

## Step 3 — Surface verdict

Parse the JSON and report:

**Verdict line:** "`PASS`" or "`FAIL`" — `<build_tool>` build, `<test_framework>` tests (`<tests_passed>` passed, `<tests_failed>` failed).

**If findings exist**, list by severity:

```
CRITICAL  <source>  <file>:<line>  <message>
HIGH      <source>  <file>:<line>  <message>
MEDIUM    <source>  <file>:<line>  <message>
```

**Verdict rules:**
- `fail` on any Critical or High → block the promote/merge.
- `pass` with Medium findings → surface them, let the user decide.
- `pass` with no findings → clear to proceed.

## Rules

- Never override a `fail` verdict — it is a hard blocker until fixed.
- If neither build nor tests ran (no system detected), say so explicitly: "No build system or test framework detected — gate cannot evaluate."
- Do not suggest fixes unless asked.
