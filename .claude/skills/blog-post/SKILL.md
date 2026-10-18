---
name: blog-post
description: Draft a new blog post or update an existing one, with accurate current information, a category, an image, SEO metadata, Article schema and honest dates. Use for any blog, article or guide request.
---

# Blog post

Follow `CLAUDE.md` (Brand voice, SEO requirements, Change workflow).

## 1. Agree the brief (one short message to the owner)
- Topic and the reader's question it answers, the target service page to link to, a category (existing labels: "Decision Guide", "Cost Guide", "Safety Guide" and similar; reuse one if it fits), and the featured image (from `/process-photos` or none).
- Check that the topic doesn't duplicate an existing post in `pages/blog/`. If it overlaps, propose updating that post instead.

## 2. Research and accuracy
- Today's date comes from the environment. Write for the current year, and use current sources for products, laws, prices and stats.
- Every price, statistic, law or product claim must be either (a) from a source you opened, which you name in the summary, or (b) phrased as general guidance ("typically", "we can confirm on site").
- Don't use claims from the CLAUDE.md "needs confirmation" list, invented customer stories, or fear-selling.

## 3. Write
- File: `pages/blog/<slug>.html` (short and descriptive, **no year in the slug**, so the URL stays valid when the post is updated). Copy the layout of the blog template listed under *Page templates* in CLAUDE.md.
- Use the category label above the H1. The byline is `By <business name> · <Month YYYY>`.
- Structure: a short intro, 3–6 H2 sections, practical lists, then the CTA box with "Related:" links. Link to at least 2 service pages and 1 related post.
- `<title>` ≤ 60 characters where possible. Unique description (120–155 characters), absolute canonical, `og:*`.
- Image: `<picture>` with WebP + JPG, `width`/`height`, `loading="lazy"`, and real alt text.
- JSON-LD `Article`: `headline`, `description`, author and publisher with `@id` = the canonical entity, plus `datePublished` and `dateModified`.

## 4. Dates (strict)
- **New post:** set `datePublished` = `dateModified` = the planned go-live date, and say in the summary that it must match the day it is actually pushed. `/prepare-deploy` re-checks this.
- **Updating a post:** never change `datePublished`. Set `dateModified` to today **only for a meaningful content change** (not a typo), and update the visible line to "Updated <Month YYYY>" at the same time.
- Never re-date an old post to make it look new.

## 5. Wire it in
Add the post to the homepage blog grid (see *Page templates* in CLAUDE.md; keep the grid tidy and ask which card to replace if it's full), `pages/sitemap.html` and `sitemap.xml`. Add a link to it from 1–2 relevant service pages.

## 6. Check, preview, summarize, stop
Run `python3 maintenance/scripts/check_site.py --quiet`, preview the post, then summarize: title, URL, description, category, word count, sources used, and the claims flagged for the owner. Don't commit. Publishing is a separate `/prepare-deploy` approval.
