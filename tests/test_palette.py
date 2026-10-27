"""Paleta sem vermelho — REQ-012 (TEST-023).

Critério da SPEC: nenhuma cor com matiz entre 345° e 15° e saturação ≥ 40%.
Verifica a paleta de config.py e as cores do tema em .streamlit/config.toml.
"""

from __future__ import annotations

import colorsys
import re
from pathlib import Path

import pytest

from garden_shop import config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _is_red(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    hue, _lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    hue_deg = hue * 360
    return (hue_deg >= 345 or hue_deg <= 15) and saturation >= 0.40


def _palette() -> list[str]:
    colors = [
        config.COLOR_PRIMARY,
        config.COLOR_BACKGROUND,
        config.COLOR_TEXT,
        config.COLOR_MUTED,
        config.PRIORITY_POINT_COLOR,
        config.OTHER_POINT_COLOR,
        *config.STATUS_COLORS.values(),
    ]
    theme = (PROJECT_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    colors += re.findall(r"#[0-9A-Fa-f]{6}", theme)
    return colors


def test_detector_recognizes_red():
    assert _is_red("#FF0000")
    assert _is_red("#C0392B")
    assert not _is_red("#003d48")


@pytest.mark.parametrize("color", _palette())
def test_023_no_red_in_palette(color):
    assert not _is_red(color), f"{color} é vermelho"


def test_023_every_status_has_a_color():
    assert set(config.STATUS_COLORS) == set(config.STATUS_ORDER)
