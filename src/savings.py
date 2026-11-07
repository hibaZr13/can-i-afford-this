"""Savings goals and deposits/withdrawals.

Decisions (copy these into your README's design section):
- Savings are kept apart from transactions, so they never count as spending.
- A withdrawal can't take a goal below 0 (you can't take out more than is saved).
"""
import pandas as pd
from src import config
from src.data_manager import load_savings_goals, load_savings_entries, save_csv, next_id
from src.validation import validate_amount, validate_date


def _save(df, path, date_column):
    """Save a table, writing its date column as plain YYYY-MM-DD (empty stays empty)."""
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column]).dt.strftime("%Y-%m-%d")
    save_csv(df, path)


def _check_goal(goal_id):
    """Return the goal's row as a Series, or raise if the id doesn't exist."""
    goals = load_savings_goals()
    match = goals[goals["goal_id"] == goal_id]
    if match.empty:
        raise ValueError(f"Goal {goal_id} not found.")
    return match.iloc[0]


def add_goal(name, target_amount, target_date=None, notes=""):
    """Create a savings goal and return its new id (G001, G002, ...)."""
    # Name is required, notes are optional
    name = str(name).strip()
    if not name:
        raise ValueError("Goal name is required.")

    # Target amount must be a positive number. Target date is optional.
    target_amount = validate_amount(target_amount)
    if target_date is None or str(target_date).strip() == "":
        target_date = ""  # stored as an empty cell
    else:
        target_date = validate_date(target_date)

    # Pick the next id and build the new row
    goals = load_savings_goals()
    goal_id = next_id(goals, "goal_id", prefix="G")
    new_row = pd.DataFrame([{
        "goal_id": goal_id, "name": name, "target_amount": target_amount,
        "target_date": target_date, "notes": str(notes).strip(),
    }], columns=config.SAVINGS_GOAL_COLUMNS)

    # Add it at the bottom and save
    goals = pd.concat([goals, new_row], ignore_index=True)
    _save(goals, config.SAVINGS_GOALS_CSV, "target_date")
    return goal_id


def get_goal_balance(goal_id):
    """How much is saved in one goal (deposits minus withdrawals)."""
    _check_goal(goal_id)  # raises if the goal doesn't exist
    entries = load_savings_entries()
    # Add up this goal's entries only. No entries means 0.0.
    return round(float(entries.loc[entries["goal_id"] == goal_id, "amount"].sum()), 2)


def add_savings_entry(goal_id, amount, date, notes=""):
    """Positive = deposit, negative = withdrawal. Returns the new entry id."""
    _check_goal(goal_id)  # raises if the goal doesn't exist

    # Amount must be a real number that isn't 0. The sign matters here.
    try:
        amount = round(float(amount), 2)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number.")
    if pd.isna(amount) or amount in (0, float("inf"), float("-inf")):
        raise ValueError("Amount must be a real number, not 0.")

    date = validate_date(date)

    # A withdrawal can't take the goal below 0
    if get_goal_balance(goal_id) + amount < 0:
        raise ValueError("Not enough saved in this goal for that withdrawal.")

    # Next id, new row, save
    entries = load_savings_entries()
    entry_id = next_id(entries, "entry_id")
    new_row = pd.DataFrame([{
        "entry_id": entry_id, "date": date, "goal_id": goal_id,
        "amount": amount, "notes": str(notes).strip(),
    }], columns=config.SAVINGS_ENTRY_COLUMNS)
    entries = pd.concat([entries, new_row], ignore_index=True)
    _save(entries, config.SAVINGS_ENTRIES_CSV, "date")
    return entry_id


def get_goal_progress(goal_id, today=None):
    """Progress of one goal, as a dict.

    monthly_needed is None when there's no target date or the date has passed.
    `today` is only here so tests can fix the date.
    """
    goal = _check_goal(goal_id)
    target = float(goal["target_amount"])
    balance = get_goal_balance(goal_id)

    # Percent of the target reached (can go above 100 if over-saved)
    percent = round(balance / target * 100, 2)
    # Never negative: once the goal is reached, nothing is left
    amount_left = round(max(target - balance, 0), 2)

    # How much per month is needed to hit the target date?
    monthly_needed = None
    if amount_left == 0:
        monthly_needed = 0.0  # already reached
    elif pd.notna(goal["target_date"]):
        today = pd.Timestamp(today) if today else pd.Timestamp.today()
        target_date = pd.Timestamp(goal["target_date"])
        if target_date > today:  # a date in the past gives None
            # Whole months left, counted by calendar month, at least 1
            months_left = (target_date.year - today.year) * 12 + target_date.month - today.month
            monthly_needed = round(amount_left / max(months_left, 1), 2)

    return {"balance": balance, "target": target, "percent": percent,
            "amount_left": amount_left, "monthly_needed": monthly_needed}


def get_total_savings():
    """Total saved across all goals."""
    entries = load_savings_entries()
    return round(float(entries["amount"].sum()), 2)