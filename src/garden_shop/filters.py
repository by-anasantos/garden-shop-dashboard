"""Filtros de dimensão sobre a visão por produto — REQ-007.

- Seleção vazia em um filtro significa "todos".
- Os filtros são combinados com E lógico.
- O período NÃO é tratado aqui: ele entra em build_product_view, antes da
  curva ABC, para que filtrar dimensões não reclassifique os produtos.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FilterSelection:
    categories: tuple[str, ...] = ()
    suppliers: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    abc: tuple[str, ...] = ()


_COLUMNS = {
    "categories": "category_name",
    "suppliers": "supplier_name",
    "statuses": "status",
    "abc": "abc_class",
}


def apply_filters(view: pd.DataFrame, selection: FilterSelection) -> pd.DataFrame:
    """Devolve as linhas que atendem a todos os filtros preenchidos (sem alterar `view`)."""
    mask = pd.Series(True, index=view.index)
    for attr, column in _COLUMNS.items():
        chosen = getattr(selection, attr)
        if chosen:
            mask &= view[column].isin(chosen)
    return view.loc[mask].copy()
