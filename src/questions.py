"""Predefined questions. Descriptive only, no financial advice."""


def how_much_spent_on_category(transactions, category, month):
    raise NotImplementedError


def top_spending_category(transactions, month):
    raise NotImplementedError


def money_left_this_month(month):
    raise NotImplementedError


def upcoming_commitments(days=30):
    raise NotImplementedError


def savings_progress_summary():
    raise NotImplementedError


QUESTIONS = {
    # "label shown in UI": function
}
