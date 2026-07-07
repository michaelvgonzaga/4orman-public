Study an external project — understand it, propose its highest-ROI improvements, simulate them, and record the findings in a dedicated private case-study repo. Never absorbs, modifies, or iterates on the target itself — that's `/absorb`'s job, this is read-only study.

---

## Phase 1 — Locate the target

Accept a local path or a git URL directly. If the user gave neither, search `~`, common dirs (`~/Desktop`, `~/Downloads`, `~/Documents`, `~/Projects`), and `/private/tmp` (macOS symlinks `/tmp` there — search both), same as `/absorb` Phase 1. Present matches, wait for confirmation.

If it's a remote URL, clone it read-only into the scratchpad — never into the 4ORMan workspace itself:
```bash
git clone --depth=1 <url> <scratchpad>/<name>
```

## Phase 2 — Full recursive scan

```bash
4orman-tools scan <target-path>
4orman-tools symbol-index <target-path>
```

`scan` gives the full file inventory, directory map, detected framework, and entry point. `symbol-index` gives every source file's declared symbols. For anything `context-rank`/`context-evidence` can answer more cheaply than a full read, use those first — but for a genuine "understand this project" pass, read enough real file content that the distillation in Phase 3 is grounded in what the code actually does, not just its file names.

## Phase 3 — Distill

Write down, plainly:
- What this project is and what problem it solves, one paragraph
- Its architecture — main components, how they relate, what's load-bearing vs. incidental
- What's genuinely solid vs. what's fragile or incomplete

## Phase 4 — Propose improvements, ranked by ROI

Propose the concrete changes that would most improve *this project*, each with:
- **ROI tier** (`highest`/`medium`/`lowest`) — your judgment call, same honest framing as the `curriculum` ledger: no formal proof exists for "best next change," state your reasoning, not a fabricated score.
- **Simulation** — a structured, written before/after prediction: what changes, the expected effect, what could break. Never claim to have "run" this. **Exception:** if the target has real build/test tooling and the change is safely testable, actually apply it on a throwaway branch/worktree inside the scratchpad clone and run the real tests — real execution beats a prediction whenever it's honestly available, but never fabricate having done it when you didn't.

## Phase 5 — Confirm before creating anything

Show the user: the distillation, every proposed change with its ROI tier and simulation. Ask: **"Does this look right? Any corrections before I create the case-study repo?"** Wait for sign-off.

## Phase 6 — Create the case-study repo

**Hard rule: one studied project gets its own repo, named `<project>-casestudy`.** Never write case-study findings into any existing repo, including 4orman itself.

Apply the `github-repo` skill (`_skills/github-repo.md`) — private, confirmed individually, same as every other repo created this way. Never skip the confirmation because a previous case-study repo was already approved.

Write two files into the new repo before the first push:

**`CASE_STUDY.md`** — the Phase 3 distillation + every Phase 4 proposal with its ROI tier and simulation.

**`4ORMAN_SNAPSHOT.md`** — a point-in-time copy of 4orman's own current state, for comparison:
```bash
4orman-tools metrics
4orman-tools architecture-list
4orman-tools curriculum-list <relevant-domain-if-any>
4orman-tools registry
```
Paste each result's JSON under its own heading. This is a snapshot, not a live link — it will go stale, and that's fine, it records what 4orman looked like at the time this project was studied.

Commit and push.

## Phase 7 — Back-port check

For each Phase 4 proposal that Claude judges *also* applies to 4orman's own architecture (not just the studied project), run it through the existing gate — do not re-derive this logic, it already exists:

```bash
4orman-tools architecture-check "<topic>" <estimated-improvement-pct> <true|false>
```

Follow the CLAUDE.md `architecture-check` guardrail exactly: `recommend: "build"` → proceed to build it into 4orman. `needsDecision: true` → stop and ask the user explicitly (benefit vs. a mitigable drawback → still worth proposing as a PR; benefit vs. an unfixable drawback → list it and move on, not now). Never silently build or silently drop a proposal that reached this gate.

## Phase 8 — Record the outcome

Once each back-ported proposal is resolved (built, rejected, or explicitly deferred), record it:
```bash
4orman-tools ledger record-architecture "<topic>" <highest|medium|lowest> <pct> <true|false> <proposed|built|rejected> "<reasoning>" "<shadow>" "<synthesis>"
```

---

## Rules

- Never modify the studied project itself. If a simulation needs a throwaway branch to actually test, that branch lives in the scratchpad clone, never pushed anywhere, never merged into the target's own remote.
- Never skip Phase 5's confirmation before creating the case-study repo.
- Never claim a simulation was "run" unless it genuinely was, on real tooling, with the actual output shown.
- Never push a case-study repo without the same explicit per-repo confirmation `/deploy-public` and `github-repo` already require.
- A proposal that only benefits the studied project, not 4orman, still belongs in `CASE_STUDY.md` — it does not need an `architecture-check` call. That gate is only for proposals Claude believes also apply back to 4orman itself.
