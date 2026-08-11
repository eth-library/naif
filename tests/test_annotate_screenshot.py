"""Tests for scripts/annotate_screenshot.py."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageFont

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

annotate_screenshot = importlib.import_module("annotate_screenshot")

annotate_figure = annotate_screenshot.annotate_figure
load_font = annotate_screenshot.load_font


def _make_source(path: Path, size: tuple[int, int] = (200, 120)) -> None:
    """Write a tiny synthetic PNG at ``path`` for use as a test fixture."""
    Image.new("RGB", size, color=(120, 140, 160)).save(path, format="PNG")


# ---------------------------------------------------------------------------
# load_font
# ---------------------------------------------------------------------------


def test_load_font_returns_usable_font() -> None:
    font = load_font(24)
    assert isinstance(font, (ImageFont.ImageFont, ImageFont.FreeTypeFont))
    # A usable font can measure text without raising.
    bbox = font.getbbox("1")
    assert bbox[2] > bbox[0]
    assert bbox[3] > bbox[1]


# ---------------------------------------------------------------------------
# annotate_figure
# ---------------------------------------------------------------------------


def test_annotate_figure_writes_output_of_source_size(tmp_path: Path) -> None:
    _make_source(tmp_path / "raw.png", size=(200, 120))
    figure = {
        "source": "raw.png",
        "output": "annotated.png",
        "marks": [{"n": 1, "x": 50, "y": 50}],
    }

    written = annotate_figure(figure, tmp_path)

    assert written == tmp_path / "annotated.png"
    with Image.open(written) as result:
        assert result.size == (200, 120)
        # Size alone would pass even if nothing were drawn, so check the badge
        # actually landed by looking for the brand accent in the output.
        counts = result.convert("RGB").getcolors(1 << 16)
        assert counts is not None
        assert annotate_screenshot.ACCENT[:3] in {colour for _, colour in counts}


def test_annotate_figure_crop_sets_output_dimensions(tmp_path: Path) -> None:
    _make_source(tmp_path / "raw.png", size=(200, 120))
    figure = {
        "source": "raw.png",
        "output": "annotated.png",
        "crop": [10, 10, 110, 90],
        "marks": [{"n": 1, "box": [5, 5, 20, 20]}],
    }

    written = annotate_figure(figure, tmp_path)

    with Image.open(written) as result:
        assert result.size == (100, 80)


def test_annotate_figure_is_deterministic(tmp_path: Path) -> None:
    _make_source(tmp_path / "raw.png", size=(200, 120))
    figure = {
        "source": "raw.png",
        "output": "annotated.png",
        "marks": [{"n": 1, "box": [24, 30, 60, 40]}, {"n": 2, "x": 150, "y": 90}],
    }

    first = annotate_figure(figure, tmp_path)
    first_bytes = first.read_bytes()

    second_dir = tmp_path / "second"
    second_dir.mkdir()
    _make_source(second_dir / "raw.png", size=(200, 120))
    second = annotate_figure(figure, second_dir)
    second_bytes = second.read_bytes()

    assert first_bytes == second_bytes


def test_annotate_figure_missing_source_raises(tmp_path: Path) -> None:
    figure = {"source": "missing.png", "output": "annotated.png"}

    with pytest.raises(FileNotFoundError):
        annotate_figure(figure, tmp_path)
