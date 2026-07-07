# 4ORMan: Claim-Check Ledger — Design (not yet built)

**Source:** direct user request, 2026-07-05, triggered by a real reasoning error during the first `/study-repo` run against a sibling project
**Last verified:** 2026-07-05
**Confidence:** High — design confirmed with the user, paused before implementation, not yet forked/built.

## What triggered this

During `/study-repo`'s Phase 3 distillation of that project, Claude correctly found that `ROADMAP.md`'s "Active Work" section was stale (claimed "Step 1, nothing built" while `MVP.md` showed 30 verified disciples), but then incorrectly let that finding discount the document's other sections too — including its genuinely durable "Teaching → self-sufficiency model" and "Online/offline execution flow" vision content, which the user then had to point out was actually the project's real mission, not stale planning.

Root cause: Claude conflated "this document's status-tracking is stale" with "this document's other content is equally unreliable," without checking whether the two claim-types even belonged to the same structural section. That check (section boundary via `4orman-tools outline`) was mechanically available and wasn't used.

## Why this needs Zig, not just a Claude-side rule

A pure CLAUDE.md guardrail ("scope findings to their section, don't generalize") relies on Claude remembering to apply it every time — no different from every other guardrail that gets forgotten under load. The user wants Zig to have a genuine, deterministic role in catching this class of error, not just more prose for Claude to (maybe) follow.

The key design constraint, established through discussion: **Zig cannot parse arbitrary English claims** — that requires semantic understanding, which is exactly what Zig structurally lacks in this framework ("Claude decides, Zig orchestrates"). So the mechanism can't be "Zig fact-checks whatever Claude says in prose." Instead: Claude translates its own claim into a **structured, deterministic check** from a fixed, small vocabulary Zig actually understands (reusing `outline`/`grep` logic that already exists), and Zig either confirms/denies it mechanically, or — if the check type isn't one Zig supports — says so honestly rather than staying silent or implying verification that didn't happen.

## Confirmed design

### New ledger category `"claim"`

Reuses existing `LedgerEntry` fields, no new fields needed:
- `domain` — the file path the claim concerns (reusing the field `curriculum` added, same "different meaning per category" convention `winner`/`shadow`/`synthesis` already establish)
- `winner` — the verdict: `"verified"` | `"contradicted"` | `"unverifiable"`
- `reasoning` — the evidence found (grep match, heading name, or the honest "no mechanical check available" statement)

`findLedgerPrecedent` must exclude `category == "claim"` too (same reason as `jungian`/`approach`/`curriculum`/`architecture` — never silently override a tool-choice decision). New sibling lookup `findClaimPrecedent`, same shape as `findApproachPrecedent`/`findCurriculumPrecedent`/`findArchitecturePrecedent`.

### `4orman-tools claim-check <file> <check-type> <check-value> <claim-description>`

- `check-type` — one of a **fixed, small set** Zig actually implements:
  - `contains-text` — literal substring presence (reuses existing grep logic)
  - `not-contains-text` — literal substring absence
  - `section-heading-exists` — does a heading matching `check-value` exist in `file` (reuses existing `outline` heading extraction)
- `claim-description` — Claude's own English framing of what this check demonstrates, stored for the ledger record only. **Zig never interprets this string** — it's metadata, not input to any check logic.
- Ledger-hit (via `findClaimPrecedent`, same `ledgerWordOverlapScore` matching, ≥50, non-stale) → reuse stored verdict, `source: "ledger"`.
- Ledger-miss → run the actual check:
  - Recognized `check-type` → run it, return `mechanicallyVerified: true|false`, `evidence: "<what was found>"`, `source: "check"`.
  - Unrecognized `check-type` → **the honest-disclosure path**: `mechanicallyVerified: null`, `evidence: "no deterministic check available for this claim type — this is Claude's own reading judgment, not Zig-verified"`, `source: "unsupported"`.

### `4orman-tools ledger record-claim <file> <check-type> <check-value> <verified|contradicted|unverifiable> <claim-description>`

Records the outcome for future reuse. `status`/verdict is a required explicit arg (same reasoning as `record-architecture` — `"unverifiable"` has no artifact-emptiness signal to derive it from, unlike `curriculum`'s `status`).

### Worked example against the actual triggering error

```
4orman-tools claim-check ROADMAP.md section-heading-exists "Active Work" \
  "the stale 'nothing built' status claim lives only under this heading, not under the 00-06 phase digest sections above it"
```
→ Zig confirms the heading boundary mechanically → the staleness finding is scoped to that section only. Sibling sections (the phase digest) default to unverified-but-not-suspect, not automatically discounted.

## What's NOT decided yet

- Whether this becomes part of `/study-repo`'s own phases, a general CLAUDE.md guardrail applied whenever Claude reads any document and finds a discrepancy, or both (leaning toward "general guardrail," matching the disclosure-culture precedent of `cacheWired: false`/`needsDecision: true`/`curriculum-check`'s `source: "none"`, but not yet confirmed).
- Exact wording of the CLAUDE.md guardrail invoking this subcommand.
- Whether the `check-type` vocabulary needs to grow beyond the initial three (e.g., a `file-modified-before`/`file-modified-after` date-comparison check was discussed conceptually but not included in the confirmed v1 scope).

## How this affects our work

Paused here, deliberately, before forking to build — this is a design record for resuming later, not yet implemented. Nothing in `4orman-tools` or `4orman`'s CLAUDE.md has been touched for this feature yet.
