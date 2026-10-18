---
name: process-photos
description: Process a batch of client photos from client-uploads/inbox. Strips GPS and metadata, optimizes and resizes them, suggests alt text and tags, proposes placements, and adds approved photos to pages. Use when the owner says they dropped or uploaded new photos.
---

# Process client photos

Raw client photos never go into the repo (it's public). Only the cleaned, resized outputs do, and only after approval.

## 1. Process (automatic, local, no paid services)
```bash
python3 maintenance/scripts/process_photos.py
```
This converts HEIC, fixes rotation, strips **all** metadata (and verifies it), makes 480/960/1600 px WebP + JPG versions, and writes `client-uploads/processed/<batch>/manifest.json`. Originals are moved to `client-uploads/originals/<batch>/` (never deleted). If the inbox is empty, tell the owner where to drop files (`client-uploads/inbox/`) and stop.

## 2. Look at every photo
Open each `*-960.jpg` with the Read tool so you actually see it. For each photo:
- **Alt text:** describe what is visible and why it matters for this business, in ≤ 125 characters, no "image of", no keyword stuffing. Example (locksmith site): "Technician rekeying a front-door deadbolt on a brick home".
- **Tags:** `category` (residential / commercial / automotive / team / van / other), `service` (matching a service page), and `city` (only if the owner told you; never guess from GPS beyond the in/out-of-area flag).
- **Suggested placement:** the page and section where it fits best, e.g. "`pages/rekey.html`, below the intro", "homepage gallery", or a blog post.
- **Flags:** any script warnings (outside the service area, small, blurry), plus anything you can see that shouldn't be published: faces without consent, house numbers, license plates, customer names, keys that could be copied, competitor branding.

Write these into `manifest.json` (`alt_text`, `tags`, `placement`; `approved` stays `false`).

## 3. Ask for approval (one table, then stop)
Show a table: **#, preview file, suggested alt text, tags, suggested page/section, flags**. Ask the owner to reply with which to use, where, and any alt-text edits. Photos flagged "outside service area" need explicit confirmation that they are the client's real jobs.

## 4. Place approved photos only
- Rename to a descriptive slug (`rekey-front-door-deadbolt-960.webp`) and copy the needed sizes into `assets/images/photos/<category>/`.
- Insert using `<picture>` with WebP first and a JPG fallback, a `srcset` of the available widths, `sizes`, `width`/`height`, `loading="lazy"` (not for the hero image), `decoding="async"`, and the approved alt text. Use the path prefix the page needs (see CLAUDE.md relative paths).
- Match the existing styling; don't add new CSS unless needed (then add it to `style.css` in the existing format).
- Set `"approved": true` and the final `placement` in the manifest.

## 5. Check, preview, summarize, stop
Run `python3 maintenance/scripts/check_site.py --quiet`. You need 0 new errors, and the GPS check must be clean. Preview the pages, then summarize which photos were placed where, with alt text and file sizes. Don't commit. `client-uploads/` itself is never committed.
