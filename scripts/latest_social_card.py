"""Make the site-level social card from the most recent post's front image.

Quarto runs this as a pre-render step after render_figures.py. The front image
is the post's `image` front matter if set, else its first Neuroglancer figure.
It is center-cropped to the 1200x630 card size and written to
figures/social-card.png. With no usable image, the static assets/social-card.png
is copied instead so the card URL always resolves.
"""

from __future__ import annotations

import io
import json
import shutil
import sys
from pathlib import Path

import yaml
from PIL import Image

from render_figures import FIGURES_DIR, MANIFEST, POSTS_DIR, ROOT, figure_urls, load_hosts

OUT = FIGURES_DIR / "social-card.png"
FALLBACK = ROOT / "assets" / "social-card.png"
W, H = 1200, 630


def log(msg: str) -> None:
    print(f"[latest_social_card] {msg}", file=sys.stderr)


def front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm) or {}


def front_image(qmd: Path, text: str, hosts: set[str], manifest: dict) -> Path | None:
    image = front_matter(text).get("image")
    if image:
        path = qmd.parent / str(image)
        return path if path.exists() else None
    rendered = [u for u in figure_urls(text, hosts) if u in manifest]
    if not rendered:
        return None
    first = min(rendered, key=text.find)
    return ROOT / manifest[first]["path"]


def crop_to_card(src: Path) -> Image.Image:
    img = Image.open(src).convert("RGB")
    target = W / H
    w, h = img.size
    if w / h > target:
        new_w = round(h * target)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = round(w / target)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img.resize((W, H), Image.LANCZOS)


def main() -> int:
    hosts = load_hosts()
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}

    posts = []
    for qmd in POSTS_DIR.rglob("index.qmd"):
        text = qmd.read_text()
        date = front_matter(text).get("date")
        if date:
            posts.append((str(date), qmd, text))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for _, qmd, text in sorted(posts, reverse=True):
        src = front_image(qmd, text, hosts, manifest)
        if src is None:
            continue
        buf = io.BytesIO()
        crop_to_card(src).save(buf, "PNG")
        # NOTE: skip unchanged writes so quarto preview does not loop on re-renders.
        if not (OUT.exists() and OUT.read_bytes() == buf.getvalue()):
            OUT.write_bytes(buf.getvalue())
        log(f"card from {qmd.relative_to(ROOT)} ({src.name})")
        return 0

    if not (OUT.exists() and OUT.read_bytes() == FALLBACK.read_bytes()):
        shutil.copyfile(FALLBACK, OUT)
    log("no post image found; using assets/social-card.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
