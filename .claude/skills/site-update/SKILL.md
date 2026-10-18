---
name: site-update
description: Make a natural-language change to the website, such as text, hours, phone, services, promotions, links, footer or social icons, or business info. Use for any "change/update/add/remove X on the site" request that is not a new city page, blog post, photo batch or reviews task.
---

# Update site content

Follow the **Change workflow** in `CLAUDE.md`. This skill adds the details for content edits.

## 1. Understand the request
- Restate it in one line: what changes, and on which pages.
- **Business facts** (hours, phone, email, license, services, social URLs) come from the *Business facts* table in `CLAUDE.md` or from the owner. If the owner gives a new value, update that table too.
- Missing a value (for example "add our Facebook link" with no URL)? **Ask, don't guess.**
- **Promotions:** get the exact offer wording, price, end date and any conditions. A promotion with an end date gets an HTML comment `<!-- PROMO ends YYYY-MM-DD -->` so `/site-check` users can find it later.

## 2. Find every place it appears
The site has no templates, so a single fact may be repeated in many files. Always search:
```bash
grep -rn --include=*.html "<old text or value>" .
```
- Hours → visible text plus `openingHours` in JSON-LD (homepage and any page whose schema has hours).
- Phone → visible text, `tel:` and `sms:` links, the mobile call bar, JSON-LD `telephone` (every page).
- Services and cities → nav dropdowns plus the mobile accordion in all page files.
- Footer social icons → check *Shared blocks* in CLAUDE.md for which pages carry the full footer. Use small inline SVG icons with `aria-label` ("<Business name> on Facebook"), plus `target="_blank" rel="noopener"`. Add confirmed profile URLs to the homepage JSON-LD `sameAs`.

## 3. Edit
- Match the existing markup, classes and tone (see *Brand guidelines*). Don't restyle.
- Don't add claims from the *Claims that need owner confirmation* list.

## 4. Check, preview, summarize, stop
- Run `python3 maintenance/scripts/check_site.py --quiet`. You need 0 new errors.
- Preview the changed pages locally (`site-preview`, http://127.0.0.1:8080/).
- Give the summary in the CLAUDE.md format, with **exact before → after text** for every change and the count of files changed for repeated blocks (for example "nav updated in 23/23 files").
- End with: "Reply *approve* to commit, or tell me what to adjust." Don't commit.
