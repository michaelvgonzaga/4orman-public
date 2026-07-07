# [Project Name] Spec

---

**The real goal:** [one sentence — what problem this actually solves, not what it builds]

**Who it's for:** [specific person in a specific situation — not "users"]

**Domain:** [the field or industry — e.g., legal, healthcare, plumbing, retail, software, education]

**Success in 30 days:** [concrete, measurable outcome — what's different about the world]

**How we'll measure it:** [the specific signal that confirms success — a number, a behavior, an observable change]

---

## Scope — v1 only

**In:**
- [Feature / capability]
- [Feature / capability]
- [Feature / capability]

**Out (explicitly):**
- [What this will never do in v1]
- [What comes later if this works]

---

## The simplest version that delivers value

[2–3 sentences. What's the absolute minimum that makes this worth using?]

---

## Risks

Known unknowns and things that could kill this project.

- [Risk 1]
- [Risk 2]
- [Risk 3]

---

## Key decisions — requires explicit sign-off

- [ ] [Decision — e.g., "Serving solo practitioners only in v1, not law firms"]
- [ ] [Decision — e.g., "Scheduling done via SMS, not a mobile app"]
- [ ] [Decision — e.g., "All data stored locally, no cloud sync in v1"]

---

## Quality floor (non-negotiable)

- **Latency:** [e.g., "Session start < 200ms", "API response < 500ms", "build < 30s"]
- **Token budget:** [e.g., "No subcommand output > 2KB", "Session-start reads < 3 files"]
- **Reliability:** [what must never fail silently — e.g., "Cache miss must not corrupt state"]
- **Reversibility:** [what must always have a rollback — e.g., "Every write is atomic"]

## Open questions (unresolved)

- [Question that still needs an answer — or "None identified"]

---

## Milestones

| Milestone | What a user can do | Done when... |
|-----------|-------------------|--------------|
| M1 — First value | [earliest usable capability] | [observable test: user can do X and get Y] |
| M2 — Core complete | [main workflow end-to-end] | [observable test: user can do X and get Y] |
| M3 — Hardened | [edge cases, error handling, polish] | [observable test: user can do X and get Y] |
