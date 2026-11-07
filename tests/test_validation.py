import pytest
import pandas as pd
from src.validation import *

CATS = pd.DataFrame({"name": ["Food", "Salary"], "flow": ["outflow", "inflow"]})


def test_amount():
    assert validate_amount("12.5") == 12.5
    for bad in [-20, 0, "", "abc", None, float("nan")]:
        with pytest.raises(ValueError):
            validate_amount(bad)


def test_date():
    assert validate_date("2026-11-02") == "2026-11-02"
    for bad in ["2026-13-45", "02/11/2026", "", None]:
        with pytest.raises(ValueError):
            validate_date(bad)


def test_flow_and_frequency():
    assert validate_flow(" Outflow ") == "outflow"
    assert validate_frequency("Monthly") == "monthly"
    with pytest.raises(ValueError):
        validate_flow("sideways")
    with pytest.raises(ValueError):
        validate_frequency("daily")


def test_category():
    assert validate_category("Food", "outflow", CATS) == "Food"
    with pytest.raises(ValueError):
        validate_category("Salary", "outflow", CATS)  # wrong flow
    with pytest.raises(ValueError):
        validate_category("Nope", "outflow", CATS)    # doesn't exist