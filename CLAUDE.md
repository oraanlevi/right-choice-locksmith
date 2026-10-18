# Right Choice Locksmith website: maintenance guide

This repo is the live marketing site for **Right Choice Locksmith** (Dallas-Fort Worth). Pink Web Studio maintains it, and Claude Code is the maintenance assistant. Read this whole file before making any change.

## Golden rules (always apply)

1. **Local only until approved.** Make changes in this working folder. Never `git commit`, `git push`, run `vercel`, merge, tag, or change anything live (Vercel settings, DNS at GoDaddy, Google Business Profile, Facebook) unless the owner says yes to *that specific action* in the current conversation. An approval for one change does not cover the next one.
2. **Never force-push**, rewrite history, or edit `.git/`. Never switch branches or reset without asking.
3. **The GitHub repo is PUBLIC.** Never put secrets, API keys, client documents, invoices, customer names or addresses, or raw client photos in it. `client-uploads/` is git-ignored for this reason.
4. **Don't invent facts.** Business facts come only from this file, the existing site, or the owner. Ask when unsure. Never invent addresses, offices, prices, review counts, guarantees, years in business, or customer stories.
5. **Change only what was asked.** Don't "improve" unrelated content. Note anything else you notice under "Also noticed" in the summary.
6. **Every change ends with:** the site check, a local preview link, and the change summary (see *Change workflow*). Then stop and wait.

## Task board (start of every session)

- Client requests, audit items, missing info and deploy states live in **`maintenance/private/TASKS.md`**. The client's messages are logged in `maintenance/private/client-log.md`. Both are **private**: git-ignored, never deployed, never quoted in commits or public files.
- A SessionStart hook (`maintenance/hooks/session_brief.py`) adds a brief from the board at the start of each session. Open the session with a 2–4 line summary: the next task, what awaits the user's review or publish, and the key blockers. If the brief is missing, read `TASKS.md` yourself.
- "Work on the next task" → `/next-task`. New client message, answers or photos → `/client-update`. "Where are we?" → `/site-tasks`.
- After **any** website change, even an ad-hoc request, update the matching task (or add one): status, missing info, files changed, deploy state, and a change-history row.

## Business facts (source of truth)

| Fact | Value |
| --- | --- |
| Business name | Right Choice Locksmith (alternate: Right Choice Locksmith Dallas) |
| Domain | https://rightchoicelocksmithdallas.com |
| Phone | (469) 640-6420 · `tel:+14696406420` · `sms:+14696406420` |
| Email | rightchoicelocksmithdallas@gmail.com |
| License | TX DPS Lic # B31212401 · Bonded · Insured |
| Hours | 24/7 (`openingHours: "Mo-Su 00:00-23:59"`) |
| Address | No street address on the website (service-area business based in Dallas, TX). Don't add an address to pages or schema without the owner's explicit confirmation |
| Canonical schema entity | `https://rightchoicelocksmithdallas.com/#locksmith` |
| Services (pages) | Residential, Commercial, Automotive, Emergency, Rekey, Lock Change & Replacement, Car Key Replacement, Key Fob Programming |
| City pages today | Dallas, Fort Worth, Plano, Allen, Frisco, Irving |
| Facebook URL | *Pending from the owner.* The footer icon is hidden until then; restore it from `maintenance/snippets/facebook-footer-icon.html`. Not "The Right Choice Locksmith" (a different business) |
| Google Business Profile | "Right Choice Locksmith Dallas", place ID `ChIJj2cBRwpTg0URThxHDmgD2a0`, CID `12527047583958768718` (verified Oct 18, 2026: phone and website match) |
| Google reviews link (site buttons/icons) | https://search.google.com/local/reviews?placeid=ChIJj2cBRwpTg0URThxHDmgD2a0 |
| Google profile `sameAs` | https://maps.google.com/?cid=12527047583958768718 |
| Google "write a review" URL | https://search.google.com/local/writereview?placeid=ChIJj2cBRwpTg0URThxHDmgD2a0 (pattern, not yet used on the site) |

When the owner gives a new fact (hours, a social URL, a new service), update this table in the same change.

## Architecture

