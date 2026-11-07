"""Streamlit interface. Run with:  streamlit run src/app.py

Keep this thin: call the other modules, don't put logic here.
"""
import streamlit as st

st.set_page_config(page_title="Can I Afford This?", layout="wide")
st.title("Can I Afford This?")

tab_overview, tab_add, tab_recurring, tab_savings, tab_questions = st.tabs(
    ["Overview", "Add entry", "Recurring", "Savings", "Ask a question"]
)

with tab_overview:
    st.write("TODO: month picker, spendable / spent / remaining, category chart")
with tab_add:
    st.write("TODO: inflow/outflow form -> transactions.add_transaction")
with tab_recurring:
    st.write("TODO: list + add subscriptions and instalment plans")
with tab_savings:
    st.write("TODO: goals, progress, add deposit/withdrawal")
with tab_questions:
    st.write("TODO: dropdown from questions.QUESTIONS")
