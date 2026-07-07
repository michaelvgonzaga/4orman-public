# Knowledgebase

Domain knowledge, research, and external signals that improve the accuracy of Claude's work across all projects.

This is shared across all projects in 4orman. Project-specific knowledge lives in `[project-name]/knowledge/`.

---

## What belongs here

- Domain research (e.g., how barista workflows actually work, what coffee certification standards say)
- Industry standards and authoritative sources
- Data schemas and ontologies for a domain
- Findings from external signals (APIs, scraped data, user interviews)
- Patterns that have been validated across multiple projects
- Common failure modes discovered in past work

## What does NOT belong here

- Code patterns or architecture (derive from the current codebase)
- Git history or change logs (use `git log`)
- Temporary task state or in-progress notes
- Anything that can be freshly looked up in under 30 seconds

---

## How to add knowledge

Create a file: `_knowledgebase/[domain]-[topic].md`

Use this format:

```markdown
# [Domain]: [Topic]

**Source:** [where this came from — URL, book, interview, experiment]
**Last verified:** [date]
**Confidence:** [high = verified from authoritative source or direct experiment; medium = reasonable inference, not directly tested; low = anecdotal or a single data point — and why]

## What we know

[The knowledge itself]

## What we're not sure about

[Open questions, caveats, conflicting signals]

## How this affects our work

[Specifically: how does this change what we build or decide?]
```

---

## When to re-verify

Before using a knowledge file to make a decision, check its **Last verified** date:

- **Under 90 days** — safe to use as-is
- **90–180 days** — use with caution; flag to user if the domain moves fast (APIs, pricing, regulations, third-party services)
- **Over 180 days** — treat as stale; re-verify before relying on it

To re-verify: check the original source, update any outdated content, and update the **Last verified** date. If the knowledge has changed significantly, note what changed in **What we're not sure about**.

---

## Current knowledge files

(Add entries here as files are created)

| File | Domain | Topic | Last verified |
|------|--------|-------|---------------|
| [zig-0.16-io-api.md](zig-0.16-io-api.md) | Zig 0.16 | std.Io file/dir/process/env API — gotchas and correct patterns | 2026-07-04 |
| [cache-architecture.md](cache-architecture.md) | 4ORMan/4orman-tools | All 5 caching layers — status, gaps, implementation order | 2026-06-30 |
| [zig-language-interop.md](zig-language-interop.md) | 4ORMan/4orman-tools | Zig-native vs. language worker decision tree — when to use Python/Node, no-bloat rule | 2026-06-30 |
| [4orman-ledger-protocol.md](4orman-ledger-protocol.md) | 4ORMan/4orman-tools | Ledger scoring protocol — Rigged Rock-Paper-Scissors, win/void conditions, storage format | 2026-07-01 |
| [4orman-fmz-format.md](4orman-fmz-format.md) | 4ORMan/4orman-tools | .fmz package format — archive structure, manifest schema, import/export behavior | 2026-07-01 |
| [foreman-agent-standardization.md](foreman-agent-standardization.md) | 4ORMan ecosystem | Proposed lifecycle/repo structure for foreman-claude/copilot/antigravity/codex — planning only, no repos created | 2026-07-02 |
| [4orman-public-full-audit-and-growth-direction.md](4orman-public-full-audit-and-growth-direction.md) | 4ORMan ecosystem | Full file-level audit of `4orman-public` vs private `4orman` (every anomaly explained), plus a deliberate divergent growth-direction call (Jungian ledger) | 2026-07-06 |
