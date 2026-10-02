import os
import uuid
import calendar
import json
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import database
import forecaster

app = Flask(__name__)
# Enable CORS for all frontend requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SQLite database schema
database.init_db()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "database": "sqlite",
        "service": "Financial Forecasting & Analytics Backend",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    txs = database.get_all_transactions()
    return jsonify(txs)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json or {}
    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        amount = 0

    if amount <= 0:
        return jsonify({"error": "Jumlah harus lebih besar dari 0"}), 400

    wallet_name = data.get('wallet', '').strip()
    tx_type = str(data.get('type', 'expense')).lower()
    if tx_type not in {'income', 'expense', 'transfer'}:
        return jsonify({"error": "Tipe transaksi tidak valid"}), 400
    transfer_to = str(data.get('transfer_to', '')).strip()
    if tx_type == 'transfer' and (not wallet_name or not transfer_to or wallet_name == transfer_to):
        return jsonify({"error": "Transfer memerlukan rekening asal dan tujuan yang berbeda"}), 400

    new_tx = {
        "id": data.get('id') or f"tx-{uuid.uuid4().hex[:8]}",
        "date": data.get('date') or date.today().strftime("%Y-%m-%d"),
        "description": data.get('description', 'Transaksi Baru'),
        "amount": amount,
        "type": tx_type,
        "category": 'Pindah Dana' if tx_type == 'transfer' else data.get('category', 'Lainnya'),
        "wallet": wallet_name,
        "transfer_to": transfer_to,
        "savings_status": 'savings' if data.get('savings_status') == 'savings' and tx_type != 'transfer' else 'non_savings',
        "created_at": datetime.now().isoformat()
    }

    if wallet_name:
        database.insert_wallet({"id": f"w-{uuid.uuid4().hex[:8]}", "name": wallet_name})
    if transfer_to:
        database.insert_wallet({"id": f"w-{uuid.uuid4().hex[:8]}", "name": transfer_to})

    database.insert_transaction(new_tx)
    return jsonify(new_tx), 201

@app.route('/api/transactions/<tx_id>', methods=['PUT'])
def update_transaction(tx_id):
    data = request.json or {}
    try:
        amount = float(data.get('amount', 0))
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        return jsonify({"error": "Jumlah harus lebih besar dari 0"}), 400

    tx_type = str(data.get('type', 'expense')).lower()
    if tx_type not in {'income', 'expense', 'transfer'}:
        return jsonify({"error": "Tipe transaksi tidak valid"}), 400
    wallet_name = str(data.get('wallet', '')).strip()
    transfer_to = str(data.get('transfer_to', '')).strip()
    if tx_type == 'transfer' and (not wallet_name or not transfer_to or wallet_name == transfer_to):
        return jsonify({"error": "Transfer memerlukan rekening asal dan tujuan yang berbeda"}), 400

    updated_tx = {
        'date': data.get('date') or date.today().isoformat(),
        'description': str(data.get('description', 'Transaksi')).strip(),
        'amount': amount,
        'type': tx_type,
        'category': 'Pindah Dana' if tx_type == 'transfer' else data.get('category', 'Lainnya'),
        'wallet': wallet_name,
        'transfer_to': transfer_to,
        'savings_status': 'savings' if data.get('savings_status') == 'savings' and tx_type != 'transfer' else 'non_savings'
    }
    if wallet_name:
        database.insert_wallet({'id': f"w-{uuid.uuid4().hex[:8]}", 'name': wallet_name})
    if transfer_to:
        database.insert_wallet({'id': f"w-{uuid.uuid4().hex[:8]}", 'name': transfer_to})
    if not database.update_transaction_by_id(tx_id, updated_tx):
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404
    return jsonify({'id': tx_id, **updated_tx})

