---
name: google-reviews
description: Manage how Google reviews appear on the site, including review links, the "see all reviews" and "leave a review" buttons, the featured reviews section, and review-request wording, within Google policy. Use for any request about reviews, ratings, testimonials or the Google profile link.
---

# Google reviews

No paid API is needed. Reviews are handled as owner-approved content plus links to the real Google profile. Read `CLAUDE.md` first.

## Links (most requests)
- Two different URLs exist. Get both from the owner (from their Google Business Profile, under "Read reviews" or "Ask for reviews"):
  - **Profile / reviews URL:** where visitors read all reviews.
  - **Write-a-review URL** (`https://g.page/r/.../review` or `https://search.google.com/local/writereview?placeid=...`): where customers leave one.
- Never guess or construct these URLs. Record them in the *Business facts* table in `CLAUDE.md`.
- Place a prominent "See our reviews on Google" button in the homepage `#reviews` section, a Google icon in the full footer (see *Shared blocks* in CLAUDE.md), and optionally a small link on city pages. Use `target="_blank" rel="noopener"`.
- Add the profile URL to the homepage JSON-LD `sameAs` only once the owner confirms it.

## Featured reviews (the homepage `#reviews` cards)
- Only use real Google reviews the owner points to. Copy the text **exactly** (light trimming with "…" is OK). Use the reviewer's name as shown on Google (first name + last initial is fine), the star rating, and the month/year.
- Label the cards "Google review" and link each one, or the section, to the Google profile. Don't use "Verified Customer" unless that's true and meaningful.
- The owner may choose which reviews to feature. Next to them, always link to *all* reviews on Google.
- **Never** write, edit the meaning of, or merge reviews. Never invent a review count or average. Only show "4.9 ★ from N reviews" if the owner supplies the current figures, and include an "as of <Month YYYY>" date.
- No `AggregateRating` or `Review` schema for the business (self-served review markup is ignored by Google and risks penalties).
- **Updated or deleted reviews:** if the owner says a featured review changed or was removed on Google, update or remove the card in the same change.

## Review requests (wording for the owner to send customers)
Draft short SMS or email text with the write-a-review link. It must be **neutral**: ask every customer, and don't offer incentives or ask only happy customers ("review gating" breaks Google policy). The dashboard doesn't send anything; the owner sends it.

## Replies to reviews (drafts only)
If asked, draft replies the owner can paste into Google. Make them polite and specific, with no customer details, no arguing, and no incentives. Claude never posts them.

## Finish
Run the check, preview, and summarize with the exact text before and after. Don't commit.
