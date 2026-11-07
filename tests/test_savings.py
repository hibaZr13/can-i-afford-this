import pytest
from src import config
from src.savings import *


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    # Point both files at a temp folder; empty files get created on first load
    monkeypatch.setattr(config, "SAVINGS_GOALS_CSV", tmp_path / "goals.csv")
    monkeypatch.setattr(config, "SAVINGS_ENTRIES_CSV", tmp_path / "entries.csv")


def test_add_goal_and_ids():
    assert add_goal("Laptop", 1200) == "G001"
    assert add_goal("Holiday", 800, "2027-07-01") == "G002"


def test_balance_and_total():
    a = add_goal("A", 1000)
    b = add_goal("B", 500)
    add_savings_entry(a, 200, "2026-11-01")
    add_savings_entry(b, 50, "2026-11-01")
    add_savings_entry(b, -20, "2026-11-05")
    assert get_goal_balance(a) == 200
    assert get_goal_balance(b) == 30
    assert get_total_savings() == 230


def test_rejects_bad_entries():
    g = add_goal("A", 1000)
    add_savings_entry(g, 50, "2026-11-01")
    with pytest.raises(ValueError):
        add_savings_entry(g, -60, "2026-11-02")      # more than saved
    with pytest.raises(ValueError):
        add_savings_entry(g, 0, "2026-11-02")        # zero
    with pytest.raises(ValueError):
        add_savings_entry("G999", 10, "2026-11-02")  # unknown goal


def test_progress():
    g = add_goal("Laptop", 1200, "2027-02-28")
    add_savings_entry(g, 200, "2026-11-01")
    p = get_goal_progress(g, today="2026-11-15")
    assert p["percent"] == 16.67
    assert p["amount_left"] == 1000
    assert p["monthly_needed"] == 333.33             # 3 months left


def test_progress_edge_cases():
    no_date = add_goal("A", 100)
    assert get_goal_progress(no_date)["monthly_needed"] is None
    past = add_goal("B", 100, "2020-01-01")
    assert get_goal_progress(past, today="2026-11-15")["monthly_needed"] is None
    done = add_goal("C", 100, "2027-01-01")
    add_savings_entry(done, 100, "2026-11-01")
    assert get_goal_progress(done)["monthly_needed"] == 0