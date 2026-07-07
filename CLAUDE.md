# App Factory

Base of operations. Every project lives here. Every project follows the 3-layer framework.

> **4ORMan exists to reduce the token and time cost of Claude reasoning about engineering state. It fails if a user session starts slower, burns more tokens, or produces a less reliable output than without it. It succeeds when session-start is under 200ms, cache hit rate exceeds 80%, and Claude never has to shell-parse a git command.**

---

## First-time setup (after cloning)

Run `/setup`. It reads `plugins.public.yml` (public plugins, tracked) and `plugins.local.yml` (your private repos, git-ignored) and clones whatever your git credentials can reach. If you have private repos to add, copy `plugins.local.yml.example` → `plugins.local.yml` and fill it in before running.

## Starting a new project

Run `/new-project`.

## Working on an existing project

Read the project's `CLAUDE.md` and `spec.md` before making any changes.

---

## The 3-Layer Framework

### Layer 1 — The Spec
Run `/new-project`. Spec interview, scaffolding, explicit sign-off before any work begins.

### Layer 2 — The Verifier
Run `/verify-output` before marking any output complete — self-review + critic agent.

---

## Guardrails

### Always do (autopilot)
**At the start of every session:** a `SessionStart` hook (`bin/session-start-hook.py`) has already injected `foremanMode`, `firstRunPending`, `compatCheck`, `doctor`, `binaryStale`, `profileCache`, `repoStatus`, `incomingChanges`, `ledgerStale`, `outcomeReviewDueCount`, `antigravityQueue`, and `otherActiveSessions` into context — zero Claude tokens spent gathering any of it. Act on what it reports:
1. `foremanMode`: `autopilot` (or unset) → decide and build without asking, per the exceptions below. `gate` → surface a proposal and wait before acting. `/gate` flips it for the rest of this terminal session only.
2. `firstRunPending: true` → run `/first-run` immediately and complete it before doing anything else.
3. `compatCheck.ok: false` → surface the `advice` string and each drifted tool's `rollback` command, then pause — do not proceed until user confirms or rolls back.
4. `doctor` missing `claude`/`git`/`gh` → prompt once: "`4orman-tools` not found — Homebrew distribution is sunset (2026-07-06); build from source: `cd 4orman-tools && zig build -Doptimize=ReleaseSafe`." `binaryStale: true` → surface once: "Local `4orman-tools` binary is stale (missing cache + context subcommands). Rebuild from source, same command." and skip all `cache-fetch`, `cache-store`, `cache-check`, `outline`, `context-*`, `yaml-query`, and `deps` calls for this session.
5. `repoStatus.upToDate: false` → the hook already fetched and bundled `incomingChanges` (commits + files-changed count) — surface the update prompt from `_skills/self-update.md` using that data directly, no need to re-fetch or re-derive it.
6. `profileCache.hit: true` (and binary not stale) → use `profileCache.value` directly, skip tool-detection shell calls.
7. `ledgerStale.stale_count > 0` → surface those entries and re-validate each via the scoring protocol before acting on them; stale entries must not be used as ground truth. `outcomeReviewDueCount > 0` → ask the user whether to record what actually happened via `ledger record-outcome` for those entries. This only surfaces the reminder — the verdict is always a deliberate judgment call, never inferred automatically.
8. `deepScanPending` non-empty → a once-per-session `Stop`-hook scan of this workspace flagged real candidates (large files, secret-scan hits, TODO/FIXME markers) with an outline attached. For each candidate: read its actual content (bounded to what was flagged, not the whole repo), judge bug vs. feature-idea vs. dismiss, file via `ledger record-bug` / `ledger record-feature` as appropriate. `null` means nothing new since the last scan (session-to-session dedup by content hash) — nothing to do.
9. `otherActiveSessions` non-empty → another session is already registered as active in this same repo (`4orman-tools session-heartbeat`, 15-minute TTL, refreshed every turn via the `Stop` hook — confirmed live: two independent sessions built the same hook and the same subcommand on the same day with zero coordination). Surface it and confirm scope with the user before starting any Standard/Full-build task this session — don't silently risk duplicating work already in flight elsewhere. This only warns; it never blocks or locks anything.

If the hook's context is missing (it failed silently, or this session started some other way), fall back to running each check manually via the subcommand table below before proceeding.

