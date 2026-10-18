# Website maintenance with Claude Code

Open this folder in Claude Code (the desktop app or `claude` in a terminal) and describe what you want in plain English. Claude reads `CLAUDE.md` automatically, so it already knows the site, the brand and the rules.

## What happens on every request

1. Claude restates the request and asks for any missing facts.
2. It edits files **locally** only.
3. It runs the site check (`maintenance/scripts/check_site.py`) and starts a local preview at http://127.0.0.1:8080/.
4. It gives you a change summary: what changed, the files, and the exact before → after text.
5. **It stops.** Nothing is committed, pushed or published until you say so.
6. When you're happy, type `/prepare-deploy`. It reviews everything and asks **"Approve commit?"**, then separately **"Push to GitHub? This publishes the live site."**

## Task board (private)

Client requests, missing info and deploy status are tracked in `maintenance/private/TASKS.md`, and the client's messages are logged in `maintenance/private/client-log.md`. Both are git-ignored and never deployed. Each Claude Code session starts with a short brief from the board (SessionStart hook `maintenance/hooks/session_brief.py`).

## Built-in safety

- `.claude/settings.json` plus `maintenance/hooks/approval_gate.py` make Claude Code ask you before any `git commit`, `git push`, merge/reset, `vercel` or `gh` command, even in auto mode. Force-push is blocked outright.
- `client-uploads/` is git-ignored, and `.vercelignore` keeps `CLAUDE.md`, `.claude/`, `maintenance/` and `client-uploads/` off the live site.
- Photo processing strips GPS and all other metadata and verifies it.

## Slash commands

| Command | What it does |
| --- | --- |
| `/site-update` | Text, hours, services, promotions, links, footer icons |
| `/service-area-page` | New or updated city/neighborhood page |
| `/blog-post` | Draft or update a blog post |
| `/process-photos` | Clean and resize photos from `client-uploads/inbox/`, suggest alt text, place approved ones |
| `/google-reviews` | Review links, featured reviews, review-request wording |
| `/site-check` | Full health check, explained in plain English |
| `/prepare-deploy` | Review, then commit (approval 1), then publish (approval 2) |
| `/next-task` | Do the next unblocked task from the board, locally, with checks and a report |
| `/client-update` | Add a client message, answers or photos to the task board |
| `/site-tasks` | Where things stand: next, awaiting review, blocked, questions for the client |

You don't have to use the commands. Plain requests work too, and Claude picks the right skill.

## Files

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` | Site architecture, business facts, brand, SEO and safety rules |
| `.claude/skills/*/SKILL.md` | The slash commands |
| `.claude/settings.json` | Permission rules and the approval hook |
| `.claude/launch.json` | Local preview server (`site-preview`) |
| `maintenance/site.config.json` | Domain, phone, image sizes, service-area box, claim patterns |
| `maintenance/scripts/check_site.py` | Read-only site check |
| `maintenance/scripts/process_photos.py` | Photo cleaning and resizing (Python 3 + Pillow) |
| `maintenance/check-baseline.txt` | Known pre-existing issues, so checks show only new ones (local only, git-ignored) |
| `maintenance/private/` | Task board and client log (local only, git-ignored) |
| `maintenance/snippets/` | Ready-made markup to restore later (e.g. the Facebook icon) |
| `maintenance/backlog.md` | Known issues from audits (local only, git-ignored: it's a client document) |

## Reusing this for another client

A generic copy of this setup (the Pink Web Studio site kit) is kept outside this repository, on the studio machine. Install it into another client's site with its `install.sh`.
