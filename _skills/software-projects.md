# Software Projects

**Works well for:** Implementation guidance specific to software projects — the framework handles any domain, but software has patterns worth capturing separately
**Confidence:** Medium — general best practices, will sharpen with real project results

## The pattern

### Read the project before writing anything

If there is an existing codebase at a known path, scan it first:

```bash
4orman-tools scan <path>
```

Use `entryPoint` to find the main file, `files` (sorted largest-first) to decide read order — largest source files are usually the most important. Use `framework` to confirm the tech stack before asking the user. Skip `find` / `ls` chains when the scan result covers it.

### Stack decisions to make before writing code
- **Runtime**: what runs this? (Python, Node, browser, mobile, etc.)
- **Data layer**: where does data live and how persistent does it need to be? Start with the simplest option (SQLite, local file, Supabase) — don't reach for Postgres until you need it
- **UI**: does this need a UI? If so, who uses it and where? (CLI, web, mobile, embedded)
- **Auth**: does it need user accounts? Don't build auth until you must

### How to execute (fill in project CLAUDE.md)
```bash
# setup
[package manager install command]

# run / work
[local dev server or run command]

# validate / test
[test runner command]
```

### Testing approach by project type
- **CLI tool**: test with real inputs, check outputs match expectations
- **Web app**: test happy path manually in browser before shipping; add automated tests for anything that handles money or sensitive data
- **API**: test endpoints with real payloads; document expected request/response shapes
- **Background job**: test with sample data; verify idempotency (can it run twice safely?)

### Common risks for software projects
- "We'll add auth later" — auth is structural, not additive; decide upfront
- Picking a complex stack for a simple problem — start minimal
- No local dev environment documented — the next session can't pick up without it
- Skipping error handling on external API calls — they will fail in production

## When to use it

- The project is a software application, API, CLI, or automation
- Choosing a tech stack for the first time on a project
- Filling in the "How to execute" section of project CLAUDE.md

## When NOT to use it

- The deliverable itself is not software — e.g., a process document, training curriculum, business plan, or physical product. Building software *for* a non-software domain still needs this skill — use alongside `domain-research.md`.
- The user has already decided the stack and just needs implementation