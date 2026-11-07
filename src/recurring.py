"""Subscriptions, recurring income and instalment plans.

Decision (copy this into your README's design section):
- Rules GENERATE real transactions only up to a given date (normally today).
- The future is only FORECAST (get_upcoming_payments), never saved.
  So planned money is never mistaken for money already spent.
- A payment counts as "already recorded" if a transaction exists with the same
  recurring_id and the same date. That's how we avoid duplicates.
"""
import pandas as pd
from src import config
from src.data_manager import load_recurring, load_transactions, load_categories, save_csv, next_id
from src.validation import (
    validate_amount, validate_date, validate_flow, validate_category, validate_frequency,
)
from src.transactions import add_transaction

# How each frequency moves the date forward (used with pd.DateOffset)
UNIT = {"weekly": "weeks", "monthly": "months", "yearly": "years"}


def _today(today=None):
    """Today's date at midnight. `today` is only here so tests can fix the date."""
    return (pd.Timestamp(today) if today else pd.Timestamp.today()).normalize()


def _save(df):
    """Save the table: dates as YYYY-MM-DD, total_payments as whole numbers."""
    df = df.copy()
    for col in ["start_date", "end_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")  # empty stays empty
    # Int64 writes 6 instead of 6.0, and keeps empty cells empty
    df["total_payments"] = pd.to_numeric(df["total_payments"]).astype("Int64")
    save_csv(df, config.RECURRING_CSV)


def _get_rule(recurring_id):
    """Return one rule as a Series, or raise if the id doesn't exist."""
    df = load_recurring()
    match = df[df["recurring_id"] == recurring_id]
    if match.empty:
        raise ValueError(f"Recurring rule {recurring_id} not found.")
    return match.iloc[0]


def _due_dates(rule, up_to):
    """All due dates of a rule from its start date up to `up_to` (a Timestamp).

    Stops at end_date and at total_payments, whichever comes first.
    """
    start = pd.Timestamp(rule["start_date"])
    unit = UNIT[rule["frequency"]]
    dates = []
    i = 0
    while True:
        # Always count from the START date (not from the last date).
        # That way Jan 31 -> Feb 28 -> Mar 31, instead of drifting to the 28th forever.
        date = start + pd.DateOffset(**{unit: i})
        if date > up_to:
            break
        if pd.notna(rule["end_date"]) and date > rule["end_date"]:
            break
        if pd.notna(rule["total_payments"]) and i >= rule["total_payments"]:
            break
        dates.append(date)
        i += 1
    return dates


def _recorded():
    """Set of (recurring_id, 'YYYY-MM-DD') for payments already in transactions."""
    t = load_transactions()
    dates = pd.to_datetime(t["date"]).dt.strftime("%Y-%m-%d")
    return set(zip(t["recurring_id"], dates))


def add_recurring(name, flow, amount, category, frequency, start_date,
                  end_date=None, total_payments=None, notes=""):
    """total_payments set -> instalment plan. Empty -> open-ended subscription."""
    # Validate everything (raises ValueError if anything is wrong)
    name = str(name).strip()
    if not name:
        raise ValueError("Name is required.")
    flow = validate_flow(flow)
    amount = validate_amount(amount)
    category = validate_category(category, flow, load_categories())
    frequency = validate_frequency(frequency)
    start_date = validate_date(start_date)

    # End date is optional, but can't be before the start
    if end_date is None or str(end_date).strip() == "":
        end_date = pd.NaT
    else:
        end_date = pd.Timestamp(validate_date(end_date))
        if end_date < pd.Timestamp(start_date):
            raise ValueError("End date can't be before the start date.")

    # Total payments is optional, but if given it must be a whole number > 0
    if total_payments is None or str(total_payments).strip() == "":
        total_payments = None
    else:
        try:
            number = float(total_payments)
        except ValueError:
            raise ValueError("Total payments must be a number.")
        if number <= 0 or number != int(number):
            raise ValueError("Total payments must be a whole number above 0.")
        total_payments = int(number)

    # New id (R001, R002, ...), build the row, add it, save
    df = load_recurring()
    recurring_id = next_id(df, "recurring_id", prefix="R")
    new_row = pd.DataFrame([{
        "recurring_id": recurring_id, "name": name, "flow": flow, "amount": amount,
        "category": category, "frequency": frequency,
        "start_date": pd.Timestamp(start_date), "end_date": end_date,
        "total_payments": total_payments, "active": True, "notes": str(notes).strip(),
    }], columns=config.RECURRING_COLUMNS)
    _save(pd.concat([df, new_row], ignore_index=True))
    return recurring_id


