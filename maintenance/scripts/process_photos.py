#!/usr/bin/env python3
"""Process a batch of client photos for the website.

  python3 maintenance/scripts/process_photos.py            # process client-uploads/inbox/
  python3 maintenance/scripts/process_photos.py --dry-run  # report only, write nothing

For each photo in client-uploads/inbox/:
  * converts HEIC/HEIF (via macOS `sips`), fixes rotation
  * strips ALL metadata (GPS, camera, date) from every output and verifies it
  * makes web sizes (site.config.json -> photo_output_widths) as WebP + JPEG
  * reports whether the photo was taken inside the business's service area
  * writes manifest.json for alt text / placement review
Outputs go to client-uploads/processed/<batch>/. Originals are MOVED (never
deleted) to client-uploads/originals/<batch>/. Nothing in the website folders
is touched; placing photos on pages is a separate, approved step.
Requires: Python 3 + Pillow (pip install Pillow). No paid services.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOADS = os.path.join(ROOT, "client-uploads")
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}

try:
    from PIL import Image, ImageOps, ImageFilter, ImageStat
except ImportError:
    sys.exit("Pillow is required: run  python3 -m pip install Pillow")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "photo"


def gps_to_deg(vals, ref):
    d, m, s = (float(v) for v in vals)
    deg = d + m / 60 + s / 3600
    return -deg if ref in ("S", "W") else deg


def read_meta(im):
    """Return (lat, lon, taken_at) from EXIF, or Nones."""
    lat = lon = taken = None
    try:
        exif = im.getexif()
        gps = exif.get_ifd(0x8825)
        if gps and 2 in gps and 4 in gps:
            lat = gps_to_deg(gps[2], gps.get(1, "N"))
            lon = gps_to_deg(gps[4], gps.get(3, "E"))
        sub = exif.get_ifd(0x8769)
        taken = sub.get(36867) or exif.get(306)
    except Exception:
        pass
    return lat, lon, taken


def mdls_gps(path):
    try:
        lat = subprocess.run(["mdls", "-raw", "-name", "kMDItemLatitude", path], capture_output=True, text=True).stdout
        lon = subprocess.run(["mdls", "-raw", "-name", "kMDItemLongitude", path], capture_output=True, text=True).stdout
        return (float(lat), float(lon)) if lat not in ("", "(null)") else (None, None)
    except Exception:
        return None, None


def open_image(path, tmpdir):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".heic", ".heif"):
        out = os.path.join(tmpdir, os.path.basename(path) + ".jpg")
        res = subprocess.run(["sips", "-s", "format", "jpeg", path, "--out", out], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError("sips could not convert HEIC: " + res.stderr.strip())
        return Image.open(out)
    return Image.open(path)


def sharpness(im):
    small = im.convert("L").resize((400, max(1, int(400 * im.height / im.width))))
    return ImageStat.Stat(small.filter(ImageFilter.FIND_EDGES)).var[0]


def clean_copy(im):
    """New image with pixels only: no EXIF/XMP/GPS travels with it."""
    im = ImageOps.exif_transpose(im)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if has_alpha else "RGB")
    clean = Image.new(im.mode, im.size)
    clean.paste(im)
    return clean, has_alpha


def verify_clean(path):
    with Image.open(path) as im:
        exif = im.getexif()
        return not exif and "xmp" not in im.info and "exif" not in im.info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=os.path.join(UPLOADS, "inbox"))
    ap.add_argument("--batch", default=datetime.now().strftime("%Y-%m-%d-%H%M"))
    ap.add_argument("--keep-originals-in-inbox", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "maintenance", "site.config.json")) as f:
        cfg = json.load(f)
    widths = cfg.get("photo_output_widths", [480, 960, 1600])
    area = cfg.get("photo_service_area")
    if area and not (area.get("lat_max") or area.get("lon_max")):
        area = None  # not configured yet

    files = sorted(f for f in os.listdir(args.inbox)
                   if os.path.splitext(f)[1].lower() in EXTS and not f.startswith("."))
    if not files:
        print(f"No photos in {os.path.relpath(args.inbox, ROOT)}/. Drop files there and run again.")
        return 0

    out_dir = os.path.join(UPLOADS, "processed", args.batch)
    orig_dir = os.path.join(UPLOADS, "originals", args.batch)
    if not args.dry_run:
        os.makedirs(out_dir, exist_ok=True)
    manifest = {"batch": args.batch, "created": datetime.now().isoformat(timespec="seconds"),
                "status": "pending-review", "photos": []}
    used = set()

    with tempfile.TemporaryDirectory() as tmp:
        for name in files:
            src = os.path.join(args.inbox, name)
            entry = {"original": name, "bytes": os.path.getsize(src)}
            try:
                with open(src, "rb") as fh:
                    entry["sha1"] = hashlib.sha1(fh.read()).hexdigest()[:12]
                im = open_image(src, tmp)
                lat, lon, taken = read_meta(im)
                if lat is None:
                    lat, lon = mdls_gps(src)
                entry["taken_at"] = str(taken) if taken else None
                entry["had_gps"] = lat is not None
                if lat is not None and area:
                    inside = area["lat_min"] <= lat <= area["lat_max"] and area["lon_min"] <= lon <= area["lon_max"]
                    entry["inside_service_area"] = inside
                    entry["approx_location"] = f"{lat:.1f}, {lon:.1f}"
                clean, alpha = clean_copy(im)
                im.close()
                w, h = clean.size
                entry["original_size"] = f"{w}x{h}"
                entry["sharpness"] = round(sharpness(clean), 1)
                warnings = []
                if w < widths[1]:
                    warnings.append(f"small image ({w}px wide); may look soft on large screens")
                if entry["sharpness"] < 60:
                    warnings.append("possibly blurry or very low detail; check before using")
                if entry.get("inside_service_area") is False:
                    warnings.append(f"GPS shows this was taken OUTSIDE {area['label']} "
                                    f"(~{entry['approx_location']}); confirm it is a real local job before using")
                entry["warnings"] = warnings

                base = slugify(os.path.splitext(name)[0])
                while base in used:
                    base += "-x"
                used.add(base)
                entry["slug"] = base
                outputs = []
                for tw in sorted({min(x, w) for x in widths}):
                    th = round(h * tw / w)
                    resized = clean.resize((tw, th), Image.LANCZOS)
                    formats = [("webp", {"quality": 80, "method": 6})]
                    formats.append(("png", {"optimize": True}) if alpha else
                                   ("jpg", {"quality": 82, "optimize": True, "progressive": True}))
                    for ext, opts in formats:
                        fn = f"{base}-{tw}.{ext}"
                        path = os.path.join(out_dir, fn)
                        if not args.dry_run:
                            img = resized if ext != "jpg" else resized.convert("RGB")
                            img.save(path, "JPEG" if ext == "jpg" else ext.upper(), **opts)
                            if not verify_clean(path):
                                raise RuntimeError(f"metadata still present in {fn}")
                            outputs.append({"file": fn, "width": tw, "height": th,
                                            "kb": round(os.path.getsize(path) / 1024)})
                        else:
                            outputs.append({"file": fn, "width": tw, "height": th})
                entry["outputs"] = outputs
                entry["metadata_removed"] = not args.dry_run
                entry.update({"alt_text": None, "tags": {"category": None, "service": None, "city": None},
                              "placement": None, "approved": False})
                if not args.dry_run and not args.keep_originals_in_inbox:
                    os.makedirs(orig_dir, exist_ok=True)
                    shutil.move(src, os.path.join(orig_dir, name))
            except Exception as e:
                entry["error"] = str(e)
            manifest["photos"].append(entry)

    if not args.dry_run:
        with open(os.path.join(out_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    print(f"Batch {args.batch}: {len(files)} photo(s)" + (" [DRY RUN, nothing written]" if args.dry_run else ""))
    for e in manifest["photos"]:
        if "error" in e:
            print(f"  ✗ {e['original']}: {e['error']}")
            continue
        gps = "GPS removed" if e["had_gps"] else "no GPS found"
        sizes = ", ".join(f"{o['file']}" + (f" ({o['kb']} KB)" if "kb" in o else "") for o in e["outputs"])
        print(f"  ✓ {e['original']} ({e['original_size']}, {gps})\n      → {sizes}")
        for w in e["warnings"]:
            print(f"      ⚠ {w}")
    if not args.dry_run:
        print(f"\nOutputs + manifest: {os.path.relpath(out_dir, ROOT)}/")
        if not args.keep_originals_in_inbox:
            print(f"Originals moved to: {os.path.relpath(orig_dir, ROOT)}/ (kept, not deleted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
