import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize Console for beautiful UI
console = Console()

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
    
    if avg and amt > avg * 1.5:
        console.print(f"[bold yellow]⚠️  SMART ALERT:[/bold yellow] This ${amt} is 50% higher than your usual {cat} spend!")

    cursor.execute("INSERT INTO expenses (date, category, amount, desc) VALUES (?, ?, ?, ?)",
                   (date, cat, amt, desc))
    conn.commit()
    conn.close()
    console.print(f"[bold green]✔ Success:[/bold green] Recorded ${amt} under {cat}.")

def show_report():
    """Generates a summary table of all spending."""
    conn = sqlite3.connect("my_budget.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount, desc FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    table = Table(title="📊 My Spending Report")
    table.add_column("Date", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Description")

    total = 0
    for row in rows:
        table.add_row(row[0], row[1], f"${row[2]:.2f}", row[3])
        total += row[2]

    console.print(table)
    console.print(Panel(f"[bold white]Total Monthly Spend: ${total:.2f}[/bold white]", expand=False))

# --- MAIN MENU LOGIC ---
def main():
    init_db()
    console.print(Panel.fit("🚀 SMART BUDGET CLI v1.0", style="bold blue"))
    
    while True:
        console.print("\n[1] Add Expense  [2] View Report  [3] Exit")
        choice = input("Select an option: ")

        if choice == "1":
            cat = input("Category (e.g. Food, Rent): ").capitalize()
            try:
                amt = float(input("Amount: "))
                desc = input("Description: ")
                add_expense(cat, amt, desc)
            except ValueError:
                console.print("[red]Invalid amount. Please enter a number.[/red]")
        
        elif choice == "2":
            show_report()
            
        elif choice == "3":
            console.print("[italic blue]Goodbye! Keep saving![/italic blue]")
            break
        else:
            console.print("[red]Invalid choice. Try again.[/red]")

if __name__ == "__main__":
    main()