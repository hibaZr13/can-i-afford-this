"""Add / edit / delete / filter money movements (inflows and outflows)."""
import pandas as pd
from src import config
from src.data_manager import load_transactions, load_categories, save_csv, next_id
from src.validation import (
    validate_amount, validate_date, validate_flow, validate_category,
)


def _text(value):
    """Turn None / NaN (empty CSV cell) into '', anything else into clean text."""
    return "" if pd.isna(value) else str(value).strip()


def _clean(date, amount, flow, category, counterparty, notes=""):
    """Validate every field and return them cleaned, as a dict.

    Shared by add and update, so the rules live in one place.
    """
    flow = validate_flow(flow)
    counterparty = _text(counterparty)
    if not counterparty:  # name is required, notes are optional
        raise ValueError("Counterparty (name) is required.")

    return {
        "date": validate_date(date),
        "amount": validate_amount(amount),
        "flow": flow,
        "category": validate_category(category, flow, load_categories()),
        "counterparty": counterparty,
        "notes": _text(notes),
    }


def _save(df):
    """Save the table, writing dates as plain YYYY-MM-DD."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    save_csv(df, config.TRANSACTIONS_CSV)


def add_transaction(date, amount, flow, category, counterparty, notes="", recurring_id=None):
    """Validate, build a record, append to transactions.csv, return the new id."""
    # 1. Validate everything (raises ValueError if anything is wrong)
    record = _clean(date, amount, flow, category, counterparty, notes)

    # 2. Load the current table and pick the next id
    df = load_transactions()
    record["transaction_id"] = next_id(df, "transaction_id")
    record["recurring_id"] = recurring_id  # None -> empty cell in the CSV

    # 3. Add the new row at the bottom and save
    new_row = pd.DataFrame([record], columns=config.TRANSACTION_COLUMNS)
    df = pd.concat([df, new_row], ignore_index=True)
    _save(df)

    # 4. Tell the caller which id we gave it
    return record["transaction_id"]


def update_transaction(transaction_id, **changes):
    """Edit an existing transaction. Example: update_transaction(3, notes='bus')."""
    df = load_transactions()

    # Find the row to edit
    mask = df["transaction_id"] == transaction_id
    if not mask.any():
        raise ValueError(f"Transaction {transaction_id} not found.")

    # Start from the current values, apply the changes, then validate it all again.
    # (An unknown field name in `changes` raises a TypeError here, which is fine.)
    fields = ["date", "amount", "flow", "category", "counterparty", "notes"]
    data = df.loc[mask, fields].iloc[0].to_dict()
    data.update(changes)
    cleaned = _clean(**data)

    # Write the cleaned values back into that one row
    for column, value in cleaned.items():
        if column == "date":
            value = pd.to_datetime(value)  # the column holds real dates
        df.loc[mask, column] = value

    _save(df)


def delete_transaction(transaction_id):
    """Remove one transaction by id."""
    df = load_transactions()

    mask = df["transaction_id"] == transaction_id
    if not mask.any():
        raise ValueError(f"Transaction {transaction_id} not found.")

    # Keep every row except the one we want gone
    _save(df[~mask])


def get_transactions(month=None, flow=None, category=None):
    """Return a filtered DataFrame. `month` like '2026-11'."""
    df = load_transactions()

    # Each filter is optional. They stack, so all given filters must match.
    if month:
        # '%Y-%m' includes the year, so 2025-11 won't match 2026-11
        df = df[df["date"].dt.strftime("%Y-%m") == month]
    if flow:
        df = df[df["flow"] == flow]
    if category:
        df = df[df["category"] == category]

    # No matches just gives an empty DataFrame, not an error
    return df