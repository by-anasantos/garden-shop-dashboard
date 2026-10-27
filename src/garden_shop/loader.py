"""Leitura e validação dos CSVs da Garden Shop — REQ-001 (SPEC, seções 6 e 7.1).

Regras:
- Lê somente os 5 arquivos e os campos usados nos indicadores; customers.csv
  nunca é lido (ADR-006).
- Erros estruturais (arquivo ou coluna ausente, ID duplicado, valor fora do
  domínio, data inválida) geram DataValidationError (ADR-007).
- Itens de pedido órfãos são descartados e registrados em `warnings`; produtos
  com categoria ou fornecedor inexistente são mantidos e registrados em
  `warnings` (o rótulo "Não cadastrada/o" é aplicado na visão por produto).
- Nenhum arquivo é alterado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from garden_shop import config


class DataValidationError(Exception):
    """Erro de estrutura ou conteúdo em um CSV, com arquivo, coluna e detalhe."""

    def __init__(self, file: str, column: str | None, detail: str) -> None:
        self.file = file
        self.column = column
        self.detail = detail
        where = f"{file}, coluna '{column}'" if column else file
        super().__init__(f"{where}: {detail}")


@dataclass
class GardenShopData:
    products: pd.DataFrame
    categories: pd.DataFrame
    suppliers: pd.DataFrame
    orders: pd.DataFrame
    order_items: pd.DataFrame
    warnings: list[str] = field(default_factory=list)


# Campos usados por arquivo (SPEC 7.1) e seu tipo.
#   int / float / str (obrigatório, não vazio) / opt_str / bool / date
SCHEMA: dict[str, dict[str, str]] = {
    "products": {
        "product_id": "int",
        "product_name": "str",
        "category_id": "int",
        "supplier_id": "int",
        "price": "float",
        "cost": "float",
        "quantity_on_hand": "int",
        "reorder_level": "int",
        "discontinued": "bool",
    },
    "categories": {"category_id": "int", "category_name": "str"},
    "suppliers": {"supplier_id": "int", "supplier_name": "str", "contact_email": "opt_str"},
    "orders": {"order_id": "int", "order_date": "date", "status": "str"},
    "order_items": {
        "order_item_id": "int",
        "order_id": "int",
        "product_id": "int",
        "quantity": "int",
        "unit_price": "float",
    },
}

PRIMARY_KEYS = {
    "products": "product_id",
    "categories": "category_id",
    "suppliers": "supplier_id",
    "orders": "order_id",
    "order_items": "order_item_id",
}

NON_NEGATIVE = {
    "products": ("price", "cost", "quantity_on_hand", "reorder_level"),
    "order_items": ("unit_price",),
}
POSITIVE = {"order_items": ("quantity",)}

_INT_RE = re.compile(r"^[+-]?\d+$")
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def load_data(data_dir: Path | str | None = None) -> GardenShopData:
    """Lê e valida os 5 CSVs da pasta indicada (padrão: config.data_dir())."""
    folder = Path(data_dir) if data_dir is not None else config.data_dir()
    frames = {name: _read_table(folder, name) for name in config.DATA_FILES}

    warnings: list[str] = []
    frames["order_items"] = _drop_orphan_items(frames, warnings)
    _warn_missing_dimensions(frames, warnings)

    return GardenShopData(warnings=warnings, **frames)


# --- Leitura e tipagem ------------------------------------------------------

def _read_table(folder: Path, name: str) -> pd.DataFrame:
    file = f"{name}.csv"
    path = folder / file
    if not path.is_file():
        raise DataValidationError(file, None, f"arquivo não encontrado em {folder}")

    raw = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    raw.columns = [c.strip() for c in raw.columns]

    schema = SCHEMA[name]
    for column in schema:
        if column not in raw.columns:
            raise DataValidationError(file, column, "coluna obrigatória ausente")

    df = pd.DataFrame(
        {column: _convert(raw[column].str.strip(), kind, file, column) for column, kind in schema.items()}
    )
    _check_constraints(df, name, file)
    return df


def _convert(values: pd.Series, kind: str, file: str, column: str) -> pd.Series:
    if kind == "opt_str":
        return values.where(values != "", None)

    empty = values[values == ""]
    if not empty.empty:
        raise DataValidationError(file, column, f"valor vazio na linha {empty.index[0] + 2}")

    if kind == "str":
        return values
    if kind == "int":
        bad = values[~values.map(lambda v: bool(_INT_RE.match(v)))]
        if not bad.empty:
            raise DataValidationError(file, column, f"valor não inteiro '{bad.iloc[0]}'")
        return values.astype("int64")
    if kind == "float":
        numbers = pd.to_numeric(values, errors="coerce")
        bad = values[numbers.isna()]
        if not bad.empty:
            raise DataValidationError(file, column, f"valor não numérico '{bad.iloc[0]}'")
        return numbers.astype("float64")
    if kind == "bool":
        lowered = values.str.lower()
        bad = values[~lowered.isin(["true", "false"])]
        if not bad.empty:
            raise DataValidationError(file, column, f"valor '{bad.iloc[0]}' não é true/false")
        return lowered == "true"
    if kind == "date":
        return values.map(lambda v: _parse_date(v, file, column))
    raise ValueError(f"tipo desconhecido: {kind}")


def _parse_date(value: str, file: str, column: str) -> date:
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise DataValidationError(file, column, f"data inválida '{value}' (use AAAA-MM-DD ou DD/MM/AAAA)")


def _check_constraints(df: pd.DataFrame, name: str, file: str) -> None:
    key = PRIMARY_KEYS[name]
    duplicated = df.loc[df[key].duplicated(), key]
    if not duplicated.empty:
        raise DataValidationError(file, key, f"ID duplicado {duplicated.iloc[0]}")

    for column in NON_NEGATIVE.get(name, ()):
        bad = df.loc[df[column] < 0, column]
        if not bad.empty:
            raise DataValidationError(file, column, f"valor negativo {bad.iloc[0]}")

    for column in POSITIVE.get(name, ()):
        bad = df.loc[df[column] <= 0, column]
        if not bad.empty:
            raise DataValidationError(file, column, f"valor deve ser maior que zero: {bad.iloc[0]}")

    if name == "orders":
        bad = df.loc[~df["status"].isin(config.ORDER_STATUSES), "status"]
        if not bad.empty:
            allowed = ", ".join(sorted(config.ORDER_STATUSES))
            raise DataValidationError(file, "status", f"valor '{bad.iloc[0]}' fora do domínio ({allowed})")


# --- Relacionamentos --------------------------------------------------------

def _drop_orphan_items(frames: dict[str, pd.DataFrame], warnings: list[str]) -> pd.DataFrame:
    items = frames["order_items"]
    known_orders = set(frames["orders"]["order_id"])
    known_products = set(frames["products"]["product_id"])

    keep = []
    for row in items.itertuples(index=False):
        problems = []
        if row.order_id not in known_orders:
            problems.append(f"order_id {row.order_id} não existe em orders.csv")
        if row.product_id not in known_products:
            problems.append(f"product_id {row.product_id} não existe em products.csv")
        if problems:
            warnings.append(f"order_items.csv: item {row.order_item_id} descartado — " + "; ".join(problems))
        keep.append(not problems)

    return items.loc[keep].reset_index(drop=True)


def _warn_missing_dimensions(frames: dict[str, pd.DataFrame], warnings: list[str]) -> None:
    products = frames["products"]
    checks = (
        ("category_id", set(frames["categories"]["category_id"]), "categories.csv"),
        ("supplier_id", set(frames["suppliers"]["supplier_id"]), "suppliers.csv"),
    )
    for column, known, source in checks:
        for row in products.loc[~products[column].isin(known)].itertuples(index=False):
            warnings.append(
                f"products.csv: produto {row.product_id} ({row.product_name}) tem {column} "
                f"{getattr(row, column)} inexistente em {source}"
            )
