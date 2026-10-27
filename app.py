"""Garden Shop — Dashboard de Estoque e Reposição (Streamlit, página única).

Esta interface não contém fórmulas: apenas chama as funções de src/garden_shop
e organiza o resultado na tela (SPEC, seção 5). Executar com:

    python -m streamlit run app.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from garden_shop import config  # noqa: E402
from garden_shop.charts import scatter_priority, stacked_status_bars, stock_value_treemap  # noqa: E402
from garden_shop.filters import FilterSelection, apply_filters  # noqa: E402
from garden_shop.formatting import fmt_days, fmt_int, fmt_pct, fmt_usd  # noqa: E402
from garden_shop.loader import DataValidationError, GardenShopData, load_data  # noqa: E402
from garden_shop.metrics import (  # noqa: E402
    build_product_view,
    compute_kpis,
    default_period,
    purchase_table,
)

st.set_page_config(page_title="Garden Shop · Estoque", page_icon="🌿", layout="wide")

# --- Estilo (paleta sem vermelho — SPEC 11.3) -------------------------------
st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 3.2rem; padding-bottom: 0; max-width: 1400px; }}
      .gs-header {{ background: {config.COLOR_PRIMARY}; color: #F5F0E6; padding: 1.1rem 1.5rem;
                    border-radius: 10px; display: flex; justify-content: space-between;
                    align-items: flex-end; flex-wrap: wrap; gap: .5rem; margin-bottom: 1rem; }}
      .gs-header h1 {{ color: #F5F0E6; font-size: 1.6rem; margin: 0; padding: 0; }}
      .gs-header p {{ margin: .2rem 0 0; opacity: .85; font-size: .95rem; }}
      .gs-header .gs-author {{ font-size: .9rem; opacity: .9; text-align: right; }}
      .gs-section {{ color: {config.COLOR_PRIMARY}; font-size: 1.1rem; font-weight: 700;
                     margin: 1.4rem 0 .2rem; border-bottom: 2px solid {config.COLOR_PRIMARY};
                     padding-bottom: .25rem; }}
      .gs-sub {{ color: #4a5462; font-size: .88rem; margin: .1rem 0 .6rem; }}
      .gs-cards {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: .75rem; }}
      @media (max-width: 1100px) {{ .gs-cards {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
      @media (max-width: 640px)  {{ .gs-cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
      .gs-card {{ background: #FFFFFF; border-radius: 10px; padding: .85rem 1rem;
                  border-top: 5px solid var(--accent); box-shadow: 0 1px 2px rgba(10,22,40,.08); }}
      .gs-card .lbl {{ font-size: .8rem; color: #4a5462; text-transform: uppercase; letter-spacing: .03em; }}
      .gs-card .val {{ font-size: 1.55rem; font-weight: 700; color: {config.COLOR_TEXT}; line-height: 1.3; }}
      .gs-card .hint {{ font-size: .78rem; color: #5b6573; }}
      .gs-msg {{ background: #FFFFFF; border-left: 5px solid {config.STATUS_COLORS[config.STATUS_URGENT]};
                 padding: .9rem 1.1rem; border-radius: 6px; color: {config.COLOR_TEXT}; margin: .5rem 0; }}
      .gs-footer {{ background: {config.COLOR_TEXT}; color: #E8E4DA; padding: 1rem 1.5rem; border-radius: 10px;
                    margin-top: 2rem; font-size: .85rem; line-height: 1.55; }}
      .gs-footer b {{ color: #FFFFFF; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def message(text: str) -> None:
    """Aviso na paleta do projeto (st.error usa vermelho, proibido — REQ-012)."""
    st.markdown(f'<div class="gs-msg">{text}</div>', unsafe_allow_html=True)


def section(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="gs-section">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="gs-sub">{subtitle}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner="Carregando os dados…")
def cached_load(data_dir: str) -> GardenShopData:
    return load_data(Path(data_dir))


def br_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# --- Cabeçalho --------------------------------------------------------------
st.markdown(
    """
    <div class="gs-header">
      <div>
        <h1>Garden Shop · Estoque e Reposição</h1>
        <p>O que está em risco, quanto vale o estoque, o que vende mais e o que comprar de quem.</p>
      </div>
      <div class="gs-author">Ana Santos</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Carga (REQ-001) --------------------------------------------------------
