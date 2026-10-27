"""Execução da interface com o testador do Streamlit — parte automática do TEST-030.

Confere que a página abre sem exceção e que as situações sem dados (REQ-010)
mostram mensagens em vez de erros. A conferência visual continua manual.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _run(**changes) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    for label, value in changes.items():
        widget = next(w for w in [*at.multiselect, *at.date_input] if w.label == label)
        widget.set_value(value)
    if changes:
        at.run()
    assert not at.exception, at.exception
    return at


def _html(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


def test_030_page_loads_with_reference_values():
    at = _run()
    html = _html(at)
    for expected in ("US$ 4.763,00", "US$ 10.389,25", "54,2%", "Ana Santos", "Limitações"):
        assert expected in html
    assert len(at.dataframe) == 1


def test_030_supplier_without_products_shows_empty_state():
    at = _run(Fornecedor=["RootWorks Supply"])
    html = _html(at)
    assert "Nenhum produto atende aos filtros selecionados." in html
    assert "US$ 0,00" in html and "—" in html
    assert len(at.dataframe) == 0


def test_030_period_without_orders_shows_message():
    at = _run(**{"Período de vendas": (date(2023, 1, 1), date(2023, 1, 31))})
    html = _html(at)
    assert "Não há vendas efetivas no período selecionado." in html
    assert "US$ 4.763,00" in html  # o estoque não muda com o período (RN-002)
