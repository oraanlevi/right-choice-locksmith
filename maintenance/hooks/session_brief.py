#!/usr/bin/env python3
"""SessionStart hook: give Claude a short brief from the private task board.

Reads maintenance/private/TASKS.md (git-ignored) and the git state, and adds
a compact summary to the session context so Claude can greet the user with
"what we're working on next". Read-only; never fails the session.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
BOARD = os.path.join(ROOT, "maintenance", "private", "TASKS.md")
PRIO = {"P1": 1, "P2": 2, "P3": 3}


def rows():
    out = []
    with open(BOARD, encoding="utf-8") as f:
        for line in f:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 6 and re.fullmatch(r"[A-Z]+-\d+", cells[0]):
                out.append(dict(zip(["id", "task", "status", "prio", "missing", "deploy"], cells)))
    return out


def git(*args):
    try:
        return subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT, capture_output=True, text=True,
                              timeout=10, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout.strip()
    except Exception:
        return ""


def brief():
    if not os.path.exists(BOARD):
        return ("Maintenance task board not found (maintenance/private/TASKS.md). "
                "Tell the user and offer to recreate it from CLAUDE.md and the client log.")
    r = rows()
    by = lambda s: [t for t in r if t["status"] == s]
    active = by("in progress")
    pending = sorted(by("pending"), key=lambda t: PRIO.get(t["prio"], 9))
    nxt = active[0] if active else (pending[0] if pending else None)
    awaiting = [t for t in r if t["status"] == "completed" and t["deploy"].startswith(("local only", "committed"))]
    changed = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
    ahead = git("rev-list", "--count", "@{u}..HEAD") or "?"
    lines = [
        "WEBSITE MAINTENANCE BRIEF (from maintenance/private/TASKS.md; private, never commit it)",
        f"Board: {len(active)} in progress, {len(pending)} pending, {len(by('blocked'))} blocked, {len(by('completed'))} completed.",
        "Next task: " + (f"{nxt['id']} {nxt['task']} ({nxt['status']}, {nxt['prio']}; missing: {nxt['missing']})" if nxt else "none unblocked"),
        "Done locally, awaiting the user's review/approval: " + (", ".join(f"{t['id']} ({t['deploy']})" for t in awaiting) or "none"),
        "Blocked on the client/user: " + (", ".join(f"{t['id']}" for t in by("blocked")) or "none"),
        f"Git: {len(changed)} uncommitted file(s); {ahead} local commit(s) not pushed. Nothing is live until the user approves a push.",
        "INSTRUCTION: Before anything else, greet the user with a 2-4 line brief: what's next, what awaits their review, "
        "and the key blockers (e.g. 'Questions for the client'). Then follow the 'Task board' section of CLAUDE.md.",
    ]
    return "\n".join(lines)


def main():
    try:
        ctx = brief()
    except Exception as e:
        ctx = f"Maintenance brief unavailable ({e}). Read maintenance/private/TASKS.md manually."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
