# [Project Name]

[One sentence: what this project does and who it's for.]

---

## Spec

See `spec.md` for the full spec. Key facts:

- **Goal:** [the real goal, from spec.md]
- **User:** [who uses this]
- **Domain:** [the field or industry — e.g., legal, healthcare, plumbing, retail, software]
- **v1 scope:** [what's in for this version]
- **Out of scope:** [what's explicitly not being built]

---

## Guardrails (project-specific)

### Always do
- Read `spec.md` and `ROADMAP.md` before any implementation work
- After completing any step: update `ROADMAP.md` (check the step done, update milestone status) before asking to proceed
- Run `/verify-output` before marking tasks complete
- Keep changes scoped to v1 — do not add features not in the spec
- Before making domain-specific decisions: read `_knowledgebase/README.md` to find relevant files, then read those files
- Before starting a new domain or project type: read `_skills/README.md` and apply any relevant playbooks
### Ask first
- Any use of an external service, API, or integration — list what's used in this project: [list here, or "None in v1"]
- Any change to the data model, schema, or core workflow
- Installing, upgrading, or removing dependencies or packages
- Any operation that writes files outside this project directory
- Any mid-project scope change — propose it, get sign-off, then update spec.md

### Never do
- Never write to a production database or live system
- Never send real messages, emails, or notifications to real users
- [Project-specific hard line — add one or more, or remove this line if none apply]
- Skip the verifier before marking work done
- Add scope without updating spec.md and getting explicit sign-off first

---

## Tools & Resources

- **Platform / runtime:** [e.g., web app, mobile, desktop, CLI, physical hardware — or "TODO: not yet decided"]
- **Key tools & services:** [e.g., Supabase, Stripe, Twilio, QuickBooks API, or specific domain software — or "TODO"]
- **Data & storage:** [e.g., SQLite, Google Sheets, Postgres, paper forms — or "TODO"]
- **Domain-specific requirements:** [e.g., HIPAA compliance, bar association rules, trade licensing, accessibility standards — or "None identified"]

---

## How to execute

```
# setup


# run / work


# validate / test

```

---

## Knowledgebase

Project knowledge: `knowledge/[topic].md`. Global: `_knowledgebase/[topic].md`.

---

## Decision log — Approved

| Date | Decision | Why |
|------|----------|-----|
| [date] | [what was decided] | [why] |

## Decision log — Declined

| Date | Proposed | Why declined | Revisit when |
|------|----------|-------------|--------------|
| [date] | [what was considered] | [why it was rejected] | [the specific condition that would change this — not "later", a real trigger] |
