"""Pure calculations on DataFrames. No file access here."""


def total_by_flow(transactions, month, flow):
    raise NotImplementedError


def spending_by_category(transactions, month):
    raise NotImplementedError


def category_share(transactions, month):
    """Each category as a percentage of the month's outflow."""
    raise NotImplementedError


def net_cash_flow(transactions, month):
    """inflows - outflows."""
    raise NotImplementedError


def monthly_trend(transactions, months=6):
    raise NotImplementedError
