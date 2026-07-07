# Foreman — Google Projects Ledger

Cross-project metadata only. This file never copies a project's own
ledger/decision-log contents — it tracks *that* a project has been
indexed and how healthy that index is, not *what* the project contains.
Cooperation rules and protocols for this ledger live in `_ledgers/AGENTS.md`,
not here — this file stays pure data.

Columns marked "Not yet measured" have no computed metric behind them
yet — the value is disclosed as absent rather than guessed. See
`_ledgers/AGENTS.md` for what's expected to eventually populate them.

| Project | Last indexed | Context health | Index coverage | Stale count | Highest ROI indexing task | Ready for Copilot review |
|---|---|---|---|---|---|---|
| 4orman-tools | 2026-07-02 | Not yet measured — no context-health metric implemented | 5 files / 239 symbols (via `symbol-index`, source-kind files only) | Not yet measured — no index-staleness detection implemented | Wire `symbol-find` to consult `symbol-index` instead of its own walk-and-parse (disclosed follow-up in M44) | Not yet determined — no review-readiness gate implemented |
| 4orman | 2026-07-02 | Not yet measured — no context-health metric implemented | 10 files / 17 symbols (via `symbol-index`, source-kind files only) | Not yet measured — no index-staleness detection implemented | No systematic `symbol-index`/`context-gate` pass has been run against this repo yet — establish a baseline | Not yet determined — no review-readiness gate implemented |

## How to update a row

Run `4orman-tools symbol-index <project-root>` for "Index coverage",
record today's date for "Last indexed". The other three columns have no
tool backing them yet — do not fill them with a guessed number; leave
"Not yet measured" until a real metric exists.
