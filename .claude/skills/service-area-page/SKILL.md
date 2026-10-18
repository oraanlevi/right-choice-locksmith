---
name: service-area-page
description: Add a new city or neighborhood service-area page, or update an existing one, with unique, accurate local content, internal links, SEO metadata and correct structured data. Use when asked for a "locksmith in <city>" page or a local landing page.
---

# Service-area page

Goal: a genuinely useful local page, **not a doorway page**. Follow the *SEO requirements* and *Change workflow* in `CLAUDE.md`.

## 1. Collect owner-confirmed facts first (ask in one message)
1. Do you actively serve <area>? Any limits (hours, services not offered there)?
2. Roughly how long does it usually take to get there, and from where? Don't promise a response time the owner hasn't confirmed.
3. Which jobs are most common there (home lockouts, rekeys after moving, car keys, business access)?
4. Any real jobs done there we can mention generally? (No customer names or addresses.)
5. Any photos taken there? (They go through `/process-photos` first.)

If the owner can't answer most of these, recommend adding the area as a short paragraph on an existing page or a "Service Areas" hub instead of a thin page. Wait for their choice.

## 2. Research local context (public facts only)
- Use well-known, checkable facts: the area's type (neighborhood vs city; e.g. "Park Cities" = Highland Park + University Park, separate towns surrounded by Dallas), housing types, major roads and districts, the county.
- **Don't invent** landmarks, statistics, crime figures, or "our office in X". If you aren't sure a fact is true, leave it out or ask.

## 3. Build the page
- File name and layout: follow the city-page template under *Page templates* in CLAUDE.md (lowercase, hyphenated slug). Copy the **layout** only. Write all copy fresh; never swap the city name into another page's text.
- **Unique content:** the hero, a services section tied to how people in that area actually use this business's services, a coverage section with nearby-area chips (link the ones that have pages), and a CTA. Keep the claims honest (see CLAUDE.md).
- `<title>`: follow the title pattern in CLAUDE.md *SEO requirements* (≤ 60 characters if possible). Write a unique meta description (120–155 characters). Absolute canonical with `.html`, plus `og:*` tags.
- JSON-LD: a **`Service`** node with `provider: {"@id": "<canonical entity>"}`, `serviceType` (the business's trade), and `areaServed: {"@type": "City" or "Place", "name": "<Area>, <State>"}`. **Never** a `LocalBusiness` (or subtype) with a `PostalAddress` for the area.
- Link out to at least 3 relevant service pages and 1–2 nearby area pages.

## 4. Wire it into the site
- Service Areas dropdown **and** the mobile accordion in every page file. Verify with `grep -c "<new-file>.html"` across all page files.
- Homepage footer "Locations" column, `pages/sitemap.html`, `sitemap.xml`.
- Add the area to the homepage JSON-LD `areaServed` if it's missing.
- Add a link back from 1–2 nearby city pages (in their location chips).

## 5. Duplicate check
Compare the new page's body text with every other area page. If any paragraph is near-identical (same sentences with the place name swapped), rewrite it. Report "similar sentences found: N" in the summary.

## 6. Check, preview, summarize, stop
Run `python3 maintenance/scripts/check_site.py --quiet` (0 new errors), preview the page on desktop and mobile widths, then summarize using the CLAUDE.md format. List every owner fact used, plus any fact you left out because it was unconfirmed. Don't commit.

## Updating an existing area page
Same rules. Change only what was asked. If the page has the known city-address schema issue (see `maintenance/backlog.md`), mention it but fix it only if the owner approves.
