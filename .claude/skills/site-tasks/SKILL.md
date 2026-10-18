---
name: site-tasks
description: Show the maintenance task board, including what's next, what awaits review or deploy, what's blocked and what to ask the client. Use when the user asks "where are we", "what's left", "status", or "what do I need from the client".
---

# Task board status

1. Read `maintenance/private/TASKS.md` (private). Run `git status --short` and `git --no-optional-locks log @{u}..HEAD --oneline` to confirm the deploy states are accurate. If the board says "local only" but those files are already committed, or "committed" but already pushed, correct the board.
2. Reply in this order, briefly:
   - **Next:** the next unblocked task (same rule as `/next-task`).
   - **Awaiting your review / publish:** tasks that are `completed` but `local only` or `committed (not pushed)`.
   - **In progress:** with what's left.
   - **Blocked:** grouped by who must act (client vs. you), with what's missing.
   - **Questions for the client:** copy-ready, numbered.
   - A counts line: pending / in progress / blocked / completed.
3. Don't change any files except to correct the board in step 1.
