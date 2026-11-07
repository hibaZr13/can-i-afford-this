"""Pure calculations on DataFrames. No file access here."""
import pandas as pd


def _in_month(transactions, month):
    """Keep only the rows from one month, e.g. '2026-11'."""
    # to_datetime makes this work even if dates are still plain strings.
    # '%Y-%m' includes the year, so 2025-11 never matches 2026-11.
    dates = pd.to_datetime(transactions["date"])
    return transactions[dates.dt.strftime("%Y-%m") == month]


def total_by_flow(transactions, month, flow):
    """Total amount for one month and one flow ('inflow' or 'outflow')."""
    rows = _in_month(transactions, month)
    rows = rows[rows["flow"] == flow]
    # sum() of nothing is 0, so an empty month returns 0.0 without a special case
    return float(rows["amount"].sum())


def spending_by_category(transactions, month):
    """Outflow per category for the month, biggest first."""
    rows = _in_month(transactions, month)
    rows = rows[rows["flow"] == "outflow"]  # spending only, no income
    # Add up each category's amounts, then sort from biggest to smallest
    return rows.groupby("category")["amount"].sum().sort_values(ascending=False)


def category_share(transactions, month):
    """Each category as a percentage of the month's outflow."""
    spending = spending_by_category(transactions, month)
    total = spending.sum()

    # No spending means total is 0. Dividing would crash, so return the empty result.
    if total == 0:
        return spending

    # Each category divided by the total, as a percentage (adds up to ~100)
    return (spending / total * 100).round(2)


def net_cash_flow(transactions, month):
    """inflows - outflows."""
    return (total_by_flow(transactions, month, "inflow")
            - total_by_flow(transactions, month, "outflow"))


def monthly_trend(transactions, months=6):
    """One row per month (inflow, outflow, net) for the last `months` months.

    The last month is the latest one in the data. Months with no data show 0.
    """
    columns = ["month", "inflow", "outflow", "net"]

    # Nothing to show if there are no transactions at all
    if transactions.empty:
        return pd.DataFrame(columns=columns)

    # Build the list of months, ending at the newest month in the data
    last = pd.to_datetime(transactions["date"]).max().to_period("M")
    month_list = [str(m) for m in pd.period_range(end=last, periods=months, freq="M")]

    # One row per month, reusing the functions above
    rows = []
    for month in month_list:
        inflow = total_by_flow(transactions, month, "inflow")
        outflow = total_by_flow(transactions, month, "outflow")
        rows.append({"month": month, "inflow": inflow,
                     "outflow": outflow, "net": inflow - outflow})

    return pd.DataFrame(rows, columns=columns)