# Idea Translation

**Works well for:** Loose, creative, metaphor-heavy proposals that take multiple rounds of "here's my restatement, is that right?" before they're concrete enough to evaluate — front-loads that clarification into one deliberate pass instead of spreading it across the main conversation.
**Confidence:** Medium — pattern identified live (2026-07-06) after several proposals in the same session (multi-agent council, zig-mechanic/zig-resident, the "keyboard" package concept) each needed multiple back-and-forth restatements before they were gradable. Not yet run end-to-end on a fresh idea.

## The pattern

When a request is loose enough that you'd otherwise need more than one "here's my restatement, is that right?" round to pin it down, spawn a dedicated translator subagent instead of iterating in the main flow.

**Translator subagent's only job:** convert the raw, metaphor-heavy input into a precise technical spec:
- What triggers it (an event, a schedule, a manual invocation?)
- What it touches (files, repos, running processes — the actual blast radius)
- What "done" looks like (a concrete, checkable definition, not a vibe)
- What existing mechanism it might already overlap with or duplicate

Give the translator the raw request plus enough surrounding context (what's already built, what similar ideas exist) to do this well — it should read the codebase/ROADMAP if it needs to, not translate blind.

**Translation is not validation.** A subagent can produce a clean, well-specified version of an idea that still doesn't need to exist — the council/zig-resident/keyboard proposals in this conversation were each eventually well-specified *and* already covered or under-justified. The translated spec still has to clear the Mathematical Proof gate (measured data, a credible source, or a concrete forcing need) before anything gets built.

**If the rewrite is still gray-area** — the translator can't pin down a concrete trigger/scope/done-condition even after a dedicated pass — drop the idea rather than carrying an ambiguous spec forward. Log it in `ROADMAP.md`'s backlog with what made it ungradable, the same way already-deprioritized proposals are logged, so it isn't silently lost, but don't build against it.

**If it's concrete and passes the Mathematical Proof gate:** the sandbox side-by-side benchmark protocol is the next stage, not a new evaluation mechanism — real candidates, real measured comparison, before/after data. If the benchmark doesn't come back positive, drop the idea the same way — and dispose of the sandbox artifacts per that protocol's own disposal rule (scratch binaries, harnesses, template scaffolding), don't leave them lying around as residue from an idea that didn't pan out.

**Full sequence:** translate → validate need → sandbox test → implement. Never translate straight into implementation, and never skip a stage because an earlier one felt convincing.

## When to use it

- A proposal is metaphor-heavy or uses invented terminology ("keyboard," "resident," "mechanic") standing in for a mechanism that hasn't been made concrete yet
- The same idea has already needed one clarifying round and still isn't gradable
- The user explicitly asks for something to be "made concrete" or "spec'd out" before building

## When NOT to use it

- The request is already a precise technical ask (a named subcommand, a specific bug, a specific file) — translating something already concrete just adds a step
- Trivial or Standard-scope tasks, per this project's own "Scale to task size" rule — this is overhead reserved for genuinely ambiguous, potentially-large proposals
