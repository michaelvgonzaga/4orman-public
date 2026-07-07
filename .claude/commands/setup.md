# 4ORMan Setup

Install plugins listed in `plugins.public.yml` and `plugins.local.yml`.

## Steps

**1. Read the plugin manifests**

Read `plugins.public.yml` from the 4ORMan root. If `plugins.local.yml` exists, read it too. Merge both plugin lists. If neither has any entries, tell the user there is nothing to install and stop.

**2. Check for plugins.local.yml**

If `plugins.local.yml` does not exist, after processing public plugins, print:

```
No plugins.local.yml found. To install your private repos:
  1. Copy plugins.local.yml.example to plugins.local.yml
  2. Add your repos following the example format
  3. Run /setup again
```

**3. For each plugin in the merged list**

- Check if the directory `<name>/` already exists in the 4ORMan root
  - If yes: mark as "already installed — skipped"
  - If no: run `git clone <repo> <name>/`
    - If clone succeeds: mark as "installed"
    - If clone fails (any error — auth, not found, network): mark as "skipped (no access or not found)" and continue. Do not stop the whole process for one failure.

**4. Print a summary table**

```
Plugin              Status
──────────────────  ──────────────────────────────
my-project          installed
other-project       already installed — skipped
private-thing       skipped (no access or not found)
```

**5. If any plugins were skipped due to access**

Print:
```
Private plugins are cloned using your existing git credentials (SSH key or HTTPS).
If a repo was skipped, verify your credentials can reach it: git clone <repo>
```

Do not suggest installing gh CLI or configuring tokens — git credentials are sufficient.

**6. Point to the next steps (especially on a new machine)**

After the plugin summary, print:

```
Next steps:
  /setup-automation    — install the auto-sync/auto-push hooks (memory + project repos). Run once per machine; the hooks are machine-local and don't travel with 4ORMan.
  /restore-projects    — pull your existing 4ORMan projects from GitHub into this workspace.
  /sync-memory restore — pull your saved Claude memory onto this machine.
```

