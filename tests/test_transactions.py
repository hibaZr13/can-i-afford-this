import pytest
import pandas as pd
from src import config
from src.transactions import *


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    # Point every CSV path at a temp folder; empty files get created on first load
    for name in ["TRANSACTIONS_CSV", "CATEGORIES_CSV"]:
        monkeypatch.setattr(config, name, tmp_path / f"{name}.csv")
    pd.DataFrame({"name": ["Food", "Salary"], "flow": ["outflow", "inflow"]}) \
        .to_csv(config.CATEGORIES_CSV, index=False)


def test_rejects_negative_amount():
    with pytest.raises(ValueError):
        add_transaction("2026-11-02", -20, "outflow", "Food", "Shop")


def test_add_transaction_persists_to_csv():
    new_id = add_transaction("2026-11-02", 25.5, "outflow", "Food", "Shop")
    assert new_id in get_transactions()["transaction_id"].values


def test_month_filter_excludes_other_months_and_years():
    add_transaction("2026-11-02", 10, "outflow", "Food", "A")
    add_transaction("2026-10-02", 10, "outflow", "Food", "B")
    add_transaction("2025-11-02", 10, "outflow", "Food", "C")
    assert len(get_transactions(month="2026-11")) == 1


def test_update_and_delete():
    new_id = add_transaction("2026-11-02", 10, "outflow", "Food", "A")
    update_transaction(new_id, notes="hello")
    assert get_transactions().iloc[0]["notes"] == "hello"
    delete_transaction(new_id)
    assert get_transactions().empty