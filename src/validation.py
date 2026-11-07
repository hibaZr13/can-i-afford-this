"""Input validation.

Style: every validate_* function either RETURNS the cleaned value
or RAISES ValueError with a clear message. No (ok, message) tuples.
"""
import math
import pandas as pd
from src import config


def validate_amount(amount):
    """Amount must be a number > 0. Direction comes from `flow`, not the sign."""
    # Try to turn it into a float ("12.5" works, "abc" and None don't)
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number.")

    # float("nan") and float("inf") convert fine but make no sense as money
    if math.isnan(amount) or math.isinf(amount):
        raise ValueError("Amount must be a real number.")

    # Zero and negatives are rejected
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    # Round to cents so we never store 12.500000001
    return round(amount, 2)


def validate_date(date):
    """Must be a real date. Returns it as 'YYYY-MM-DD'.

    Future dates are allowed (useful for planned payments).
    """
    # Works for strings, date objects and datetime objects (Streamlit gives dates).
    # Keeping the first 10 characters gives 'YYYY-MM-DD' in every case.
    text = str(date).strip()[:10]

    # Strict format: '2026-13-45' or '02/11/2026' become NaT (invalid)
    parsed = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    if pd.isna(parsed):
        raise ValueError("Date must be a real date like 2026-11-02.")

    return parsed.strftime("%Y-%m-%d")


def validate_flow(flow):
    """Must be 'inflow' or 'outflow'."""
    # Clean it up a little so ' Outflow ' still works
    flow = str(flow).strip().lower()

    if flow not in config.FLOWS:
        raise ValueError(f"Flow must be one of: {', '.join(config.FLOWS)}.")

    return flow


def validate_category(category, flow, categories_df):
    """Category must exist AND belong to the given flow."""
    category = str(category).strip()

    # Look for this category name in the categories table
    match = categories_df[categories_df["name"] == category]
    if match.empty:
        raise ValueError(f"Unknown category: '{category}'.")

    # It exists, but is it the right type? ('Salary' can't be an outflow)
    if flow not in match["flow"].values:
        raise ValueError(f"Category '{category}' can't be used for {flow}.")

    return category


def validate_frequency(frequency):
    """Must be one of config.FREQUENCIES (weekly / monthly / yearly)."""
    frequency = str(frequency).strip().lower()

    if frequency not in config.FREQUENCIES:
        raise ValueError(f"Frequency must be one of: {', '.join(config.FREQUENCIES)}.")

    return frequency