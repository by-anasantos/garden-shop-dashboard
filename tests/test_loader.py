"""Testes de carga e validação — REQ-001 (SPEC, seção 13.2: TEST-001 a TEST-005).

Escritos antes do loader.py, a partir dos critérios de aceitação da SPEC.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from garden_shop.loader import DataValidationError, load_data


def _rewrite(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"trecho não encontrado em {path.name}: {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


# --- TEST-001: carga da base completa ---------------------------------------

def test_001_full_base_row_counts(full_data_dir):
    data = load_data(full_data_dir)
    assert len(data.products) == 24
    assert len(data.categories) == 8
    assert len(data.suppliers) == 6
    assert len(data.orders) == 24
    assert len(data.order_items) == 48
    assert data.warnings == []


def test_001_full_base_types(full_data_dir):
    data = load_data(full_data_dir)
    p = data.products
    assert p["discontinued"].dtype == bool
    assert bool(p.loc[p["product_id"] == 24, "discontinued"].item()) is True
    assert p["discontinued"].sum() == 1
    assert pd.api.types.is_integer_dtype(p["quantity_on_hand"])
    assert pd.api.types.is_float_dtype(p["cost"])
    o = data.orders
    assert o.loc[o["order_id"] == 17, "order_date"].item() == date(2024, 4, 3)
    assert o["order_date"].min() == date(2024, 1, 15)
    assert o["order_date"].max() == date(2024, 6, 14)


def test_001_missing_email_is_kept_as_missing(full_data_dir):
    s = load_data(full_data_dir).suppliers
    ironwood = s.loc[s["supplier_id"] == 5, "contact_email"].item()
    assert pd.isna(ironwood)


def test_001_customers_is_never_read(full_data_dir, monkeypatch):
    opened: list[str] = []
    real_read_csv = pd.read_csv

    def spy(path, *args, **kwargs):
        opened.append(Path(path).name)
        return real_read_csv(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", spy)
    load_data(full_data_dir)
    assert "customers.csv" not in opened
    assert sorted(opened) == sorted(
        ["products.csv", "categories.csv", "suppliers.csv", "orders.csv", "order_items.csv"]
    )


def test_001_source_files_are_not_modified(full_data_dir):
    before = {f.name: f.read_bytes() for f in full_data_dir.glob("*.csv")}
    load_data(full_data_dir)
    after = {f.name: f.read_bytes() for f in full_data_dir.glob("*.csv")}
    assert before == after


# --- TEST-002: coluna obrigatória ausente -----------------------------------

def test_002_missing_column_raises(data_copy):
    orders = data_copy / "orders.csv"
    df = pd.read_csv(orders, dtype=str, keep_default_na=False)
    df.drop(columns="status").to_csv(orders, index=False)
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "orders.csv" in str(exc.value)
    assert "status" in str(exc.value)


def test_002_missing_file_raises(data_copy):
    (data_copy / "suppliers.csv").unlink()
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "suppliers.csv" in str(exc.value)


# --- TEST-003: valor fora do domínio ----------------------------------------

def test_003_unknown_status_raises(data_copy):
    _rewrite(data_copy / "orders.csv", "2024-04-03,,cancelled,", "2024-04-03,,returned,")
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "orders.csv" in str(exc.value)
    assert "returned" in str(exc.value)


def test_003_negative_stock_raises(data_copy):
    _rewrite(data_copy / "products.csv", "Hanging Basket,4,2,14.00,6.00,0,", "Hanging Basket,4,2,14.00,6.00,-1,")
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "quantity_on_hand" in str(exc.value)


def test_003_duplicate_id_raises(data_copy):
    path = data_copy / "categories.csv"
    path.write_text(path.read_text(encoding="utf-8") + "8,Duplicada\n", encoding="utf-8")
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "categories.csv" in str(exc.value)
    assert "category_id" in str(exc.value)


def test_003_invalid_date_raises(data_copy):
    _rewrite(data_copy / "orders.csv", "17,9,2024-04-03", "17,9,2024-13-40")
    with pytest.raises(DataValidationError) as exc:
        load_data(data_copy)
    assert "order_date" in str(exc.value)


# --- TEST-004: formatos de data e booleano ----------------------------------

def test_004_date_and_bool_formats_give_same_result(full_data_dir, data_copy):
    orders = data_copy / "orders.csv"
    df = pd.read_csv(orders, dtype=str, keep_default_na=False)
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%d/%m/%Y")
    df.to_csv(orders, index=False)

    products = data_copy / "products.csv"
    text = products.read_text(encoding="utf-8")
    products.write_text(text.replace(",false\n", ",FALSE\n").replace(",true\n", ",TRUE\n"), encoding="utf-8")

    original = load_data(full_data_dir)
    converted = load_data(data_copy)
    pd.testing.assert_frame_equal(original.orders, converted.orders)
    pd.testing.assert_frame_equal(original.products, converted.products)


# --- TEST-005: item de pedido órfão -----------------------------------------

def test_005_orphan_item_is_dropped_with_warning(data_copy):
    path = data_copy / "order_items.csv"
    path.write_text(path.read_text(encoding="utf-8") + "49,24,999,1,5.00\n", encoding="utf-8")
    data = load_data(data_copy)
    assert len(data.order_items) == 48
    assert 999 not in set(data.order_items["product_id"])
    assert len(data.warnings) == 1
    assert "999" in data.warnings[0]


def test_005_product_with_unknown_supplier_warns(data_copy):
    _rewrite(data_copy / "products.csv", "Bird Feeder,8,5,", "Bird Feeder,8,99,")
    data = load_data(data_copy)
    assert len(data.products) == 24
    assert len(data.warnings) == 1
    assert "supplier_id" in data.warnings[0]
