"""Configuração comum dos testes.

- Coloca src/ no caminho de importação.
- `full_data_dir`: a base completa em data/raw/ (somente leitura).
- `data_copy`: cópia da base em uma pasta temporária, para os testes que
  precisam alterar um CSV sem tocar nos originais (AGENTS.md, seção 7).

O recorte de referência da SPEC (seção 13.1) entra aqui na Fase 2.
"""

from __future__ import annotations

import shutil
import sys
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
