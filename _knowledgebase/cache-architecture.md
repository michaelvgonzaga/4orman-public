# Cache Architecture

All caching layers in 4ORMan + 4orman-tools, with status and gaps.

---

## Knowledge State Taxonomy (v0.60.0+)

Three tiers with distinct invalidation rules:

| Tier | Location | Invalidation | Never |
|---|---|---|---|
| **Permanent Truth** | `~/.4orman/` (ledger, session-snapshot, profile, state/) | Never — append-only or hardware-only | Touched by any hook |
| **Pinned Knowledge** | `~/.cache/4orman-tools/` sub-keys: guardrails, state, milestones, outline | Source file hash mismatch → invalidate, regenerate, re-store | Deleted preemptively |
| **Disposable Cache** | `~/.cache/4orman-tools/` all other entries | Auto-invalidated by hash on access; Stop hook purges >30 days | Cleared on session start |

**Rule:** Essential knowledge is not deleted; it is invalidated, regenerated, and verified.

The five-layer map below (L1–L5) describes the *storage mechanism*. The taxonomy above describes the *architectural role*. Pinned Knowledge lives in L5 (disk cache) but is promoted above ordinary cache — it self-heals rather than being cleared.

---

## Layer Map

```
L1  Anthropic prompt cache       — in Claude's infrastructure, 5-min TTL
L2  Zig binary internals         — comptime maps, shared helpers, per-invocation
L3  Git subprocess calls         — spawned via runGit(), no cross-call dedup
L4  Claude reading behavior      — what gets read per session, cache-fetch pattern
L5  Disk cache                   — ~/.cache/4orman-tools/, persistent
```

---

## L1 — Anthropic Prompt Cache

**What it is:** Claude's infrastructure caches the full conversation context with a 5-minute TTL. Within an active session (user responding in under 5 minutes), the context is warm and cheap. Across restarts or idle gaps >5 min: always cold.

**What we control:** Nothing — this is infrastructure. The only lever is keeping CLAUDE.md lean so the cold-start cost is low.

**Status:** ✅ No action needed. CLAUDE.md token-discipline guardrail is the only mitigation.

---

## L2 — Zig Binary Internals

### L2a — Comptime maps (optimal)

```zig
const FRAMEWORK_MAP: std.StaticStringMap([]const u8) = ...
const CONFIG_FILE_MAP: std.StaticStringMap(void) = ...
const SKIP_DIR_SET: std.StaticStringMap(void) = ...
const BINARY_EXT_SET: std.StaticStringMap(void) = ...
```

All four are `comptime` — zero runtime cost, O(1) lookup. Used in every filesystem walk. **No gaps.**

### L2b — Shared helpers (good)

| Helper | Used by |
|--------|---------|
| `sha256Hex` | `computeFileHash`, `computeCacheCheck`, `computeCacheStore`, `computeCacheFetch`, `computeTarballSha` |
| `writeCacheEntry` | `computeCacheCheck`, `computeCacheStore` |
| `cacheEntryPath` | `computeCacheStore`, `computeCacheFetch` |
| `runGit` | All git-touching compute functions |
| `computeScan` | `computeContextScan` (calls internally, no duplication) |

**No gaps.**

### L2c — Within-invocation state (stateless by design)

Each subcommand is a separate process. There is no in-process cache between calls. This is intentional — it keeps the binary simple and avoids state corruption. The downside: if Claude calls `cache-fetch` and gets a miss, then reads the file, then calls `cache-store`, the file is read from disk twice in two separate invocations.

**Status:** ⚠️ Accepted limitation of the stateless model. The disk cache (L5) compensates for the next session; within one session, two disk reads is acceptable.

### L2d — Atomic writes (GAP)

`writeCacheEntry` uses `createFileAbsolute` — a direct overwrite. On power loss mid-write, the cache file is partially written. `cache-fetch` will return `hit: false` because the stored SHA won't match (safe miss), but the corrupted file remains until the next successful write overwrites it.

**Fix:** `atomicRenameAbsolute` helper writes to `<entry_path>.tmp`, flushes, closes, then calls `std.c.rename(tmp, final)`. Applied to both `writeCacheEntry` (cache-check path) and `computeCacheStore` inline write. `std.c.rename` is the correct Zig 0.16 path — `std.posix.rename` does not exist.

**Status:** ✅ Implemented in v0.30.0.

