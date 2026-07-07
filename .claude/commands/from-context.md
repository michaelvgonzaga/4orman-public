Paste raw context — notes, requirements, code snippets, research, design docs, anything — and Claude will synthesize it into a project plan, recommend the right toolchain, and identify CLI tool candidates for long-term token savings before starting spec work.

---

## Step 1 — Collect context

Ask the user:

> "Paste your context. Can be notes, requirements, code, API docs, design ideas — anything relevant. One big paste is fine."

Wait. Do not start analysis until the user has finished pasting.

---

## Step 2 — Synthesize

Read everything. Build a complete picture:

- **What it does** — one sentence
- **Who it's for** — user or system (automated, CLI, background service)
- **Core operations** — the repeated actions this project will perform (list each one)
- **Tech signals** — languages, APIs, data formats mentioned or implied

---

## Step 3 — CLI tool evaluation

For every core operation, decide whether a CLI tool would save tokens across future sessions:

**Use `4orman-tools` (Zig subcommand)** when ALL of these are true:
- Reads git refs, filesystem state, or project metadata
- Will run on every session open, every release, or every build cycle
- Needs <10ms startup (no acceptable latency budget)
- No external dependencies beyond system `git` / `gh`
- Useful across multiple projects (not just this one)

**Use a standalone script (Python / bash / zsh)** when:
- Python: complex parsing, API calls, data transformation, rich library needed
- bash/zsh: shell glue, environment setup, tool orchestration, simple file ops
- Project-specific — won't reuse across other 4ORMan projects

**Skip** when:
- Operation is truly one-off (runs once ever)
- Requires interactive input or auth tokens
- Already handled by an existing tool

For each CLI candidate, output:

```
CLI candidate: `<name> <args>`
Language: Zig (4orman-tools) | Python | bash | zsh
Why: <one line — what makes this language the right fit>
Replaces: <the shell reasoning or tool Claude would otherwise run>
Frequency: every session | every release | per project setup | one-off
Cross-project: yes | no
Savings: ~<N> tokens per invocation × <M> invocations/session = ~<total>/session
```

---

## Step 4 — Recommendation

Present to the user:

```
Project: <name>
What it does: <one sentence>

Toolchain recommendation:
  Core: <language/framework>
  <CLI tool candidates — one per line with language and savings>

4ORMan project type: standard project | plugin | standalone script

Next: proceed to spec? (yes / adjust)
```

If any 4orman-tools candidates surfaced: ask "Add these to 4orman-tools/spec.md now, or after the project spec?" Do not add without confirmation.

---

## Step 5 — Hand off

On confirmation, run `/new-project` with the synthesized context pre-loaded — skip questions that are already answered. Only ask what is still genuinely unknown.

---

## Rules

- Never start spec work before Step 4 confirmation.
- Never recommend Zig for one-off or project-specific operations — 4orman-tools is for cross-project, high-frequency work only.
- If the pasted context is too vague to evaluate CLI candidates, ask one clarifying question before Step 3.
- If the user pastes a GitHub URL instead of context, run `/absorb` instead.
