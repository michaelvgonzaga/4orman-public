Package a plugin directory as a zip file that anyone can install into their 4ORMan instance via `/install-plugin`.

## Steps

**1. Identify the plugin**

The user will provide a plugin name (directory name). If not provided, list all available plugin directories in the 4ORMan root (root-level dirs that don't start with `_` or `.`) and ask which to export.

**2. Verify the directory exists**

If `<name>/` does not exist in the 4ORMan root, stop and tell the user.

**3. Create the zip**

Run from the 4ORMan root:

```bash
zip -r <name>-plugin.zip <name>/ \
  -x "*/.git/*" \
  -x "*/.git" \
  -x "*.env" \
  -x "*/.env*" \
  -x "*/__pycache__/*" \
  -x "*/*.pyc" \
  -x "*/.DS_Store" \
  -x "*/node_modules/*"
```

Save the zip to the 4ORMan root directory.

**4. Confirm and instruct**

Print the zip filename, size, and: "Send to anyone with 4ORMan. To install: drop it anywhere and run `/install-plugin <path>`."
