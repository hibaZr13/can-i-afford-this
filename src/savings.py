"""Savings goals and deposits/withdrawals."""


def add_goal(name, target_amount, target_date=None, notes=""):
    raise NotImplementedError


def add_savings_entry(goal_id, amount, date, notes=""):
    """Positive = deposit, negative = withdrawal."""
    raise NotImplementedError


def get_goal_balance(goal_id):
    raise NotImplementedError


def get_goal_progress(goal_id):
    """TODO: percent of target reached, amount left, monthly saving needed."""
    raise NotImplementedError


def get_total_savings():
    raise NotImplementedError