- Plain static HTML/CSS/JS. **No build step, no framework, no package.json.** What's in the repo is what's served.
- Hosting: **Vercel**, assumed to deploy automatically when `main` is pushed to `github.com/oraanlevi/right-choice-locksmith`. Confirmed: the live site is served by Vercel and matches this repo. *Not yet confirmed:* the Git integration and the plan tier. Ask the owner to confirm in the Vercel dashboard.
- `vercel.json` has one 308 redirect: `/pages/privacy.html` → `/privacy`.
- DNS is at GoDaddy. Don't touch it.

```
index.html                 homepage (only page with the full 4-column footer, reviews and blog grid)
pages/*.html               service pages, city pages (locksmith-<city>.html), about, sitemap.html
pages/blog/*.html          blog posts
privacy/index.html         privacy policy (served at /privacy)
assets/css/style.css       the only stylesheet
assets/js/main.js          nav dropdowns, mobile menu
assets/images/             logo + job photos
sitemap.xml, robots.txt    hand-maintained
maintenance/               Claude maintenance tooling (not part of the website)
client-uploads/            drop folder for new photos (git-ignored, never deployed)
```

### Relative paths

- From `index.html` use `pages/x.html` and `assets/...`.
- From `pages/*.html` use `x.html`, `../index.html` and `../assets/...`.
- From `pages/blog/*.html` use `../x.html`, `../../index.html` and `../../assets/...`.
- Canonical URLs are absolute and keep `.html`, e.g. `https://rightchoicelocksmithdallas.com/pages/rekey.html`.

### Shared blocks are copied into every page (no templates)

There are no includes, so a change to a shared block must be repeated in every file that has it. Use `grep -l` to find them all, and confirm the count in the summary.

- **Desktop nav dropdowns** (Services, Service Areas) and the **mobile accordion menu**: `index.html` + every file in `pages/` and `pages/blog/` (23 files).
- **Full footer** (`footer-inner`, 4 columns): `index.html` only. Other pages use the slim `footer-bottom` footer.
- **Mobile call bar** at the bottom of every page.
- Phone number, license line, and the copyright year appear on every page.

### Page templates (copy the closest existing page)

| New page type | Copy from | Must also update |
| --- | --- | --- |
| Service page | `pages/rekey.html` | Services dropdown + mobile menu (all 23 files), homepage services section if relevant, footer Services column, `sitemap.xml`, `pages/sitemap.html` |
| City / service-area page | `pages/locksmith-plano.html` (layout only, write new content) | Service Areas dropdown + mobile menu (23 files), homepage footer Locations column, `sitemap.xml`, `pages/sitemap.html`, nearby city chips, homepage `areaServed` if missing |
| Blog post | `pages/blog/rekey-vs-replace-locks.html` | Homepage blog grid (`#blog`), `sitemap.xml`, `pages/sitemap.html`, links from 1–2 related service pages |

## Brand guidelines

- **Look:** "cold metallic" dark theme. Colors are in `:root` of `style.css`: background `#050c12`, green accent `#00e87a`, ice blue `#7ecfed`, silver `#b8cfe0`, text `#eef6ff`. Reuse the existing classes (`btn-primary`, `btn-secondary`, `svc-card`, `loc-chip`, `eyebrow`, `section-title`, `accent`). Don't add new colors or fonts.
- **Fonts:** Rajdhani (headings and labels) and Exo 2 (body), loaded from Google Fonts in each page `<head>`.
- **Voice:** calm, plain, honest, practical. Say "generally", "typically", or "a locksmith can confirm on site" rather than absolutes. No hype, no fear-selling, no pressure. Earlier commits deliberately softened pricing and removed unsupported claims. Keep it that way.
- **Calls to action:** "📞 Call (469) 640-6420" (`btn-primary`) and "Send a Text" / "💬 Text". Every page ends with a call CTA.
- **Logo:** `assets/images/logo.png`. Alt text: "Right Choice Locksmith Logo".

## SEO requirements