---

## L3 — Git Subprocess Calls

`runGit()` spawns a child process for every git operation. 20 call sites across 8 compute functions.

### Per-invocation git call counts

| Subcommand | git calls | Notes |
|------------|-----------|-------|
| `status` | 2–3 | rev-parse HEAD, rev-parse origin/main, rev-list --count (if behind) |
| `release-info` | 4 | rev-parse HEAD, describe --tags, rev-list --count, status --porcelain |
| `changes-preview` | 2+ | log HEAD..origin/main, diff --name-only HEAD..origin/main |
| `git-diff` | 2 | --numstat, --name-status |
| `context-changed` | 3–11 | numstat + name-status + 1 diff per file (capped at 8 files) |
| `commits` | 1 | log since tag |
| `tag-exists` | 1 | tag -l |
| `repo-info` | 1 | remote get-url |

### Session-start cost (typical)

```
doctor          → 1 subprocess (claude --version)
git fetch       → 1 git (shell, in self-update skill)
status          → 2–3 git calls
changes-preview → 2 git calls
Total: 6–7 subprocess spawns just to start a session
```

### Cross-session git cache (GAP)

No caching of git results between sessions. `status` re-runs 2–3 git calls every session open even if HEAD hasn't changed since yesterday.

**Fix:** `git-cache` subcommand (W2-B in ROADMAP) — cache git status/log keyed to HEAD SHA. `changed: false` when HEAD matches stored HEAD → skip all git calls.

**Status:** ❌ Not implemented. Target: Wave 2.

### `context-changed` call reduction (minor gap)

`context-changed` runs numstat and name-status as two separate git calls then correlates them. These could be combined by running `diff --stat --name-status` but the output formats are harder to parse together. The current 2-call approach trades one git spawn for simpler parsing. Acceptable tradeoff.

**Status:** ⚠️ Accepted. Not worth the parsing complexity.

---

## L4 — Claude Reading Behavior

### What gets read every session (cold start)

| File | Size | How often | Can be cached? |
|------|------|-----------|---------------|
| CLAUDE.md | 14KB | Every session (system prompt) | No — loaded by Claude Code automatically |
| ROADMAP.md | ~5KB | Every session (guardrail) | Yes — cache-fetch "state" |
| spec.md (per project) | ~15KB | Per project session | Yes — cache-fetch "milestones" |
| project CLAUDE.md | ~2KB | Per project session | Yes — cache-fetch "guardrails" |
| source files (root.zig etc.) | 147KB+ | When implementing | Yes — cache-fetch "outline" |

### Pattern (now documented in CLAUDE.md guardrail)

```
1. cache-fetch <abs-path> <sub-key>
   → hit: true  → use value, skip read entirely
   → hit: false → read file + extract key facts as JSON → cache-store
```

Standard sub-keys:
- `spec.md` → `"milestones"`
- `CLAUDE.md` → `"guardrails"`
- `ROADMAP.md` → `"state"`
- source files → `"outline"`
- manifest files → `"deps"`

### Skills with no cache wiring (GAP)

No skill or command currently calls `cache-fetch` before reading. The guardrail exists but relies on Claude acting on it consistently. Skills need explicit cache calls to be reliable.

**Fix 1:** Wire `cache-fetch/store` into `_skills/self-update.md` — it reads git data every session; cache keyed to HEAD SHA.  
**Fix 2:** `warm-up` subcommand (see L5 gap below) — single call pre-warms all key files.

**Status:** ❌ Skills not wired. Guardrail exists. Target: Wave 2.

---

## L5 — Disk Cache

**Location:** `~/.cache/4orman-tools/`  
**Persistence:** On-disk. Survives restarts, power loss (safe miss on partial write), internet outages.  
**Invalidation:** Content-addressed (SHA256 of file content). File changes → automatic miss on next fetch.  
**Current entries:** 4 (as of 2026-06-30). Barely used.

### Entry format

`cache-check`: `~/.cache/4orman-tools/<SHA256(file_path)>` → `<SHA256(file_content)>`  
`cache-store/fetch`: `~/.cache/4orman-tools/<SHA256(file_path + ":" + sub_key)>` → `<SHA256(file_content)>\n<value_json>`

### Session warm-up (GAP — highest ROI)

No subcommand warms the cache for a project at session start. Claude must call `cache-fetch` on each file individually, which it often skips.

