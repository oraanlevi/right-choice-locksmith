---
name: client-update
description: Incorporate a new client message, answer, request, or batch of photos into the private task board and client log. Use when the user pastes or forwards something from the client (text, email, call notes, screenshots), says "the client sent...", or drops new photos.
---

# Incorporate client input

Everything here stays in `maintenance/private/` (git-ignored). Never copy client messages into tracked files, commit messages or public pages, except approved website content.

## 1. Log it
Add an entry at the **top** of `maintenance/private/client-log.md`: the date, the source (text, email, call notes, photos), and a short summary of what was asked or answered. Leave out customer names, addresses, phone numbers, prices quoted to customers, and anything personal. Keep only what the website work needs.

## 2. Map it to tasks
For each request or answer:
- **Answers a missing item** → update that task: clear or adjust "Missing / blocked on", change `blocked` → `pending` when nothing is left missing, and record the facts in Task details. Remove the answered question from "Questions for the client". New business facts (hours, URLs, services) also go into the CLAUDE.md *Business facts* table; that's a tracked file, so public business facts only.
- **New request** → add a new board row (next free ID, status `pending` or `blocked`, priority, missing info, deploy state `not started`) and a Task details section. Split big requests into tasks that can each be finished and reviewed on their own.
- **Changes or cancels a request** → update the task. Cancelled tasks become `completed` with "Cancelled by client (date)" in their details. Don't delete rows.
- **Approval of wording or a change** → note it in the task details as "client approved <what> (date)". The user's own approval is still required before any commit or push.

## 3. Photos
If photos arrived, make sure they're in `client-uploads/inbox/`, then follow `/process-photos` up to the approval table. Link the batch (manifest path) to the relevant task(s). Photos flagged outside the service area, or showing people, plates or house numbers, need the client's confirmation and get a question added.

## 4. Report
Reply briefly:
- what was logged
- the tasks created, unblocked or changed (IDs)
- questions still open for the client, ready to copy into a message
- the new "next task"

Don't change website files in this skill unless the user asks to start the work.
