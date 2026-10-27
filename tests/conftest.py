"""Configuração comum dos testes.

- Coloca src/ no caminho de importação.
- `full_data_dir`: a base completa em data/raw/ (somente leitura).
- `data_copy`: cópia da base em uma pasta temporária, para os testes que
  precisam alterar um CSV sem tocar nos originais (AGENTS.md, seção 7).
- `sample_data`: o recorte de referência da SPEC (seção 13.1), montado a
  partir das linhas reais dos CSVs: produtos 1, 9, 14 e 24 e os pedidos
  1, 7, 10, 17, 18 e 24 (somente os itens desses produtos).
"""

from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

FULL_DATA_DIR = PROJECT_ROOT / "data" / "raw"


@pytest.fixture
def full_data_dir() -> Path:
    return FULL_DATA_DIR


@pytest.fixture
def data_copy(tmp_path: Path) -> Path:
    """Cópia dos 5 CSVs em uma pasta temporária, que pode ser alterada."""
    for csv in FULL_DATA_DIR.glob("*.csv"):
        shutil.copy(csv, tmp_path / csv.name)
    return tmp_path


SAMPLE_PRODUCTS = {1, 9, 14, 24}
SAMPLE_ORDERS = {1, 7, 10, 17, 18, 24}

# Período de referência da SPEC: 2024-01-15 a 2024-06-14 (152 dias)
FULL_START = date(2024, 1, 15)
FULL_END = date(2024, 6, 14)


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """Grava o recorte da SPEC 13.1 como CSVs em uma pasta temporária."""
    import pandas as pd

    def subset(name: str, column: str, keep: set[int]) -> pd.DataFrame:
        df = pd.read_csv(FULL_DATA_DIR / f"{name}.csv", dtype=str, keep_default_na=False)
        return df[df[column].astype(int).isin(keep)]

    subset("products", "product_id", SAMPLE_PRODUCTS).to_csv(tmp_path / "products.csv", index=False)
    subset("orders", "order_id", SAMPLE_ORDERS).to_csv(tmp_path / "orders.csv", index=False)
    items = subset("order_items", "order_id", SAMPLE_ORDERS)
    items = items[items["product_id"].astype(int).isin(SAMPLE_PRODUCTS)]
    items.to_csv(tmp_path / "order_items.csv", index=False)
    for name in ("categories", "suppliers"):
        shutil.copy(FULL_DATA_DIR / f"{name}.csv", tmp_path / f"{name}.csv")
    return tmp_path


@pytest.fixture
def sample_data(sample_dir: Path):
    from garden_shop.loader import load_data

    return load_data(sample_dir)


@pytest.fixture
def full_data(full_data_dir: Path):
    from garden_shop.loader import load_data

    return load_data(full_data_dir)
