import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'finance.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table: transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        wallet TEXT DEFAULT '',
        transfer_to TEXT DEFAULT '',
        savings_status TEXT NOT NULL DEFAULT 'non_savings',
        created_at TEXT NOT NULL
    )
    """)

    # Table: wallets (user-defined wallet/account names)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        initial_balance REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    transaction_columns = {row['name'] for row in cursor.execute("PRAGMA table_info(transactions)")}
    if 'wallet' not in transaction_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN wallet TEXT DEFAULT ''")
    if 'transfer_to' not in transaction_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN transfer_to TEXT DEFAULT ''")
    if 'savings_status' not in transaction_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN savings_status TEXT NOT NULL DEFAULT 'non_savings'")

    wallet_columns = {row['name'] for row in cursor.execute("PRAGMA table_info(wallets)")}
    if 'initial_balance' not in wallet_columns:
        cursor.execute("ALTER TABLE wallets ADD COLUMN initial_balance REAL NOT NULL DEFAULT 0")

    # Table: planned_expenses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planned_expenses (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        probability INTEGER DEFAULT 100,
        date TEXT NOT NULL,
        notes TEXT,
        wallet TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)
    planned_columns = {row['name'] for row in cursor.execute("PRAGMA table_info(planned_expenses)")}
    if 'wallet' not in planned_columns:
        cursor.execute("ALTER TABLE planned_expenses ADD COLUMN wallet TEXT DEFAULT ''")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_expenses (
        id TEXT PRIMARY KEY,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        total_occurrences INTEGER NOT NULL DEFAULT 1,
        remaining_occurrences INTEGER NOT NULL DEFAULT 1,
        type TEXT NOT NULL DEFAULT 'expense',
        wallet TEXT DEFAULT '',
        transfer_to TEXT DEFAULT '',
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_templates (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        total_occurrences INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_template_sets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_template_items (
        id TEXT PRIMARY KEY,
        template_id TEXT NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        total_occurrences INTEGER NOT NULL DEFAULT 1,
        type TEXT NOT NULL DEFAULT 'expense',
        wallet TEXT DEFAULT '',
        transfer_to TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (template_id) REFERENCES monthly_template_sets(id) ON DELETE CASCADE
    )
    """)

    monthly_columns = {row['name'] for row in cursor.execute("PRAGMA table_info(monthly_expenses)")}
    for column, definition in {
        'type': "TEXT NOT NULL DEFAULT 'expense'",
        'wallet': "TEXT DEFAULT ''",
        'transfer_to': "TEXT DEFAULT ''"
    }.items():
        if column not in monthly_columns:
            cursor.execute(f"ALTER TABLE monthly_expenses ADD COLUMN {column} {definition}")
    template_item_columns = {row['name'] for row in cursor.execute("PRAGMA table_info(monthly_template_items)")}
    for column, definition in {
        'type': "TEXT NOT NULL DEFAULT 'expense'",
        'wallet': "TEXT DEFAULT ''",
        'transfer_to': "TEXT DEFAULT ''"
    }.items():
        if column not in template_item_columns:
            cursor.execute(f"ALTER TABLE monthly_template_items ADD COLUMN {column} {definition}")

    # Table: settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)

    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('payday_start_day', '24')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('payday_end_day', '23')")
    template_migration = cursor.execute(
        "SELECT value FROM settings WHERE key = 'monthly_templates_parent_v1'"
    ).fetchone()
    if not template_migration:
        old_templates = cursor.execute("SELECT * FROM monthly_templates").fetchall()
        for old in old_templates:
            cursor.execute(
                "INSERT OR IGNORE INTO monthly_template_sets (id, name, created_at) VALUES (?, ?, ?)",
                (old['id'], old['title'], old['created_at'])
            )
            cursor.execute("""
            INSERT OR IGNORE INTO monthly_template_items
                            (id, template_id, title, amount, category, total_occurrences, type, wallet, transfer_to, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, 'expense', '', '', ?)
            """, (
                f"{old['id']}-item", old['id'], old['title'], old['amount'], old['category'],
                old['total_occurrences'], old['created_at']
            ))
        cursor.execute("INSERT INTO settings (key, value) VALUES ('monthly_templates_parent_v1', 'done')")
    salary_category_migration = cursor.execute(
        "SELECT value FROM settings WHERE key = 'salary_category_normalization_v1'"
    ).fetchone()
    if not salary_category_migration:
        cursor.execute("""
        UPDATE transactions
        SET category = 'Gaji & Upah'
        WHERE type = 'income' AND category = 'Gaji & Transfer Masuk'
        """)
        cursor.execute("INSERT INTO settings (key, value) VALUES ('salary_category_normalization_v1', 'done')")
    phantom_cleanup = cursor.execute(
        "SELECT value FROM settings WHERE key = 'legacy_phantom_wallet_cleanup_v1'"
    ).fetchone()
    if not phantom_cleanup:
        cursor.execute("""
        DELETE FROM transactions
        WHERE type = 'transfer_in'
          AND wallet = 'Bank Lain / E-Wallet'
          AND category = 'Transfer Antar Rekening / Diri Sendiri'
        """)
        cursor.execute("""
        DELETE FROM wallets
        WHERE name = 'Bank Lain / E-Wallet'
          AND NOT EXISTS (
              SELECT 1 FROM transactions
              WHERE wallet = wallets.name OR transfer_to = wallets.name
          )
        """)
        cursor.execute("INSERT INTO settings (key, value) VALUES ('legacy_phantom_wallet_cleanup_v1', 'done')")
    cursor.execute("""
    UPDATE transactions
    SET category = 'Pindah Dana'
    WHERE type = 'transfer' AND category != 'Pindah Dana'
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO wallets (id, name, created_at)
    SELECT 'w-' || lower(hex(randomblob(8))), wallet, ?
    FROM transactions
    WHERE wallet IS NOT NULL AND trim(wallet) != ''
    GROUP BY wallet
    """, (datetime.now().isoformat(),))

    conn.commit()
    conn.close()

