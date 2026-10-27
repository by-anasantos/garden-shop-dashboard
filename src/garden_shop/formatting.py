"""Formatação dos valores exibidos (RNF-001): padrão brasileiro de milhar e decimal."""

from __future__ import annotations

import math

from garden_shop import config


def _br(value: float, decimals: int) -> str:
    """1234.5 → '1.234,50' (com `decimals` casas)."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_usd(value: float) -> str:
    return f"US$ {_br(value, 2)}"


def fmt_pct(value: float | None) -> str:
    return "—" if value is None else f"{_br(value * 100, 1)}%"


def fmt_int(value: int) -> str:
    return _br(value, 0)


def fmt_days(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return config.NO_TURNOVER
    if value == 0:
        return "0 dias"
    return f"{_br(value, 1)} dias"
