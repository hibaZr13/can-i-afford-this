"""Subscriptions, recurring income and instalment plans.

OPEN DESIGN QUESTION: do recurring rules auto-generate transactions,
or only forecast upcoming ones? Decide before implementing.
"""


def add_recurring(name, flow, amount, category, frequency, start_date,
                  end_date=None, total_payments=None, notes=""):
    """total_payments set -> instalment plan. Empty -> open-ended subscription."""
    raise NotImplementedError


def get_active_recurring():
    raise NotImplementedError


def generate_due_transactions(up_to_date):
    """TODO: create transactions for due rules, without duplicating."""
    raise NotImplementedError


def get_upcoming_payments(days=30):
    raise NotImplementedError


def get_instalment_progress(recurring_id):
    """TODO: payments made, payments left, amount remaining."""
    raise NotImplementedError


def cancel_recurring(recurring_id):
    raise NotImplementedError
