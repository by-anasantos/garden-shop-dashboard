"""Regras de cálculo da Garden Shop — funções puras (SPEC, seções 6, 7.2 e 9).

Cobre REQ-002 (vendas efetivas), REQ-003 (status), REQ-004 (cards),
REQ-005 (cobertura), REQ-006 (curva ABC), REQ-009 (tabela de compras) e
REQ-010 (situações sem dados).

As funções assumem dados já validados pelo loader (AGENTS.md, seção 8).
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from garden_shop import config
from garden_shop.loader import GardenShopData


# --- Período ----------------------------------------------------------------

def default_period(orders: pd.DataFrame) -> tuple[date, date]:
    """Da menor à maior order_date (REQ-007)."""
    return orders["order_date"].min(), orders["order_date"].max()


def period_days(start: date, end: date) -> int:
    """Dias do período, contando o primeiro e o último (ADR-009)."""
    return (end - start).days + 1


# --- REQ-002: vendas efetivas por produto -----------------------------------

def effective_sales(data: GardenShopData, start: date, end: date) -> pd.DataFrame:
    """qty_sold e revenue por product_id, agregados ANTES de juntar com produtos (RN-006)."""
    orders = data.orders
    valid = orders["status"].isin(config.VALID_SALE_STATUSES)
    in_period = (orders["order_date"] >= start) & (orders["order_date"] <= end)
    valid_ids = orders.loc[valid & in_period, "order_id"]

    items = data.order_items[data.order_items["order_id"].isin(valid_ids)]
    sales = (
        items.assign(line_revenue=items["quantity"] * items["unit_price"])
        .groupby("product_id", as_index=False)
        .agg(qty_sold=("quantity", "sum"), revenue=("line_revenue", "sum"))
    )
    return sales


# --- REQ-003 / RN-004 / RN-005: regras de estoque ---------------------------

def stock_status(df: pd.DataFrame) -> pd.Series:
    """Um status por produto: a primeira condição verdadeira (REQ-003)."""
    qoh = df["quantity_on_hand"]
    reorder = df["reorder_level"]
    conditions = [
        df["discontinued"].astype(bool),
        qoh == 0,
        qoh <= reorder,
        qoh <= reorder * config.ALERT_FACTOR,
    ]
    choices = [
        config.STATUS_DISCONTINUED,
        config.STATUS_STOCKOUT,
        config.STATUS_URGENT,
        config.STATUS_ALERT,
    ]
    return pd.Series(np.select(conditions, choices, default=config.STATUS_HEALTHY), index=df.index)


def add_stock_rules(view: pd.DataFrame) -> pd.DataFrame:
    """Valores de estoque, déficit, status e sugestão de compra (REQ-003, REQ-004, REQ-009)."""
    out = view.copy()
    out["stock_cost_value"] = out["quantity_on_hand"] * out["cost"]
    out["stock_sale_value"] = out["quantity_on_hand"] * out["price"]
    out["stock_deficit"] = (out["reorder_level"] - out["quantity_on_hand"]).clip(lower=0).astype("int64")
    out["status"] = stock_status(out)
    out["purchase_suggestion"] = out["stock_deficit"].where(~out["discontinued"].astype(bool), 0).astype("int64")
    return out


# --- REQ-005: venda média e cobertura ---------------------------------------

def add_coverage(view: pd.DataFrame, days: int) -> pd.DataFrame:
    out = view.copy()
    out["period_days"] = days
    out["avg_daily_sales"] = out["qty_sold"] / days
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = out["quantity_on_hand"] / out["avg_daily_sales"]
    out["coverage_days"] = np.where(
        out["quantity_on_hand"] == 0,
        0.0,
        np.where(out["qty_sold"] == 0, np.nan, ratio),  # NaN = "Sem giro"
    )
    return out


# --- REQ-006: curva ABC -----------------------------------------------------

def abc_classes(revenue: pd.Series) -> pd.Series:
    """Classe ABC por product_id (índice), pela participação acumulada ANTERIOR (ADR-003)."""
    result = pd.Series(config.ABC_NO_SALES, index=revenue.index, dtype=object)
    sold = revenue[revenue > 0]
    total = sold.sum()
    if total == 0:
        return result

    ordered = (
        sold.rename("revenue")
        .rename_axis("product_id")
        .reset_index()
        .sort_values(["revenue", "product_id"], ascending=[False, True])
    )
    prev_share = (ordered["revenue"].cumsum() - ordered["revenue"]) / total
    classes = np.where(
        prev_share < config.ABC_A_LIMIT,
        "A",
        np.where(prev_share < config.ABC_B_LIMIT, "B", "C"),
    )
    result.loc[ordered["product_id"].to_numpy()] = classes
    return result


# --- Visão por produto (SPEC 7.2) -------------------------------------------

def build_product_view(data: GardenShopData, start: date, end: date) -> pd.DataFrame:
    """Uma linha por produto, para o período informado, ANTES dos filtros de dimensão."""
    products = data.products
    categories = data.categories[["category_id", "category_name"]]
    suppliers = data.suppliers[["supplier_id", "supplier_name", "contact_email"]]

    view = (
        products.merge(categories, on="category_id", how="left", validate="many_to_one")
        .merge(suppliers, on="supplier_id", how="left", validate="many_to_one")
        .merge(effective_sales(data, start, end), on="product_id", how="left", validate="one_to_one")
    )
    view["category_name"] = view["category_name"].fillna(config.MISSING_CATEGORY)
    view["supplier_name"] = view["supplier_name"].fillna(config.MISSING_SUPPLIER)
    view["qty_sold"] = view["qty_sold"].fillna(0).astype("int64")
    view["revenue"] = view["revenue"].fillna(0.0)

    view = add_stock_rules(view)
    view = add_coverage(view, period_days(start, end))
    view["abc_class"] = abc_classes(view.set_index("product_id")["revenue"]).to_numpy()

    assert len(view) == len(products), "a visão deve ter uma linha por produto (RN-006)"
    return view.reset_index(drop=True)


# --- REQ-004: cards ---------------------------------------------------------

def compute_kpis(view: pd.DataFrame) -> dict[str, float | int | None]:
    """Os seis cards sobre a visão filtrada. Margem = None se não houver valor de venda."""
    active = view[~view["discontinued"].astype(bool)]
    cost_value = float(view["stock_cost_value"].sum())
    sale_value = float(view["stock_sale_value"].sum())
    return {
        "stock_cost_value": cost_value,
        "stock_sale_value": sale_value,
        "gross_margin": (sale_value - cost_value) / sale_value if sale_value > 0 else None,
        "stockout_count": int((active["quantity_on_hand"] == 0).sum()),
        "below_reorder_count": int((active["quantity_on_hand"] <= active["reorder_level"]).sum()),
        "total_deficit": int(active["stock_deficit"].sum()),
    }


# --- REQ-009: tabela de compras ---------------------------------------------

PURCHASE_COLUMNS = {
    "product_name": "Produto",
    "category_name": "Categoria",
    "supplier_name": "Fornecedor",
    "contact_email": "E-mail do fornecedor",
    "quantity_on_hand": "Estoque atual",
    "reorder_level": "Nível de reposição",
    "purchase_suggestion": "Déficit mínimo (sugestão de compra)",
    "avg_daily_sales": "Venda média diária",
    "coverage_days": "Dias de cobertura",
    "abc_class": "Curva ABC",
    "status": "Status",
}


def purchase_table(view: pd.DataFrame, only_recommended: bool = False) -> pd.DataFrame:
    """Tabela de compras ordenada por status, ABC, déficit (desc.) e nome."""
    table = view.copy()
    if only_recommended:
        table = table[table["purchase_suggestion"] > 0]

    table["contact_email"] = table["contact_email"].fillna(config.MISSING_EMAIL)
    table["_status_rank"] = table["status"].map({s: i for i, s in enumerate(config.STATUS_ORDER)})
    table["_abc_rank"] = table["abc_class"].map({c: i for i, c in enumerate(config.ABC_ORDER)})
    table = table.sort_values(
        ["_status_rank", "_abc_rank", "stock_deficit", "product_name"],
        ascending=[True, True, False, True],
    )
    return table[list(PURCHASE_COLUMNS)].rename(columns=PURCHASE_COLUMNS).reset_index(drop=True)
