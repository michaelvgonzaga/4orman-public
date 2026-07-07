#!/usr/bin/env python3
"""SessionStart hook: gathers the checks CLAUDE.md's "Always do" list
otherwise requires Claude to run manually every session, into one JSON
blob injected as context. Zero Claude tokens spent gathering this.

Decisions (pause on drift, run /first-run, ask about outcome review) stay
Claude's job — this script only gathers deterministic facts, never judges.
"""

import json
import os
import subprocess
import sys


def read_stdin_session_id():
    """Every hook event's stdin JSON includes session_id -- confirmed via
    Claude Code's own hooks docs, stable across SessionStart/SessionEnd for
    the same session. Fails soft to None (session coordination just gets
    silently skipped, same as any other optional check here) rather than
    ever blocking the rest of the hook on a stdin-parsing problem.
    """
    try:
        payload = json.load(sys.stdin)
        sid = payload.get("session_id")
        return sid if isinstance(sid, str) and sid else None
    except Exception:
        return None


def run_tool(*args):
    try:
        r = subprocess.run(
            ["4orman-tools", *args], capture_output=True, text=True, timeout=10
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


def main():
    lines = []
    session_id = read_stdin_session_id()
    data = {"foremanMode": os.environ.get("FOREMAN_MODE", "autopilot"), "sessionId": session_id}

    root = workspace_root()

    # Confirmed live (2026-07-06): two independent sessions built the same
    # hook and the same subcommand on the same day with zero coordination.
    # session-heartbeat registers this session's presence and returns every
    # other non-stale session already active in this repo.
    other_sessions = None
    if session_id:
        heartbeat = run_tool("session-heartbeat", root, session_id)
        if heartbeat:
            other_sessions = heartbeat.get("otherActiveSessions", [])
    data["otherActiveSessions"] = other_sessions
    if other_sessions:
        ids = ", ".join(o["sessionId"] for o in other_sessions)
        lines.append(
            f"{len(other_sessions)} other session(s) already active in this repo ({ids}) — "
            "confirm scope with the user before starting Standard/Full-build work to avoid duplicating it"
        )

    first_run_path = os.path.join(root, ".first-run")
    data["firstRunPending"] = os.path.exists(first_run_path)
    if data["firstRunPending"]:
        lines.append("`.first-run` marker present — run /first-run before anything else")

    compat = run_tool("compat-check")
    data["compatCheck"] = compat
    if compat and not compat.get("ok", True):
        lines.append(f"compat-check: {compat.get('advice', 'drift detected')}")

    doctor = run_tool("doctor")
    data["doctor"] = doctor
    missing = [k for k in ("claude", "git", "gh") if doctor and not doctor.get(k)]
    if missing:
        lines.append(f"doctor: missing {', '.join(missing)}")

    try:
        probe = subprocess.run(
            ["4orman-tools", "cache-fetch", "/dev/null", "x"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except Exception:
        probe = ""
    binary_stale = "unknown subcommand" in probe
    data["binaryStale"] = binary_stale
    if binary_stale:
        lines.append(
            "Homebrew binary is stale (missing cache/context subcommands) — run /brew-release"
        )

    if not binary_stale:
        profile_path = os.path.expanduser("~/.4orman/profile.json")
        data["profileCache"] = run_tool("cache-fetch", profile_path, "device")
    else:
        data["profileCache"] = None

    try:
        subprocess.run(
            ["git", "-C", root, "fetch", "origin", "main", "--quiet"],
            capture_output=True,
            timeout=15,
        )
    except Exception:
        pass
    repo_status = run_tool("status", root)
    data["repoStatus"] = repo_status
    # Not just a boolean — when behind, bundle the actual incoming commits +
    # file count so the surfaced line is something to act on, not just a flag
    # to re-derive with a second call.
    incoming_changes = None
    if repo_status and repo_status.get("upToDate") is False:
        incoming_changes = run_tool("changes-preview", root)
        behind = repo_status.get("behindBy", "?")
        commit_summary = (
            "; ".join(c.get("message", "") for c in incoming_changes.get("commits", [])[:5])
            if incoming_changes
            else ""
        )
        lines.append(
            f"workspace is behind origin by {behind} commit(s) — {commit_summary}"
            if commit_summary
            else f"workspace is behind origin by {behind} commit(s)"
        )
    data["incomingChanges"] = incoming_changes

    stale_ledger = run_tool("ledger", "check-stale")
    data["ledgerStale"] = stale_ledger
    if stale_ledger and stale_ledger.get("stale_count", 0) > 0:
        lines.append(
            f"{stale_ledger['stale_count']} stale ledger entry(ies) — re-validate before trusting"
        )

    ledger_all = run_tool("ledger", "show")
    review_due = []
    if ledger_all:
        review_due = [
            e for e in ledger_all.get("entries", []) if e.get("outcomeReviewDue")
        ]
    data["outcomeReviewDueCount"] = len(review_due)
    if review_due:
        lines.append(
            f"{len(review_due)} ledger entry(ies) have outcomeReviewDue — ask user whether to record what happened"
        )

    deep_scan_pending_path = os.path.expanduser("~/.4orman/deep-scan-pending.json")
    deep_scan_pending = None
    if os.path.exists(deep_scan_pending_path):
        try:
            with open(deep_scan_pending_path) as f:
                deep_scan_pending = json.load(f)
        except Exception:
            deep_scan_pending = None
    data["deepScanPending"] = deep_scan_pending
    if deep_scan_pending and deep_scan_pending.get("projects"):
        total = sum(len(v) for v in deep_scan_pending["projects"].values())
        projects_str = "/".join(deep_scan_pending["projects"].keys())
        lines.append(
            f"{total} deep-scan candidate(s) pending review across {projects_str}"
        )

    summary = "; ".join(lines) if lines else "all checks clean"
    result = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "Ground truth from SessionStart hook (zero Claude tokens spent "
                "gathering this):\n" + json.dumps(data, indent=2)
            ),
        }
    }

    quiet_path = os.path.expanduser("~/.4orman/4orman-quiet")
    quiet = os.path.exists(quiet_path) and open(quiet_path).read().strip() == "1"
    if not quiet:
        result["systemMessage"] = "SessionStart: " + summary

    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
