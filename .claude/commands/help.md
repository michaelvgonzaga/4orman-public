# 4ORMan Help

---

**Core workflow**

| Command | What it does |
|---------|-------------|
| `/help` | Show this list |
| `/new-project` | Start a new project — spec interview, scaffolding, and sign-off before any work begins |
| `/verify-output` | Verify any output before marking it done — self-review + independent critic agent |
| `/gate` | Toggle autopilot vs. confirm-before-acting for the rest of this terminal session |
| `/build` | Build the project and surface structured errors with file:line navigation |
| `/run-tests` | Run the project's test suite and surface structured failures |
| `/quality-gate` | Run build + tests and get a severity-bucketed pass/fail verdict |
| `/prod-ready` | Composite production readiness check — build, tests, quality gate, secrets, env |

**Setup & plugins**

| Command | What it does |
|---------|-------------|
| `/setup` | Install available plugins from the public list and your private repos |
| `/setup-automation` | Install per-machine auto-sync/auto-push Stop hooks into `~/.claude/settings.json` — run once on a new machine |
| `/first-run` | First-run wizard — dependency checks, GitHub auth, mode selection, knowledge restore |
| `/export-plugin <name>` | Package a plugin as a zip file to share with anyone |
| `/install-plugin <path>` | Install a plugin from a zip file |
| `/new-worker` | Scaffold a permanent stdlib-only language worker in `_workers/` |

**Projects**

| Command | What it does |
|---------|-------------|
| `/absorb` | Find a file, repo, or project → bring it into 4ORMan → scan, fix, and iterate to production |
| `/study-repo` | Study an external project read-only — distill it, propose ROI-ranked improvements, simulate them, record findings in a dedicated `<project>-casestudy` repo |
| `/from-context` | Paste raw notes/requirements/code and turn them into a scoped task |

**Releases**

| Command | What it does |
|---------|-------------|
| `/release` | Cut a GitHub release — CHANGELOG, tag, push, GitHub release |
| `/auto-private-release` | Fully automated private release — one confirmation, then runs end-to-end |
| `/manual-private-release` | Manual private release — pauses for confirmation before each push and tag |

**Memory & cache**

| Command | What it does |
|---------|-------------|
| `/sync-memory` | Back up machine-local Claude memory to a private repo, or restore it on a new machine |
| `/auto-delete-cache` | Delete all disposable cache entries automatically, no confirmation |
| `/manual-delete-cache` | Delete disposable cache entries with a preview and explicit confirmation |
| `/4orman-quiet` | Suppress `4orman-tools` hook activity in the terminal |
| `/4orman-watch` | Show `4orman-tools` hook activity in the terminal |

**Plugin files**

| File | What it is |
|------|------------|
| `plugins.public.yml` | Public plugins anyone can install — add your public plugins here |
| `plugins.local.yml` | Your private repos — git-ignored, never pushed (create from `.example`) |

**First time here?**
Run `/first-run`.

---
