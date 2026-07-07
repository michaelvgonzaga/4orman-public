#!/usr/bin/env python3
"""PostToolUse hook: appends every real Bash command to
~/.4orman/task-log.jsonl -- a plain observation log for whatever tooling
you build to analyze recurring routine work later. Append-only, no
analysis here.
"""

import json
import os
import sys
import time


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        print("{}")
        return

    if event.get("tool_name") != "Bash":
        print("{}")
        return

    command = (event.get("tool_input") or {}).get("command", "")
    if not command:
        print("{}")
        return

    # cwd matters -- most commands are only meaningful replayed from the
    # same directory they actually ran in.
    cwd = event.get("cwd", "")
    entry = {"tool": "Bash", "command": command, "cwd": cwd, "timestamp": int(time.time())}
    log_path = os.path.expanduser("~/.4orman/task-log.jsonl")
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
