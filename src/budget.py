"""Spendable money for a month."""


def set_spendable_amount(month, amount):
    raise NotImplementedError


def get_spendable_amount(month):
    """TODO: what if no entry exists for that month? Carry over the previous one?"""
    raise NotImplementedError


def calculate_remaining(month):
    """spendable - outflows. DECIDE: do savings transfers count as spent?"""
    raise NotImplementedError
