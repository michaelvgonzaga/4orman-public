Layer 1 spec interview. Uncover the real goal, write the spec, scaffold the project, require sign-off on every decision before work begins.

**Before starting the interview:** If the user has already provided a project name, check whether `[project-name]/spec.md` already exists. If it does, stop immediately and say: "A spec already exists for '[name]'. If you want to start over, delete the existing `spec.md` and `CLAUDE.md` first. If you want to update the spec, edit `spec.md` directly." Do not proceed with the interview.

This applies across any domain — software, legal, healthcare, trades, retail, and beyond.

## Rules for this interview

- **`gate` mode (or `foremanMode` missing from context): ask ONE question at a time, exactly as below.** Never bundle questions. Wait for the answer before asking the next one. If an answer is vague, dig one level deeper before moving on. If a user says "no" to a question, accept it as "none" and move to the next question.
- **`autopilot` mode: skip asking the sequence one at a time.** Infer a reasonable answer for each question from the user's own request and visible context (existing `_projects.md` patterns, similar recent projects, stated goals) — the same "decide without asking" judgment autopilot mode already uses everywhere else. State every inferred answer explicitly in the draft spec (e.g. "Assumed: solo practitioners only in v1 — no signal either way in the request"), never silently. If one specific question genuinely has no reasonable default to infer (not just "requires judgment," but truly nothing to go on), ask that one question directly rather than guessing wildly — everything else still gets inferred. Proceed straight to "After the interview" once every question has an answer or an inferred assumption. The Step 6 confirmation gate below is unchanged and is what catches a wrong assumption — inferring answers doesn't skip sign-off, it only changes when the back-and-forth happens.
- Bias toward small, compartmentalized scope. When in doubt, cut scope.

## Question sequence (adapt based on answers)

1. "What's the one thing this project needs to do well to be worth building?"
2. "Who uses this, and what's their situation when they need it?" (real person, real context)
3. "What does success look like in 30 days? What's different?"
4. "What's the fastest way someone could get value from this — before it's fully built?"
5. "What have you already tried, or what exists today that's close?"
6. "Any constraints I should know about — timeline, budget, existing tools or systems you're working within, regulatory requirements, or industry-specific rules?"
7. "What's off the table — what should this never do?"

## After the interview

1. **Confirm the project name.** Ask: "What do you want to call this project? This becomes the directory name — keep it short, lowercase, no spaces (e.g., `injury-intake`, `plumbing-scheduler`, `lease-drafter`)."

2. **Check the knowledgebase and skills before writing anything:**
   - If the user provides an existing codebase path, run `4orman-tools scan <path>` first — it returns framework, key files, dep count, directory map, entry point, and a file inventory (sorted largest-first). Use `entryPoint` and the top `files` entries to prioritize reads instead of running `find` or `ls`.
   - Read `_knowledgebase/README.md` and any relevant files before writing the spec.
   - Read `_skills/README.md` — identify which playbooks apply:
     - If the domain is unfamiliar: read and apply `_skills/domain-research.md`
     - If the project is a software build: read and apply `_skills/software-projects.md`
     - Apply any other relevant skills found in the index

3. **Read `_templates/spec_output.md`** before writing. Use that exact format — do not invent a different structure.

4. **Write the spec** and save it to `[project-name]/spec.md`. Fill in every field from the interview and knowledgebase. For sections with nothing to say, write "None identified" — do not leave placeholder text.

   **Exceptions — these must always have real content, never "None identified":**
   - **Risks**: Actively infer at least 2–3. Think beyond tech: unvalidated workflow assumptions, domain-specific compliance risks (regulations, licensing, liability), dependencies on third parties. Every project in every field has risks.
   - **Milestones**: Fill with real content from the interview, not M1/M2/M3 examples.

5. **Scaffold the project directory:**
   - Create `[project-name]/` and `[project-name]/knowledge/` if they don't exist
   - Read `_templates/project_claude.md` and write its contents to `[project-name]/CLAUDE.md`
   - Fill in from the interview: title, goal, user, domain, scope, guardrails, tools, integrations, domain-specific requirements
   - Replace `[list here]` with actual external services or integrations identified, or "None in v1"
   - For "Never do" hard lines: keep the two universals and add domain-specific ones (e.g., "never store patient data unencrypted", "never provide legal advice — only information"). Remove the placeholder label.
     - Universal: "Never write to a production database or live system"
     - Universal: "Never send real messages, emails, or notifications to real users"
   - If tools and platform not yet decided, leave those fields as `TODO: not yet decided`
   - Read `_templates/roadmap_output.md` and write it to `[project-name]/ROADMAP.md` — fill in all milestones, their "Done when" criteria, and an initial step breakdown for M1. Leave M2/M3 steps as placeholders until M1 is complete.
   - Run `git init -b main` inside `[project-name]/` to initialize it as its own repository (the project directory is already excluded from 4orman's git by `.gitignore` — no manual entry needed). If git version is older than 2.28 and `-b` is unsupported, run `git init` then `git symbolic-ref HEAD refs/heads/main`.
   - Ask the user: "Should this project be **public** (anyone can see it on GitHub) or **private** (only you)?" — then apply the `github-repo` skill (`_skills/github-repo.md`) to create the GitHub repo and wire up the remote immediately. Record visibility in `_projects.md` and `[project-name]/CLAUDE.md`.

6. **Present the spec to the user** and say:

   "Check each decision box. Confirm what's right or tell me what to change."

   - If the user **confirms** a decision: mark it `[x]` in the spec
   - If the user **rejects** a decision: discuss the alternative, update the decision text to reflect what was agreed, then re-present it for confirmation before proceeding
   - Do not proceed until every `[ ]` box is either confirmed or replaced with an agreed alternative and confirmed

7. **After all decisions confirmed:**
   - Mirror each confirmed decision into the decision log table in `[project-name]/CLAUDE.md`:

     | Date | Decision | Why |
     |------|----------|-----|
     | [today's date] | [the decision] | [reason from the interview] |

   - Add a row to `_projects.md` with: project name | visibility (public/private) | `active` | today's date (Started) | today's date (Last updated) | one-sentence goal