**Fix:** `4orman-tools warm-up <project-root>` subcommand — in one call:
1. `cache-fetch` on key files (spec.md, CLAUDE.md, ROADMAP.md, entry point)
2. For each miss: read file, extract standard values (milestones, guardrails, state, outline), `cache-store`
3. Return: `{ warmed: N, hits: N, misses: N, files: [{path, sub_key, hit}] }`

Claude calls this once at session start instead of N separate cache-fetch calls. This is the highest-ROI addition in Wave 2.

**Status:** ❌ Not implemented. Target: 4orman-tools v0.30.0 (first Wave 2 item).

### Scan result caching (GAP)

`scan` and `context-scan` re-run a full filesystem walk every session. If the project files haven't changed, this is wasted work.

**Fix:** After running `scan <path>`, call `cache-store <path>/build.zig "scan"` (or whichever manifest is the key file). On next session, `cache-fetch` → if hit and manifest unchanged → skip the walk.

**Limitation:** Directory-level change detection requires hashing all files, which is slower than the scan itself. Better approach: cache keyed to the manifest file (Cargo.toml, package.json, etc.) — a manifest change is the signal that the project structure may have changed.

**Status:** ❌ Not implemented. Target: Wave 2 after warm-up.

---

## Full Status Summary

| Layer | Component | Status | Target |
|-------|-----------|--------|--------|
| L1 | Anthropic prompt cache | ✅ N/A | — |
| L2a | Comptime maps | ✅ Optimal | — |
| L2b | Shared Zig helpers | ✅ Good | — |
| L2c | Within-invocation state | ⚠️ Stateless (accepted) | — |
| L2d | Atomic writes | ✅ Fixed v0.30.0 | — |
| L3a | Per-invocation git calls | ⚠️ Minimized per fn | — |
| L3b | Cross-session git cache | ❌ Missing | Wave 2 (W2-B) |
| L3c | context-changed call count | ⚠️ Accepted tradeoff | — |
| L4a | Claude cache-fetch pattern | ⚠️ Guardrail only | Wave 2 |
| L4b | Skills wired to cache | ❌ None wired | Wave 2 |
| L5a | Disk cache persistence | ✅ Solid | — |
| L5b | Atomic writes | ✅ Fixed v0.30.0 | — |
| L5c | Session warm-up | ❌ Missing | v0.30.0 (first W2) |
| L5d | Scan result caching | ❌ Missing | Wave 2 |

---

---

## Hardware Utilization (M3 Pro, 36GB RAM)

**Bottleneck is I/O, not CPU.** The binary is subprocess-bound (git calls ~20ms each) and disk-bound (file reads). The M3's CPU cores are idle during most operations.

| What | Status | Action |
|------|--------|--------|
| Build optimization | `ReleaseSafe` ✅ | Correct — reads untrusted data, keep safety checks |
| CPU target | Generic arm64 → changed to `apple_m3` | `-Dcpu=apple_m3` in build command — enables M3 SIMD for string ops |
| `ReleaseFast` | ❌ Do not use | Removes bounds checks; 4orman-tools reads untrusted filesystem/git data |
| Parallel file reads | ❌ Not yet | `context-rank` reads files sequentially; parallelism requires Zig threading (Wave 4) |
| Memory allocator | `GeneralPurposeAllocator` ✅ | Correct for this use case; binary exits after each command |
| Universal binary | arm64 + x86_64 ✅ | M3 runs arm64 natively; no Rosetta overhead |

**Real-world session time breakdown:**
- API latency: 300–2000ms → not controllable
- Git subprocesses: ~20ms each → reducible with git-cache
- Binary startup: ~5ms → already fast
- Disk I/O: <1ms per file → already fast
- CPU compute: <1ms → not the bottleneck

---

## Implementation Order (by ROI)

1. **`warm-up` subcommand** (v0.30.0) — single call, pre-warms all key files. Highest ROI.
2. **Atomic writes** (v0.30.0) — 5-line change in `writeCacheEntry`. Eliminates corrupted entries.
3. **Wire self-update skill to cache** — cache git status keyed to HEAD. Saves 3–5 git calls per session.
4. **`git-cache` subcommand** (W2-B) — full cross-session git result cache.
5. **Scan result caching** — cache `context-scan` keyed to manifest file.
