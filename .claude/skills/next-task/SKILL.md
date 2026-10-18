---
name: next-task
description: Pick the next unblocked task from the private maintenance task board, implement it locally, run checks, preview, and report. Use when the user says "work on the next task", "what's next, do it", or names a task ID to work on.
---

# Work on the next task

The board is `maintenance/private/TASKS.md` (private, git-ignored; never `git add` it). Follow `CLAUDE.md` for every change.

## 1. Choose the task
- If the user named a task ID, use it (if it's `blocked`, say what's missing and stop).
- Otherwise use the first `in progress` task. If there is none, use the first `pending` task in board order with the highest priority (P1 before P2 before P3).
- Read its **Task details** section and any linked notes (`maintenance/backlog.md`, `maintenance/private/client-log.md`).

## 2. Check the working tree first
Run `git status --short`. If there are uncommitted changes belonging to **another** task (look at the board's "local only" tasks and their file lists), tell the user and recommend one of these:
- **a)** review and commit that task first with `/prepare-deploy` (keeps one task per commit, which makes rollback easy), or
- **b)** continue anyway; the changes will be committed together later.

Wait for their choice before editing anything.

## 3. Confirm scope in one short message
Give the task ID and title, what you'll change (pages and files), the facts you'll rely on, and anything that needs the client's OK before deploy. If the task needs information that's missing, set it to `blocked`, record what's missing, add the question to **Questions for the client**, and stop. Otherwise set the status to `in progress` and continue without waiting, unless the change involves content wording the client hasn't approved; then show the proposed wording first.

## 4. Implement locally
Use the matching skill's rules: `/site-update`, `/service-area-page`, `/blog-post`, `/process-photos` or `/google-reviews`. Preserve the existing architecture, design and classes. Change only what the task covers.

## 5. Verify
- `python3 maintenance/scripts/check_site.py --quiet`: 0 new errors.
- Local preview (`python3 -m http.server 8080` from the repo root, or the `site-preview` launch config) of every changed page, at desktop and mobile widths when the layout changed.

## 6. Update the board
- Status: `completed` if done and checks pass; `in progress` if partly done; `blocked` if stopped on missing info.
- Missing / blocked on: what's still needed (e.g. "client's OK on wording before deploy"), or `—`.
- Deploy state: `local only`.
- Task details: add "Done (date)", the **Files changed** list (from `git status --short`), and the check result.
- Add a row to **Change history**, and update "Last updated".

## 7. Report and stop
Use the CLAUDE.md summary format (what changed, files, exact before → after text, checks, preview links, also noticed). Finish with the next suggested task and: "Reply *approve* to commit this task, or tell me what to adjust." Never commit, push or deploy in this skill.
