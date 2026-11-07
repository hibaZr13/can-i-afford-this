import pandas as pd
from src.analytics import *

COLS = ["date", "amount", "flow", "category"]


def make(rows):
    return pd.DataFrame(rows, columns=COLS)


T = make([
    ["2026-11-02", 100, "outflow", "Food"],
    ["2026-11-03", 300, "outflow", "Shopping"],
    ["2026-11-04", 1000, "inflow", "Salary"],
    ["2026-10-05", 999, "outflow", "Food"],   # other month
    ["2025-11-05", 999, "outflow", "Food"],   # same month, other year
])


def test_other_months_excluded():
    assert total_by_flow(T, "2026-11", "outflow") == 400


def test_empty_dataset_does_not_crash():
    empty = make([])
    assert total_by_flow(empty, "2026-11", "outflow") == 0
    assert spending_by_category(empty, "2026-11").empty
    assert category_share(empty, "2026-11").empty
    assert monthly_trend(empty).empty


def test_category_share_adds_up_to_100():
    share = category_share(T, "2026-11")
    assert share["Shopping"] == 75
    assert round(share.sum()) == 100


def test_net_and_trend_zeros():
    assert net_cash_flow(T, "2026-11") == 600
    trend = monthly_trend(T, 3)
    assert list(trend["month"]) == ["2026-09", "2026-10", "2026-11"]
    assert trend.iloc[0]["outflow"] == 0   # September has no data