"""Generate the fallback site-level social card image.

The site card normally comes from the most recent post's front image
(scripts/latest_social_card.py); this card is used only when no post has one.
Run it once and commit the output; it is not part of the Quarto build.

    uv run python scripts/make_social_card.py

Output: assets/social-card.png at 1200x630 (the standard card size). The look
follows the site theme (theme.scss): the indigo ground, the accent color, the
Gabarito display face for the title, and the Neuroglancer-style crosshair motif
from the link badge (ngbadge.lua).
"""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "social-card.png"

# Theme colors, from theme.scss.
GROUND = "#e4e7f7"
ACCENT = "#5c6bc0"
ACCENT_DEEP = "#3f4d9e"
INK = "#1a1a1a"
INK_SOFT = "#4a4f6e"
PAPER = "#ffffff"

W, H = 1200, 630
MARGIN = 84

TITLE = "Notes from the Neuropil"
SUBTITLE = (
    "Readers send us weird finds from Neuroglancer. Scientists who work "
    "in that data write back and explain what they are."
)

# The site display face; a system face is the fallback if the download fails.
GABARITO_URL = (
    "https://github.com/google/fonts/raw/main/ofl/gabarito/Gabarito%5Bwght%5D.ttf"
)
FALLBACK_FONTS = [
    "/System/Library/Fonts/Avenir Next.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial.ttf",
]


def load_display_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Gabarito if reachable, else the first available system face."""
    try:
        with urllib.request.urlopen(GABARITO_URL, timeout=15) as resp:
            data = resp.read()
        return ImageFont.truetype(io.BytesIO(data), size)
    except Exception as exc:  # noqa: BLE001
        print(f"[make_social_card] Gabarito download failed ({exc}); using a system font")
    for path in FALLBACK_FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def crosshair(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, color: str) -> None:
    """The Neuroglancer link-badge motif: a square with a quadrant filled."""
    draw.rectangle([x, y, x + size, y + size], outline=color, width=5)
    draw.line([x + size // 2, y, x + size // 2, y + size], fill=color, width=5)
    draw.line([x, y + size // 2, x + size, y + size // 2], fill=color, width=5)
    draw.rectangle(
        [x, y + size // 2, x + size // 2, y + size], fill=color
    )


def main() -> int:
    img = Image.new("RGB", (W, H), GROUND)
    draw = ImageDraw.Draw(img)

    # A paper sheet inset, echoing the post .sheet in the theme.
    draw.rectangle([MARGIN, MARGIN, W - MARGIN, H - MARGIN], fill=PAPER, outline=INK, width=3)

    pad = MARGIN + 56
    inner_w = (W - MARGIN) - pad - 56

    # Badge motif, top-left of the sheet.
    crosshair(draw, pad, pad, 72, ACCENT)

    title_font = load_display_font(74)
    sub_font = load_display_font(34)

    y = pad + 120
    for line in wrap(draw, TITLE, title_font, inner_w):
        draw.text((pad, y), line, font=title_font, fill=INK)
        y += 84

    y += 24
    for line in wrap(draw, SUBTITLE, sub_font, inner_w):
        draw.text((pad, y), line, font=sub_font, fill=INK_SOFT)
        y += 46

    # Accent rule near the bottom of the sheet.
    rule_y = H - MARGIN - 64
    draw.rectangle([pad, rule_y, pad + 220, rule_y + 8], fill=ACCENT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"[make_social_card] wrote {OUT.relative_to(ROOT)} ({W}x{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
