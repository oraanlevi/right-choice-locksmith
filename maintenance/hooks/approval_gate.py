#!/usr/bin/env python3
"""PreToolUse hook: require the owner's approval before anything that could
commit, publish, deploy or change a remote service.

Claude Code runs this before every Bash call (see .claude/settings.json).
Reading files and local edits are never blocked; risky commands become an
explicit approval prompt ("ask") and force-pushes are refused ("deny").

Deliberately conservative: it matches anywhere in the command (so `bash -c`,
`env git push`, `/usr/bin/git push`, python subprocess calls, chained
commands are caught) and it also scans local script files the command runs.
It is a guardrail against mistakes, not a sandbox: GitHub credentials and
Claude Code's own permission prompts remain the outer safety net.
If the hook itself fails, it asks rather than allowing.
"""
import json
import os
import re
import sys

I = re.I
FORCE = [r"\bpush\b[^\n]*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S+:)", r"\bpush\b[^\n]*\s--mirror\b",
         r"\bpush\b[^\n]*\s--delete\b"]
GIT_WRITE = r"\b(push|commit|merge|rebase|reset|tag|revert|cherry-pick|checkout|switch|restore|rm|clean|stash|" \
            r"am|apply|filter-branch|filter-repo|update-ref|send-pack|subtree|remote|config|worktree|gc|prune)\b"
DEPLOY = [
    r"\b(vercel|netlify|wrangler|firebase|surge|heroku|flyctl|railway|render)\b",
    r"(?<!prepare-)\bdeploy\b",
    r"\b(gh|hub|glab)\s",
    r"\b(npm|pnpm|yarn|bun)\s+(publish|run\s+(deploy|release|publish))\b",
    r"api\.(vercel|github|netlify|cloudflare)\.com|api\.render\.com|hooks\.(vercel|netlify)|mybusiness|businessprofile",
]
NET_WRITE = r"\b(curl|wget|http|https|xh|httpie)\b[^\n]*(\s-X\s*(POST|PUT|PATCH|DELETE)\b|--request\s*=?\s*(POST|PUT|PATCH|DELETE)\b|" \
            r"\s-d\b|\s--data|\s-F\b|\s--form|\s--json\b|\s-T\b|\s--upload-file|--post-data|--post-file|--method)"
REMOTE = r"\b(ssh|scp|sftp|rsync|ftp|lftp)\b"
OBFUSCATION = [r"\beval\b", r"base64\s+(-d|-D|--decode)", r"\b(ba|z|da|k)?sh\s+-c\b", r"\bxargs\b[^\n]*\bgit\b",
               r"\b(python3?|node|ruby|perl|osascript)\s+-(c|e)\b[^\n]*\b(git|subprocess|system|exec|http|request|fetch|urllib)\b"]
SCRIPT_RUN = r"(?:^|[\s;&|(])(?:(?:ba|z|da|k)?sh|source|\.|python3?|node|ruby|perl)\s+([^\s;&|]+)|(?:^|[\s;&|(])(\./[^\s;&|]+)"

PROJECT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TRUSTED = {os.path.join("maintenance", "scripts", n) for n in ("check_site.py", "process_photos.py")}


def decide(cmd, depth=0):
    """Return (decision, reason) or None."""
    has_git = re.search(r"\bgit\b", cmd, I)
    if has_git and re.search(r"\badd\b", cmd, I) and re.search(r"(\s-f\b|--force|maintenance/private|client-uploads|backlog\.md|check-baseline)", cmd, I):
        return "deny", "Private client notes, uploads and ignored files must never be added to git (public repo)."
    for p in FORCE:
        if has_git and re.search(p, cmd, I):
            return "deny", "Force-push / mirror / remote delete is never allowed on this site."
    if has_git and re.search(r"\bpush\b", cmd, I):
        return "ask", "PUSH = PUBLISH: pushing to GitHub triggers a live deploy. Approve only if the owner approved this push."
    if has_git and re.search(GIT_WRITE, cmd, I):
        return "ask", "This git command changes history, config, remotes or discards work. Owner approval required."
    for p in DEPLOY:
        if re.search(p, cmd, I):
            return "ask", "Hosting/deploy tool or hosting API: can change the live site or accounts. Owner approval required."
    if re.search(NET_WRITE, cmd, I):
        return "ask", "Outgoing write request to a web service. Owner approval required."
    if re.search(REMOTE, cmd, I):
        return "ask", "Remote copy/shell command: could change a server. Owner approval required."
    for p in OBFUSCATION:
        if re.search(p, cmd, I):
            return "ask", "Indirect command (eval/sh -c/inline code) that the gate cannot fully inspect. Owner approval required."
    if re.search(r"\brm\s+-\w*[rR]", cmd):
        return "ask", "Recursive delete. Owner approval required."
    if depth == 0:  # look inside local scripts the command executes
        for m in re.finditer(SCRIPT_RUN, cmd):
            path = (m.group(1) or m.group(2) or "").strip("'\"")
            if not path or path.startswith("-"):
                continue
            full = path if os.path.isabs(path) else os.path.join(PROJECT, path)
            rel = os.path.relpath(full, PROJECT)
            if not os.path.isfile(full):
                continue
            try:
                with open(full, errors="ignore") as f:
                    body = f.read(200_000)
            except OSError:
                continue
            if rel in TRUSTED and not re.search(r"\bpush\b|\bdeploy\b|requests\.|urlopen|http\.client", body):
                continue
            # scan script body line by line plus as a whole (catches ['git', 'push'])
            flat = re.sub(r"['\",\[\]]", " ", body)
            for chunk in [flat] + flat.splitlines():
                hit = decide(chunk, depth=1)
                if hit:
                    return "ask", f"Script {rel} contains a risky command ({hit[1]})"
    return None


def main():
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        cmd = (data.get("tool_input") or {}).get("command", "") or ""
        hit = decide(cmd)
    except Exception as e:  # fail closed
        hit = ("ask", f"Approval gate error ({e}); asking to be safe.")
    if hit:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": hit[0],
                                                 "permissionDecisionReason": hit[1]}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
