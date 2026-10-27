"""Testes das regras de cálculo — REQ-002 a REQ-006, REQ-009 e REQ-010.

SPEC, seção 13.2: TEST-010 a TEST-018, TEST-020 e TEST-021.
Escritos antes de metrics.py, a partir dos valores calculados à mão na seção 13.1.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from conftest import FULL_END, FULL_START

from garden_shop import config
from garden_shop.metrics import (
    abc_classes,
    build_product_view,
    compute_kpis,
    default_period,
    purchase_table,
    stock_status,
)


def _row(view: pd.DataFrame, product_id: int) -> pd.Series:
    return view.set_index("product_id").loc[product_id]


@pytest.fixture
def sample_view(sample_data):
    return build_product_view(sample_data, FULL_START, FULL_END)


@pytest.fixture
def full_view(full_data):
    return build_product_view(full_data, FULL_START, FULL_END)


# --- Período padrão ---------------------------------------------------------

def test_default_period_is_min_to_max_order_date(full_data):
    assert default_period(full_data.orders) == (FULL_START, FULL_END)


# --- TEST-010 / TEST-011: vendas efetivas (REQ-002, RN-001) -----------------

def test_010_cancelled_order_is_excluded(sample_view):
    shears = _row(sample_view, 9)
    assert shears["qty_sold"] == 1
    assert shears["revenue"] == pytest.approx(22.00)


def test_011_pending_and_processing_count_as_sales(full_data):
    view = build_product_view(full_data, date(2024, 5, 1), date(2024, 5, 1))
    # Pedido 7 (pending, 2024-05-01): 1 Pruning Shears e 2 Hand Cultivator
    assert _row(view, 9)["qty_sold"] == 1
    assert _row(view, 11)["qty_sold"] == 2
    # Pedido 4 (processing, 2024-04-07): 5 Sunflower Seeds e 2 Tulip Bulbs
    view = build_product_view(full_data, date(2024, 4, 7), date(2024, 4, 7))
    assert _row(view, 6)["qty_sold"] == 5
    assert _row(view, 8)["qty_sold"] == 2


def test_010_sample_sales_of_product_1(sample_view):
    fig = _row(sample_view, 1)
    assert fig["qty_sold"] == 5
    assert fig["revenue"] == pytest.approx(160.00)


def test_010_full_base_effective_sales_totals(full_view):
    # 47 itens efetivos, 86 unidades, US$ 1.107,00
    assert full_view["qty_sold"].sum() == 86
    assert full_view["revenue"].sum() == pytest.approx(1107.00)


# --- TEST-012: filtro de período × estoque atual (REQ-002, RN-002) ----------

def test_012_period_changes_sales_but_not_stock(sample_data, sample_view):
    view = build_product_view(sample_data, date(2024, 3, 1), date(2024, 6, 30))
    fig = _row(view, 1)
    assert fig["qty_sold"] == 3
    assert fig["period_days"] == 122
    assert fig["quantity_on_hand"] == 14
    assert compute_kpis(view) == compute_kpis(sample_view)


def test_012_period_days_is_inclusive(sample_view):
    assert (sample_view["period_days"] == 152).all()


# --- TEST-013: status de estoque (REQ-003) ----------------------------------

def test_013_sample_statuses(sample_view):
    statuses = sample_view.set_index("product_id")["status"].to_dict()
    assert statuses == {
        1: config.STATUS_HEALTHY,
        9: config.STATUS_HEALTHY,
        14: config.STATUS_STOCKOUT,
        24: config.STATUS_DISCONTINUED,
    }


@pytest.mark.parametrize(
    ("qoh", "expected"),
    [
        (0, config.STATUS_STOCKOUT),
        (8, config.STATUS_URGENT),
        (10, config.STATUS_ALERT),
        (11, config.STATUS_HEALTHY),
    ],
)
def test_013_status_boundaries(qoh, expected):
    df = pd.DataFrame({"quantity_on_hand": [qoh], "reorder_level": [8], "discontinued": [False]})
    assert stock_status(df).iloc[0] == expected


def test_013_discontinued_takes_precedence():
    df = pd.DataFrame({"quantity_on_hand": [0], "reorder_level": [8], "discontinued": [True]})
    assert stock_status(df).iloc[0] == config.STATUS_DISCONTINUED


def test_013_full_base_status_counts(full_view):
    counts = full_view["status"].value_counts().to_dict()
    assert counts == {
        config.STATUS_HEALTHY: 17,
        config.STATUS_URGENT: 4,
        config.STATUS_STOCKOUT: 1,
        config.STATUS_ALERT: 1,
        config.STATUS_DISCONTINUED: 1,
    }
    by_status = full_view.groupby("status")["product_id"].apply(set).to_dict()
    assert by_status[config.STATUS_URGENT] == {4, 7, 11, 20}
    assert by_status[config.STATUS_STOCKOUT] == {14}
    assert by_status[config.STATUS_ALERT] == {22}


# --- TEST-014: cards do recorte (REQ-004) -----------------------------------

def test_014_sample_kpis(sample_view):
    k = compute_kpis(sample_view)
    assert k["stock_cost_value"] == pytest.approx(482.00)
    assert k["stock_sale_value"] == pytest.approx(912.00)
    assert round(k["gross_margin"], 3) == 0.471
    assert k["stockout_count"] == 1
    assert k["below_reorder_count"] == 1
    assert k["total_deficit"] == 10


# --- TEST-015: sem duplicação (RN-006) --------------------------------------

def test_015_one_row_per_product(sample_data, sample_view):
    assert len(sample_view) == 4
    assert sample_view["product_id"].is_unique
    assert sample_view["stock_cost_value"].sum() == pytest.approx(482.00)


def test_015_naive_join_would_duplicate(sample_data):
    """Documenta o erro evitado: a junção direta produtos × itens dá 1.404,00."""
    naive = sample_data.products.merge(sample_data.order_items, on="product_id")
    assert (naive["quantity_on_hand"] * naive["cost"]).sum() == pytest.approx(1404.00)


def test_015_full_base_one_row_per_product(full_data, full_view):
    assert len(full_view) == len(full_data.products) == 24
    assert full_view["product_id"].is_unique


# --- TEST-016: cobertura (REQ-005) ------------------------------------------

def test_016_coverage(sample_view):
    assert round(_row(sample_view, 1)["coverage_days"], 1) == 425.6
    assert round(_row(sample_view, 9)["coverage_days"], 1) == 2736.0
    assert _row(sample_view, 14)["coverage_days"] == 0
    assert pd.isna(_row(sample_view, 24)["coverage_days"])


def test_016_avg_daily_sales(sample_view):
    assert _row(sample_view, 1)["avg_daily_sales"] == pytest.approx(5 / 152)
    assert _row(sample_view, 24)["avg_daily_sales"] == 0


# --- TEST-017: curva ABC (REQ-006) ------------------------------------------

def test_017_sample_abc(sample_view):
    classes = sample_view.set_index("product_id")["abc_class"].to_dict()
    assert classes == {1: "A", 9: "B", 14: config.ABC_NO_SALES, 24: config.ABC_NO_SALES}


def test_017_full_base_abc(full_view):
    by_class = full_view.groupby("abc_class")["product_id"].apply(set).to_dict()
    assert len(by_class["A"]) == 13
    assert by_class["B"] == {16, 17, 21, 9, 10}
    assert by_class["C"] == {20, 11, 7, 23}
    assert by_class[config.ABC_NO_SALES] == {14, 24}


def test_017_product_crossing_80_percent_is_a(full_view):
    assert _row(full_view, 8)["abc_class"] == "A"


def test_017_single_product_is_a():
    revenue = pd.Series({1: 100.0, 2: 0.0, 3: 0.0})
    assert abc_classes(revenue).to_dict() == {1: "A", 2: config.ABC_NO_SALES, 3: config.ABC_NO_SALES}


def test_017_ties_break_by_product_id():
    revenue = pd.Series({2: 10.0, 1: 10.0})
    # Empate: o produto 1 vem antes (prev 0% → A); o 2 tem prev 50% → A
    assert abc_classes(revenue).to_dict() == {1: "A", 2: "A"}


# --- TEST-018: recomendação de compra (REQ-009, RN-004, RN-005) -------------

def test_018_sample_recommendation(sample_view):
    suggestion = sample_view.set_index("product_id")["purchase_suggestion"].to_dict()
    assert suggestion == {1: 0, 9: 0, 14: 10, 24: 0}


def test_018_full_purchase_table(full_view):
    table = purchase_table(full_view, only_recommended=True)
    assert list(table["Produto"]) == [
        "Hanging Basket",
        "Pothos 'Golden'",
        "Tomato Seeds 'Roma'",
        "Hand Cultivator",
        "Orchid Food",
    ]
    assert list(table["Déficit mínimo (sugestão de compra)"]) == [10, 4, 35, 7, 4]
    assert list(table["Curva ABC"]) == [config.ABC_NO_SALES, "A", "C", "C", "C"]
    assert table.loc[table["Produto"] == "Hand Cultivator", "E-mail do fornecedor"].item() == config.MISSING_EMAIL
    assert "Bird Feeder" not in set(table["Produto"])


def test_018_full_table_keeps_all_products_and_columns(full_view):
    table = purchase_table(full_view)
    assert len(table) == 24
    assert list(table.columns) == [
        "Produto",
        "Categoria",
        "Fornecedor",
        "E-mail do fornecedor",
        "Estoque atual",
        "Nível de reposição",
        "Déficit mínimo (sugestão de compra)",
        "Venda média diária",
        "Dias de cobertura",
        "Curva ABC",
        "Status",
    ]
    bird = table.loc[table["Produto"] == "Bird Feeder"].iloc[0]
    assert bird["Déficit mínimo (sugestão de compra)"] == 0
    assert table.iloc[-1]["Status"] == config.STATUS_DISCONTINUED


def test_018_reorder_equal_to_stock_has_zero_suggestion(full_view):
    view = full_view.copy()
    view.loc[view["product_id"] == 1, ["quantity_on_hand", "reorder_level"]] = [10, 10]
    from garden_shop.metrics import add_stock_rules

    row = _row(add_stock_rules(view), 1)
    assert row["status"] == config.STATUS_URGENT
    assert row["purchase_suggestion"] == 0


# --- TEST-020: período sem pedidos (REQ-010) --------------------------------

def test_020_period_without_orders(full_data):
    view = build_product_view(full_data, date(2023, 1, 1), date(2023, 1, 31))
    assert (view["qty_sold"] == 0).all()
    assert (view["abc_class"] == config.ABC_NO_SALES).all()
    zero_stock = view["quantity_on_hand"] == 0
    assert (view.loc[zero_stock, "coverage_days"] == 0).all()
    assert view.loc[~zero_stock, "coverage_days"].isna().all()
    assert compute_kpis(view)["stock_cost_value"] == pytest.approx(4763.00)


# --- TEST-021: valores de referência da base completa (REQ-004) -------------

def test_021_full_base_kpis(full_view):
    k = compute_kpis(full_view)
    assert k["stock_cost_value"] == pytest.approx(4763.00)
    assert k["stock_sale_value"] == pytest.approx(10389.25)
    assert round(k["gross_margin"], 3) == 0.542
    assert k["stockout_count"] == 1
    assert k["below_reorder_count"] == 5
    assert k["total_deficit"] == 60


def test_021_labels_for_missing_dimensions(data_copy):
    path = data_copy / "products.csv"
    path.write_text(path.read_text(encoding="utf-8").replace("Bird Feeder,8,5,", "Bird Feeder,99,77,"), encoding="utf-8")
    from garden_shop.loader import load_data

    view = build_product_view(load_data(data_copy), FULL_START, FULL_END)
    bird = _row(view, 24)
    assert bird["category_name"] == config.MISSING_CATEGORY
    assert bird["supplier_name"] == config.MISSING_SUPPLIER
    assert len(view) == 24
