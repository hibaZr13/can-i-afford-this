"""Input validation.

DECIDE: raise ValueError, or return (ok, error_message)? Be consistent.
"""


def validate_amount(amount):
    """TODO: numeric and > 0 (direction comes from `flow`, not the sign)."""
    raise NotImplementedError


def validate_date(date):
    """TODO: valid date, stored as YYYY-MM-DD. Are future dates allowed?"""
    raise NotImplementedError


def validate_flow(flow):
    """TODO: must be one of config.FLOWS."""
    raise NotImplementedError


def validate_category(category, flow, categories_df):
    """TODO: category must exist AND match the flow."""
    raise NotImplementedError


def validate_frequency(frequency):
    """TODO: must be one of config.FREQUENCIES."""
    raise NotImplementedError
