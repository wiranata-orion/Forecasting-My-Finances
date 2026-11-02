import csv
import shutil
import sqlite3
from pathlib import Path

recovery_dir = Path(__file__).parent
snapshot = recovery_dir / "finance-sqlite-snapshot.db"
transactions_csv = recovery_dir / "recovered-original-transactions.csv"
plans_csv = recovery_dir / "carved-planned-expenses.csv"
recovered_db = recovery_dir / "finance-recovered-preview.db"

if recovered_db.exists():
    recovered_db.unlink()

shutil.copy2(snapshot, recovered_db)

with transactions_csv.open(encoding="utf-8", newline="") as file:
    transactions = list(csv.DictReader(file))
with plans_csv.open(encoding="utf-8", newline="") as file:
    plans = list(csv.DictReader(file))

connection = sqlite3.connect(recovered_db)
connection.execute("PRAGMA foreign_keys = ON")
connection.execute("DELETE FROM transactions")
connection.execute("DELETE FROM planned_expenses")
connection.execute("DELETE FROM wallets")
connection.execute("DELETE FROM wallet_adjustments")
connection.execute("DELETE FROM settings WHERE key IN ('cycle_periods', 'payday_start_day', 'payday_end_day')")
connection.executemany(
    """
    INSERT INTO transactions
        (id, date, description, amount, type, category, wallet, transfer_to, savings_status, created_at)
    VALUES
        (:id, :date, :description, :amount, :type, :category, :wallet, :transfer_to, :savings_status, :created_at)
    """,
    transactions,
)
connection.executemany(
    """
    INSERT INTO planned_expenses
        (id, title, amount, category, probability, date, notes, created_at)
    VALUES
        (:id, :title, :amount, :category, :probability, :date, :notes, :created_at)
    """,
    plans,
)

wallet_names = sorted({
    name.strip()
    for transaction in transactions
    for name in (transaction["wallet"], transaction["transfer_to"])
    if name and name.strip()
})
connection.executemany(
    "INSERT INTO wallets (id, name, initial_balance, created_at) VALUES (?, ?, 0, ?)",
    [(f"recovered-wallet-{index}", name, "2026-11-02T22:30:00") for index, name in enumerate(wallet_names, start=1)],
)
connection.executemany(
    "INSERT INTO settings (key, value) VALUES (?, ?)",
    [
        ("payday_start_day", "24"),
        ("payday_end_day", "23"),
        ("cycle_periods", "{}"),
    ],
)
connection.commit()

integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
transaction_count = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
wallet_count = connection.execute("SELECT COUNT(*) FROM wallets").fetchone()[0]
plan_count = connection.execute("SELECT COUNT(*) FROM planned_expenses").fetchone()[0]
connection.close()

print(f"Preview database: {recovered_db}")
print(f"Integrity: {integrity}")
print(f"Recovered transactions: {transaction_count}")
print(f"Recovered wallets: {wallet_count}")
print(f"Recovered planned expenses: {plan_count}")
