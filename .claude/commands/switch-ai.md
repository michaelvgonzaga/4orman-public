Detect which AI CLIs are installed and how to switch to one or add another account. Manual only — no automatic detection of usage/rate limits exists (Claude Code hooks never see API quota events, only session lifecycle), so this never fires on its own.

Never touches credentials — presence-check only, same boundary `doctor` already holds for claude/git/gh.

1. Check for each of: `claude`, `codex`, `gemini`, `cursor-agent`, `opencode` via `command -v <tool>` (do not guess others without checking).
2. For each one found, run `<tool> --help 2>&1 | head -30` (or `-h`) to find its actual login/auth/account subcommand — don't hardcode a remembered flag, tools change; read what's actually there right now.
3. Report a short table: tool, installed y/n, and (if installed) the exact command to add/switch an account, taken from that tool's own `--help` output.
4. If the user names a specific tool to switch to, give the exact command to launch it — do not launch it yourself.