@app.route('/api/transactions/<tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    success = database.delete_transaction_by_id(tx_id)
    if not success:
        return jsonify({"error": "Transaksi tidak ditemukan"}), 404
    return jsonify({"message": "Transaksi berhasil dihapus", "id": tx_id})

@app.route('/api/planned', methods=['GET'])
def get_planned():
    planned = database.get_all_planned()
    return jsonify(planned)

@app.route('/api/planned', methods=['POST'])
def add_planned():
    data = request.json or {}
    try:
        amount = float(data.get('amount', 0))
    except (ValueError, TypeError):
        amount = 0

    if amount <= 0:
        return jsonify({"error": "Perkiraan nominal harus lebih dari 0"}), 400

    new_plan = {
        "id": data.get('id') or f"plan-{uuid.uuid4().hex[:8]}",
        "title": data.get('title', 'Kemungkinan Pengeluaran'),
        "amount": amount,
        "category": data.get('category', 'Lainnya'),
        "probability": int(data.get('probability', 100)),
        "date": data.get('date') or date.today().strftime("%Y-%m-%d"),
        "notes": data.get('notes', ''),
        "wallet": str(data.get('wallet', '')).strip(),
        "created_at": datetime.now().isoformat()
    }

    database.insert_planned(new_plan)
    return jsonify(new_plan), 201

@app.route('/api/planned/<plan_id>', methods=['DELETE'])
def delete_planned(plan_id):
    success = database.delete_planned_by_id(plan_id)
    if not success:
        return jsonify({"error": "Item rencana tidak ditemukan"}), 404
    return jsonify({"message": "Rencana berhasil dihapus", "id": plan_id})

@app.route('/api/planned/<plan_id>', methods=['PUT'])
def update_planned(plan_id):
    data = request.json or {}
    try:
        amount = float(data.get('amount', 0))
        probability = int(data.get('probability', 100))
    except (ValueError, TypeError):
        return jsonify({"error": "Data rencana tidak valid"}), 400
    if amount <= 0 or not str(data.get('title', '')).strip():
        return jsonify({"error": "Nama dan nominal rencana wajib diisi"}), 400
    updated = {
        'title': str(data.get('title')).strip(), 'amount': amount,
        'category': str(data.get('category', 'Lain-lain')).strip(),
        'probability': max(0, min(100, probability)),
        'date': data.get('date') or date.today().isoformat(),
        'notes': str(data.get('notes', '')).strip(),
        'wallet': str(data.get('wallet', '')).strip()
    }
    if not database.update_planned_by_id(plan_id, updated):
        return jsonify({"error": "Rencana tidak ditemukan"}), 404
    return jsonify({'id': plan_id, **updated})

def is_current_cycle(year, month):
    start_day = int(database.get_setting('payday_start_day', '24'))
    end_day = int(database.get_setting('payday_end_day', '23'))
    start_date, end_date = get_period_bounds(year, month, start_day, end_day)
    return start_date <= date.today() <= end_date

def get_period_bounds(year, month, start_day=None, end_day=None):
    try:
        periods = json.loads(database.get_setting('cycle_periods', '{}'))
        stored = periods.get(f'{year:04d}-{month:02d}', {})
        if stored.get('start') and stored.get('end'):
            return date.fromisoformat(stored['start']), date.fromisoformat(stored['end'])
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    if start_day is None:
        start_day = int(database.get_setting('payday_start_day', '24'))
    if end_day is None:
        end_day = int(database.get_setting('payday_end_day', '23'))
    return get_cycle_bounds(year, month, start_day, end_day)

def monthly_transaction_fields(data):
    transaction_type = str(data.get('type', 'expense')).lower()
    if transaction_type not in {'income', 'expense', 'transfer'}:
        raise ValueError('Tipe transaksi tidak valid')
    wallet = str(data.get('wallet', '')).strip()
    transfer_to = str(data.get('transfer_to', '')).strip()
    if transaction_type == 'transfer' and (not wallet or not transfer_to or wallet == transfer_to):
        raise ValueError('Transfer memerlukan rekening asal dan tujuan yang berbeda')
    return {
        'type': transaction_type,
        'wallet': wallet,
        'transfer_to': transfer_to
    }

def calculate_active_savings_amount(transactions):
    """Calculate net funds held in wallets participating in savings allocations."""
    configured_value = database.get_setting('savings_wallets', '[]')
    try:
        configured_wallets = {str(name).strip() for name in json.loads(configured_value) if str(name).strip()}
    except (TypeError, ValueError, json.JSONDecodeError):
        configured_wallets = set()
    if configured_wallets:
        amount = 0.0
        for tx in transactions:
            source = str(tx.get('wallet', '')).strip()
            target = str(tx.get('transfer_to', '')).strip()
            value = float(tx.get('amount', 0) or 0)
            if tx.get('type') == 'transfer':
                if source in configured_wallets:
                    amount -= value
                if target in configured_wallets:
                    amount += value
            elif source in configured_wallets:
                amount += value if tx.get('type') == 'income' else -value
        return amount
    active_wallets = {
        str(tx.get('transfer_to', '')).strip()
        for tx in transactions
        if tx.get('type') == 'transfer'
        and tx.get('savings_status') == 'savings'
        and str(tx.get('transfer_to', '')).strip()
    }
    amount = 0.0
    for tx in transactions:
        wallet = str(tx.get('wallet', '')).strip()
        tx_type = tx.get('type')
        value = float(tx.get('amount', 0) or 0)
        if tx_type == 'transfer':
            if tx.get('savings_status') == 'savings' and wallet not in active_wallets and tx.get('transfer_to') in active_wallets:
                amount += value
        elif wallet in active_wallets:
            if tx_type == 'income':
                amount += value
            elif tx_type == 'expense' and tx.get('savings_status') == 'savings':
                amount -= value
    return amount

@app.route('/api/monthly-needs', methods=['GET'])
def get_monthly_needs():
    try:
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))
    except (TypeError, ValueError):
        return jsonify({"error": "Bulan kebutuhan tidak valid"}), 400
    return jsonify(database.get_monthly_expenses(year, month))

