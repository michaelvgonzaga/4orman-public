Build the project and surface structured errors with file:line navigation.

## Step 1 — Resolve path

If inside a project directory (has `spec.md` and `CLAUDE.md`), use it. Otherwise ask.

## Step 2 — Run build

```bash
4orman-tools build <abs-path>
```

## Step 3 — Surface results

Parse the JSON output and report:

**If `success: true`:** "Build passed — `<tool>` in `<duration_ms>`ms." List any warnings with file:line.

**If `success: false`:** List each error as:
```
ERROR  <file>:<line>:<col>  <message>
```
Then: "`<count>` error(s) — build failed (`<tool>`). Fix these before proceeding."

**If no build system detected:** "No build system detected in `<path>`. Nothing to build."

## Rules

- Errors block all further work — do not proceed past a failing build.
- Surface warnings even on success so the user can decide whether to address them.
- If `truncated: true`, note: "Error list truncated — run `<command>` directly for the full output."
- Do not suggest fixes unless asked — just surface the errors.
