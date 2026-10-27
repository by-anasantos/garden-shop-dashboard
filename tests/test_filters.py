"""Testes dos filtros — REQ-007 e REQ-010 (SPEC, seção 13.2: TEST-019)."""

from __future__ import annotations

from conftest import FULL_END, FULL_START

from garden_shop import config
from garden_shop.filters import FilterSelection, apply_filters
from garden_shop.metrics import build_product_view, compute_kpis, purchase_table


def _view(full_data):
    return build_product_view(full_data, FULL_START, FULL_END)


def test_empty_selection_means_all(full_data):
    view = _view(full_data)
    assert len(apply_filters(view, FilterSelection())) == 24


def test_category_filter(full_data):
    out = apply_filters(_view(full_data), FilterSelection(categories=("Tools",)))
    assert set(out["product_id"]) == {9, 10, 11}


def test_filters_combine_with_and(full_data):
    sel = FilterSelection(categories=("Houseplants",), statuses=(config.STATUS_URGENT,))
    assert set(apply_filters(_view(full_data), sel)["product_id"]) == {4}


def test_abc_filter_uses_classes_from_full_catalog(full_data):
    """A ABC é calculada antes do filtro de dimensão: filtrar não reclassifica."""
    view = _view(full_data)
    tools = apply_filters(view, FilterSelection(categories=("Tools",)))
    assert tools.set_index("product_id")["abc_class"].to_dict() == {9: "B", 10: "B", 11: "C"}


# --- TEST-019: filtro sem resultados ---------------------------------------

def test_019_supplier_without_products_gives_empty_view(full_data):
    out = apply_filters(_view(full_data), FilterSelection(suppliers=("RootWorks Supply",)))
    assert out.empty
    k = compute_kpis(out)
    assert k["stock_cost_value"] == 0
    assert k["stock_sale_value"] == 0
    assert k["gross_margin"] is None
    assert k["stockout_count"] == 0
    assert k["below_reorder_count"] == 0
    assert k["total_deficit"] == 0
    assert purchase_table(out).empty


def test_filter_does_not_mutate_input(full_data):
    view = _view(full_data)
    before = view.copy()
    apply_filters(view, FilterSelection(categories=("Tools",)))
    assert view.equals(before)
