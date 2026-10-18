---
name: site-check
description: Run the website maintenance check (broken links, SEO tags, structured data, sitemap, image size and GPS metadata, claims and dates) and explain the results in plain English with suggested fixes. Read-only. Use for "check the site", health checks, or before deploying.
---

# Site maintenance check (read-only)

1. Run:
   ```bash
   python3 maintenance/scripts/check_site.py
   ```
   It never changes files. **NEW** issues are ones not in `maintenance/check-baseline.txt`. Known issues are the pre-existing ones listed in `maintenance/backlog.md`.
2. Also check these read-only items:
   - `git status --short` (uncommitted work?) and `git --no-optional-locks log -1 --format='%h %ad %s' --date=short`.
   - Promotions past their end date: `grep -rn "PROMO ends" --include=*.html .` and compare with today.
   - Copyright year in footers vs. the current year.
   - **Optional, with the owner's OK** (reads the public live site, changes nothing): `curl -sI <live domain from CLAUDE.md>/` for status and the hosting server header, and compare the live homepage with the local file using `curl -s <domain>/ | shasum` vs `shasum index.html` to see whether local changes are unpublished.
3. Report in plain English:
   - **Needs attention now:** new errors, broken links, GPS in images, expired promotions.
   - **Worth fixing:** warnings grouped by type, with the number of pages affected.
   - **Known backlog:** a one-line count, pointing to `maintenance/backlog.md`.
   - For each item, a suggested fix and which skill would do it (e.g. `/process-photos` for image issues).
4. Don't fix anything in this skill. Offer to, and wait for the owner to pick.

Only run `--save-baseline` when the owner explicitly accepts the current issues as known (for example after a deploy). Say so in the summary when you do.
