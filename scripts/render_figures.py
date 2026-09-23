"""Render Neuroglancer figures for the site build (TASK-7).

Quarto runs this as a pre-render step. It scans posts for Neuroglancer links that
should become figures, renders each one to a content-addressed PNG in figures/
with ngsnap, and writes figures/manifest.json so ngbadge.lua knows the image path.

Figure vs badge rule (kept in sync with ngbadge.lua):
  - A Neuroglancer link alone in its own paragraph becomes a figure.
  - A link inside prose stays a badge (not rendered here).
  - Overrides on a markdown link: {.ng-figure} forces a figure even inline;
    {.ng-badge-only} forces a badge even when alone in a paragraph.

Caching: the filename is ngsnap's cache_key(url, spec), so an unchanged link and
style are not re-rendered. Cross-CI-run caching and the failure policy are TASK-8.

Local builds without a working browser get a placeholder image and a warning
instead of a hard failure (see README for enabling real local renders).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
FIGURES_DIR = ROOT / "figures"
STYLE_FILE = ROOT / "ngsnap-style.toml"
CONFIG_FILE = ROOT / "_quarto.yml"
MANIFEST = FIGURES_DIR / "manifest.json"

VIEWER_SIZE = (1600, 1200)  # 4:3, matches the house style config.


def log(msg: str) -> None:
    print(f"[render_figures] {msg}", file=sys.stderr)


def load_hosts() -> set[str]:
    """Read the one Neuroglancer host list from project metadata."""
    data = yaml.safe_load(CONFIG_FILE.read_text()) or {}
    hosts = (data.get("neuroglancer") or {}).get("hosts") or []
    return {str(h).strip().lower() for h in hosts if str(h).strip()}


def url_host(url: str) -> str | None:
    """Authority between '://' and the first / ? or #.

    Ignores '#!' encoded state and '#!middleauth+https://' fragments.
    """
    m = re.match(r"^[a-z][a-z0-9+.\-]*://([^/?#]+)", url, re.IGNORECASE)
    if not m:
        return None
    host = m.group(1)
    host = re.sub(r"^[^@]*@", "", host)
    host = re.sub(r":\d+$", "", host)
    return host.lower()


# One Neuroglancer link: a markdown link [text](url){attrs} or a bare URL{attrs}.
MD_LINK = re.compile(r"\[[^\]]*\]\((?P<url>\S+?)\)(?:\{(?P<attrs>[^}]*)\})?")
BARE_URL = re.compile(r"(?P<url>https?://\S+?)(?:\{(?P<attrs>[^}]*)\})?$")


def strip_code_fences(text: str) -> str:
    return re.sub(r"(?ms)^```.*?^```\s*$", "", text)


def has_class(attrs: str | None, cls: str) -> bool:
    if not attrs:
        return False
    return f".{cls}" in attrs.split()


def figure_urls(text: str, hosts: set[str]) -> set[str]:
    """Return the Neuroglancer URLs in one document that should become figures."""
    body = strip_code_fences(text)
    found: set[str] = set()

    def is_ng(url: str) -> bool:
        h = url_host(url)
        return h is not None and h in hosts

    # 1) Paragraph-sole links become figures unless marked .ng-badge-only.
    for para in re.split(r"\n\s*\n", body):
        block = para.strip()
        if not block:
            continue
        m = MD_LINK.fullmatch(block) or BARE_URL.fullmatch(block)
        if m and is_ng(m.group("url")) and not has_class(m.groupdict().get("attrs"), "ng-badge-only"):
            found.add(m.group("url"))

    # 2) Any link explicitly marked .ng-figure becomes a figure, even inline.
    for m in MD_LINK.finditer(body):
        if is_ng(m.group("url")) and has_class(m.group("attrs"), "ng-figure"):
            found.add(m.group("url"))

    return found


def make_placeholder(out_path: Path, reason: str) -> None:
    """Write a neutral placeholder PNG so a local build without a browser works."""
    from PIL import Image, ImageDraw

    w, h = 800, 600
    img = Image.new("RGB", (w, h), "#e4e7f7")
    draw = ImageDraw.Draw(img)
    draw.rectangle([1, 1, w - 2, h - 2], outline="#5c6bc0", width=3)
    draw.text((24, 24), "Neuroglancer figure placeholder", fill="#1a1a1a")
    draw.text((24, 48), reason, fill="#4a4f6e")
    img.save(out_path, "PNG")


def main() -> int:
    hosts = load_hosts()
    if not hosts:
        log("no neuroglancer.hosts configured; nothing to render")

    # Collect the figure URLs across all posts.
    urls: set[str] = set()
    for qmd in sorted(POSTS_DIR.rglob("*.qmd")):
        urls |= figure_urls(qmd.read_text(), hosts)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load the house style. If ngsnap or the style file is unavailable, every
    # figure falls back to a placeholder rather than failing the build.
    # Set NFTN_NO_RENDER=1 to force placeholders (fast local builds, no browser).
    spec = None
    cache_key = None
    if os.getenv("NFTN_NO_RENDER"):
        log("NFTN_NO_RENDER set; using placeholders")
    else:
        try:
            from ngsnap import Spec, cache_key as _cache_key

            spec = Spec.from_file(STYLE_FILE)
            cache_key = _cache_key
        except Exception as exc:  # noqa: BLE001
            log(f"ngsnap unavailable ({exc}); using placeholders")

    # Precompute keys and paths.
    entries: dict[str, dict[str, object]] = {}
    for url in sorted(urls):
        key = cache_key(url, spec) if cache_key else re.sub(r"[^A-Za-z0-9]", "", url)[-40:]
        safe_key = re.sub(r"[^A-Za-z0-9._-]", "_", str(key))
        entries[url] = {"key": safe_key, "path": f"figures/{safe_key}.png"}

    # Which images still need rendering (skip-if-exists = local cache).
    to_render = {
        url: e for url, e in entries.items() if not (ROOT / str(e["path"])).exists()
    }
    log(f"{len(urls)} figure link(s); {len(to_render)} to render, "
        f"{len(urls) - len(to_render)} cached")

    session = None
    if to_render and spec is not None:
        try:
            from ngsnap import RenderSession

            session = RenderSession(timeout=90)
            session.__enter__()
        except Exception as exc:  # noqa: BLE001
            log(f"could not start a browser ({exc}); using placeholders")
            session = None

    for url, e in to_render.items():
        out = ROOT / str(e["path"])
        if session is not None:
            try:
                session.render(url, out, spec=spec)
                e["ok"] = True
                log(f"rendered {e['key']}.png")
                continue
            except Exception as exc:  # noqa: BLE001
                log(f"render failed for {url[:60]}... ({exc}); using placeholder")
        make_placeholder(out, "Run 'uv sync' and a browser to render this locally.")
        e["ok"] = False

    if session is not None:
        session.__exit__(None, None, None)

    # Entries already on disk from a previous build are considered ok.
    for url, e in entries.items():
        e.setdefault("ok", (ROOT / str(e["path"])).exists())

    MANIFEST.write_text(json.dumps(entries, indent=2, sort_keys=True))
    log(f"wrote {MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
