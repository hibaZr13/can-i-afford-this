"""Data layer: the ONLY module that reads/writes CSV files."""
import pandas as pd
from src import config

# Columns that should be converted to real dates / numbers when loaded
DATE_COLUMNS = ["date", "start_date", "end_date", "target_date"]
NUMBER_COLUMNS = ["amount", "target_amount", "spendable_amount", "total_payments"]


def load_csv(path, columns): 
    """Load a CSV into a DataFrame with the right dtypes."""
    # Try to read the file. If it's missing or completely empty,
    # start from an empty table that only has the headers.
    try:
        df = pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=columns)
        save_csv(df, path)  # create the file so it exists next time

    # Turn date columns into real dates (bad or empty values become NaT)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")


    # Turn number columns into numbers (bad or empty values become NaN)
    for col in NUMBER_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # A text column that is empty everywhere gets read as float (all NaN).
    # Turn it into a normal "object" column so it can hold text later.
    for col in df.columns:
        if col not in DATE_COLUMNS + NUMBER_COLUMNS and df[col].dtype == "float64":
            df[col] = df[col].astype(object)

    return df




def save_csv(df, path):
    """Write a DataFrame to CSV (overwrites the whole file)."""
    # We always load, change, then save the full table, so overwrite is simplest.
    # index=False stops pandas from adding an extra 0,1,2... column.
    df.to_csv(path, index=False)


def next_id(df, id_column, prefix="", width=3): #auto generate ids
    """Return the next unused id.

    prefix="" -> plain numbers: 1, 2, 3
    prefix="R" -> 'R001', 'R002', ...
    """
    # Pull the digits out of every id ("R003" -> 3, 7 -> 7)
    numbers = df[id_column].astype(str).str.extract(r"(\d+)")[0].dropna().astype(int)

    # Highest number so far (0 if the table is empty), plus one
    new_number = int(numbers.max()) + 1 if not numbers.empty else 1

    # Plain number, or prefixed and zero-padded
    if prefix == "":
        return new_number
    return f"{prefix}{new_number:0{width}d}"

#example: next_id(load_recurring(), "recurring_id", prefix="R")    # 'R004'


# One-liners: each loader just calls load_csv with its own file and columns
def load_transactions():
    return load_csv(config.TRANSACTIONS_CSV, config.TRANSACTION_COLUMNS)

def load_recurring():
    return load_csv(config.RECURRING_CSV, config.RECURRING_COLUMNS)

def load_budgets():
    return load_csv(config.BUDGETS_CSV, config.BUDGET_COLUMNS)

def load_savings_goals():
    return load_csv(config.SAVINGS_GOALS_CSV, config.SAVINGS_GOAL_COLUMNS)

def load_savings_entries():
    return load_csv(config.SAVINGS_ENTRIES_CSV, config.SAVINGS_ENTRY_COLUMNS)

def load_categories():
    return load_csv(config.CATEGORIES_CSV, ["name", "flow"])