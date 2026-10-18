---
name: prepare-deploy
description: Review all local changes, run checks, and prepare a release. Commits only after the owner approves and pushes (which publishes the live site) only after a second, separate approval. Includes rollback steps. Use when the owner says approve, publish, deploy, go live, or "ship it".
disable-model-invocation: true
---

# Prepare and review a deployment

Pushing `main` to GitHub publishes the live site through Vercel. Treat a push as a live change.

## Gate 0: review (no approval needed, changes nothing)
1. `git status --short` and `git diff --stat`. List every changed file. Make sure nothing unexpected is included:
   - No files from `client-uploads/`, no `.env` or keys, no raw/HEIC photos, no `.DS_Store`, no huge images (> budget).
   - Maintenance tooling (`CLAUDE.md`, `.claude/`, `maintenance/`) is OK to commit if the owner wants. `.vercelignore` keeps it off the live site.
2. Run `python3 maintenance/scripts/check_site.py --quiet`. **Stop if there are any new errors.**
3. Blog dates: any new post's `datePublished` must equal today's date (the go-live day). If not, propose updating it first.
4. Map the changes to task IDs on `maintenance/private/TASKS.md` (one task per commit is preferred; if several tasks are mixed, list them). Never stage anything under `maintenance/private/`, `client-uploads/` or `maintenance/backlog.md`.
5. Re-read the full diff (`git diff`) and write the **release summary**: what changes on the live site, per page, in plain English, with the exact before → after text for wording, prices, hours and links.
6. Ask: **"Approve commit?"** Then stop.

## Gate 1: commit (only after the owner says yes to the commit)
- Stage only the files listed in the summary, by name (no `git add -A`).
- Write one clear commit message: a short subject in the existing style (e.g. "Add Garland service-area page and wire into navigation"), then a body listing the changes.
- `git commit`. The approval hook will prompt; that's expected. Show `git log -1 --stat`.
- Update the board: those tasks' deploy state becomes `committed (not pushed)` (note the commit hash), plus a change-history row.
- Ask: **"Push to GitHub? This publishes to the live site within about a minute."** Then stop.

## Gate 2: push / publish (only after a second, explicit yes)
- `git push origin main` (never `--force`).
- After about 60–90 seconds, verify read-only: `curl -sI <live domain from CLAUDE.md>/<changed-page>` returns 200, and the live file matches the local one (`curl -s <url> | shasum` vs `shasum <file>`). Check that `/CLAUDE.md` returns 404 (tooling must not be public).
- Update the board: deploy state `deployed YYYY-MM-DD` for the included tasks, plus a change-history row.
- Report the result. Suggest `python3 maintenance/scripts/check_site.py --save-baseline` only if the owner wants to accept the remaining known issues.

## Rollback (explain; do only with approval)
- **Fastest:** in the Vercel dashboard → Deployments → previous deployment → "Instant Rollback". The owner does this (Claude can't sign in).
- **In git:** `git revert <commit>` creates a new commit that undoes the change. It then goes through Gate 1 and Gate 2 again. Never use `reset --hard` or force-push.
