Run the project's test suite and surface structured failures.

## Step 1 — Resolve path

If inside a project directory (has `spec.md` and `CLAUDE.md`), use it. Otherwise ask.

## Step 2 — Run tests

```bash
4orman-tools run-tests <abs-path>
```

## Step 3 — Surface results

Parse the JSON output and report:

**If `success: true`:** "Tests passed — `<passed>` passed, `<skipped>` skipped in `<duration_ms>`ms (`<framework>`)."

**If `success: false`:** List each failure as:
```
FAIL  <file>:<line>  <test>
      <message>
```
Then: "`<failed>` failed, `<passed>` passed (`<framework>`). Fix these before proceeding."

**If `framework` is null (no test framework detected):** "No test framework detected in `<path>`. Add tests or run manually."

## Rules

- Never interpret failures as warnings — a failing test is a blocker until fixed.
- If `truncated: true`, note: "Output truncated — run the test suite directly for the full list."
- Do not suggest fixes unless asked — just surface the failures.
