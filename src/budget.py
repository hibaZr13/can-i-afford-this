"""Spendable money for a month.

Decisions (copy these into your README's design section):
- Savings do NOT count as spent. They live in their own CSV and move money,
  they aren't consumption. Remaining only looks at outflow transactions.
- Inflows do NOT change spendable. Spendable is a number the user chooses.
- No entry for a month -> carry over the most recent earlier month.
  If there is no earlier month either, spendable is 0.
"""
import pandas as pd
from src.data_manager import load_budgets, load_transactions, save_csv
from src.validation import validate_date
from src import config
from src.analytics import total_by_flow


def _check_month(month):
    """Month must look like '2026-11'. Returns it unchanged if valid."""
    # Reuse the date validator by adding a day: '2026-11' -> '2026-11-01'
    validate_date(f"{month}-01")
    return month


def remaining_amount(spendable, spent):
    """The pure math, kept separate so it's easy to test: spendable - spent."""
    # Can go negative on purpose: -200 means "200 over the limit"
    return round(spendable - spent, 2)


def set_spendable_amount(month, amount):
    """Set the spendable amount for a month (replaces it if it already exists)."""
    _check_month(month)

    # 0 is allowed here (unlike transaction amounts), negatives are not
    try:
        amount = round(float(amount), 2)
    except (TypeError, ValueError):
        raise ValueError("Spendable amount must be a number.")
    if amount < 0:
        raise ValueError("Spendable amount can't be negative.")

    df = load_budgets()

    # Drop the old row for this month (if any), so there's never a duplicate
    df = df[df["month"] != month]

    # Add the new row, keep months in order, save
    new_row = pd.DataFrame([{"month": month, "spendable_amount": amount}],
                           columns=config.BUDGET_COLUMNS)
    df = pd.concat([df, new_row], ignore_index=True).sort_values("month")
    save_csv(df, config.BUDGETS_CSV)


def get_spendable_amount(month):
    """Spendable amount for a month, carrying over the last known one if needed."""
    _check_month(month)
    df = load_budgets()

    # Exact match: use it
    exact = df[df["month"] == month]
    if not exact.empty:
        return float(exact.iloc[0]["spendable_amount"])

    # No match: look at earlier months. 'YYYY-MM' strings sort correctly as text.
    earlier = df[df["month"] < month].sort_values("month")
    if not earlier.empty:
        return float(earlier.iloc[-1]["spendable_amount"])  # latest earlier month

    # Nothing set at all yet
    return 0.0


def calculate_remaining(month):
    """spendable - outflows for the month."""
    spendable = get_spendable_amount(month)
    spent = total_by_flow(load_transactions(), month, "outflow")
    return remaining_amount(spendable, spent)