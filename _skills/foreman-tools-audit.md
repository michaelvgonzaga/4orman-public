# 4orman-tools Audit

**Works well for:** Catching shell patterns worth promoting to a native subcommand before they get copied across more files
**Confidence:** High

## When to run

- After `/new-project`
- After adding or editing any command or skill file
- When you notice the same shell command appearing in multiple places

## The check (under 1 minute)

Scan the new or changed file(s) for shell commands that read data:
- Git refs, log, diff, or status
- File existence or filesystem metadata
- GitHub data via `gh`

For each pattern found, answer three questions:

1. **Already in 4orman-tools?** (`4orman-tools status`, `4orman-tools commits`) → use it, done.
2. **Appears in 2+ commands or skills?** → candidate for a new subcommand.
3. **Appears only here?** → skip. One-off shell commands stay as shell commands.

## Proposing a new subcommand

If a pattern passes the repetition test, surface it to the user:

```
4orman-tools candidate: `4orman-tools <name> <args>`

What it replaces: <describe the current shell pattern>
Appears in: <list the commands/skills that use it>
Output schema: { "<field>": <type>, ... }
Estimated savings: ~<N> tokens per session

Add to 4orman-tools/spec.md? (yes / skip)
```

If yes → add to `4orman-tools/spec.md` under the next milestone. Do not implement without a spec entry and user sign-off.

## What NOT to propose

- One-off project-specific queries (e.g. "get issues for this specific repo")
- Commands that run once during setup and never repeat
- Anything that requires interactive input or auth tokens — 4orman-tools is read-only and auth-free
- Shell commands that are already trivially fast (single `cat`, `ls`)