# Transactions Queries
def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_transaction(tx):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO transactions (id, date, description, amount, type, category, wallet, transfer_to, savings_status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tx['id'],
        tx['date'],
        tx['description'],
        tx['amount'],
        tx['type'],
        tx['category'],
        tx.get('wallet', ''),
        tx.get('transfer_to', ''),
        tx.get('savings_status', 'non_savings'),
        tx.get('created_at', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def update_transaction_by_id(tx_id, tx):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE transactions
    SET date = ?, description = ?, amount = ?, type = ?, category = ?, wallet = ?, transfer_to = ?, savings_status = ?
    WHERE id = ?
    """, (
        tx['date'], tx['description'], tx['amount'], tx['type'], tx['category'],
        tx.get('wallet', ''), tx.get('transfer_to', ''),
        tx.get('savings_status', 'non_savings'), tx_id
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_transaction_by_id(tx_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# Planned Expenses Queries
def get_all_planned():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM planned_expenses ORDER BY date ASC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_planned(plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO planned_expenses (id, title, amount, category, probability, date, notes, wallet, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plan['id'],
        plan['title'],
        plan['amount'],
        plan['category'],
        plan.get('probability', 100),
        plan['date'],
        plan.get('notes', ''),
        plan.get('wallet', ''),
        plan.get('created_at', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def delete_planned_by_id(plan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM planned_expenses WHERE id = ?", (plan_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_planned_by_id(plan_id, plan):
    conn = get_connection()
    cursor = conn.execute("""
    UPDATE planned_expenses
    SET title = ?, amount = ?, category = ?, probability = ?, date = ?, notes = ?, wallet = ?
    WHERE id = ?
    """, (
        plan['title'], plan['amount'], plan['category'], plan['probability'],
        plan['date'], plan.get('notes', ''), plan.get('wallet', ''), plan_id
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

# Monthly Needs Queries
def get_monthly_expenses(year, month):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM monthly_expenses WHERE year = ? AND month = ? ORDER BY category ASC, created_at DESC",
        (year, month)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_monthly_templates():
    conn = get_connection()
    sets = conn.execute("SELECT * FROM monthly_template_sets ORDER BY created_at DESC").fetchall()
    items = conn.execute("SELECT * FROM monthly_template_items ORDER BY created_at ASC").fetchall()
    conn.close()
    item_map = {}
    for row in items:
        item = dict(row)
        item.pop('template_id', None)
        item_map.setdefault(row['template_id'], []).append(item)
    return [{**dict(row), 'items': item_map.get(row['id'], [])} for row in sets]

def get_monthly_template_by_id(template_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM monthly_template_sets WHERE id = ?", (template_id,)).fetchone()
    items = conn.execute(
        "SELECT * FROM monthly_template_items WHERE template_id = ? ORDER BY created_at ASC", (template_id,)
    ).fetchall()
    conn.close()
    if not row:
        return None
    return {**dict(row), 'items': [dict(item) for item in items]}

def insert_monthly_template(item):
    conn = get_connection()
    conn.execute("""
    INSERT INTO monthly_template_sets (id, name, created_at)
    VALUES (?, ?, ?)
    """, (
        item['id'], item['name'], item.get('created_at', datetime.now().isoformat())
    ))
    for template_item in item['items']:
        conn.execute("""
        INSERT INTO monthly_template_items
                    (id, template_id, title, amount, category, total_occurrences, type, wallet, transfer_to, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template_item['id'], item['id'], template_item['title'], template_item['amount'],
                        template_item['category'], template_item['total_occurrences'], template_item.get('type', 'expense'),
                        template_item.get('wallet', ''), template_item.get('transfer_to', ''),
            template_item.get('created_at', datetime.now().isoformat())
        ))
    conn.commit()
    conn.close()

def update_monthly_template(template_id, item):
    conn = get_connection()
    cursor = conn.execute("""
    UPDATE monthly_template_sets SET name = ?
    WHERE id = ?
    """, (item['name'], template_id))
    conn.execute("DELETE FROM monthly_template_items WHERE template_id = ?", (template_id,))
    for template_item in item['items']:
        conn.execute("""
        INSERT INTO monthly_template_items
                    (id, template_id, title, amount, category, total_occurrences, type, wallet, transfer_to, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template_item['id'], template_id, template_item['title'], template_item['amount'],
                        template_item['category'], template_item['total_occurrences'], template_item.get('type', 'expense'),
                        template_item.get('wallet', ''), template_item.get('transfer_to', ''), datetime.now().isoformat()
        ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_monthly_template(template_id):
    conn = get_connection()
    conn.execute("DELETE FROM monthly_template_items WHERE template_id = ?", (template_id,))
    cursor = conn.execute("DELETE FROM monthly_template_sets WHERE id = ?", (template_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def insert_monthly_expense(item):
    conn = get_connection()
    conn.execute("""
    INSERT INTO monthly_expenses
            (id, year, month, title, amount, category, total_occurrences, remaining_occurrences, type, wallet, transfer_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item['id'], item['year'], item['month'], item['title'], item['amount'], item['category'],
        item['total_occurrences'], item['remaining_occurrences'], item.get('type', 'expense'), item.get('wallet', ''),
        item.get('transfer_to', ''), item.get('created_at', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def update_monthly_expense(item_id, item):
    conn = get_connection()
    cursor = conn.execute("""
    UPDATE monthly_expenses
    SET title = ?, amount = ?, category = ?, total_occurrences = ?, remaining_occurrences = ?, type = ?, wallet = ?, transfer_to = ?
    WHERE id = ?
    """, (
        item['title'], item['amount'], item['category'], item['total_occurrences'],
        item['remaining_occurrences'], item.get('type', 'expense'), item.get('wallet', ''), item.get('transfer_to', ''), item_id
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_monthly_expense(item_id):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM monthly_expenses WHERE id = ?", (item_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_monthly_expense_by_id(item_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM monthly_expenses WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def realize_monthly_expense(item_id, quantity, transaction):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT remaining_occurrences FROM monthly_expenses WHERE id = ?", (item_id,)
        ).fetchone()
        if not row or row['remaining_occurrences'] < quantity:
            return False, 'Jumlah transaksi melebihi sisa template'
        conn.execute("""
        INSERT INTO transactions
          (id, date, description, amount, type, category, wallet, transfer_to, savings_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction['id'], transaction['date'], transaction['description'], transaction['amount'],
            transaction['type'], transaction['category'], transaction.get('wallet', ''), transaction.get('transfer_to', ''),
            transaction.get('savings_status', 'non_savings'),
            transaction['created_at']
        ))
        conn.execute(
            "UPDATE monthly_expenses SET remaining_occurrences = remaining_occurrences - ? WHERE id = ?",
            (quantity, item_id)
        )
        conn.commit()
        return True, None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Settings Queries
def get_setting(key, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def get_forecast_log(year, month):
    import json
    key = f"forecast_log_{year}_{month}"
    val = get_setting(key)
    if val:
        try:
            return json.loads(val)
        except Exception:
            return {"amount": float(val), "updated_at": None, "period": ""}
    # Check default fallback log
    val_default = get_setting("forecast_log_default")
    if val_default:
        try:
            return json.loads(val_default)
        except Exception:
            return {"amount": float(val_default), "updated_at": None, "period": ""}
    return None

def save_forecast_log(year, month, amount, period_label=""):
    import json
    data = {
        "amount": float(amount),
        "period": period_label,
        "updated_at": datetime.now().strftime("%d %b %Y, %H:%M")
    }
    json_str = json.dumps(data)
    set_setting(f"forecast_log_{year}_{month}", json_str)
    set_setting("forecast_log_default", json_str)
    return data

def clear_all_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM planned_expenses")
    conn.commit()
    conn.close()

# Wallet Queries
def get_all_wallets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wallets ORDER BY created_at ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def insert_wallet(wallet):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO wallets (id, name, initial_balance, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        wallet['id'],
        wallet['name'],
        float(wallet.get('initial_balance', 0)),
        wallet.get('created_at', datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def delete_wallet_by_id(wallet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wallets WHERE id = ?", (wallet_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_wallet_initial_balance(wallet_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE wallets SET initial_balance = ? WHERE id = ?", (float(amount), wallet_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_wallet_balances(start_date=None, end_date=None):
    """Calculate account closing balances, optionally scoped to accounts active in a date range."""
    conn = get_connection()
    cursor = conn.cursor()
    wallets = cursor.execute("SELECT id, name, initial_balance FROM wallets ORDER BY name").fetchall()
    period_only = bool(start_date and end_date)
    if period_only:
        activity_rows = cursor.execute(
            "SELECT wallet, transfer_to FROM transactions WHERE date >= ? AND date <= ?",
            (start_date, end_date)
        ).fetchall()
        rows = cursor.execute(
            "SELECT wallet, transfer_to, type, amount FROM transactions WHERE date <= ?",
            (end_date,)
        ).fetchall()
        balances = {
            row['name']: {
                'id': row['id'],
                'balance': float(row['initial_balance'] or 0),
                'initial_balance': float(row['initial_balance'] or 0)
            }
            for row in wallets
        }
    else:
        rows = cursor.execute("SELECT wallet, transfer_to, type, amount FROM transactions").fetchall()
        activity_rows = rows
        balances = {
            row['name']: {
                'id': row['id'],
                'balance': float(row['initial_balance'] or 0),
                'initial_balance': float(row['initial_balance'] or 0)
            }
            for row in wallets
        }
    conn.close()
    wallet_ids = {row['name']: row['id'] for row in wallets}
    active_wallets = {
        name.strip()
        for row in activity_rows
        for name in (row['wallet'], row['transfer_to'])
        if name and name.strip()
    }

    def add_movement(wallet_name, amount):
        name = (wallet_name or '').strip()
        if not name:
            return
        if name not in balances:
            balances[name] = {'id': wallet_ids.get(name), 'balance': 0.0, 'initial_balance': 0.0}
        balances[name]['balance'] += amount

    for row in rows:
        amount = float(row['amount'] or 0)
        tx_type = str(row['type']).lower()
        if tx_type == 'income':
            add_movement(row['wallet'], amount)
        elif tx_type == 'expense':
            add_movement(row['wallet'], -amount)
        elif tx_type == 'transfer':
            add_movement(row['wallet'], -amount)
            add_movement(row['transfer_to'], amount)
        elif tx_type == 'transfer_in':
            add_movement(row['wallet'], amount)

    result = [
        {'wallet': name, **values}
        for name, values in balances.items()
        if (name in active_wallets if period_only else values['balance'] > 0)
    ]
    result.sort(key=lambda item: item['balance'], reverse=True)
    return result
