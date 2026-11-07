"""Data layer: the ONLY module that reads/writes CSV files."""
import pandas as pd


def load_csv(path, columns):
    """Load a CSV into a DataFrame with the right dtypes.

    TODO: handle missing file (create empty with `columns`), empty file,
    parse dates, make amount numeric.
    """
    raise NotImplementedError


def save_csv(df, path):
    """Write a DataFrame to CSV.

    TODO: decide on overwrite vs. append.
    """
    raise NotImplementedError


def next_id(df, id_column):
    """Return the next unused id for `id_column`.

    TODO: decide id format (int vs. 'R001' style) and handle empty df.
    """
    raise NotImplementedError


def load_transactions(): raise NotImplementedError
def load_recurring(): raise NotImplementedError
def load_budgets(): raise NotImplementedError
def load_savings_goals(): raise NotImplementedError
def load_savings_entries(): raise NotImplementedError
def load_categories(): raise NotImplementedError
