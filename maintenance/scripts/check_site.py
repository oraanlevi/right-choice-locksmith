#!/usr/bin/env python3
"""Read-only maintenance check for a static HTML site.

Usage:
  python3 maintenance/scripts/check_site.py              # full report
  python3 maintenance/scripts/check_site.py --save-baseline
  python3 maintenance/scripts/check_site.py --quiet       # only NEW issues

Never modifies site files. Settings: maintenance/site.config.json.
Known (pre-existing) issues are stored in maintenance/check-baseline.txt so a
change is judged only by the NEW issues it introduces. Exit code 1 = new errors.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG = os.path.join(ROOT, "maintenance", "site.config.json")
BASELINE = os.path.join(ROOT, "maintenance", "check-baseline.txt")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.desc, self.canonical, self.robots = None, None, None, ""
        self.h1 = 0
        self.links, self.imgs, self.ids, self.jsonld = [], [], set(), []
        self._in_title = self._in_ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "title":
            self._in_title, self._buf = True, []
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description":
                self.desc = a.get("content", "")
            elif name == "robots":
                self.robots = a.get("content", "").lower()
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href") is not None:
            self.links.append((a["href"], self.getpos()[0]))
        elif tag == "link" and a.get("href") and (a.get("rel") or "") in ("stylesheet", "icon"):
            self.links.append((a["href"], self.getpos()[0]))
        elif tag == "script" and a.get("src"):
            self.links.append((a["src"], self.getpos()[0]))
        elif tag == "script" and (a.get("type") or "") == "application/ld+json":
            self._in_ld, self._buf = True, []
        elif tag in ("img", "source"):
            src = a.get("src") or (a.get("srcset") or "").split(",")[0].strip().split(" ")[0]
            if src:
                self.imgs.append((tag, src, a.get("alt"), self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title, self._in_title = "".join(self._buf).strip(), False
        elif tag == "script" and self._in_ld:
            self.jsonld.append("".join(self._buf))
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title or self._in_ld:
            self._buf.append(data)


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, rel, msg, line=None):
        where = f"{rel}:{line}" if line else rel
        self.items.append((level, where, msg, f"{level}|{rel}|{msg}"))


def load_config():
    with open(CONFIG) as f:
        return json.load(f)


def page_files(cfg):
    files = []
    for g in cfg["html_globs"]:
        files += sorted(glob.glob(os.path.join(ROOT, g)))
    return [os.path.relpath(f, ROOT) for f in files]


def url_for(cfg, rel):
    if rel == "index.html":
        return cfg["domain"] + "/"
    if rel.endswith("/index.html"):
        return cfg["domain"] + "/" + rel[: -len("index.html")].rstrip("/")
    return cfg["domain"] + "/" + rel


def redirects():
    try:
        with open(os.path.join(ROOT, "vercel.json")) as f:
            return {r["source"] for r in json.load(f).get("redirects", [])}
    except Exception:
        return set()


def resolve(rel_page, href):
    """Return repo-relative target path for an internal href, or None if external."""
    p = urlparse(href)
    if p.scheme in ("http", "https", "mailto", "tel", "sms", "javascript", "data") or p.netloc:
        return None
    path = p.path
    if not path:
        return rel_page
    if path.startswith("/"):
        target = path.lstrip("/")
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(rel_page), path))
    if target in ("", "."):
        target = "index.html"
    if os.path.isdir(os.path.join(ROOT, target)):
        target = os.path.join(target, "index.html")
    return target


def git_first_added(rel):
    try:
        out = subprocess.run(
            ["git", "--no-optional-locks", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", rel],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout.split()
        return out[-1] if out else None
    except Exception:
        return None


def walk_ld(node, out):
    if isinstance(node, dict):
        out.append(node)
        for v in node.values():
            walk_ld(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_ld(v, out)


def has_gps(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            exif = im.getexif()
            gps = exif.get_ifd(0x8825) if exif else None
            return bool(gps)
    except Exception:
        pass
    try:  # macOS fallback (handles HEIC)
        out = subprocess.run(["mdls", "-raw", "-name", "kMDItemLatitude", path],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out not in ("", "(null)")
    except Exception:
        return None


def run(cfg):
    r = Report()
    pages = page_files(cfg)
    parsed = {}
    for rel in pages:
        p = Page()
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            p.feed(f.read())
        parsed[rel] = p
    redirect_sources = redirects()
    titles, descs = defaultdict(list), defaultdict(list)
    claim_res = [re.compile(c, re.I) for c in cfg.get("claims_to_verify", [])]
    tel = cfg.get("phone_tel")
    canon_id = cfg.get("canonical_entity_id")

    for rel, p in parsed.items():
        noindex = "noindex" in p.robots
        if not p.title:
            r.add("ERROR", rel, "missing <title>")
        else:
            titles[p.title].append(rel)
            if len(p.title) > 70:
                r.add("WARN", rel, f"title is {len(p.title)} chars (aim ≤ 60–65)")
        if not p.desc:
            r.add("ERROR", rel, "missing meta description")
        else:
            descs[p.desc].append(rel)
            if not 70 <= len(p.desc) <= 165:
                r.add("WARN", rel, f"meta description is {len(p.desc)} chars (aim 120–155)")
        if not noindex:
            if not p.canonical:
                r.add("ERROR", rel, "missing canonical link")
            elif p.canonical.rstrip("/") != url_for(cfg, rel).rstrip("/"):
                r.add("WARN", rel, f"canonical {p.canonical} does not match page URL {url_for(cfg, rel)}")
        if p.h1 != 1:
            r.add("ERROR", rel, f"has {p.h1} <h1> elements (need exactly 1)")

        for href, line in p.links:
            if href.startswith("tel:") and tel and href != f"tel:{tel}":
                r.add("WARN", rel, f"phone link {href} differs from {tel}", line)
            target = resolve(rel, href)
            if target is None:
                continue
            path_only = urlparse(href).path
            if path_only in redirect_sources:
                continue
            if not os.path.exists(os.path.join(ROOT, target)):
                r.add("ERROR", rel, f"broken internal link: {href}", line)
                continue
            frag = urlparse(href).fragment
            if frag and target.endswith(".html") and target in parsed and frag not in parsed[target].ids:
                r.add("ERROR", rel, f"link to missing anchor #{frag} in {target}", line)

        for tag, src, alt, line in p.imgs:
            target = resolve(rel, src)
            if target and not os.path.exists(os.path.join(ROOT, target)):
                r.add("ERROR", rel, f"missing image file: {src}", line)
            if tag == "img" and alt is None:
                r.add("ERROR", rel, f"image without alt attribute: {src}", line)

        for block in p.jsonld:
            try:
                data = json.loads(block)
            except Exception as e:
                r.add("ERROR", rel, f"JSON-LD does not parse: {e}")
                continue
            nodes = []
            walk_ld(data, nodes)
            for n in nodes:
                if n.get("@id") == canon_id and isinstance(n.get("address"), dict):
                    loc = n["address"].get("addressLocality")
                    if loc and loc != cfg.get("home_locality"):
                        r.add("WARN", rel, f"canonical entity declared with address in {loc} (implies a second location)")
                if n.get("@type") in ("AggregateRating", "Review") or "aggregateRating" in n:
                    r.add("WARN", rel, "self-served review/rating markup (Google ignores it for local businesses)")
                if n.get("@type") in ("Article", "BlogPosting"):
                    dp = n.get("datePublished")
                    if not dp:
                        r.add("ERROR", rel, "Article without datePublished")
                    elif rel.startswith(os.path.dirname(cfg.get("blog_glob", "x/x"))):
                        first = git_first_added(rel)
                        if first and (date.fromisoformat(first) - date.fromisoformat(dp[:10])).days > 2:
                            r.add("WARN", rel, f"datePublished {dp} is earlier than first commit {first}")

        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            for i, text in enumerate(f, 1):
                plain = re.sub(r"<[^>]+>", " ", text)
                for cre in claim_res:
                    m = cre.search(plain)
                    if m:
                        r.add("CLAIM", rel, f"verify claim: \"{m.group(0).strip()}\"", i)

    for t, rels in titles.items():
        if len(rels) > 1:
            r.add("WARN", ", ".join(rels), f"duplicate title: {t}")
    for d, rels in descs.items():
        if len(rels) > 1:
            r.add("WARN", ", ".join(rels), "duplicate meta description")

    sm = cfg.get("sitemap_file")
    if sm and os.path.exists(os.path.join(ROOT, sm)):
        with open(os.path.join(ROOT, sm)) as f:
            locs = re.findall(r"<loc>([^<]+)</loc>", f.read())
        listed = set()
        for loc in locs:
            path = urlparse(loc).path.lstrip("/")
            target = resolve("index.html", "/" + path) if path else "index.html"
            listed.add(target)
            if not os.path.exists(os.path.join(ROOT, target)):
                r.add("ERROR", sm, f"sitemap URL has no file: {loc}")
        for rel, p in parsed.items():
            if "noindex" in p.robots or rel in cfg.get("sitemap_exclude", []):
                continue
            if rel not in listed:
                r.add("WARN", sm, f"page not in sitemap: {rel}")

    budget = cfg.get("image_budget_kb", 400) * 1024
    for d in cfg.get("image_dirs", []):
        for path in sorted(glob.glob(os.path.join(ROOT, d, "**", "*"), recursive=True)):
            if not os.path.isfile(path):
                continue
            rel = os.path.relpath(path, ROOT)
            ext = os.path.splitext(path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic", ".heif", ".gif"):
                continue
            size = os.path.getsize(path)
            if size > budget:
                r.add("WARN", rel, f"image is {size // 1024} KB (budget {budget // 1024} KB)")
            if ext in (".heic", ".heif"):
                r.add("WARN", rel, "HEIC file in public site folder (browsers can't show it)")
            if has_gps(path):
                r.add("ERROR", rel, "image contains GPS location metadata")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-baseline", action="store_true", help="record current issues as known")
    ap.add_argument("--quiet", action="store_true", help="show only NEW issues")
    args = ap.parse_args()
    cfg = load_config()
    rep = run(cfg)

    if args.save_baseline:
        with open(BASELINE, "w") as f:
            f.write("# Known issues accepted as baseline. Regenerate with --save-baseline.\n")
            for key in sorted({k for *_, k in rep.items}):
                f.write(key + "\n")
        print(f"Saved {len(rep.items)} issues to {os.path.relpath(BASELINE, ROOT)}")
        return 0

    known = set()
    if os.path.exists(BASELINE):
        with open(BASELINE) as f:
            known = {l.rstrip("\n") for l in f if l.strip() and not l.startswith("#")}

    new = [i for i in rep.items if i[3] not in known]
    old = [i for i in rep.items if i[3] in known]
    order = {"ERROR": 0, "WARN": 1, "CLAIM": 2}

    def show(title, items):
        print(f"\n== {title} ({len(items)}) ==")
        for level, where, msg, _ in sorted(items, key=lambda i: (order[i[0]], i[1])):
            print(f"  [{level}] {where}  {msg}")

    print(f"Checked {len(page_files(cfg))} pages in {ROOT}")
    show("NEW issues (caused by current changes)", new)
    if not args.quiet:
        show("Known issues (baseline, not caused by this change)", old)
    new_errors = sum(1 for i in new if i[0] == "ERROR")
    print(f"\nResult: {new_errors} new error(s), {len(new) - new_errors} new warning(s)/claim(s), "
          f"{len(old)} known issue(s).")
    return 1 if new_errors else 0


if __name__ == "__main__":
    sys.exit(main())
