# 4ORMan: Ledger Protocol — Rigged Rock-Paper-Scissors

**Source:** CLAUDE.md guardrails + 4orman-tools source (`computeLedger*` in root.zig) + direct experiment
**Last verified:** 2026-07-01
**Confidence:** High — derived directly from the implementation

---

## What we know

### The game is rigged toward mathematical truth

Every contested decision between Claude reasoning and Zig stored data runs through this protocol. Neither player wins automatically — the scoring is designed to favor whoever has the stronger mathematical backing.

### Scoring formula (Zig computes, Claude never self-certifies)

```
4orman-tools ledger score <question> <sources-json>
```

Returns `{ composite, sample_count, winner, void, reason, zig_entry_found, zig_entry_stale }`.

Per source: cited URL retrieved this session + exact claim = 10 pts; training memory alone = 0 pts; contradicted by another source = −10 pts.

`composite = total_points / (sample_count × 10) × 100`

Minimum 10 sources or automatic void. Composite must reach exactly 100% for a Claude win.

### Win/void conditions

**Claude wins when ALL FOUR hold:**
1. Composite = 100%
2. ≥10 sampled sources retrieved online this session
3. Every source cited with exact URL and specific claim
4. No valid non-stale Zig ledger entry exists for this question

**Zig wins when ALL THREE hold:**
1. A ledger entry exists at `~/.4orman/ledger.json`
2. Entry is not stale (recorded within 365 days)
3. Claude cannot produce 10 verified sources that contradict it

**Round is void when:** composite <100%, fewer than 10 sources, or evidence contradictory. No promotion, no decision.

**Tiebreaker:** Zig wins. A 100% Claude score that agrees with a valid Zig entry confirms the entry — Zig retains the win.

### Storage format

File: `~/.4orman/ledger.json`
Structure: `{ "entries": [ { id, winner, question, reasoning, recorded_at, revalidation_due_ts, is_stale } ] }`

- `id` — first 16 hex chars of sha256(winner:question:date)
- Question matching — case-insensitive substring both directions (conservative: Zig wins more than it should, never less)
- Append-only — old entries are never deleted, only superseded by newer entries on the same question
- Staleness — `revalidation_due_ts` = recorded_at + 365 days in Unix time

### Promotion gate

Only a confirmed win triggers promotion:
- Claude win → capability promoted to permanent Zig subcommand or worker immediately
- Zig win → stored entry confirmed, no new build needed
- Void → no promotion

### Session start check

`4orman-tools ledger check-stale` runs at every session start. Stale entries surface immediately — Claude never silently relies on outdated Zig data.

---

## What we're not sure about

- Question matching via substring is conservative but may produce false positives if two different questions share a long common phrase. No case observed yet.
- The 365-day staleness window is arbitrary. Fast-moving domains (API behavior, tool versions) may need shorter windows — not yet implemented.

---

## How this affects our work

- Before reasoning about any contested claim, run `4orman-tools ledger show` first. If Zig has a stored entry (non-stale), use it. Zero tokens.
- Never score your own round — call `ledger score` and read the JSON verdict.
- Training memory alone scores 0. A claim backed only by training memory can never win a round.
- After a confirmed win, call `4orman-tools ledger record <winner> <question> <reasoning>` immediately — do not defer.