@app.route('/api/monthly-templates', methods=['GET', 'POST'])
def monthly_templates():
    if request.method == 'GET':
        return jsonify(database.get_monthly_templates())
    data = request.json or {}
    try:
        name = str(data.get('name', '')).strip()
        raw_items = data.get('items', [])
        if not name or not isinstance(raw_items, list) or not raw_items:
            raise ValueError
        items = []
        for raw_item in raw_items:
            amount = float(raw_item.get('amount', 0))
            occurrences = int(raw_item.get('total_occurrences', 0))
            title = str(raw_item.get('title', '')).strip()
            if not title or amount <= 0 or occurrences <= 0:
                raise ValueError
            items.append({
                'id': f"template-item-{uuid.uuid4().hex[:8]}", 'title': title, 'amount': amount,
                'category': str(raw_item.get('category', 'Lain-lain')).strip(),
                'total_occurrences': occurrences, **monthly_transaction_fields(raw_item)
            })
    except (TypeError, ValueError):
        return jsonify({"error": "Nama template dan minimal satu item wajib diisi"}), 400
    item = {'id': f"template-{uuid.uuid4().hex[:8]}", 'name': name, 'items': items, 'created_at': datetime.now().isoformat()}
    database.insert_monthly_template(item)
    return jsonify(item), 201

@app.route('/api/monthly-templates/<template_id>', methods=['PUT', 'DELETE'])
def manage_monthly_template(template_id):
    if request.method == 'DELETE':
        if not database.delete_monthly_template(template_id):
            return jsonify({"error": "Template tidak ditemukan"}), 404
        return jsonify({"message": "Template dihapus", "id": template_id})
    data = request.json or {}
    try:
        name = str(data.get('name', '')).strip()
        items = []
        for raw_item in data.get('items', []):
            amount = float(raw_item.get('amount', 0))
            occurrences = int(raw_item.get('total_occurrences', 0))
            title = str(raw_item.get('title', '')).strip()
            if not title or amount <= 0 or occurrences <= 0:
                raise ValueError
            items.append({
                'id': f"template-item-{uuid.uuid4().hex[:8]}", 'title': title, 'amount': amount,
                'category': str(raw_item.get('category', 'Lain-lain')).strip(),
                'total_occurrences': occurrences, **monthly_transaction_fields(raw_item)
            })
        if not name or not items:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Nama template dan minimal satu item wajib diisi"}), 400
    item = {'name': name, 'items': items}
    if not database.update_monthly_template(template_id, item):
        return jsonify({"error": "Template tidak ditemukan"}), 404
    return jsonify({'id': template_id, **item})

