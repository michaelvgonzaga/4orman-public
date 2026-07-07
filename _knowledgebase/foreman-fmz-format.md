# 4ORMan: .fmz Plugin/Project Format

**Source:** 4orman-tools source (`computeExport`, `computeImport`, `exportWriteManifest` in root.zig) + direct experiment
**Last verified:** 2026-07-01
**Confidence:** High — derived directly from the v0.60.0 implementation

---

## What we know

### .fmz is a renamed tar.gz

A `.fmz` file (4ORMan Module Zip) is a standard gzip-compressed tar archive with a `.fmz` extension. Any `tar -xzf` command can extract it. The extension signals "this is a 4ORMan package" and triggers special handling in `4orman-tools import`.

### Archive structure

```
<name>-<version>/
├── 4orman.manifest.json      ← required — package identity and metadata
├── project/                   ← git archive of HEAD (all tracked files)
│   ├── CLAUDE.md
│   ├── spec.md
│   └── ...
└── knowledge/                 ← optional — copied from <project>/knowledge/ if present
    └── *.md
```

For workspace backup format (`--format backup`):
```
4orman-backup/
├── 4orman.manifest.json      ← kind: "workspace"
├── CLAUDE.md                  ← framework files
├── ROADMAP.md
├── _templates/
├── _knowledgebase/
├── _skills/
├── ledger.json                ← ~/.4orman/ledger.json snapshot
└── projects/
    ├── my-api-v1.3.0.fmz
    └── my-tool-v0.2.0.fmz
```

### 4orman.manifest.json schema

```json
{
  "name": "my-api",
  "version": "v1.3.0",
  "foreman_min": "v0.60.0",
  "description": "",
  "kind": "project",
  "github_url": "https://github.com/user/my-api",
  "deps": {
    "brew": [],
    "apt": [],
    "winget": []
  },
  "knowledge_files": []
}
```

| Field | Type | Notes |
|---|---|---|
| `name` | string | basename of project directory |
| `version` | string | latest git tag or `"0.0.0"` if untagged |
| `foreman_min` | string | 4orman-tools VERSION at export time |
| `kind` | string | `"project"` or `"workspace"` — import uses this to detect backup vs project |
| `github_url` | string | parsed from git remote origin; empty if no remote |
| `deps.brew/apt/winget` | array | runtime deps for installer scripts (currently always empty — manual population needed) |
| `knowledge_files` | array | reserved — currently always empty |

### Import behavior

`4orman-tools import <path.fmz> [<4orman-root>]`

1. Extracts to `/tmp/4orman-import-<pid>/`
2. Reads `4orman.manifest.json`
3. If `kind == "workspace"`: restores framework files + ledger + recursively imports `projects/*.fmz`
4. If `kind == "project"`: copies `project/` tree to `<4orman-root>/<name>/`, carries over `knowledge/`
5. Aborts with `success: false` if destination already exists

### Export formats summary

| Format | Output | Use case |
|---|---|---|
| `fmz` | `<name>-<version>.fmz` | Machine-to-machine transfer; import on any 4ORMan install |
| `backup` | `4orman-backup.fmz` | Full workspace snapshot; emergency migration |
| `brew` | `<name>-install-brew.sh` | Teammate with Homebrew — one script to clone + install |
| `mac` | `<name>-install-mac.sh` | Teammate on fresh Mac — includes Homebrew bootstrap |
| `linux` | `<name>-install-linux.sh` | apt/dnf detection, no Homebrew |
| `windows` | `<name>-install-windows.ps1` | PowerShell + winget |

---

## What we're not sure about

- `deps` arrays are always empty in the current implementation. If a project has brew/apt deps, the user must populate the manifest manually after export and repack — no tooling for this yet.
- `knowledge_files` is reserved but unused. The intent is to list which files from `knowledge/` are "canonical" vs generated, but the distinction has not been implemented.
- Import does not run `git init` on the extracted project — the project arrives as a plain directory. The user must run `git init` + `gh repo create` if they want it tracked as a new repo.

---

## How this affects our work

- Use `4orman-tools knowledge-audit` before export — `ready: true` is the gate. Export before audit = incomplete knowledge transfer.
- The `.fmz` format is the canonical portable unit for 4ORMan projects. Use it for: archiving a completed project, moving to a new machine, sharing with a teammate.
- Workspace backup (`--format backup`) includes the ledger snapshot. Restore with `4orman-tools import 4orman-backup.fmz` to get full session state on a new machine.
- For public sharing, use `--format brew` or `--format mac` — these generate a script that only pulls from the project's GitHub repo (no 4ORMan internals included).