- One `<h1>` per page. Unique `<title>` (aim ≤ 60 characters, pattern `Topic City TX | Right Choice Locksmith`). Unique meta description (aim 120–155 characters). Absolute canonical. `og:title`, `og:description`, `og:site_name`.
- **Structured data:**
  - The homepage holds the full `Locksmith` entity with `@id` = the canonical entity. Other pages *reference* it by `@id`; they don't redefine it.
  - Service pages use `Service` with `provider: {"@id": canonical}`.
  - Blog posts use `Article` with author and publisher `@id` = canonical, plus a real `datePublished` and `dateModified`.
  - **New city pages:** use `Service` with `provider` set to the canonical `@id` and `areaServed` set to that city or neighborhood. **Never add a `PostalAddress` or office for a city.** (Some older pages may not follow this yet; see the local backlog.)
  - No `AggregateRating` or `Review` markup for the business itself. Google ignores self-served review stars, and it risks a manual action.
  - `sameAs` only with URLs the owner has confirmed (Facebook, Google Business Profile).
- **Internal links:** every new page links to at least 3 relevant existing pages and is linked from at least 2. Use descriptive anchor text, not "click here".
- **Sitemap:** add every new indexable page to `sitemap.xml` and `pages/sitemap.html`.
- **No doorway pages:** a city page needs real, specific local content (owner-confirmed service facts and local context). If there isn't enough, propose a paragraph on an existing page instead.
- **Dates:** blog `datePublished` = the day it actually goes live. Never backdate, and never present an old post as new. A real update changes `dateModified` and the visible "Updated <Month YYYY>" line together.

## Claims that need owner confirmation

Don't add or change these without the owner's confirmation: review counts or ratings, response-time promises or guarantees, superlatives ("most trusted", "#1", "best"), specific prices, years of experience, and named customers or testimonials. `maintenance/scripts/check_site.py` lists them as warnings.

## Change workflow (every natural-language request)

1. **Understand:** restate the request in one or two lines. If a fact is missing (a URL, hours, a price), ask before editing. If the request is ambiguous, ask one question.
2. **Plan:** list the files you'll touch (remember the shared blocks above).
3. **Edit locally.** Match the existing markup and classes.
4. **Check:** run `python3 maintenance/scripts/check_site.py`. Fix every **NEW** error you caused. Known, pre-existing issues are listed separately; leave them unless asked.
5. **Preview:** start the local preview (`site-preview` in `.claude/launch.json`, or `python3 -m http.server 8080`) and open the changed pages. Check desktop and mobile widths when layout changed.
6. **Summarize** in this format:
   - **What changed:** plain-English bullets, per page.
   - **Files:** the output of `git status --short` and `git diff --stat`.
   - **Exact text:** before → after for any wording, hours, prices or links.
   - **Checks:** new errors and warnings (should be 0 new errors).
   - **Preview:** local URLs to look at.
   - **Also noticed:** anything else you saw but didn't change.
   - **Next step:** "Reply *approve* to commit, or tell me what to adjust." Then **stop**.
   - Before stopping, update `maintenance/private/TASKS.md` (status, files changed, deploy state `local only`).
7. **Only after approval:** use the `prepare-deploy` skill, which commits, and then pushes only after a *second*, separate approval.

## Skills (slash commands) in this project

| Command | Use it to |
| --- | --- |
| `/site-update` | Change any text, hours, services, promotions, links, or footer/social icons |
| `/service-area-page` | Add or update a city/neighborhood page |
| `/blog-post` | Draft or update a blog post |
| `/process-photos` | Process photos dropped in `client-uploads/inbox/` and place approved ones |
| `/google-reviews` | Update review links, featured reviews, review-request text |
| `/site-check` | Run the full maintenance check and explain the results |
| `/prepare-deploy` | Review all local changes, commit after approval, push after a second approval |
| `/next-task` | Pick the next unblocked task from the board, implement locally, check, report |
| `/client-update` | Log a client message, answers or photos, and update the task board |
| `/site-tasks` | Board status: next, awaiting review, blocked, questions for the client |

## Reference

- `maintenance/README.md`: how this setup works, for the owner.
- `maintenance/backlog.md`: known issues from audits. It's **local only and git-ignored** because it's a client document, so it may be missing on another machine. Don't fix these issues unless asked.
- `maintenance/site.config.json`: settings used by the check and photo scripts.
