"""Central place for paths and constants. No logic here."""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TRANSACTIONS_CSV = DATA_DIR / "transactions.csv"
RECURRING_CSV = DATA_DIR / "recurring.csv"
BUDGETS_CSV = DATA_DIR / "budgets.csv"
SAVINGS_GOALS_CSV = DATA_DIR / "savings_goals.csv"
SAVINGS_ENTRIES_CSV = DATA_DIR / "savings_entries.csv"
CATEGORIES_CSV = DATA_DIR / "categories.csv"

TRANSACTION_COLUMNS = [
    "transaction_id", "date", "amount", "flow",
    "category", "counterparty", "notes", "recurring_id",
]
RECURRING_COLUMNS = [
    "recurring_id", "name", "flow", "amount", "category", "frequency",
    "start_date", "end_date", "total_payments", "active", "notes",
]
BUDGET_COLUMNS = ["month", "spendable_amount"]
SAVINGS_GOAL_COLUMNS = ["goal_id", "name", "target_amount", "target_date", "notes"]
SAVINGS_ENTRY_COLUMNS = ["entry_id", "date", "goal_id", "amount", "notes"]

FLOWS = ("inflow", "outflow")
FREQUENCIES = ("weekly", "monthly", "yearly")
