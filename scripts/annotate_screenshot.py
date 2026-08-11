#!/usr/bin/env python3
"""Draw numbered annotation badges onto screenshots.

Reads a JSON specification, loads each source screenshot, draws highlight
boxes and numbered badges on it, and writes the annotated copy. Keeping the
annotations in a committed spec file means a figure can be regenerated after
the underlying page changes, instead of being re-drawn by hand.

The spec is a JSON object with a ``figures`` list. Paths are resolved relative
to the directory containing the spec file::

    {
      "figures": [
        {
          "source": "hei-about-raw.png",
          "output": "hei-about-annotated.png",
          "marks": [
            {"n": 1, "box": [24, 96, 620, 280]},
            {"n": 2, "x": 700, "y": 420}
          ]
        }
      ]
    }

Each mark draws a badge with the number ``n``. ``box`` is ``[x, y, width,
height]`` in pixels and is optional; when given without explicit ``x``/``y``,
the badge is placed on the box's top-left corner.

A figure may also carry ``"crop": [left, top, right, bottom]``, applied before
anything is drawn. Marks are then authored against the cropped frame. Cropping
matters because the site caps figure height, so a tall capture is scaled down
until its annotations stop being readable.

Any other key is ignored, which leaves room for provenance. The specs in this
repository carry a ``"capture"`` string recording the
``npm run screenshot:clean`` invocation that produced ``source``, so a figure
can be rebuilt end to end from the committed spec alone.

Usage::

    uv run python scripts/annotate_screenshot.py posts/<entry>/images/annotations.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

# NAIF brand accent (see _brand.yml), with white numerals for contrast.
ACCENT = (31, 58, 95, 255)
BADGE_TEXT = (255, 255, 255, 255)
BADGE_OUTLINE = (255, 255, 255, 255)

# Marks are authored in the source image's own pixels. Only the badge and
# stroke sizes adapt, so annotations stay legible on narrow captures too.
BADGE_DIVISOR = 76
MIN_BADGE_RADIUS = 16
BOX_WIDTH = 3

FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


def load_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Return a bold font at ``size``, falling back to Pillow's default."""
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # pragma: no cover - very old Pillow
        return ImageFont.load_default()


def draw_mark(
    draw: ImageDraw.ImageDraw,
    mark: dict[str, Any],
    radius: int,
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont,
) -> None:
    """Draw one highlight box and its numbered badge."""
    box = mark.get("box")

    if box is not None:
        left, top, width, height = box
        draw.rectangle(
            (left, top, left + width, top + height),
            outline=ACCENT,
            width=BOX_WIDTH,
        )
        default_x, default_y = left, top
    else:
        default_x, default_y = radius, radius

    centre_x = mark.get("x", default_x)
    centre_y = mark.get("y", default_y)

    draw.ellipse(
        (centre_x - radius, centre_y - radius, centre_x + radius, centre_y + radius),
        fill=ACCENT,
        outline=BADGE_OUTLINE,
        width=BOX_WIDTH,
    )

    label = str(mark["n"])
    text_left, text_top, text_right, text_bottom = draw.textbbox(
        (0, 0), label, font=font
    )
    draw.text(
        (
            centre_x - (text_right + text_left) / 2,
            centre_y - (text_bottom + text_top) / 2,
        ),
        label,
        font=font,
        fill=BADGE_TEXT,
    )


def annotate_figure(figure: dict[str, Any], base_dir: Path) -> Path:
    """Render one annotated figure and return the written path."""
    source_path = base_dir / figure["source"]
    output_path = base_dir / figure["output"]

    if not source_path.exists():
        raise FileNotFoundError(f"Source screenshot not found: {source_path}")

    image = Image.open(source_path).convert("RGBA")

    # Crop first: marks are authored against the cropped frame, and the site caps
    # figure height, so trimming dead space is what keeps a figure readable.
    crop = figure.get("crop")
    if crop is not None:
        image = image.crop(tuple(crop))

    radius = max(MIN_BADGE_RADIUS, round(image.width / BADGE_DIVISOR))
    font = load_font(round(radius * 1.15))
    draw = ImageDraw.Draw(image)

    for mark in figure.get("marks", []):
        draw_mark(draw, mark, radius, font)

    image.convert("RGB").save(output_path, format="PNG", optimize=True)
    return output_path


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Draw numbered annotation badges onto screenshots.",
    )
    parser.add_argument(
        "spec", type=Path, help="Path to the annotation spec JSON file."
    )
    args = parser.parse_args()

    spec_path: Path = args.spec
    if not spec_path.exists():
        print(f"Error: {spec_path} not found.", file=sys.stderr)
        sys.exit(1)

    with spec_path.open(encoding="utf-8") as handle:
        spec = json.load(handle)

    figures = spec.get("figures", [])
    if not figures:
        print(f"Error: {spec_path} contains no figures.", file=sys.stderr)
        sys.exit(1)

    base_dir = spec_path.resolve().parent
    for figure in figures:
        written = annotate_figure(figure, base_dir)
        print(f"Wrote {written.relative_to(Path.cwd())}", file=sys.stderr)


if __name__ == "__main__":
    main()
