#!/usr/bin/env python3
"""Stop hook: cache purge, unreleased-subcommand reminder, and a once-per-
session deep-scan across all three orman projects, filing candidates into
~/.4orman/deep-scan-pending.json for the next SessionStart to surface.
Runs at session end, not per-task, to bound cost.
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


def run_tool(*args):
    try:
        r = subprocess.run(
            ["4orman-tools", *args], capture_output=True, text=True, timeout=30
        )
        return json.loads(r.stdout)
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


def session_heartbeat_line(session_id):
    """Refreshes this session's presence entry every turn -- Stop firing
    reliably per-turn is what makes the 15-min TTL meaningful instead of
    expiring a still-active, merely-quiet session. Repeats the warning every
    turn the collision persists rather than only once -- a persistent
    coordination problem should stay visible, not fall silent after the
    first mention."""
    if not session_id:
        return None
    heartbeat = run_tool("session-heartbeat", workspace_root(), session_id)
    if not heartbeat:
        return None
    others = heartbeat.get("otherActiveSessions", [])
    if not others:
        return None
    ids = ", ".join(o["sessionId"] for o in others)
    return f"{len(others)} other session(s) active in this repo ({ids}) — confirm scope before continuing Standard/Full-build work"


def purge_old_cache():
    try:
        subprocess.run(
            ["find", os.path.expanduser("~/.cache/4orman-tools"), "-mtime", "+30", "-delete"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def promotion_queue_line():
    pq = run_tool("promotion-queue", "list")
    if not pq or pq.get("count", 0) <= 0:
        return None
    names = ", ".join(e["name"] for e in pq.get("entries", []))
    return f"{pq['count']} Zig subcommand(s) built locally, not yet released: {names}. Run /release to ship."


def run_deep_scan():
    projects = {
        "4orman": os.path.expanduser("~/4orman"),
    }
    results = {}
    for name, path in projects.items():
        if not os.path.isdir(path):
            continue
        scan = run_tool("deep-scan", path)
        if scan and scan.get("candidates"):
            results[name] = scan["candidates"]

    pending_path = os.path.expanduser("~/.4orman/deep-scan-pending.json")
    if results:
        os.makedirs(os.path.dirname(pending_path), exist_ok=True)
        with open(pending_path, "w") as f:
            json.dump({"projects": results}, f, indent=2)
    elif os.path.exists(pending_path):
        # Nothing pending this time -- clear a stale prior pending file so
        # the next SessionStart doesn't re-surface already-reviewed items.
        os.remove(pending_path)
    return results


def main():
    purge_old_cache()
    lines = []

    session_id = read_stdin_session_id()
    hb_line = session_heartbeat_line(session_id)
    if hb_line:
        lines.append(hb_line)

    pq_line = promotion_queue_line()
    if pq_line:
        lines.append(pq_line)

    deep_scan_results = run_deep_scan()
    total_candidates = sum(len(v) for v in deep_scan_results.values())
    if total_candidates > 0:
        projects_str = "/".join(deep_scan_results.keys())
        lines.append(f"{total_candidates} deep-scan candidate(s) pending review across {projects_str}")

    if lines:
        print(json.dumps({"systemMessage": "; ".join(lines)}))
    else:
        print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