def get_active_recurring():
    """Only the rules that haven't been cancelled."""
    df = load_recurring()
    # astype(str) so it works whether the CSV gave us True or "true"
    return df[df["active"].astype(str).str.lower() == "true"]


def generate_due_transactions(up_to_date, since=None):
    """Create the missing transactions for every active rule, up to `up_to_date`.

    Safe to run many times: payments already recorded are skipped.
    `since` ignores older due dates (otherwise a rule starting in January
    would create all the old months at once). Returns how many were created.
    """
    up_to = pd.Timestamp(validate_date(up_to_date))
    since = pd.Timestamp(validate_date(since)) if since else None
    recorded = _recorded()
    created = 0

    for _, rule in get_active_recurring().iterrows():
        # enumerate gives the payment number (1, 2, 3...) used in the note
        for number, date in enumerate(_due_dates(rule, up_to), start=1):
            if since is not None and date < since:
                continue
            key = (rule["recurring_id"], date.strftime("%Y-%m-%d"))
            if key in recorded:
                continue  # already in transactions.csv

            # Instalment plans get a note like "Installment 2 of 6"
            notes = ""
            if pd.notna(rule["total_payments"]):
                notes = f"Installment {number} of {int(rule['total_payments'])}"

            add_transaction(key[1], rule["amount"], rule["flow"], rule["category"],
                            rule["name"], notes, rule["recurring_id"])
            recorded.add(key)
            created += 1

    return created


def get_upcoming_payments(days=30, today=None):
    """Forecast: payments due from today to today + days that aren't recorded yet.

    Nothing is saved. Includes inflows too (use the 'flow' column to filter).
    """
    today = _today(today)
    end = today + pd.Timedelta(days=days)
    recorded = _recorded()

    rows = []
    for _, rule in get_active_recurring().iterrows():
        for date in _due_dates(rule, end):
            key = (rule["recurring_id"], date.strftime("%Y-%m-%d"))
            if date >= today and key not in recorded:
                rows.append({
                    "date": date, "name": rule["name"], "flow": rule["flow"],
                    "amount": rule["amount"], "category": rule["category"],
                    "recurring_id": rule["recurring_id"],
                })

    columns = ["date", "name", "flow", "amount", "category", "recurring_id"]
    return pd.DataFrame(rows, columns=columns).sort_values("date").reset_index(drop=True)


def get_instalment_progress(recurring_id):
    """Progress of an instalment plan, as a dict."""
    rule = _get_rule(recurring_id)
    if pd.isna(rule["total_payments"]):
        raise ValueError(f"{recurring_id} is not an instalment plan.")

    # Payments made = transactions created by this rule
    t = load_transactions()
    paid = t[t["recurring_id"] == recurring_id]

    total = int(rule["total_payments"])
    made = len(paid)
    left = max(total - made, 0)
    return {
        "payments_made": made,
        "payments_left": left,
        "amount_paid": round(float(paid["amount"].sum()), 2),
        "amount_remaining": round(left * float(rule["amount"]), 2),
    }


def cancel_recurring(recurring_id):
    """Stop a rule. Its old transactions stay (history is kept)."""
    _get_rule(recurring_id)  # raises if it doesn't exist
    df = load_recurring()
    df["active"] = df["active"].astype(object)  # so the column can hold True/False cleanly
    df.loc[df["recurring_id"] == recurring_id, "active"] = False
    _save(df)