try:
    data = cached_load(str(config.data_dir()))
except DataValidationError as exc:
    message(f"<b>Não foi possível carregar os dados.</b><br>{exc}<br>"
            "Corrija ou restaure os CSVs em <code>data/raw/</code> e recarregue a página.")
    st.stop()

if data.warnings:
    with st.expander(f"⚠️ {len(data.warnings)} aviso(s) na carga dos dados"):
        for w in data.warnings:
            st.write("•", w)

first_day, last_day = default_period(data.orders)

# --- Filtros (REQ-007) ------------------------------------------------------
with st.container(border=True):
    c_period, c_cat, c_sup, c_status, c_abc = st.columns([1.3, 1, 1, 1, 0.8])
    period = c_period.date_input(
        "Período de vendas",
        value=(first_day, last_day),
        min_value=date(first_day.year - 1, 1, 1),
        max_value=date(last_day.year + 1, 12, 31),
        format="DD/MM/YYYY",
        help="Afeta só vendas, venda média, cobertura e curva ABC. O estoque é sempre a posição atual.",
    )
    categories = c_cat.multiselect(
        "Categoria", sorted(data.categories["category_name"]), placeholder="Todas"
    )
    suppliers = c_sup.multiselect(
        "Fornecedor", sorted(data.suppliers["supplier_name"]), placeholder="Todos"
    )
    statuses = c_status.multiselect("Status", list(config.STATUS_ORDER), placeholder="Todos")
    abc = c_abc.multiselect("Curva ABC", list(config.ABC_ORDER), placeholder="Todas")

# Uma única data escolhida = período de um dia (REQ-007)
if isinstance(period, (tuple, list)):
    start = period[0]
    end = period[1] if len(period) > 1 else period[0]
else:
    start = end = period

view_all = build_product_view(data, start, end)
selection = FilterSelection(tuple(categories), tuple(suppliers), tuple(statuses), tuple(abc))
view = apply_filters(view_all, selection)
kpis = compute_kpis(view)
period_days = (end - start).days + 1

# --- Cards (REQ-004) --------------------------------------------------------
section(
    "Situação do estoque",
    f"Posição atual · {fmt_int(len(view))} de {fmt_int(len(view_all))} produtos nos filtros. "
    "Ruptura, abaixo do ponto e déficit consideram só produtos ativos.",
)
cards = [
    ("Valor do estoque (custo)", fmt_usd(kpis["stock_cost_value"]), "capital imobilizado", config.COLOR_PRIMARY),
    ("Valor potencial de venda", fmt_usd(kpis["stock_sale_value"]), "a preço de tabela", config.COLOR_PRIMARY),
    ("Margem bruta em estoque", fmt_pct(kpis["gross_margin"]), "(venda − custo) / venda", config.COLOR_PRIMARY),
    ("Produtos em ruptura", fmt_int(kpis["stockout_count"]), "estoque zerado",
     config.STATUS_COLORS[config.STATUS_STOCKOUT]),
    ("Abaixo do ponto de reposição", fmt_int(kpis["below_reorder_count"]), "estoque ≤ nível de reposição",
     config.STATUS_COLORS[config.STATUS_URGENT]),
    ("Déficit total de peças", fmt_int(kpis["total_deficit"]), "para voltar ao nível de reposição",
     config.STATUS_COLORS[config.STATUS_ALERT]),
]
st.markdown(
    '<div class="gs-cards">'
    + "".join(
        f'<div class="gs-card" style="--accent:{accent}"><div class="lbl">{lbl}</div>'
        f'<div class="val">{val}</div><div class="hint">{hint}</div></div>'
        for lbl, val, hint, accent in cards
    )
    + "</div>",
    unsafe_allow_html=True,
)

# --- Estado sem resultados (REQ-010) ----------------------------------------
if view.empty:
    section("Análises")
    message("<b>Nenhum produto atende aos filtros selecionados.</b><br>"
            "Remova ou altere algum filtro para ver os gráficos e a tabela de compras.")
