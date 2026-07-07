# 4ORMan: Foreman Agent Standardization — Planning

**Source:** direct user request, 2026-07-02, recommending a consistent lifecycle/repo structure across cooperating Foreman agents
**Last verified:** 2026-07-04
**Confidence:** Low — this doc's original assumptions were wrong on the ground truth (see "What we know" below, corrected 2026-07-04). Remaining open questions are still unconfirmed.

## What we know

Four cooperating agents are referenced in `_ledgers/AGENTS.md`:
Foreman-Copilot, Codex, zig-antigravity, and Foreman itself (Claude).
Standardizing their lifecycle and repo layout keeps generic reusable
code shareable and public while private project knowledge (decision
logs, solutions, ledger entries) never leaves a project's own
`~/.4orman/` state or its own repo.

### Standard lifecycle (applies to every Foreman agent)

1. Bootstrap its own public GitHub repository.
2. Build its own engine.
3. Manage many projects.
4. Update only local project ledgers.
5. Keep only generic reusable code in its public repo.
6. Teach its Zig stand-in.
7. Hand off when usage thresholds are reached.
8. Resume when frontier reasoning is needed.

### Standard repo structure (proposed, for new repos)

```
foreman-<agent>/
├── README.md
├── CLAUDE.md          # agent-specific behavior (only if the agent reads Claude-style instructions)
├── AGENTS.md           # shared AI behavior, if applicable
├── ledgers/
│   ├── AGENTS.md        # cooperation rules for this ledger/domain
│   └── *.md             # pure data, no protocol, no personality
├── roadmaps/
├── standards/
├── templates/
└── prompts/
```

This repo (`4orman`) already applies the same data/protocol split under
`_ledgers/` (underscore-prefixed here specifically because this repo's
`.gitignore` treats any non-underscore top-level directory as a private
per-project dir — a constraint that won't necessarily apply to a fresh
`foreman-<agent>` repo, so the diagram above keeps the un-prefixed
`ledgers/` form as the general recommendation).

### Target repos — corrected against actual GitHub state (checked 2026-07-04)

| Repo | Actual status | Actual shape |
|---|---|---|
| `foreman-claude` | Does not exist | Not needed — `4orman`/`4orman-tools` already fill this role for the Claude agent |
| `foreman-copilot` | **Created 2026-07-04**, private, unlicensed | Lightweight toolkit, matching `foreman-antigravity` — see reasoning below |
| `foreman-antigravity` | Exists, private, MIT | Lightweight, matches original plan: reusable prompts/templates/interfaces for a conservative indexing agent, explicitly not an orchestrator, no ledgers/credentials |
| `foreman-codex` | Exists, private, unlicensed | **Not** a lightweight curriculum store as originally assumed — it is "Foreman Codex," a full fork of the `4orman` framework adapted for Codex CLI, with its own `foreman-codex-tools` (76 subcommands), skills, ROADMAP, CHANGELOG |

The original assumption that all four repos would share one lightweight
shape was wrong: the Foreman lineup already has two different shapes in
practice — full framework forks (`4orman` for Claude, `foreman-codex`
for Codex) and lightweight toolkits (`foreman-antigravity`). Any
standardization proposal must account for both shapes, not force one
onto the other.

`foreman-codex`'s description was corrected 2026-07-04 (previously said
"curriculum store," which was inaccurate). Its license was deliberately
left unset to match `4orman` (private, unlicensed) rather than defaulting
to MIT — revisit licensing across all Foreman repos together, not
piecemeal.

## foreman-copilot shape — decided 2026-07-04

Lightweight toolkit, not a full framework fork. Grounded in the
existing cooperation contract in `_ledgers/AGENTS.md`, not a guess:

- Foreman-Copilot's job there is explicitly narrow — project map,
  context health, staleness warnings, dependency/symbol summaries —
  and explicitly *"do not suggest code refactors... the review itself
  is Copilot's job, not Foreman's."* Pure measurement/advisory role.
- It never runs its own project lifecycle (no spec-interview, no
  verify-output equivalent needed), unlike Codex CLI which is a full
  agentic coding CLI that runs entire projects end-to-end — the reason
  `foreman-codex` needed the full fork.
- `foreman-antigravity` already proves the lightweight shape for
  exactly this kind of role: reusable interfaces/prompts, explicitly
  "not an orchestrator," doesn't manage projects itself.

## Visibility and licensing — decided 2026-07-04

Surveyed every repo in the account via `gh api`/`gh repo list`, not a
guess:

- **Visibility: private.** Every repo is private except the two
  explicit `-public` mirrors (`4orman-public`, `4orman-tools-public`),
  which exist only because `/deploy-public` deliberately pushed
  sanitized snapshots there. `foreman-copilot` is not a deploy target,
  so it follows the 100%-private default.
- **License: none.** `foreman-antigravity`'s MIT is the outlier, not
  the norm — `4orman`, `4orman-tools`, `foreman-codex`,
  `foreman-codex-tools`, and even the *public* `4orman-public`/
  `4orman-tools-public` are all unlicensed (6 of 7 sampled repos).
  `foreman-copilot` stays unlicensed to match the dominant convention;
  revisit only if a public mirror is ever deliberately planned, the
  same way the existing public mirrors stayed unlicensed.

## How this affects our work

All four target repos are now resolved: `foreman-claude` intentionally
skipped (role filled by `4orman`/`4orman-tools`), `foreman-copilot`
created at github.com/michaelvgonzaga/foreman-copilot (private,
unlicensed, `main` default branch, scaffold mirrors
`foreman-antigravity`'s layout: README/CLAUDE.md/CONTRIBUTING.md,
docs/, policies/, prompts/, templates/, scripts/, examples/, src/),
`foreman-antigravity` and `foreman-codex` already existed. This
standardization effort is complete — no more open questions remain.
