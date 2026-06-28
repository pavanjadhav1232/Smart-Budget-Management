import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# --- DATABASE LOGIC ---
def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect("my_budget.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                   (id INTEGER PRIMARY KEY, date TEXT, category TEXT, 
                    amount REAL, desc TEXT)''')
    conn.commit()
    conn.close()

def add_expense(cat, amt, desc):
    """Saves a new expense and checks for overspending logic."""
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("my_budget.db")
    cursor = conn.cursor()
    
    # SMART LOGIC: Check average for this category before adding
    cursor.execute("SELECT AVG(amount) FROM expenses WHERE category = ?", (cat,))
    avg = cursor.fetchone()[0]
    
    # Show Streamlit warning instead of Rich print
    if avg and amt > avg * 1.5:
        st.warning(f"⚠️ **SMART ALERT:** This ${amt:.2f} is 50% higher than your usual {cat} spend!")

    cursor.execute("INSERT INTO expenses (date, category, amount, desc) VALUES (?, ?, ?, ?)",
                   (date, cat, amt, desc))
    conn.commit()
    conn.close()
    st.success(f"✔ **Success:** Recorded ${amt:.2f} under {cat}.")

def get_expenses():
    """Fetches all expenses as a Pandas DataFrame for easy Streamlit viewing."""
    conn = sqlite3.connect("my_budget.db")
    df = pd.read_sql_query("SELECT date AS Date, category AS Category, amount AS Amount, desc AS Description FROM expenses", conn)
    conn.close()
    return df

# --- APP LAYOUT ---
st.set_page_config(page_title="Smart Budget", page_icon="🚀")

# Initialize the database when the app loads
init_db()

st.title("🚀 SMART BUDGET APP")

# Use tabs to replicate your CLI menu
tab1, tab2 = st.tabs(["➕ Add Expense", "📊 View Report"])

# --- TAB 1: ADD EXPENSES ---
with tab1:
    st.subheader("Record a New Expense")
    
    # A form groups the inputs together until the user clicks submit
    with st.form("expense_form", clear_on_submit=True):
        cat = st.text_input("Category (e.g. Food, Rent)").capitalize()
        amt = st.number_input("Amount ($)", min_value=0.0, format="%.2f", step=1.0)
        desc = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            if cat and amt > 0:
                add_expense(cat, amt, desc)
            else:
                st.error("Please enter a valid category and an amount greater than 0.")

# --- TAB 2: VIEW REPORT ---
with tab2:
    st.subheader("📊 My Spending Report")
    df = get_expenses()
    
    if not df.empty:
        # Format the amount column for display
        df_display = df.copy()
        df_display['Amount'] = df_display['Amount'].apply(lambda x: f"${x:.2f}")
        
        # Display the interactive table
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Calculate and show the total using a nice metric widget
        total = df['Amount'].sum()
        st.metric(label="Total Monthly Spend", value=f"${total:.2f}")
    else:
        st.info("No expenses recorded yet. Head over to the 'Add Expense' tab to get started!")