"""Figuras Plotly do dashboard — REQ-008, com a paleta de REQ-012.

Todas as cores vêm de config.py (color_discrete_map explícito); nenhuma
figura depende das paletas padrão do Plotly.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from garden_shop import config
from garden_shop.formatting import fmt_days, fmt_usd

FONT = dict(family="sans-serif", color=config.COLOR_TEXT, size=13)


def _base_layout(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text="", traceorder="normal"),
        hoverlabel=dict(bgcolor="white", font=FONT),
    )
    return fig


# --- Barras empilhadas: categoria × status ----------------------------------

def stacked_status_bars(view: pd.DataFrame) -> go.Figure:
    counts = view.groupby(["category_name", "status"]).size().unstack(fill_value=0)
    # Categoria com mais produtos em situação crítica no topo
    critical = [s for s in (config.STATUS_STOCKOUT, config.STATUS_URGENT, config.STATUS_ALERT) if s in counts]
    order = counts.assign(_crit=counts[critical].sum(axis=1) if critical else 0, _tot=counts.sum(axis=1))
    categories = order.sort_values(["_crit", "_tot"], ascending=True).index.tolist()

    fig = go.Figure()
    for status in config.STATUS_ORDER:
        if status not in counts:
            continue
        values = counts.loc[categories, status]
        fig.add_bar(
            y=categories,
            x=values.tolist(),
            name=status,
            orientation="h",
            marker=dict(color=config.STATUS_COLORS[status], line=dict(color=config.COLOR_BACKGROUND, width=1)),
            hovertemplate="%{y}<br>" + status + ": %{x} produto(s)<extra></extra>",
        )
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_xaxes(title_text="Número de produtos", dtick=1, gridcolor="#E2DACB", zeroline=False)
    fig.update_yaxes(title_text="")
    return _base_layout(fig, height=360)


# --- Treemap: valor do estoque a custo --------------------------------------

def stock_value_treemap(view: pd.DataFrame) -> go.Figure:
    data = view[view["stock_cost_value"] > 0]
    cat_totals = data.groupby("category_name")["stock_cost_value"].sum()

    ids = list(cat_totals.index) + [f"{c}/{p}" for c, p in zip(data["category_name"], data["product_name"])]
    labels = list(cat_totals.index) + data["product_name"].tolist()
    parents = [""] * len(cat_totals) + data["category_name"].tolist()
    values = cat_totals.tolist() + data["stock_cost_value"].tolist()
    colors = [config.COLOR_PRIMARY] * len(cat_totals) + [config.STATUS_COLORS[s] for s in data["status"]]
    custom = [fmt_usd(v) for v in cat_totals] + [
        f"{fmt_usd(v)} · {s}" for v, s in zip(data["stock_cost_value"], data["status"])
    ]

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors, line=dict(color=config.COLOR_BACKGROUND, width=2)),
            customdata=custom,
            texttemplate="<b>%{label}</b><br>%{customdata}",
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            textfont=dict(color="white"),
            tiling=dict(pad=2),
            pathbar=dict(visible=False),
        )
    )
    return _base_layout(fig, height=360)


# --- Dispersão: quadrante de prioridade -------------------------------------

def priority_flags(plotted: pd.DataFrame) -> tuple[pd.Series, float, float]:
    """Prioridade = vendas acima da mediana E cobertura abaixo da mediana (ADR-008)."""
    median_x = float(plotted["qty_sold"].median())
    median_y = float(plotted["coverage_days"].median())
    flags = (plotted["qty_sold"] > median_x) & (plotted["coverage_days"] < median_y)
    return flags, median_x, median_y


def scatter_priority(view: pd.DataFrame) -> tuple[go.Figure | None, int]:
    """Devolve a figura (ou None, se nenhum produto vendeu) e quantos produtos ficaram de fora."""
    plotted = view[view["qty_sold"] > 0].copy()
    excluded = len(view) - len(plotted)
    if plotted.empty:
        return None, excluded

    flags, median_x, median_y = priority_flags(plotted)
    plotted["priority"] = flags
    plotted["coverage_text"] = plotted["coverage_days"].map(fmt_days)

    fig = go.Figure()
    for is_priority, name, color, size in (
        (False, "Demais produtos", config.OTHER_POINT_COLOR, 10),
        (True, "Prioridade", config.PRIORITY_POINT_COLOR, 14),
    ):
        part = plotted[plotted["priority"] == is_priority]
        if part.empty:
            continue
        fig.add_scatter(
            x=part["qty_sold"],
            y=part["coverage_days"],
            mode="markers+text" if is_priority else "markers",
            name=name,
            text=part["product_name"] if is_priority else None,
            textposition="middle right",
            textfont=dict(color=config.COLOR_PRIMARY, size=11),
            marker=dict(color=color, size=size, line=dict(color="white", width=1)),
            customdata=part[["product_name", "status", "coverage_text"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Vendas: %{x} un.<br>"
            "Cobertura: %{customdata[2]}<br>Status: %{customdata[1]}<extra></extra>",
        )

    line = dict(color=config.COLOR_TEXT, width=1, dash="dot")
    fig.add_vline(x=median_x, line=line, annotation_text=f"mediana: {median_x:g} un.", annotation_position="top")
    fig.add_hline(
        y=median_y, line=line, annotation_text=f"mediana: {fmt_days(median_y)}", annotation_position="top left"
    )
    fig.update_xaxes(title_text="Vendas efetivas no período (unidades)", gridcolor="#E2DACB", zeroline=False)
    fig.update_yaxes(title_text="Dias de cobertura", gridcolor="#E2DACB", zeroline=False, rangemode="tozero")
    return _base_layout(fig, height=420), excluded