else:
    # --- Gráficos (REQ-008) -------------------------------------------------
    col_bars, col_tree = st.columns(2, gap="large")
    with col_bars:
        section("Onde estão os problemas", "Produtos por categoria e status de estoque.")
        st.plotly_chart(stacked_status_bars(view), width="stretch", config={"displayModeBar": False})
    with col_tree:
        section("Onde está o capital", "Valor do estoque a custo por categoria e produto; cor = status.")
        st.plotly_chart(stock_value_treemap(view), width="stretch", config={"displayModeBar": False})

    section(
        "Quadrante de prioridade",
        f"Vendas efetivas × dias de cobertura entre {br_date(start)} e {br_date(end)} ({period_days} dias). "
        "Em destaque: vendem acima da mediana e têm cobertura abaixo da mediana.",
    )
    fig_scatter, excluded = scatter_priority(view)
    if fig_scatter is None:
        message("Não há vendas efetivas no período selecionado.")
    else:
        st.plotly_chart(fig_scatter, width="stretch", config={"displayModeBar": False})
        if excluded:
            st.caption(f"{excluded} produto(s) sem vendas no período não aparecem no gráfico.")

    # --- Tabela de compras (REQ-009) ----------------------------------------
    section("Tabela de compras", "Ordenada por status, curva ABC e déficit. Descontinuados nunca recebem sugestão.")
    only_rec = st.toggle("Somente recomendações de compra", value=True)
    table = purchase_table(view, only_recommended=only_rec)

    if table.empty:
        message("Nenhum produto dos filtros precisa de reposição.")
    else:
        display = table.copy()
        display["Dias de cobertura"] = display["Dias de cobertura"].map(fmt_days)
        display["Venda média diária"] = display["Venda média diária"].round(3)

        def status_style(value: str) -> str:
            color = config.STATUS_COLORS.get(value)
            if not color:
                return ""
            text = config.COLOR_TEXT if value == config.STATUS_ALERT else "#FFFFFF"
            return f"background-color: {color}; color: {text}; font-weight: 600"

        st.dataframe(
            display.style.map(status_style, subset=["Status"]),
            hide_index=True,
            width="stretch",
            column_config={
                "Produto": st.column_config.TextColumn(width="medium"),
                "E-mail do fornecedor": st.column_config.TextColumn(width="medium"),
                "Estoque atual": st.column_config.NumberColumn("Estoque", width="small"),
                "Nível de reposição": st.column_config.NumberColumn("Reposição", width="small"),
                "Déficit mínimo (sugestão de compra)": st.column_config.NumberColumn("Sugestão de compra", width="small"),
                "Venda média diária": st.column_config.NumberColumn("Venda/dia", format="%.3f", width="small"),
                "Dias de cobertura": st.column_config.TextColumn("Cobertura", width="small"),
                "Curva ABC": st.column_config.TextColumn("ABC", width="small"),
            },
        )
        st.download_button(
            "⬇️ Exportar CSV",
            data=display.to_csv(index=False).encode("utf-8-sig"),
            file_name="lista_compras_garden_shop.csv",
            mime="text/csv",
        )

# --- Rodapé (REQ-011) -------------------------------------------------------
st.markdown(
    f"""
    <div class="gs-footer">
      <b>Fonte:</b> CSVs da Garden Shop (products, categories, suppliers, orders e order_items).
      Pedidos de {br_date(first_day)} a {br_date(last_day)}. Vendas efetivas = pedidos shipped, pending e
      processing; cancelados não contam.<br>
      <b>Limitações:</b> sem prazo de entrega (lead time) dos fornecedores · sem histórico de movimentações
      do estoque · sem lote mínimo de compra (MOQ) · janela curta de vendas (≈5 meses), sujeita à
      sazonalidade da jardinagem · volume pequeno de vendas, por isso a cobertura serve para comparar
      produtos, não como previsão.<br>
      <b>Autora:</b> Ana Santos
    </div>
    """,
    unsafe_allow_html=True,
)
