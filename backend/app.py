import os
import uuid
import calendar
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
        "savings_status": 'savings' if data.get('savings_status') == 'savings' else 'non_savings',
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
        'savings_status': 'savings' if data.get('savings_status') == 'savings' else 'non_savings'
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
            start_date, end_date = get_cycle_bounds(year, month, start_day, end_day)
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

    # Label periode berikutnya untuk log
    if cur_month == 12:
        nxt_y = cur_year + 1
        nxt_m = 1
    else:
        nxt_y = cur_year
        nxt_m = cur_month + 1
    target_period_label = f"{MONTH_NAMES_ID[nxt_m]} {nxt_y}"

    raw_inc = req_data.get('expected_income')
    is_saving_log = req_data.get('is_saving_log', False)

    if raw_inc is not None and (is_saving_log or float(raw_inc) > 0):
        try:
            expected_income = float(raw_inc)
            saved_log = database.save_forecast_log(cur_year, cur_month, expected_income, target_period_label)
        except (ValueError, TypeError):
            expected_income = None
            saved_log = database.get_forecast_log(cur_year, cur_month)
    else:
        saved_log = database.get_forecast_log(cur_year, cur_month)
        if saved_log and 'amount' in saved_log:
            expected_income = float(saved_log['amount'])
        else:
            expected_income = None

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
        all_time=all_time
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
        start_date, end_date = get_cycle_bounds(cur_year, cur_month, start_day, end_day)

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
            'savings_status_amount': sum(
                float(tx.get('amount', 0)) for tx in cur_txs if tx.get('savings_status') == 'savings'
            )
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
