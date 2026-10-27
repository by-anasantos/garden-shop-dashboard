"""Formatação de valores na interface — RNF-001 (US$ com 2 casas, % com 1 casa)."""

from __future__ import annotations

import math

from garden_shop.formatting import fmt_days, fmt_int, fmt_pct, fmt_usd


def test_usd():
    assert fmt_usd(4763) == "US$ 4.763,00"
    assert fmt_usd(10389.25) == "US$ 10.389,25"
    assert fmt_usd(0) == "US$ 0,00"


def test_pct():
    assert fmt_pct(0.5415453) == "54,2%"
    assert fmt_pct(None) == "—"


def test_days():
    assert fmt_days(425.6315) == "425,6 dias"
    assert fmt_days(2736.0) == "2.736,0 dias"
    assert fmt_days(0) == "0 dias"
    assert fmt_days(math.nan) == "Sem giro"


def test_int():
    assert fmt_int(1234) == "1.234"
