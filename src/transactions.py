"""Add / edit / delete / filter money movements (inflows and outflows)."""


def add_transaction(date, amount, flow, category, counterparty, notes="", recurring_id=None):
    """Validate, build a record, append to transactions.csv, return the new id."""
    raise NotImplementedError


def update_transaction(transaction_id, **changes):
    """TODO: edit an existing transaction (fix a typo, add a note)."""
    raise NotImplementedError


def delete_transaction(transaction_id):
    raise NotImplementedError


def get_transactions(month=None, flow=None, category=None):
    """Return a filtered DataFrame. `month` like '2026-11'."""
    raise NotImplementedError
