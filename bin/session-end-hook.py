#!/usr/bin/env python3
"""SessionEnd hook: best-effort immediate cleanup of this session's active-
sessions entry. Not the sole cleanup path -- SessionEnd can be bypassed
entirely by SIGKILL or a terminal close (confirmed via Claude Code's own
hooks docs and issue tracker), so session-heartbeat's 15-min TTL is the
real safety net. This is just a fast path so a clean exit doesn't leave a
ghost entry lingering for up to 15 minutes.
"""

import json
import os
import subprocess
import sys


def read_stdin_session_id():
    try:
        payload = json.load(sys.stdin)
        sid = payload.get("session_id")
        return sid if isinstance(sid, str) and sid else None
    except Exception:
        return None


def workspace_root():
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def main():
    session_id = read_stdin_session_id()
    if session_id:
        try:
            subprocess.run(
                ["4orman-tools", "session-unregister", workspace_root(), session_id],
                capture_output=True,
                timeout=10,
            )
        except Exception:
            pass
    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
