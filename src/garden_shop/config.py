"""Caminhos, constantes de negócio, rótulos e paleta (SPEC, seções 5.2, 8.3 e 11.3)."""

from __future__ import annotations

import os
from pathlib import Path

# --- Caminhos ---------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def data_dir() -> Path:
    """Pasta dos CSVs: GARDEN_SHOP_DATA_DIR, se definida; senão data/raw/."""
    env = os.environ.get("GARDEN_SHOP_DATA_DIR")
    return Path(env) if env else DEFAULT_DATA_DIR


# --- Arquivos lidos (customers.csv nunca é lido — ADR-006) -------------------
DATA_FILES = ("products", "categories", "suppliers", "orders", "order_items")

# --- Domínios ---------------------------------------------------------------
ORDER_STATUSES = frozenset({"shipped", "pending", "processing", "cancelled"})
VALID_SALE_STATUSES = frozenset({"shipped", "pending", "processing"})  # RN-001

# --- Constantes de negócio --------------------------------------------------
ALERT_FACTOR = 1.25   # Alerta limítrofe: qoh <= reorder_level * 1,25 (REQ-003)
ABC_A_LIMIT = 0.80    # Classe A: participação acumulada anterior < 80% (REQ-006)
ABC_B_LIMIT = 0.95    # Classe B: participação acumulada anterior < 95%

# --- Rótulos e ordens -------------------------------------------------------
STATUS_DISCONTINUED = "Descontinuado"
STATUS_STOCKOUT = "Ruptura"
STATUS_URGENT = "Reposição urgente"
STATUS_ALERT = "Alerta limítrofe"
STATUS_HEALTHY = "Saudável"

# Ordem de prioridade usada na tabela de compras e nos gráficos (REQ-009)
STATUS_ORDER = (
    STATUS_STOCKOUT,
    STATUS_URGENT,
    STATUS_ALERT,
    STATUS_HEALTHY,
    STATUS_DISCONTINUED,
)

ABC_NO_SALES = "Sem vendas"
ABC_ORDER = ("A", "B", "C", ABC_NO_SALES)

MISSING_CATEGORY = "Não cadastrada"
MISSING_SUPPLIER = "Não cadastrado"
MISSING_EMAIL = "Sem e-mail — buscar outro canal"
NO_TURNOVER = "Sem giro"

# --- Paleta sem vermelho (SPEC 11.3, REQ-012) -------------------------------
COLOR_PRIMARY = "#003d48"
COLOR_BACKGROUND = "#F5F0E6"
COLOR_TEXT = "#0a1628"
COLOR_MUTED = "#9AA0A6"

STATUS_COLORS = {
    STATUS_STOCKOUT: "#3d1f0f",
    STATUS_URGENT: "#8B5A2B",
    STATUS_ALERT: "#C9A227",
    STATUS_HEALTHY: "#4F8A94",
    STATUS_DISCONTINUED: "#9AA0A6",
}

PRIORITY_POINT_COLOR = COLOR_PRIMARY
OTHER_POINT_COLOR = COLOR_MUTED
