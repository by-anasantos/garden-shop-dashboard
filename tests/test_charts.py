"""Testes da regra do quadrante e das figuras — REQ-008 (TEST-022)."""

from __future__ import annotations

import pandas as pd
import pytest
from conftest import FULL_END, FULL_START

from garden_shop import config
from garden_shop.charts import (
    priority_flags,
    scatter_priority,
    stacked_status_bars,
    stock_value_treemap,
)
from garden_shop.metrics import build_product_view, compute_kpis


# --- TEST-022: regra do quadrante (exemplo da SPEC) -------------------------

def test_022_quadrant_rule_example():
    df = pd.DataFrame(
        {
            "product_name": ["X", "Y", "Z"],
            "qty_sold": [10, 2, 6],
            "coverage_days": [50.0, 500.0, 100.0],
        }
    )
    flags, median_x, median_y = priority_flags(df)
    assert median_x == 6
    assert median_y == 100
    assert flags.tolist() == [True, False, False]


@pytest.fixture
def full_view(full_data):
    return build_product_view(full_data, FULL_START, FULL_END)


def test_scatter_excludes_products_without_sales(full_view):
    fig, excluded = scatter_priority(full_view)
    plotted = sum(len(trace.x) for trace in fig.data)
    assert plotted == 22
    assert excluded == 2


def test_scatter_with_no_sales_returns_none(full_view):
    no_sales = full_view.assign(qty_sold=0)
    fig, excluded = scatter_priority(no_sales)
    assert fig is None
    assert excluded == len(full_view)


def test_bars_sum_equals_number_of_products(full_view):
    fig = stacked_status_bars(full_view)
    assert sum(sum(trace.x) for trace in fig.data) == len(full_view)
    assert [trace.name for trace in fig.data] == [s for s in config.STATUS_ORDER if s in set(full_view["status"])]


def test_treemap_total_equals_cost_card(full_view):
    fig = stock_value_treemap(full_view)
    trace = fig.data[0]
    leaves = [v for v, p in zip(trace.values, trace.parents) if p != ""]
    assert sum(leaves) == pytest.approx(compute_kpis(full_view)["stock_cost_value"])