- **Strict-mode finalize gate, even in autopilot:** for any Standard or Full-build task (Trivial is exempt, same boundary as `/verify-output`), before treating a commit/push/release/deploy as finished, squeeze it through one last verification pass — build, tests, and whatever safety check applies (`quality-gate`, `public-release-check`, etc.). A pass that doesn't come back clean means autopilot does not finalize on its own; it surfaces the failure and waits, same as `gate` mode. The gate only pauses — it never reverts, deletes, or force-fixes anything itself; that stays a separate, deliberate decision. Also compare this run's duration against the relevant subcommand's own previously-reported timing (`duration_ms`/similar, already present in `build`/`run-tests`/`worker-run`/`shell-run` output) — a measurable regression gets surfaced the same way a failed check would, not silently absorbed. The same applies in the other direction: a task framed as an optimization does not clear this gate on a claimed speedup alone — it needs the before/after numbers the Mathematical proof rule already requires, captured and shown, before autopilot treats it as finished. No numbers, no finalize, same as no numbers, no promotion. No silent "probably fine": the same standard `4orman-tools` itself holds to (compile-time errors over runtime guesses), applied to the moment work gets called done.
- **No silent errors, ever — and every message earns its keep:** every failure, from any surface (CLI, hook, subcommand), surfaces an explicit message; a bare non-zero exit or empty output is never acceptable on its own. Every surfaced message is actionable — state what to do next, not just what broke, the same pattern `compat-check`'s `rollback` field and `doctor`'s install-prompt already use, extended everywhere. Guard against user mistakes without condescension: validate and guide, never scold or over-explain what a competent user already knows. Keep the voice consistent across every surface — splash, `/help`, error text, hook messages — terse and action-oriented everywhere, not a stack trace in one place and marketing copy in another.
- **Verify the real artifact, not just the source fix:** a fix isn't finished when the source and tests pass — confirm the actual deployed/installed thing (the binary on `PATH`, the pushed repo, the live release) reflects it. Confirmed live: a Zig bug got fixed, tested, and "verified" three separate times against a local build before anyone noticed the globally-installed binary was three versions stale and still had the original bug — the source fix was real, but nothing checked whether it was actually running anywhere. Before calling a fix or release done, check what's actually installed/running/live, never just what's sitting in a source tree or a local build directory.
- **Idea-translation pass for loose/creative proposals** (`_skills/idea-translation.md`): when a request is loose, metaphor-heavy, or would otherwise take more than one "here's my restatement, is that right?" round to pin down, spawn a dedicated translator subagent instead of iterating in the main flow — its only job is converting the raw input into a precise spec (trigger, blast radius, definition of done, overlap with existing mechanisms). Translation is not validation: a well-specified idea can still not need to exist, so the translated spec still has to clear the Mathematical Proof gate before anything gets built. Still gray-area after the rewrite → drop it, log why in `ROADMAP.md`'s backlog, do not carry an ambiguous spec forward. Concrete and validated → the sandbox benchmark protocol below is the next stage, not a new evaluation mechanism; no positive benchmark → drop it and dispose of the sandbox artifacts per that protocol's own rule, same as any other non-winning candidate. Full sequence: translate → validate need → sandbox test → implement — never translate straight into implementation.
- **Sandbox side-by-side benchmark protocol:** before choosing between candidate modules/tools/libraries (or deciding whether a new one is even needed), check the ledger first for a non-stale precedent on this exact comparison — the same fuzzy word-overlap matching `findLedgerPrecedent` already does for tool-choice decisions. A match means reuse that verdict; do not re-run the benchmark. No precedent → build a disposable sandbox and run every candidate through the same real workload for 490 iterations — a single noisy run never decides this. Score on exactly three axes — speed, accuracy, correctness — as exact measured values, never a synthetic higher-is-vaguer rating. If the data shows a genuinely better option, apply it, then re-benchmark for another 490 iterations: original vs. updated, confirming the improvement is real before treating the decision as settled. If benchmarking a candidate fairly requires a Zig subcommand that doesn't exist yet, build it every time the need arises, same as the Zig-first escalation ladder already requires. Once a winner is chosen: dispose of every sandbox artifact tied to a losing candidate — scratch binaries, harnesses, template scaffolding — restoring anything reused back to its original, unmodified state. Exception: a new Zig capability built to run the benchmark and confirmed as the winning approach gets promoted (`capability-promote`), not disposed of — it earned its place the same way any other Zig-first win does. Record the result via `ledger record <winning-candidate> <question describing the comparison> <reasoning with the actual measured numbers>` — same `rps` category, same 365-day staleness rule as every other measured-data decision. No new ledger category or subcommand needed: the benchmark protocol is just another consumer of the ledger mechanism that already exists.
- **Bug tickets carry a lesson, not just a fix:** when `ledger record-bug` files something, its `reasoning` field captures what pattern it reveals, not just what broke. On every routine ledger check (the `SessionStart` hook's `ledgerStale`/`outcomeReviewDueCount` pass), also scan bug-category entries for a lesson that looks recurring or significant, not a one-off — that's a kaizen-ticket candidate. A kaizen-ticket candidate re-enters the sandbox side-by-side benchmark protocol above: build the disposable sandbox, test a proposed fix against the original for 490 iterations, and only apply it if the numbers back it up.
- **Zig-first (non-negotiable):** Before any action — data lookup, shell command, file read, build, test — check if a `4orman-tools` subcommand covers the need. One JSON call (~10–50ms) replaces 200–2000 tokens of Claude reasoning. Break-even or better → use Zig. When in doubt: `4orman-tools capability-check <what>` returns `{ available, subcommand }`. If no native subcommand exists: (1) check `_workers/` for an existing language worker → invoke via `4orman-tools worker-run <lang> _workers/<path> '<json>'`; (2) if no worker exists and the need is language-specific (web, ML, concurrency, JS ecosystem), run `/new-worker` to scaffold a permanent stdlib-only worker following senior-quality standards — one file, typed I/O contract, graceful errors, no external deps; (3) if pure computation with no existing coverage, use `4orman-tools shell-run <cmd>` so output is JSON, never raw text; (4) run `4orman-tools capability-promote <cmd>` — if the need appears 2+ times this session or score is high, implement it as a permanent Zig subcommand immediately: write to `4orman-tools/src/root.zig` + `main.zig`, bump VERSION, run `zig build -Doptimize=ReleaseSafe` so it is live in this session, then call `4orman-tools promotion-queue add <name> <description>` to queue it for the next release. The Stop hook will surface pending entries at session end. Claude decides. Zig orchestrates. Workers execute. Claude reads structured data. Repeated needs become permanent Zig subcommands or permanent workers. **Escalation ladder, explicit:** Zig solves it if a subcommand/worker covers it → else Claude designs and builds one via `capability-promote`/`/new-worker` → else, if Claude genuinely cannot design a solution (true unknown, not just unbuilt), stop and ask the user rather than guessing or fabricating an answer. Once a capability is promoted, checking for it via `capability-check`/`route` before reasoning is mandatory on every later occurrence of the same need — never re-solve by hand something Zig already knows how to do.
- **Subagent spawning is autonomous, not an ask-first action:** deploy the `Agent` tool whenever a task is genuinely broad, parallel, or context-heavy (multi-file exploration, isolated research, protecting main context from bulk results) — no confirmation needed, in autopilot or gate mode alike. It is a native Claude Code capability already covered by the session, not an external paid call, so it does not fall under "Any action that costs money." Do not spawn one for anything answerable with 1–2 direct tool calls. **Repeated roadblock, same approach, twice:** stop retrying inline — either delegate to a fork/subagent for a genuinely different angle, or recognize the blocker is an external constraint (missing dependency, environment limit) no amount of retrying or delegating will fix, and surface it to the user directly instead of spinning.
- **Before any action that touches git data, filesystem state, or project metadata:** use `4orman-tools` — full subcommand map:
  | Need | Subcommand |
  |---|---|
  | session deps (claude/git/gh present) | `4orman-tools doctor` |
  | tool version drift check vs baseline | `4orman-tools compat-check` |
  | workspace up-to-date vs origin | `4orman-tools status <workspace>` |
  | incoming commits + files changed | `4orman-tools changes-preview <repo>` |
  | commits since a tag (for release notes) | `4orman-tools commits <repo> [tag]` |
  | GitHub auth + login | `4orman-tools gh-user` |
  | latest tag, next version, dirty state | `4orman-tools release-info <repo>` |
  | remote owner/repo/url | `4orman-tools repo-info <repo>` |
  | check if a tag exists | `4orman-tools tag-exists <repo> <tag>` |
  | project structure, entry point, file inventory (use instead of find/ls) | `4orman-tools scan <path>` |
  | deterministic (import-count) vs actual (git first-commit) file ordering, side by side — a heuristic, not a resolved dependency graph | `4orman-tools recon-timeline <path>` |
  | structural diff of two directories (use instead of diff -r or manual comparison) | `4orman-tools diff-dirs <path1> <path2>` |
  | search for a string across multiple files (use instead of bash grep/rg) | `4orman-tools grep <root-path> <pattern> [ext]` |
  | find files by name/glob (use instead of bash find) | `4orman-tools find-files <root-path> <glob>` |
  | extract a value from a JSON file (use instead of reading the whole file) | `4orman-tools json-query <file-path> <dot-path>` |
  | structured diff summary — use instead of reading raw git diff output | `4orman-tools git-diff <repo-path> [ref]` |
  | immediate directory contents (use instead of bash ls or shallow find) | `4orman-tools list-dir <path>` |
  | line count + byte size of a file (use instead of wc -l or stat) | `4orman-tools file-stats <file-path>` |
  | .env* file keys in a project root (keys only, never values) | `4orman-tools env-scan <root-path>` |
  | extract a value from a TOML file (Cargo.toml, pyproject.toml) | `4orman-tools toml-query <file-path> <dot-path>` |
  | stack trace in context — pipe it here to get structured file:line:col:fn JSON instead of reading it manually | `4orman-tools parse-stack` (reads stdin) |
  | GitHub repos with isForeman + isLocal flags (use instead of gh repo list + per-repo API) | `4orman-tools list-projects <4orman-root>` |
  | GitHub tarball SHA256 with retry (use for a Homebrew formula update instead of curl \| shasum) | `4orman-tools tarball-sha <owner> <repo> <tag>` |
  | Homebrew formula fields — url, sha256, version (use instead of reading .rb by hand) | `4orman-tools formula-info <tap-path> <formula-name>` |
  | Claude Code Stop hooks present check (use in /setup-automation and /first-run instead of jq) | `4orman-tools validate-hooks` |
  | GitHub release creation via notes file (use in /release instead of --notes "...") | `4orman-tools gh-release <owner> <repo> <tag> <title> <notes-file>` |
  | SHA256 hash of a local file (use before re-reading to detect if file changed) | `4orman-tools file-hash <abs-file-path>` |
  | Skip re-reading an unchanged file — `hit: true` means use `value` directly without reading; `hit: false` means read + extract + call cache-store | `4orman-tools cache-fetch <abs-file-path> <sub-key>` |
  | Store extracted JSON after a cache miss so next call is a hit (stdin → cache, auto-invalidates when file changes) | `echo '<json>' \| 4orman-tools cache-store <abs-file-path> <sub-key>` |
  | Use ONLY when you need to know if a file changed and have no extracted value to store (rare) | `4orman-tools cache-check <abs-file-path>` |
  | **One-call Compact Context Manifest** for any task touching more than one file — composes context-rank, context-changed, secret-scan, context-classifier, and (for architecture_refactor tasks) context-dependency-graph + context-compressor internally. Call this FIRST, before any ad-hoc multi-file read or a manual context-scan+context-rank+context-changed chain — it replaces all three | `4orman-tools context-gate <abs-path> --task "<description>"` |
  | Compact project summary (structure + top 10 files by size) — use instead of `scan` when only structure is needed, not the full file inventory | `4orman-tools context-scan <abs-path>` |
  | deep-scan — composes context-scan/secret-scan/grep(TODO\|FIXME) into flagged candidates with an outline attached; session-to-session deduped by content hash (`~/.4orman/deep-scan-seen.json`) so an unresolved marker isn't re-flagged every session. Runs automatically once per session via the `Stop` hook, written to `~/.4orman/deep-scan-pending.json`; `SessionStart` surfaces `deepScanPending` — when non-empty, read each candidate's actual content and file it via `ledger record-bug`/`record-feature` as appropriate, or dismiss if neither applies | `4orman-tools deep-scan <abs-path>` |
  | Relevance ranking — score and rank files by query relevance so Claude reads most-important files first (top 15, content + name match) | `4orman-tools context-rank <abs-root-path> <query>` |
  | Changed files with unified diff content — orient to what changed without reading raw git output (first 8 files, 100 lines/file) | `4orman-tools context-changed <repo-path> [ref]` |
  | Evidence packets — relevant excerpts from a file without reading the whole thing (case-insensitive, ±10 lines context, merged windows, up to 8 chunks) | `4orman-tools context-evidence <abs-file-path> <pattern>` |
  | extract a value from a YAML file (GitHub Actions, docker-compose, k8s, Rails) | `4orman-tools yaml-query <file-path> <dot-path>` |
  | structural outline of a source file (function/class/struct names + line numbers) — use instead of reading the full file when you only need to understand its structure | `4orman-tools outline <abs-file-path>` |
  | project dependencies from any package manifest (package.json/Cargo.toml/go.mod/requirements.txt) — use instead of reading the manifest when you only need the dep list | `4orman-tools deps <abs-root-path>` |
  | run tests + get structured pass/fail/failures (use instead of running the test command and reading raw output); `resolvedBy` is `"detection"` (unambiguous), `"ledger"` (multiple frameworks found, an exact-match ledger precedent named one), or `"tie-break"` (`roleConfidence: "uncertain"` — no precedent, picked `uncertaintyCandidates[0]` by priority order, resolve and `ledger record`) | `4orman-tools run-tests <abs-root-path>` |
  | detect build system, run build, get structured errors/warnings (use instead of running the build command and parsing raw compiler output); same `resolvedBy`/`roleConfidence` contract as `run-tests` | `4orman-tools build <abs-root-path>` |
  | detect languages, runtimes, package managers, and missing deps for a project (use instead of running which/--version loops) | `4orman-tools env-inspect <abs-root-path>` |
  | locate a symbol's definition and all references across a project (use instead of grep + read N files) | `4orman-tools symbol-find <abs-root-path> <symbol>` |
  | scan for hardcoded secrets (API keys, tokens, passwords, private keys) across a project | `4orman-tools secret-scan <abs-root-path>` |
  | match raw log text (stdin) against a caller-supplied pattern-library JSON file — domain-agnostic, no log-format vocabulary baked into the binary; the domain knowledge lives in the caller's own pattern file | `4orman-tools log-match <pattern-file>` |
  | best-effort immediate cleanup of a session's `session-heartbeat` presence entry on clean exit — not the sole cleanup path, the 15-min TTL is the real safety net | `4orman-tools session-unregister <repo-path> <session-id>` |
  | domain-agnostic doc-vs-reality drift check — which of a caller-supplied list of names is missing (whole-word) from a doc file; e.g. command files vs `/help`, or a registry dump vs this file | `4orman-tools names-check <doc-path> <comma-separated-names>` |
  | snapshot hardware + tools + optimal settings to `~/.4orman/profile.json` (run once per device) | `4orman-tools device-scan` |
  | changed symbols since a ref + their callers — use instead of reading raw diffs for impact analysis | `4orman-tools delta-context <repo-path> [ref]` |
  | branch, HEAD SHA, dirty state, ahead/behind, last 10 commits — cached by HEAD SHA, hit: true within same HEAD | `4orman-tools git-cache <repo-path>` |
  | read/write project decisions and known patterns across sessions (state at `~/.4orman/state/`) | `4orman-tools project-state <abs-path> [record-decision <what> [<why>]]` |
  | decision ledger — show/record/validate Claude-vs-Zig decisions with 365-day staleness (stored at `~/.4orman/ledger.json`) | `4orman-tools ledger [show \| record <winner> <question> <reasoning> \| check-stale \| validate <id>]` |
  | Jungian ledger category — for values/trade-off decisions with no measured data, no credible source, no formal proof (the "Mathematical proof" gate has nothing to check), and that can't be deferred. No winner, no contest — record `chosen` (the decision), `shadow` (the strongest case against it, not a strawman), and `synthesis` (what's retained from the rejected alternative, what's consciously sacrificed). Never consulted by `capability-check`/`route`/`build`/`run-tests` — values trade-offs must never silently override a factual or tool-choice decision | `4orman-tools ledger record-jungian <question> <chosen> <shadow> <synthesis>` |
  | ledger outcome tracking — retrospective: did a past decision's prediction actually hold up? Applies to any entry, rps or jungian. `<matched\|diverged>` must be exactly one of those two words. `ledger show` surfaces `outcomeReviewDue: true` (30+ days unrecorded, a shorter clock than the 365-day staleness one) — reminder only, never auto-judged | `4orman-tools ledger record-outcome <id> <outcome> <matched\|diverged>` |
  | score a contested decision — Zig computes composite from cited sources, checks ledger, returns winner/void verdict | `4orman-tools ledger score <question> <sources-json>` |
  | bug-fix ticket ledger — same `~/.4orman/ledger.json`, `category: "bug"`, tagged by `<project>` so it stays useful across every project in your workspace, not just one. `find-bug` fuzzy-matches by word overlap (default threshold 30) and returns every match above it with a `score` — read the fix and judge whether it's actually the same bug, don't trust a single hit blindly. Before deep-diagnosing an unfamiliar error, run `find-bug` first; after fixing a genuine bug (not a design decision), run `record-bug`. Pass `[vendor-name]` when a 3rd-party app/plugin/service is the root cause (Claude's own judgment call, never auto-detected) — the JSON output then also carries a `vendorEmail` (subject/bullets aggregating every past+present ticket against that vendor/signature placeholder) with `needsFrom`/`needsTo`/`needsCc: true`: ask the user for those three addresses before treating the draft as usable. Never auto-sent — no email transport exists here | `4orman-tools ledger record-bug <project> <error-signature> <fix> [fixed\|open] [vendor-name] / ledger find-bug <query> [threshold] [max-results]` |
  | feature-ticket ledger — same `~/.4orman/ledger.json`, `category: "feature"`. Whenever a substantial brainstorm/idea gets pasted in conversation, evaluate it with the same rigor `/new-project`'s spec interview would (fit, feasibility, what's genuinely uncertain — ask the user only for that), bias toward the richest feasible scope rather than a minimal one, then file the result. `readiness` is `ready` (confidently scoped) \| `needs-input` (had to ask the user) \| `deferred` (evaluated, not pursued now); `status` derives from `artifact-ref` — empty until `/new-project` actually scaffolds something from it | `4orman-tools ledger record-feature <domain> <idea-summary> <ready\|needs-input\|deferred> <tool\|doc\|project\|none> <artifact-ref> <reasoning> <shadow> <synthesis>` |
  | run a shell command safely — blocks destructive patterns, captures stdout/stderr as JSON, tracks duration | `4orman-tools shell-run [--timeout <ms>] <shell-command>` |
  | aggregate build + test results into a severity-bucketed verdict (pass/fail + critical/high/medium/low findings) | `4orman-tools quality-gate <abs-path>` |
  | validate a JSON file against a JSON Schema subset — returns violations with $-rooted paths | `4orman-tools validate-schema <abs-file> <abs-schema>` |
  | composite production readiness check — runs quality-gate + secret-scan + env-inspect; returns `{ ready, blockers, warnings }` | `4orman-tools prod-ready <abs-path>` |
  | machine-readable catalog of all subcommands — returns `{ version, subcommands: [{name, description, args}] }` | `4orman-tools registry` |
  | check if a capability is natively available, has a non-stale ledger precedent, or needs Claude fallback — `source` is `native`\|`ledger`\|`claude`; `needsDecision: true` means neither exists — resolve now and `ledger record` the verdict | `4orman-tools capability-check <query...>` |
  | task router — same 3-way check as `capability-check`, enriched into steps `{ routed, steps: [{layer, subcommand, argHint, confidence, reason}], fallback, reason }`; a `ledger`-layer step means reuse the recorded decision, don't re-reason | `4orman-tools route <task...>` |
  | recommend solo vs multi-agent for a Standard/Full-build task — ledger `record-approach` precedent first, then a trivial/standard/full-build heuristic; `needsDecision: true` means genuinely ambiguous, resolve and `ledger record-approach` afterward | `4orman-tools delegation-check <task-type> <trivial\|standard\|full-build>` |
  | ROI-ranked learn/build inventory check for a tech domain/topic — ledger `record-curriculum` precedent only, no fallback taxonomy; `needsDecision: true` means decide the ROI tier as a values call and record via `ledger record-curriculum` | `4orman-tools curriculum-check <domain> <topic>` |
  | all recorded curriculum entries for a domain, sorted highest-ROI first | `4orman-tools curriculum-list <domain>` |
  | gated ROI check for a proposed change to 4orman's own architecture — `recommend: "build"` only if estimated improvement is >= 1% with no drawbacks, else `"reconsider-with-user"`; ledger `record-architecture` precedent first | `4orman-tools architecture-check <topic> <estimated-improvement-pct> <true\|false>` |
  | all recorded architecture-change proposals, sorted highest-ROI first — the growth-monitoring view | `4orman-tools architecture-list` |
  | composite project status — git state + build + tests + secrets → `{ status, confidence, issues, nextAction }` | `4orman-tools report <abs-path>` |
  | telemetry snapshot — cache entry count, project-state decisions/patterns, device-profile + compat-baseline presence, estimated token savings | `4orman-tools metrics` |
  | write ground-truth session state (version, wave, current step, pending errors) to `~/.4orman/session-snapshot.json` — called by PreCompact hook before every compaction | `4orman-tools session-snapshot <4orman-root>` |
  | classify a shell operation by severity (safe/caution/destructive/blocked) and return whether it is allowed — use before any shell command that modifies state | `4orman-tools sandbox-check <command...>` |
  | snapshot/list/revert git state — capture current HEAD+branch, list stored snapshots, or get revert commands for a snapshot | `4orman-tools rollback <repo-path> [--list \| --revert <id>]` |
  | score a repeated shell command for 4orman-tools promotion eligibility — use in `/verify-output` Step 7 for any command repeated 2+ times this session | `4orman-tools capability-promote <command...>` |
  | list files changed in a path since a timestamp (mtime-based, no git required) — use at session start to find what changed since last session | `4orman-tools ant <path> [--since <ms>]` |
  | run a script in a language runtime (python/node/deno/bun/go/ruby/bash/swift/zig/lua/php) — returns `{ lang, interpreter, exit_code, stdout, stderr, duration_ms, timed_out, truncated }` | `4orman-tools worker-run <lang> <script> [args...]` |
  | list all supported language workers with binary name and file extension | `4orman-tools worker-list` |
  | focused project slice — top 8 files ranked by relevance + evidence excerpts; give to a subagent instead of full context | `4orman-tools context-slice <abs-path> <focus-query>` |
  | merge two JSON objects — array fields concatenated, non-array fields v2 wins; combine multi-agent partial results | `4orman-tools state-merge <file1> <file2>` |
  | interactive split-panel project dashboard — left panel lists projects, right panel shows release state + MVP readiness; j/k nav, r reload, q quit | `4orman-tools tui [<4orman-root>]` |
  | pre-export/archive gate — scans a project for spec.md, CLAUDE.md decision log, knowledge/ mirror, git cleanliness, push state, ledger refs, _skills/ mentions; returns `{ ready, captured, unextracted, warnings }` | `4orman-tools knowledge-audit <project-path> [<4orman-root>]` |
  | package a project as .fmz archive or generate a platform installer script — formats: fmz, brew, mac, linux, windows, backup | `4orman-tools export <project-path> [--format fmz\|brew\|mac\|linux\|windows\|backup] [--out <dir>]` |
  | absorb a .fmz or raw project directory into the 4orman workspace; detects workspace backup vs single project; restores knowledge/ | `4orman-tools import <source-path> [<4orman-root>]` |
  | track Zig subcommands built locally but not yet released — Stop hook surfaces pending count at session end | `4orman-tools promotion-queue [list \| add <name> <description> \| clear]` |
  | list installed plugins (name, lang, description, args) — use in `/install-plugin`/`/export-plugin` instead of reading plugin.json by hand | `4orman-tools plugin-list` |
  | execute an installed plugin via its worker runtime — returns plugin JSON output verbatim | `4orman-tools plugin-run <name> [args...]` |
- **Before any task that will touch more than one file (a bug fix, a refactor, "what's in this project" exploration):** call `4orman-tools context-gate <abs-path> --task "<task description>"` first — it returns a Compact Context Manifest (`taskType`, ranked `include.files`, `token_estimate`, `risk`, `next_action.send_to_ai`) instead of Claude chaining `context-scan`/`context-rank`/`context-changed`/`secret-scan` calls itself. If `next_action.send_to_ai` is `false`, stop and follow `reason` (secrets found → redact first; risk `high` → narrow the task) before reading any of the listed files. This is the entry point for the Zig Context Translator (Wave 5 Phases 1–2) — every subcommand it composes still exists standalone for narrower needs, but a multi-file task should start here, not with a manual `context-scan` + `context-rank` chain.
- **Before reading any large project file (spec.md, CLAUDE.md, ROADMAP.md, any source file >2KB):** call `cache-fetch <abs-path> <sub-key>` first — if `hit: true` use `value` and skip the read entirely. If `hit: false`: read the file, extract the key facts as JSON, call `cache-store`. Cache is local disk (`~/.cache/4orman-tools/`), persistent across restarts and power loss, auto-invalidates on file change. Standard sub-keys: `spec.md` → `"milestones"`, `CLAUDE.md` → `"guardrails"`, `ROADMAP.md` → `"state"`, source files → `"outline"`.
- **At the start of every session, and whenever the user says "next", "continue", or similar:** determine the absolute path to `ROADMAP.md` in the 4orman workspace root (same directory as this CLAUDE.md), then call `4orman-tools cache-fetch <abs-path-to-ROADMAP.md> state` — if `hit: true`, use the cached state directly. If miss or stale binary, read `ROADMAP.md`. The "Active Work" section at the top shows exactly where to resume. Do not ask the user what they were doing; the answer is there.
- **Knowledge State Taxonomy — three tiers, three rules:**
  - **Permanent Truth** — never touched by any hook or command: `~/.4orman/ledger.json`, `~/.4orman/session-snapshot.json`, `~/.4orman/profile.json` (clear only on hardware change), `~/.4orman/state/`
  - **Pinned Knowledge** — promoted out of cache; required at every session start; *not deleted, only invalidated then regenerated*: `CLAUDE.md → guardrails`, `ROADMAP.md → state`, `spec.md → milestones`, `_skills/README.md → outline`. Rule: source file hash same → use pinned value directly. Hash changed → rebuild that sub-key only, re-store. Value corrupt or source missing → mark stale, rebuild from source, never trust stale. Essential knowledge is not deleted; it is invalidated, regenerated, and verified.
  - **Disposable Cache** — outlines for changed source files, parse summaries, build artifacts, temp results. Hash invalidation handles stale entries automatically on next access. On session close: Stop hook purges entries older than 30 days. After `knowledge-audit ready: true`: that project's disposable entries may be cleared. Full purge of `~/.cache/4orman-tools/` is last-resort only (confirmed corruption). Never clear on session start.
- **At the start of every session:** if `_projects.md` does not exist, create it by copying `_templates/projects.md`. `_projects.md` is git-ignored **local** state (your private project index) — it is never tracked by or committed to the framework repo, so editing it never makes the workspace dirty or blocks self-update.
- Run `/verify-output` before marking any task complete — Claude runs this, not the user. Skip for trivial tasks (see **Scale to task size** below).
- **After any contested decision where Claude overrides Zig data OR Zig proves superior:** record via `4orman-tools ledger record <winner> <question> <reasoning>` — winner is "claude" or "zig", question is the contested claim, reasoning is the evidence summary. Only record confirmed wins; void rounds are not recorded.
- **After completing any milestone step:** update `ROADMAP.md` in that project — check the step done (`[x]`), update the current milestone status — before asking the user to proceed with the next step. Never skip this update.
- Document key decisions in the project's `CLAUDE.md` decision log (not spec.md)
- Check `_skills/README.md` for relevant playbooks before starting work in a new domain or project type
- Update `_knowledgebase/` and `_skills/` when candidates surface during `/verify-output` Step 6
- Prefer editing existing files over creating new ones
- Keep changes small and reversible
- **After `/new-project` or after adding/editing any command or skill:** read and follow `_skills/foreman-tools-audit.md` — one-minute check for shell patterns worth promoting to a 4orman-tools subcommand.
- **After committing changes to any project:** read and follow `_skills/release-notes.md` — check if commits have accumulated since the last tag and, if so, remind the user: "You have unreleased changes in `<project>` since `<last-tag>`. Run `/release` when ready to publish." Do not generate notes unprompted — just surface the reminder.
- **Every compaction summary MUST open with this exact block** (populated from the `session-snapshot` values injected by the PreCompact hook):
  ```
  Current version: vX.X.X
  Last completed: [subcommand name]
  Next step: [exact text from ROADMAP Active Work **Current:** line]
  Pending errors: [none | verbatim error text]
  ```
  These four lines are machine-readable ground truth. Never recall them from memory — they come from the hook. Claude narrates context below this block; the block itself is never paraphrased or omitted.

### Scale to task size

Before starting, classify the task and match the treatment:

- **Trivial** — question, lookup, one-liner fix. Answer directly. No spec, no `/verify-output`.
- **Standard** — a bug fix, a contained feature, a single-file change. Run the normal workflow. Skip `/verify-output` only when the change is a single, obvious, reversible fix.
- **Full build** — a new project, a major feature, anything touching multiple files or introducing new architecture. Full 3-layer treatment without exception: spec → build → verify-output.

**Dry-run-first standard, every Standard/Full-build task — not optional:** before running a newly-written or generated command/script for the first time for real, validate it via real execution first — a disposable workspace, a real subprocess, a real exit code, never a simulated guess. Require a real pass before trusting the command for real. This standard exists precisely to catch the class of failure where a failing or name-colliding generation could silently destroy prior, already-proven output — the goal is to catch that before it touches anything real, and to avoid re-doing work a dry run would have caught first.

Before any Standard or Full build task (skip Trivial — no informational value, same reason `/verify-output` is skipped), call `4orman-tools delegation-check <task-type> <trivial|standard|full-build>`. If it returns `needsDecision: true`, resolve deliberately (default to its `recommend` if genuinely unclear) and `ledger record-approach` the actual outcome afterward so the same task type isn't re-litigated next time.

On an explicit user request naming a tech domain/profession, or a recurring knowledge/tool gap noticed 2+ times this session, call `4orman-tools curriculum-check <domain> <topic>` before deciding to learn/build something new for it. If a stored decision exists, reuse it. If `needsDecision: true`, decide the ROI tier as a values call — no formal proof exists for "highest ROI topic to learn," treat it like the Jungian ledger protocol (chosen priority, strongest case against it, what's sacrificed) — then `ledger record-curriculum` so it isn't re-derived for the same domain+topic. Check `4orman-tools curriculum-list <domain>` first to see the accumulated inventory before deciding what's next.

Before proposing any change to 4orman's own architecture (a new guardrail, subcommand, or hook — not a bug fix, not a change to a consuming project), call `4orman-tools architecture-check <topic> <estimated-improvement-pct> <true|false>` with an honest estimate and drawback assessment. If `recommend: "build"`, proceed. If `"reconsider-with-user"` (or `needsDecision: true`), stop and ask explicitly rather than silently building or silently dropping it — the gate exists specifically so anything short of it is a deliberate human call. Afterward, `ledger record-architecture` the outcome so it's never re-litigated for the same topic. Check `4orman-tools architecture-list` for the accumulated backlog and `4orman-tools metrics`'s `architectureLedger` field to see how it's growing over time before proposing something that might already be recorded.

### Ask first (consequences)
- Any action that costs money — API calls, cloud deploys, paid services
- Installing, upgrading, or removing packages
- Copying, moving, or creating files outside the current project's directory
- Any database read or write operation
- Sending messages, emails, or notifications of any kind
- Any one-way or hard-to-reverse decision **not** covered by the auto-execute rule below
- Running scripts you didn't write
- Any mid-project scope change — propose the change, get sign-off, then update spec.md

### Auto-execute (commit/push, no ask)

Commit and push without asking when the change already cleared full validation: build/tests/relevant Zig checks (`public-release-check`, `quality-gate`, `architecture-check`, etc.) all green, zero errors, no contradictions between them. If Zig returns a `recommend`/`winner` field, take it — don't re-ask something Zig already answered. If several valid options exist and none contradict, ship all of them rather than picking one to ask about. If the outcome is genuinely uncertain, run the real test/verification first — a clean result after testing **is** the approval, no separate ask needed. Report what shipped after the fact instead of asking before.

Fall back to asking first when validation fails, is incomplete, or gives ambiguous/contradictory signals, or for anything still listed under "Ask first" above (money, messaging, packages, destructive ops) — this rule only relaxes commit/push on already-validated work, not those.

### Mathematical proof (non-negotiable)

Every architectural decision, performance claim, or worker promotion must be backed by one of:
- **Measured data** — `4orman-tools metrics` before and after; state both numbers
- **100% credible online source** — state the exact URL and specific claim; training memory alone is not evidence
- **Formal proof** — state the algorithm, complexity class, and why it dominates

If neither is available: do not proceed. Run the measurement first, then decide. **Exception:** a values/trade-off decision with genuinely no factual answer and that can't be deferred — use `ledger record-jungian` instead of guessing (see subcommand table). This is not a loophole around measuring when measurement is possible; it's for the class of decision measurement can't touch.

When a worker or subcommand produces output: `confidence` and `self_healed` fields quantify result quality mathematically. `confidence: 1.0` = complete. `confidence < 0.8` = degraded; report to user before acting on the result.

**First: check Zig's memory.** `capability-check`/`route` already do this automatically — before falling back to Claude they consult the ledger for a non-stale precedent (`source: "ledger"`). `build`/`run-tests` do too: when tool/framework detection is genuinely ambiguous (e.g. both `Cargo.toml` and `build.zig` present), they check the ledger for an exact-match precedent *before* choosing which tool to invoke — if an unambiguous one exists (`resolvedBy: "ledger"`), it overrides the tie-break; if not, they flag `roleConfidence: "uncertain"` (`resolvedBy: "tie-break"`) instead of silently guessing. `quality-gate` (which runs both) reports the resolved case as a `low`-severity note and the unresolved case as `medium` — a priority decision to resolve and `ledger record`. For anything not going through these, run `4orman-tools ledger show` directly — if Zig has a stored entry for this question (non-stale), use it. Zero tokens. Only when nothing has a native or ledger answer does Claude reason fresh and enter the scoring protocol below — and must `ledger record` the verdict afterward so it isn't re-litigated next time.

### The Ledger — Rigged Rock-Paper-Scissors

Every contested decision between Claude reasoning and Zig stored data runs through this protocol. The game is rigged toward mathematical truth, not toward either player.

**Claude wins a round when all four conditions are met:**
1. Composite confidence score is exactly 100%
2. Score is backed by minimum 10 sampled sources retrieved online this session
3. Every source is cited with exact URL and specific claim — no paraphrasing
4. Zig has no stored ledger entry on this question, or the stored entry is stale

**Zig wins a round when all three conditions are met:**
1. A ledger entry exists for this question at `~/.4orman/ledger.json`
2. Entry is not stale — recorded within the last 365 days
3. Claude cannot produce 10 verified sources that contradict the stored data

**Round is void when:** composite below 100%, fewer than 10 sources, or evidence is contradictory. No promotion, no decision — gather more evidence first.

**Scoring formula** — Zig computes, Claude never self-certifies:
```
4orman-tools ledger score <question> <sources-json>
```
Returns `{ composite, sample_count, winner, void, reason, zig_entry_found, zig_entry_stale }`.

Per source: cited URL retrieved this session + exact claim = 10 pts; training memory alone = 0 pts; contradicted by another source = −10 pts. Composite = total_points / (sample_count × 10) × 100. Minimum 10 sources or automatic void.

**Tiebreaker:** Zig wins. Stored verified data costs zero tokens. A 100% Claude score that agrees with a valid Zig entry confirms the entry — Zig retains the win.

**Staleness:** After 365 days Zig's entry is stale. `4orman-tools ledger check-stale` runs at every session start. Stale entries surface immediately — Claude never silently relies on outdated Zig data. Claude re-samples 10 sources; if score reaches 100% on updated data, Claude wins and the ledger updates.

**Promotion gate:** Only a confirmed win triggers promotion. Claude win → capability promoted to permanent Zig subcommand or worker immediately. Zig win → stored entry confirmed, no new build needed. Void → no promotion.

**Hard rules:**
- Claude never scores its own round — Zig computes and returns the JSON verdict
- Training memory alone scores 0 — never counts toward the 100% threshold
- A void round never promotes anything
- The ledger is append-only — old entries are never deleted, only superseded by newer entries on the same question

### Self-healing (automatic, modular)

Workers and subcommands self-heal before escalating to the user:
1. **Detect** — output schema is declared; violations surface as `schema_violations` in JSON
2. **Retry** — network workers retry 3× with exponential backoff before reporting failure
3. **Degrade gracefully** — partial results are valid; `confidence` quantifies completeness
4. **Report** — `self_healed: true` marks any output that required recovery; never silently wrong
5. **Escalate** — only if `success: false` after all retries; surface structured error, not raw exception

Claude reads `confidence` and `self_healed` on every worker output. If `confidence < 0.8`: investigate before acting. If `self_healed: true`: note it but proceed if `success: true`.

### Never do (hard lines)
- Touch production systems, databases, or live infrastructure
- Expose, log, print, or echo API keys, passwords, tokens, or secrets
- Send real emails, SMS, or messages to real users
- Modify another project's files without explicit permission
- Delete any file — deletion is blocked; if a file needs to go, tell the user and let them do it
- Skip the spec interview (`/new-project`) when starting fresh work
- Commit or push code that hasn't cleared the auto-execute validation bar (see below) or been reviewed
- Add features, abstractions, or error handling beyond what was asked
- Make an architectural decision based on a guess — measure first, decide after
- Accept worker output with `schema_violations` as correct — investigate the violation

### Token discipline (when editing framework files)

Every line in every command, skill, template, and CLAUDE.md loads into Claude's context and costs tokens on every use. When making changes to framework files:

- **Earn your tokens** — every line must change behavior or prevent a real mistake. If removing it wouldn't change what Claude does, remove it.
- **One location per rule** — if a rule exists in CLAUDE.md, it must not be repeated in a command or skill. Pick the authoritative location and delete the duplicate.
- **No rationale commentary** — explain the *what*, never the *why*. The reason a rule exists belongs in a commit message or PR description, not in the prompt file loaded every session.
- **No placeholder sections** — "Results: TBD", "TODO: fill in later", projected future entries. If it has no content yet, delete the section entirely.
- **No obvious instructions** — don't tell Claude things it already knows (e.g. "read the file before editing", "don't guess", "use good judgment"). Reserve instructions for non-obvious constraints only.
- **Tighten, don't expand** — when editing framework files, the default move is to shorten. If your edit makes a file longer, you need a strong reason.

---

## Directory Structure

```
4orman/
├── CLAUDE.md
├── .claude/
│   ├── settings.json          ← permissions & hooks
│   └── commands/
│       ├── new-project.md     ← Layer 1: spec interview + scaffolding
│       └── verify-output.md   ← Layer 2: self-review + critic agent
├── _templates/
│   ├── project_claude.md      ← per-project CLAUDE.md template
│   └── spec_output.md         ← spec format (single source of truth)
├── plugins.public.yml         ← public plugins anyone can install via /setup
├── plugins.local.yml          ← your private repos (git-ignored — create from .example)
├── plugins.local.yml.example  ← template for plugins.local.yml
├── _projects.md               ← index of all projects and their status
├── _knowledgebase/            ← domain knowledge shared across all projects
├── _skills/                   ← reusable prompt patterns & playbooks
└── [project-name]/            ← each project lives here (git-ignored — own private repo)
    ├── CLAUDE.md
    ├── spec.md
    ├── knowledge/             ← project-specific knowledge
    └── ...
```

## Projects vs Plugins

**Projects** — built inside `4orman/`, own git repo, git-ignored by pattern (any root dir not starting with `_` or `.`). Public or private GitHub repo.
**Plugins** — extend 4ORMan (new commands, skills, knowledgebase). Listed in `plugins.public.yml` (tracked) or `plugins.local.yml` (git-ignored). Share private plugins as zip: `/export-plugin` → `/install-plugin`.

---

## Completing a project

When all M3 criteria are met: run `/verify-output` against the M3 "Done when..." criteria, then update `_projects.md` to `complete`. Do not mark complete if any M3 criterion is unmet — downscope or move to v2.

---

## Updating a spec mid-project

Stop implementation → propose the change (what's changing, why, what it affects) → get explicit sign-off → update `spec.md` → log the decision in `[project]/CLAUDE.md` → continue.
