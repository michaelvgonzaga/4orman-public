# Rubric-Driven Verification

**Works well for:** Any output where "quality" is subjective — AI-generated reports, document drafts, structured data exports, code review outputs, anything where a human might disagree about whether it's good enough
**Reference implementation:** an internal project (2026-06-28)
**Confidence:** High

## The pattern

Write the rubric before writing verification code or generating output.

### Step 1 — Write the rubric first

Create `[project]/knowledge/[output-type]-rubric.md` with:
- One criterion per section, each with a clear **Fail condition** (not just a description of what good looks like)
- A scoring table: Pass / Revise / Reject, with explicit triggers for Reject (e.g., "if criterion 2 or 7 fails, always Reject — never Revise")
- A version and changelog

### Step 2 — Build the structural checker against the rubric

The checker enforces what can be checked mechanically — presence, format, required values. It does not try to evaluate quality.

- Check every criterion that has a mechanical signal (section present, field contains a required value, count meets a minimum)
- Each failure message names the criterion by the same name used in the rubric document
- Return a list of failures — empty list = pass; non-empty = fail
- Never silently skip a criterion because another one already failed

### Step 3 — Surface the gap honestly in output

When the checker passes, tell the user what it checked and what it did not:

```
**Verification: PASSED (structural)** — [what was checked].

> Note: Structural checks do not verify [what was not checked].
> Before acting on this output, a human reviewer should confirm: [list the unverified rubric criteria].
```

When the checker fails, name each failure specifically so the user (or a regeneration loop) knows exactly what to fix.

### Step 4 — Use the rubric as the critic's brief

When running `/verify-output`, hand the rubric criteria directly to the critic fork as the evaluation checklist. The critic's job is to find gaps between the rubric and the actual output — not to invent new criteria.

## When to use it

- The output type has multiple quality dimensions that can't all be checked mechanically
- The project will generate many instances of this output (a report, a document, a structured artifact)
- You need a human reviewer and an automated checker to agree on what "done" means

## When NOT to use it

- The output is deterministic code with a test suite — tests are the rubric
- The quality criteria are purely subjective with no mechanical signals at all — a rubric won't help and will create false confidence

## Results

- **An internal project** — rubric document written before `rubric.py`; during `/verify-output`, critic caught that the confidence check was conditional on other failures passing (violating the rubric's "always evaluated" intent). Bug fixed before shipping. Pattern worked exactly as intended.
