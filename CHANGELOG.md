# Changelog

## v1.34.0 — 2026-07-06

### New
- Strict-mode finalize gate: autopilot now runs build/tests/the relevant safety check before treating any commit, push, release, or deploy as finished — a failure surfaces and pauses instead of being silently absorbed. Extended to optimization claims: a claimed speedup doesn't finalize without real before/after numbers.
- No-silent-errors guardrail: every failure, on every surface, produces an explicit, actionable message — no bare exit codes standing in for an explanation.
- Verify-the-real-artifact guardrail: a fix isn't finished when source and tests pass — confirm the actual deployed/installed thing reflects it, not just a local build.
- Sandbox side-by-side benchmark protocol: before choosing between candidate tools/modules, run every candidate through the same workload for 490 iterations, scored on exact speed/accuracy/correctness values. Checks the ledger for a prior verdict before re-running, records the result after.
- Self-update detection added to the `SessionStart` hook — bundles actual incoming commits and file counts, not just a boolean.
- Dry-run-first standard for Standard/Full-build tasks, every project.
- Autopilot-mode fast path for `/new-project`'s spec interview.

### Fixed
- `/deploy-public`'s Step 6 now `git init`s the scratch snapshot before re-verifying — previously the check scanned an empty, non-git target and always reported clean regardless of actual content.
- `/deploy-public` no longer leaves private-repo `git clone` URLs in the public snapshot (they'd 404 for anyone installing from the public mirror).

### Improved
- Startup splash redesigned: commands are now grouped by category with truncated one-line descriptions pulled from `/help`'s own table, replacing a flat 31-command dump that broke alignment on wrap.

## v1.32.0 — 2026-07-05

### New
- Explicit third tier on the Zig-first escalation ladder: if Claude genuinely can't design a solution (a true unknown, not just unbuilt), stop and ask the user rather than guessing. Also makes explicit that once a capability is promoted, checking for it via `capability-check`/`route` before reasoning is mandatory on every later occurrence of the same need.

## v1.31.0 — 2026-07-05

### New
- Auto-execute guardrail — commit/push now proceeds without asking once build/tests/relevant Zig checks are clean with no contradictions, a Zig `recommend`/`winner` field is taken directly instead of re-asking, and compatible multi-option results all ship together. Genuinely uncertain outcomes get tested first — a clean result after testing is the approval, not a separate ask.
- Scoped the `git push --force` permission deny to protect only the private main repos (`origin` remote) while allowing the sanctioned `/deploy-public` force-push to `*-public.git` mirrors, which push to the mirror's explicit URL instead of a named remote so the two cases are distinguishable.

## v1.30.0 — 2026-07-05

### New
- `SessionStart` hook (`bin/session-start-hook.py`) automates the manual startup checklist — `compat-check`, `doctor`, a binary-staleness probe, `.first-run` check, profile-cache lookup, and ledger staleness — gathered into one JSON blob at session start, zero Claude tokens spent gathering it. The "Always do" guardrail list now describes what to do with each field instead of how to gather it.
- `curriculum-check`/`curriculum-list`/`ledger record-curriculum` guardrail — before learning/building something new for a tech domain or profession, check the ledger for a stored ROI-ranked precedent first.
- `architecture-check`/`architecture-list`/`ledger record-architecture` guardrail — a stricter sibling scoped to 4orman's own architecture, hard-gated on ≥1% estimated improvement with no drawbacks.
- `/study-repo` skill — study an external project read-only, distill it, propose ROI-ranked improvements with simulations, and record findings in a dedicated `<project>-casestudy` repo, reusing the `architecture-check` gate to decide whether any proposal should also be back-ported into 4orman itself.

### Docs
- Recorded a design (not yet implemented) for a `claim-check` ledger mechanism — a deterministic, ledger-backed way to mechanically verify specific factual claims Claude makes about a scanned document, with an explicit honest-disclosure path when no check applies.
- `/help` now lists `/deploy-public`.

## v1.29.0 — 2026-07-05

### New
- `delegation-check` guardrail — call `4orman-tools delegation-check` before any Standard/Full-build task for a ledger-backed solo-vs-multi-agent recommendation
- Foreman agent standardization: created `foreman-copilot` (lightweight toolkit, private, unlicensed), resolved visibility/licensing conventions across the whole Foreman lineup (4orman, foreman-codex, foreman-antigravity, foreman-copilot)
- `/deploy-public` command — push a sanitized snapshot of a private repo to its public counterpart
- Multi-profile `/first-run` support
- Cross-project ledger (`_ledgers/`) tracking indexing health across repos
- Subagent spawning codified as autonomous, not an ask-first action
- Startup banner now shows per-command descriptions
- `context-gate` wired into session-start guardrails

### Fixed
- Ghost-feature audit: broken skill reference, hardcoded paths, stale branding
- Removed superseded `foreman-quiet`/`foreman-watch` commands and stale `bin/foreman-ai`
- Splash banner centered horizontally and vertically

### Docs
- Role-boundary uncertainty signals in `build`/`run-tests`/`quality-gate`
- Ledger-precedent override for `build`/`run-tests` tool selection
- Jungian ledger category, ledger outcome tracking, outcome-review-due detection
- Public-mirror release step in `/brew-release`

---

## v1.28.0 — 2026-07-01

### Changed
- Renamed "Foreman" to "4ORMan" across docs, commands, hooks, and launcher

---

## v1.27.1 — 2026-07-01

### Docs
- Guardrail reminding to open a new terminal after upgrading `orman-ai`/`orman-tools`

---

## v1.27.0 — 2026-07-01

### New
- CLAUDE.md guardrails updated to cover every `4orman-tools` subcommand shipped through Wave 4: `capability-check`, `route`, `report`, `metrics`, `session-snapshot`, `sandbox-check`, `rollback`, `capability-promote`, `worker-run`/`worker-list`, `quality-gate`, `validate-schema`, `prod-ready`, `shell-run`, `project-state`, `git-cache`, `delta-context`, `device-scan`, `secret-scan`, `symbol-find`, `env-inspect`, `build`, `run-tests`
- Self-healing worker protocol and Mathematical Proof guardrails
- Zig-first rule — check `4orman-tools` before any shell reasoning
- Ledger protocol — Rigged Rock-Paper-Scissors (Claude-vs-Zig contested decisions)
- Governance layer: declined-decision tracking, quality floor, reputation check
- Auto/manual public and private release commands
- Language worker framework

### Docs
- Public repo sanitized (personal references removed), README rewritten with flowchart + token-savings section

---

## v1.26.0 — 2026-06-30

### New
- `foreman-tools deps <abs-root-path>` — declared dependencies from any package manifest without reading the full file; auto-detects package.json (npm), Cargo.toml (cargo), go.mod (go), requirements.txt (pip); returns name + version + dev flag; use in `/absorb` and `/new-project` to understand what a project depends on

---

## v1.25.0 — 2026-06-30

### New
- `foreman-tools outline <abs-file-path>` — structural outline of any source file: function/class/struct/enum names with line numbers; covers Go, Python, JS, TS, Rust, Zig, Ruby, Java, Kotlin, C#, Swift, PHP; use instead of reading the full file when you only need to understand its structure or find a specific symbol

---

## v1.24.0 — 2026-06-29

### New
- `foreman-tools yaml-query <file-path> <dot-path>` — extract a value from any YAML file (GitHub Actions, docker-compose, k8s, Rails config); same shape as `json-query` and `toml-query`; supports nested mappings and sequence indexing (`steps.0.uses`); use before reading the whole file when you only need one value

---

## v1.23.0 — 2026-06-29

### New
- `foreman-tools context-rank <abs-root-path> <query>` — relevance ranking: score and rank project files by query relevance so Claude reads the most important files first; top 15 results, composite score (content hits + name match + file kind); use before reading files to determine read order

### Fixed
- `foreman-tools scan` (and all subcommands using scan) now excludes `.DS_Store`, `Thumbs.db`, and binary files (images, fonts, audio, video, archives, compiled objects)

---

## v1.22.0 — 2026-06-29

### New
- `foreman-tools context-changed <repo-path> [ref]` — changed files with unified diff content in one call; default ref is HEAD (all uncommitted changes); first 8 files, 100 lines of diff each; use instead of running `git diff` and reading raw output

---

## v1.21.0 — 2026-06-29

### New
- `foreman-tools context-evidence <abs-file-path> <pattern>` — evidence packets: relevant excerpts from a file without reading the whole thing; case-insensitive literal search, ±10 lines context per match, overlapping windows merged, up to 8 chunks; use instead of reading a full file when you only need to answer a question about a specific function, rule, or keyword

---

## v1.20.0 — 2026-06-29

### New
- `foreman-tools context-scan <path>` — compact project summary: framework, entryPoint, fileCount, per-kind counts (source/test/config/docs/other), top 10 files by size, keyFiles, dirs; use instead of `scan` when only structure is needed — one JSON read beats exploring the filesystem

---

## v1.19.0 — 2026-06-29

### New
- `foreman-tools cache-store <file-path> <sub-key>` (value JSON via stdin) — stores extracted JSON keyed to file hash; auto-invalidates when file changes
- `foreman-tools cache-fetch <file-path> <sub-key>` — `hit: true` means file unchanged + value cached; skip the read entirely and use `value` directly

---

## v1.18.0 — 2026-06-29

### New
- `foreman-tools cache-check <abs-path>` — persistent change detection; returns `{sha256, changed, cached}`; stores hash in `~/.cache/foreman-tools/`; `changed: false` means the file is byte-for-byte identical to the last check — skip the read entirely

---

## v1.17.0 — 2026-06-29

### New
- `foreman-tools file-hash <abs-path>` — returns SHA256 + byte size of any local file; foundation for cache-engine change detection; callers store the hash and compare on next invocation to skip unchanged reads

---

## v1.16.0 — 2026-06-29

### Changed
- `foreman-tools/api-schema.md` created — locked JSON output contract for all 24 subcommands; field changes now require explicit version bump

---

## v1.15.0 — 2026-06-29

### Improved
- `/release` and `/brew-release` now use `foreman-tools gh-release` to create GitHub releases via a notes file, eliminating heredoc/quote escaping issues with multiline release notes

---

## v1.14.0 — 2026-06-29

### Improved
- `/brew-release` now uses `foreman-tools tarball-sha` to compute GitHub tarball SHA256 with automatic retry, replacing `curl | shasum -a 256`
- `/brew-release` now uses `foreman-tools formula-info` to read the current formula state, replacing manual .rb file parsing
- `/setup-automation` now uses `foreman-tools validate-hooks` to verify Stop hooks exist, replacing `jq` traversal of settings.json

---

## v1.6.0 — 2026-06-28

### New
- `/from-context` — paste any raw context (notes, requirements, code, docs) and Claude synthesizes the project, picks the right toolchain (Zig/Python/bash/none), and flags CLI tool candidates with token savings estimates before spec work begins
- `foreman-tools-audit` skill — runs after every new project and command/skill edit; scans for shell patterns worth promoting to a native CLI subcommand
- `foreman-tools-first` guardrail — Claude checks for a `foreman-tools` subcommand before any data-gathering shell command; warns at session start if `foreman-tools` is not installed

---

## v1.5.0 — 2026-06-28

### New
- `foreman-tools` binary now installs automatically alongside `foreman-ai` via Homebrew — no separate install step

### Improvements
- `self-update` skill uses `foreman-tools status` when available — one JSON read replaces two git subprocess calls; falls back cleanly without it
- `/release` command uses `foreman-tools commits` when available — pre-categorized JSON replaces raw `git log`; falls back cleanly without it

---

## v1.4.0 — 2026-06-28

### New commands
- `/first-run` — guided first-time setup wizard: dependency checks, GitHub auth, per-machine automation hooks, project restore, memory sync, and plugin install
- `/release` — cut a GitHub release for any project (CHANGELOG, tag, push, publish GitHub release)
- `/setup-automation` — install per-machine auto-sync and auto-push Stop hooks into `~/.claude/settings.json`; portable across usernames, idempotent
- `/sync-memory` — back up and restore Claude Code memory across machines via a private GitHub repo
- `/restore-projects` — pull existing Foreman projects from GitHub into a fresh workspace (clone missing, fast-forward existing, push nothing)

### Improvements
- **Token efficiency pass** — net −348 lines across all 27 commands, skills, and templates; removed preamble boilerplate, redundant rules sections, over-specified examples, and placeholder content
- **Token discipline guardrail** — CLAUDE.md now enforces rules for keeping framework files lean when making future edits (earn every token, one location per rule, no rationale commentary, no placeholders)
- **Proportional effort guardrail** — trivial/standard/full-build tiers with appropriate verification; `/verify-output` (second-agent critic) only fires when the work warrants it
- Auto-push hooks hardened for concurrent Claude sessions — `pull --rebase` fallback prevents push rejection when another session pushed first
- Self-update and release-notes skills wired into CLAUDE.md session-start guardrails for automatic behavior
- `_projects.md` is now git-ignored local state seeded from template at session start (never committed to the framework repo)

### Docs
- Foreman reframed: "a foreman directs Claude Code" — not an AI
- README overhauled: identity, who it's for, prerequisites (added `gh`), getting started, commands table
- GitHub repo description updated

### Fixes
- `.gitignore`: inline comments moved to their own lines (were silently ignored by git)
- a private-project command file gitignored and scrubbed from git history via `git filter-repo` (was accidentally public)

---

## v1.3.1 — 2026-06-28

- Launcher now `git clone`s the workspace (was `cp -r`) so `/self-update` works correctly
- Tag and tap formula aligned with `main`

## v1.3.0 — 2026-06-28

- Auto-release notes skill; GitHub repo skill wired into `/new-project` and `/absorb`
- Auto-commit and auto-push Stop hooks for project repos

## v1.2.0

- Plugin system: `/export-plugin`, `/install-plugin`, public/private plugin model

## v1.1.0

- `/absorb` command — import any file, repo, or project into Foreman

## v1.0.0

- Initial release: 3-layer framework, `/new-project`, `/verify-output`, self-update skill