@app.route('/api/monthly-templates/<template_id>/apply', methods=['POST'])
def apply_monthly_template(template_id):
    data = request.json or {}
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
    except (TypeError, ValueError):
        return jsonify({"error": "Bulan kebutuhan tidak valid"}), 400
    if not is_current_cycle(year, month):
        return jsonify({"error": "Template hanya dapat diterapkan pada bulan yang sedang berjalan"}), 400
    template = database.get_monthly_template_by_id(template_id)
    if not template:
        return jsonify({"error": "Template tidak ditemukan"}), 404
    existing = database.get_monthly_expenses(year, month)
    if existing and not data.get('force', False):
        return jsonify({"error": "Bulan ini sudah memiliki list kebutuhan", "requires_confirmation": True}), 409
    created_items = []
    for template_item in template['items']:
        item = {
            'id': f"need-{uuid.uuid4().hex[:8]}", 'year': year, 'month': month,
            'title': template_item['title'], 'amount': template_item['amount'],
            'category': template_item['category'], 'total_occurrences': template_item['total_occurrences'],
            'remaining_occurrences': template_item['total_occurrences'], 'type': template_item.get('type', 'expense'),
            'wallet': template_item.get('wallet', ''), 'transfer_to': template_item.get('transfer_to', ''),
            'created_at': datetime.now().isoformat()
        }
        database.insert_monthly_expense(item)
        created_items.append(item)
    return jsonify({'template': template['name'], 'items': created_items}), 201

@app.route('/api/monthly-needs', methods=['POST'])
def add_monthly_need():
    data = request.json or {}
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        amount = float(data.get('amount', 0))
        occurrences = int(data.get('total_occurrences', 0))
        transaction_fields = monthly_transaction_fields(data)
    except (TypeError, ValueError):
        return jsonify({"error": "Data kebutuhan bulanan tidak valid"}), 400
    if not is_current_cycle(year, month):
        return jsonify({"error": "Kebutuhan hanya dapat dibuat pada bulan yang sedang berjalan"}), 400
    title = str(data.get('title', '')).strip()
    category = str(data.get('category', 'Lain-lain')).strip()
    if not title or amount <= 0 or occurrences <= 0:
        return jsonify({"error": "Nama, harga, dan jumlah transaksi wajib valid"}), 400
    item = {
        'id': f"need-{uuid.uuid4().hex[:8]}", 'year': year, 'month': month,
        'title': title, 'amount': amount, 'category': category,
        'total_occurrences': occurrences, 'remaining_occurrences': occurrences,
        **transaction_fields,
        'created_at': datetime.now().isoformat()
    }
    database.insert_monthly_expense(item)
    return jsonify(item), 201

@app.route('/api/monthly-needs/<item_id>', methods=['PUT', 'DELETE'])
def manage_monthly_need(item_id):
    if request.method == 'DELETE':
        item = database.get_monthly_expense_by_id(item_id)
        if not item:
            return jsonify({"error": "Template kebutuhan tidak ditemukan"}), 404
        if not is_current_cycle(item['year'], item['month']):
            return jsonify({"error": "Template hanya dapat dihapus pada bulan yang sedang berjalan"}), 400
        if not database.delete_monthly_expense(item_id):
            return jsonify({"error": "Template kebutuhan tidak ditemukan"}), 404
        return jsonify({"message": "Template kebutuhan dihapus", "id": item_id})
    data = request.json or {}
    try:
        amount = float(data.get('amount', 0))
        total_occurrences = int(data.get('total_occurrences', 0))
        remaining_occurrences = int(data.get('remaining_occurrences', 0))
        year = int(data.get('year'))
        month = int(data.get('month'))
        transaction_fields = monthly_transaction_fields(data)
    except (TypeError, ValueError):
        return jsonify({"error": "Data kebutuhan bulanan tidak valid"}), 400
    if amount <= 0 or total_occurrences <= 0 or remaining_occurrences < 0 or remaining_occurrences > total_occurrences:
        return jsonify({"error": "Harga dan jumlah transaksi tidak valid"}), 400
    item = {
        'title': str(data.get('title', '')).strip(), 'amount': amount,
        'category': str(data.get('category', 'Lain-lain')).strip(),
        'total_occurrences': total_occurrences, 'remaining_occurrences': remaining_occurrences,
        **transaction_fields
    }
    if not item['title'] or not is_current_cycle(year, month):
        return jsonify({"error": "Template hanya dapat diedit pada bulan yang sedang berjalan"}), 400
    if not database.update_monthly_expense(item_id, item):
        return jsonify({"error": "Template kebutuhan tidak ditemukan"}), 404
    return jsonify({'id': item_id, **item})

