# client-uploads

Drop new client photos (JPG, PNG, HEIC from an iPhone, WebP) into **`inbox/`**, then ask Claude to run `/process-photos`.

- `inbox/`: put new photos here.
- `processed/<batch>/`: cleaned web versions plus `manifest.json` (alt text, tags, placement).
- `originals/<batch>/`: your untouched originals, moved here after processing (never deleted).

This whole folder is **git-ignored and never deployed**. The GitHub repo is public, so raw photos (which can contain GPS locations, faces or addresses) must never be committed. Only approved, metadata-free versions are copied into `assets/images/photos/`.
