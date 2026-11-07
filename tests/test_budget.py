import pytest
import pandas as pd
from src import config
from src.budget import *


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    # Point both files at a temp folder; empty files get created on first load
    monkeypatch.setattr(config, "BUDGETS_CSV", tmp_path / "budgets.csv")
    monkeypatch.setattr(config, "TRANSACTIONS_CSV", tmp_path / "transactions.csv")


@pytest.mark.parametrize("spendable, spent, expected", [
    (1800, 1200, 600),
    (1800, 1800, 0),
    (1800, 2000, -200),
    (0, 0, 0),
])
def test_remaining_budget_cases(spendable, spent, expected):
    assert remaining_amount(spendable, spent) == expected


def test_set_replaces_instead_of_duplicating():
    set_spendable_amount("2026-11", 1000)
    set_spendable_amount("2026-11", 1200)
    assert len(load_budgets()) == 1
    assert get_spendable_amount("2026-11") == 1200


def test_carry_over_and_nothing_set():
    assert get_spendable_amount("2026-11") == 0          # nothing set yet
    set_spendable_amount("2026-10", 900)
    assert get_spendable_amount("2026-12") == 900        # carried over
    assert get_spendable_amount("2026-09") == 0          # nothing earlier


def test_rejects_bad_input():
    with pytest.raises(ValueError):
        set_spendable_amount("2026-13", 100)             # bad month
    with pytest.raises(ValueError):
        set_spendable_amount("2026-11", -5)              # negative


def test_calculate_remaining():
    from src.transactions import add_transaction
    pd.DataFrame({"name": ["Food"], "flow": ["outflow"]}).to_csv(config.CATEGORIES_CSV, index=False)
    set_spendable_amount("2026-11", 500)
    add_transaction("2026-11-02", 120, "outflow", "Food", "Shop")
    assert calculate_remaining("2026-11") == 380