@app.route('/api/monthly-needs/<item_id>/realize', methods=['POST'])
def realize_monthly_need(item_id):
    data = request.json or {}
    try:
        quantity = int(data.get('quantity', 0))
        year = int(data.get('year'))
        month = int(data.get('month'))
    except (TypeError, ValueError):
        return jsonify({"error": "Jumlah transaksi tidak valid"}), 400
    if quantity <= 0 or not is_current_cycle(year, month):
        return jsonify({"error": "Template hanya dapat direalisasikan pada bulan yang sedang berjalan"}), 400
    items = database.get_monthly_expenses(year, month)
    item = next((entry for entry in items if entry['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Template kebutuhan tidak ditemukan"}), 404
    tx = {
        'id': f"tx-{uuid.uuid4().hex[:8]}", 'date': date.today().isoformat(),
        'description': item['title'], 'amount': float(item['amount']) * quantity,
        'category': item['category'], 'type': item.get('type', 'expense'),
        'wallet': item.get('wallet', ''), 'transfer_to': item.get('transfer_to', ''),
        'created_at': datetime.now().isoformat()
    }
    success, error = database.realize_monthly_expense(item_id, quantity, tx)
    if not success:
        return jsonify({"error": error}), 400
    return jsonify({'transaction': tx, 'quantity': quantity}), 201

# -- Wallet endpoints --
@app.route('/api/wallets', methods=['GET'])
def get_wallets():
    wallets = database.get_all_wallets()
    return jsonify(wallets)

@app.route('/api/wallets', methods=['POST'])
def add_wallet():
    data = request.json or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "Nama wallet harus diisi"}), 400
    try:
        initial_balance = float(data.get('initial_balance', 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Saldo awal harus berupa angka"}), 400

    new_wallet = {
        "id": f"w-{uuid.uuid4().hex[:8]}",
        "name": name,
        "initial_balance": initial_balance,
        "created_at": datetime.now().isoformat()
    }
    database.insert_wallet(new_wallet)
    return jsonify(new_wallet), 201

@app.route('/api/wallets/<wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    success = database.delete_wallet_by_id(wallet_id)
    if not success:
        return jsonify({"error": "Wallet tidak ditemukan"}), 404
    return jsonify({"message": "Wallet berhasil dihapus", "id": wallet_id})

@app.route('/api/wallets/<wallet_id>/initial-balance', methods=['PUT'])
def update_wallet_initial_balance(wallet_id):
    data = request.json or {}
    try:
        initial_balance = float(data.get('initial_balance'))
    except (TypeError, ValueError):
        return jsonify({"error": "Saldo awal harus berupa angka"}), 400
    if not database.update_wallet_initial_balance(wallet_id, initial_balance):
        return jsonify({"error": "Rekening tidak ditemukan"}), 404
    return jsonify({"id": wallet_id, "initial_balance": initial_balance})

@app.route('/api/wallet-balances', methods=['GET'])
def get_wallet_balances():
    all_time = request.args.get('all', 'false').lower() == 'true'
    start_date = end_date = None
    if not all_time:
        try:
            year = int(request.args.get('year', date.today().year))
            month = int(request.args.get('month', date.today().month))
            start_day = int(database.get_setting('payday_start_day', '24'))
            end_day = int(database.get_setting('payday_end_day', '23'))
            start_date, end_date = get_period_bounds(year, month, start_day, end_day)
        except (TypeError, ValueError):
            return jsonify({"error": "Periode saldo tidak valid"}), 400
    balances = database.get_wallet_balances(
        start_date.isoformat() if start_date else None,
        end_date.isoformat() if end_date else None
    )
    return jsonify(balances)

@app.route('/api/settings/cutoff-day', methods=['GET', 'PUT'])
def payday_cutoff_setting():
    if request.method == 'GET':
        return jsonify({
            "start_day": int(database.get_setting('payday_start_day', '24')),
            "end_day": int(database.get_setting('payday_end_day', '23'))
        })
    try:
        data = request.json or {}
        start_day = int(data.get('start_day'))
        end_day = int(data.get('end_day'))
    except (TypeError, ValueError):
        return jsonify({"error": "Tanggal mulai dan selesai harus berupa angka"}), 400
    if not 1 <= start_day <= 31 or not 1 <= end_day <= 31:
        return jsonify({"error": "Tanggal mulai dan selesai harus antara 1 dan 31"}), 400
    database.set_setting('payday_start_day', start_day)
    database.set_setting('payday_end_day', end_day)
    return jsonify({"start_day": start_day, "end_day": end_day})

@app.route('/api/settings/cycle-period', methods=['GET', 'PUT'])
def cycle_period_setting():
    payload = request.args if request.method == 'GET' else (request.json or {})
    try:
        year = int(payload.get('year'))
        month = int(payload.get('month'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Tahun dan bulan periode tidak valid'}), 400
    key = f'{year:04d}-{month:02d}'
    try:
        periods = json.loads(database.get_setting('cycle_periods', '{}'))
    except (TypeError, ValueError, json.JSONDecodeError):
        periods = {}
    if request.method == 'GET':
        start_date, end_date = get_period_bounds(year, month)
        return jsonify({'year': year, 'month': month, 'start': start_date.isoformat(), 'end': end_date.isoformat()})
    try:
        start_date = date.fromisoformat(str(payload.get('start')))
        end_date = date.fromisoformat(str(payload.get('end')))
    except (TypeError, ValueError):
        return jsonify({'error': 'Tanggal mulai dan selesai harus valid'}), 400
    if start_date > end_date:
        return jsonify({'error': 'Tanggal mulai tidak boleh setelah tanggal selesai'}), 400
    periods[key] = {'start': start_date.isoformat(), 'end': end_date.isoformat()}
    database.set_setting('cycle_periods', json.dumps(periods))
    return jsonify({'year': year, 'month': month, 'start': start_date.isoformat(), 'end': end_date.isoformat()})

@app.route('/api/settings/savings-wallets', methods=['GET', 'PUT'])
def savings_wallet_setting():
    if request.method == 'GET':
        try:
            wallets = json.loads(database.get_setting('savings_wallets', '[]'))
        except (TypeError, ValueError, json.JSONDecodeError):
            wallets = []
        return jsonify({'wallets': wallets if isinstance(wallets, list) else []})
    data = request.json or {}
    wallets = data.get('wallets', [])
    if not isinstance(wallets, list):
        return jsonify({'error': 'Daftar rekening tabungan tidak valid'}), 400
    normalized = list(dict.fromkeys(str(wallet).strip() for wallet in wallets if str(wallet).strip()))
    database.set_setting('savings_wallets', json.dumps(normalized))
    return jsonify({'wallets': normalized})

def get_cycle_bounds(year, month, start_day, end_day):
    if start_day > end_day:
        previous_year = year - 1 if month == 1 else year
        previous_month = 12 if month == 1 else month - 1
        actual_start_day = min(start_day, calendar.monthrange(previous_year, previous_month)[1])
        actual_end_day = min(end_day, calendar.monthrange(year, month)[1])
        start_date = date(previous_year, previous_month, actual_start_day)
        end_date = date(year, month, actual_end_day)
    else:
        actual_start_day = min(start_day, calendar.monthrange(year, month)[1])
        actual_end_day = min(end_day, calendar.monthrange(year, month)[1])
        start_date = date(year, month, actual_start_day)
        end_date = date(year, month, actual_end_day)
    return start_date, end_date

@app.route('/api/forecast', methods=['GET', 'POST'])
def run_forecast():
    req_data = request.json if request.is_json else {}
    if not req_data and request.method == 'GET':
        req_data = request.args

    today = date.today()
    try:
        cur_year = int(req_data.get('year')) if req_data.get('year') else today.year
        cur_month = int(req_data.get('month')) if req_data.get('month') else today.month
        if not (1 <= cur_month <= 12):
            cur_month = today.month
    except (ValueError, TypeError):
        cur_year = today.year
        cur_month = today.month

    start_day = int(database.get_setting('payday_start_day', '24'))
    end_day = int(database.get_setting('payday_end_day', '23'))
    all_time = bool(req_data.get('all_time', False))
    try:
        period_ranges = json.loads(database.get_setting('cycle_periods', '{}'))
    except (TypeError, ValueError, json.JSONDecodeError):
        period_ranges = {}

    target_period_label = f"{MONTH_NAMES_ID[cur_month]} {cur_year}"

    expected_income = None
    saved_log = None

    txs = database.get_all_transactions()
    plans = database.get_all_planned()

    result = forecaster.calculate_forecast(
        transactions=txs,
        planned_expenses=plans,
        expected_next_income=expected_income,
        base_year=cur_year,
        base_month=cur_month,
        saved_log=saved_log,
        start_day=start_day,
        end_day=end_day,
        all_time=all_time,
        period_ranges=period_ranges
    )
    return jsonify(result)

MONTH_NAMES_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

@app.route('/api/summary', methods=['GET'])
def get_summary():
    txs = database.get_all_transactions()
    plans = database.get_all_planned()
    today = date.today()
    req_all = request.args.get('all', 'false').lower() == 'true'
    req_year = request.args.get('year')
    req_month = request.args.get('month')
    is_all_time = req_all or req_year == 'all'

    if is_all_time:
        cur_year = cur_month = None
        month_label = 'Seluruh Data Historis'
    else:
        try:
            cur_year = int(req_year) if req_year else today.year
            cur_month = int(req_month) if req_month else today.month
            if not 1 <= cur_month <= 12:
                cur_month = today.month
        except (ValueError, TypeError):
            cur_year, cur_month = today.year, today.month
        month_label = f"{MONTH_NAMES_ID[cur_month]} {cur_year}"

    start_day = int(database.get_setting('payday_start_day', '24'))
    end_day = int(database.get_setting('payday_end_day', '23'))
    if not is_all_time:
        start_date, end_date = get_period_bounds(cur_year, cur_month, start_day, end_day)

    def is_salary_income(tx):
        category = str(tx.get('category', '')).casefold()
        return tx.get('type') == 'income' and ('gaji' in category or 'upah' in category)

    cur_txs = []
    daily_map = {}
    for tx in txs:
        try:
            transaction_date = datetime.strptime(str(tx['date'])[:10], '%Y-%m-%d').date()
        except (KeyError, TypeError, ValueError):
            continue
        if not is_all_time and not start_date <= transaction_date <= end_date:
            continue
        if not is_all_time and start_date <= today <= end_date and transaction_date > today:
            continue
        cur_txs.append(tx)
        date_key = transaction_date.isoformat()
        daily = daily_map.setdefault(date_key, {'date': date_key, 'income': 0.0, 'expense': 0.0, 'count': 0})
        amount = float(tx.get('amount', 0))
        if is_salary_income(tx):
            daily['income'] += amount
        elif tx.get('type') == 'expense':
            daily['expense'] += amount
        daily['count'] += 1

    total_income = sum(float(tx['amount']) for tx in cur_txs if is_salary_income(tx))
    total_expense = sum(float(tx['amount']) for tx in cur_txs if tx.get('type') == 'expense')
    total_planned = 0.0
    planned_count = 0
    for plan in plans:
        try:
            planned_date = datetime.strptime(plan['date'], '%Y-%m-%d').date()
        except (KeyError, TypeError, ValueError):
            continue
        if not is_all_time and not start_date <= planned_date <= end_date:
            continue
        total_planned += float(plan.get('amount', 0)) * float(plan.get('probability', 100)) / 100
        planned_count += 1

    all_wallet_balances = database.get_wallet_balances()
    total_funds = sum(item['balance'] for item in all_wallet_balances)
    category_map = {}
    for tx in cur_txs:
        if tx.get('type') == 'expense':
            category = tx.get('category', 'Lainnya')
            category_map[category] = category_map.get(category, 0) + float(tx.get('amount', 0))

    cycle_wallet_balances = database.get_wallet_balances(
        start_date.isoformat() if not is_all_time else None,
        end_date.isoformat() if not is_all_time else None
    )
    return jsonify({
        'current_month': {
            'is_all_time': is_all_time,
            'month': cur_month,
            'year': cur_year,
            'month_name': month_label,
            'period_start': start_date.isoformat() if not is_all_time else None,
            'period_end': end_date.isoformat() if not is_all_time else None,
            'start_day': start_day,
            'end_day': end_day,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_planned': total_planned,
            'sisa_tabungan': total_funds,
            'savings_ratio': 0,
            'savings_status_amount': calculate_active_savings_amount(cur_txs)
        },
        'daily_analytics': sorted(daily_map.values(), key=lambda item: item['date']),
        'categories': sorted(
            [{'category': category, 'amount': amount} for category, amount in category_map.items()],
            key=lambda item: item['amount'], reverse=True
        ),
        'transaction_count': len(cur_txs),
        'planned_count': planned_count,
        'wallet_balances': cycle_wallet_balances,
        'all_wallet_balances': all_wallet_balances
    })

@app.route('/api/clear-all', methods=['POST'])
def clear_all():
    database.clear_all_data()
    return jsonify({"message": "Seluruh data transaksi dan rencana berhasil dikosongkan"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f"Starting Python SQLite Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
