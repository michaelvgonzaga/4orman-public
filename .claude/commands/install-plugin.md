Install a plugin from a zip file exported by `/export-plugin`.

## Input

The user provides a path to a `.zip` file. The path can be absolute or relative to the 4ORMan root.

## Steps

**1. Validate the zip**

- Verify the file exists and has a `.zip` extension
- Run `unzip -l <path>` to inspect its contents
- Identify the top-level directory name inside the zip — this becomes the plugin name
- If there is no consistent top-level directory (files are loose at the root of the zip), stop and tell the user: "This zip doesn't look like a 4ORMan plugin export. Expected a single top-level directory."

**2. Check for conflicts**

If the directory already exists, warn and ask to overwrite before proceeding.

**3. Install**

Run from the 4ORMan root:

```bash
unzip -o <path> -d .
```

**4. Confirm**

Print the installed path, source zip name, and "If it has a CLAUDE.md, read it before use."

**5. Clean up (optional)**

Ask: "Delete the zip? (yes/no)" — if yes, give the path for the user to remove.
