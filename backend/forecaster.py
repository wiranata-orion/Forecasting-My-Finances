import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from sklearn.linear_model import LinearRegression

MONTH_NAMES_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

def parse_date(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except Exception:
        try:
            return datetime.fromisoformat(str(date_str)).date()
        except Exception:
            return date.today()

def cycle_period(value, start_day, end_day):
    month_length = calendar.monthrange(value.year, value.month)[1]
    actual_start_day = min(start_day, month_length)
    actual_end_day = min(end_day, month_length)
    if start_day > end_day:
        if value.day >= actual_start_day:
            return (value.year + 1, 1) if value.month == 12 else (value.year, value.month + 1)
        return value.year, value.month
    if value.day < actual_start_day:
        return (value.year - 1, 12) if value.month == 1 else (value.year, value.month - 1)
    if value.day > actual_end_day:
        return (value.year + 1, 1) if value.month == 12 else (value.year, value.month + 1)
    return value.year, value.month

def cycle_bounds(year, month, start_day, end_day):
    if start_day > end_day:
        previous_year = year - 1 if month == 1 else year
        previous_month = 12 if month == 1 else month - 1
        actual_start_day = min(start_day, calendar.monthrange(previous_year, previous_month)[1])
        actual_end_day = min(end_day, calendar.monthrange(year, month)[1])
        return date(previous_year, previous_month, actual_start_day), date(year, month, actual_end_day)
    actual_start_day = min(start_day, calendar.monthrange(year, month)[1])
    actual_end_day = min(end_day, calendar.monthrange(year, month)[1])
    return date(year, month, actual_start_day), date(year, month, actual_end_day)

def calculate_forecast(transactions, planned_expenses, expected_next_income=None, base_year=None, base_month=None, saved_log=None, start_day=24, end_day=23, all_time=False):
    """
    Real Historical Forecasting Engine & Accuracy Evaluator:
    - Proyeksi keuangan untuk bulan depan dari basis bulan yang sedang dilihat.
    - Menghitung seberapa akurat hasil forecasting terhadap data riil di bulan depan
      ketika melihat bulan-bulan sebelumnya (aktif saat data bulan depannya sudah selesai atau akhir bulan).
    - Terintegrasi dengan 1 log input acuan tersimpan.
    """
    today = date.today()
    start_day = max(1, min(31, int(start_day)))
    end_day = max(1, min(31, int(end_day)))
    current_period = cycle_period(today, start_day, end_day)
    cur_year = int(base_year) if base_year else current_period[0]
    cur_month = int(base_month) if base_month else current_period[1]
    if all_time:
        cur_year, cur_month = current_period

    # Target bulan depan
    if cur_month == 12:
        next_year = cur_year + 1
        next_month = 1
    else:
        next_year = cur_year
        next_month = cur_month + 1

    next_start, next_end = cycle_bounds(next_year, next_month, start_day, end_day)
    days_in_next_month = (next_end - next_start).days + 1
    next_month_name = MONTH_NAMES_ID[next_month]
    target_ym = f"{next_year}-{next_month:02d}"
    base_ym = f"{cur_year}-{cur_month:02d}"

    # Apakah sedang melihat bulan lampau?
    is_past_month = (cur_year, cur_month) < current_period

    # Status waktu bulan depan
    if (next_year, next_month) < current_period:
        timing_status = "selesai"
        is_next_month_completed = True
    elif (next_year, next_month) == current_period:
        if today >= next_end:
            timing_status = "akhir_bulan"
            is_next_month_completed = True
        else:
            timing_status = "belum_akhir_bulan"
            is_next_month_completed = False
    else:
        timing_status = "masa_depan"
        is_next_month_completed = False

    # Format 1 log acuan yang tersimpan
    log_info = {
        'exists': bool(saved_log and saved_log.get('amount')),
        'amount': float(saved_log.get('amount', 0)) if saved_log else 0.0,
        'period': saved_log.get('period', f"{next_month_name} {next_year}") if saved_log else f"{next_month_name} {next_year}",
        'updated_at': saved_log.get('updated_at', '') if saved_log else ''
    }

    if not transactions:
        return generate_empty_forecast(
            today, days_in_next_month, next_month_name, next_year, next_month,
            cur_year, cur_month, is_past_month, is_next_month_completed, timing_status, log_info
        )

    # Rollover is represented by account balances, never as synthetic income rows.
    all_records = []
    for tx in transactions:
        t_date = parse_date(tx.get('date', ''))
        amt = float(tx.get('amount', 0))
        t_type = str(tx.get('type', 'expense')).lower()
        cat = tx.get('category', 'Lainnya')
        all_records.append({
            'date': t_date,
            'year': t_date.year,
            'month': t_date.month,
            'ym': f"{cycle_period(t_date, start_day, end_day)[0]}-{cycle_period(t_date, start_day, end_day)[1]:02d}",
            'amount': amt,
            'type': t_type,
            'category': cat
        })

    df_all = pd.DataFrame(all_records)

    # Transaksi training (hingga bulan yang sedang dilihat)
    df_training = df_all[df_all['ym'] <= base_ym]
    # Transaksi riil bulan depan
    df_next = df_all[df_all['ym'] == target_ym]

    # Data riil aktual bulan depan
    real_next_income = float(
        df_next[
            (df_next['type'] == 'income')
            & df_next['category'].astype(str).str.casefold().str.contains(r'gaji|upah', regex=True)
        ]['amount'].sum()
    ) if not df_next.empty else 0.0
    real_next_expense = float(df_next[df_next['type'] == 'expense']['amount'].sum()) if not df_next.empty else 0.0
    real_next_savings = max(0.0, real_next_income - real_next_expense)
    real_tx_count = len(
        df_next[
            (df_next['type'] == 'expense')
            | (
                (df_next['type'] == 'income')
                & df_next['category'].astype(str).str.casefold().str.contains(r'gaji|upah', regex=True)
            )
        ]
    ) if not df_next.empty else 0

    # 2. Bangun time-series bulanan dari data training
    distinct_yms = sorted(df_training['ym'].unique()) if not df_training.empty else []
    if distinct_yms:
        first_year, first_month = map(int, distinct_yms[0].split('-'))
        distinct_yms = []
        period_year, period_month = first_year, first_month
        while (period_year, period_month) <= (cur_year, cur_month):
            distinct_yms.append(f"{period_year}-{period_month:02d}")
            if period_month == 12:
                period_year, period_month = period_year + 1, 1
            else:
                period_month += 1

    monthly_stats = []
    for ym in distinct_yms:
        ym_df = df_training[df_training['ym'] == ym]
        y_val, m_val = int(ym.split('-')[0]), int(ym.split('-')[1])

        salary_rows = ym_df[
            (ym_df['type'] == 'income')
            & ym_df['category'].astype(str).str.casefold().str.contains(r'gaji|upah', regex=True)
        ]
        inc = float(salary_rows['amount'].sum())
        exp = float(ym_df[ym_df['type'] == 'expense']['amount'].sum())
        savings = inc - exp
        s_ratio = round((savings / inc * 100), 1) if inc > 0 else 0.0

        cat_exp = ym_df[ym_df['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()

        is_current = (y_val == cur_year and m_val == cur_month)
        is_past = (y_val < cur_year) or (y_val == cur_year and m_val < cur_month)

        monthly_stats.append({
            'period': f"{MONTH_NAMES_ID[m_val]} {y_val}",
            'year': y_val,
            'month': m_val,
            'ym': ym,
            'income': inc,
            'expense': exp,
            'savings': savings,
            'savings_ratio': s_ratio,
            'is_current': is_current,
            'is_past': is_past,
            'categories': cat_exp
        })

    past_months = [m for m in monthly_stats if m['is_past']]
    current_month_stat = next((m for m in monthly_stats if m['is_current']), None)

    cur_actual_income = current_month_stat['income'] if current_month_stat else 0.0
    cur_actual_expense = current_month_stat['expense'] if current_month_stat else 0.0

    # Rencana pengeluaran untuk bulan berjalan
    cur_planned_total = 0.0
    for p in planned_expenses:
        p_date = parse_date(p.get('date', ''))
        if cycle_period(p_date, start_day, end_day) == (cur_year, cur_month) or not p.get('date'):
            prob = float(p.get('probability', 100)) / 100.0
            cur_planned_total += float(p.get('amount', 0)) * prob

    accuracy_series = []
    for index, month_data in enumerate(monthly_stats):
        if index == 0 or ((month_data['year'], month_data['month']) == current_period and today < cycle_bounds(*current_period, start_day, end_day)[1]):
            continue
        previous = monthly_stats[:index]
        if len(previous) >= 2:
            previous_expenses = np.array([item['expense'] for item in previous])
            prior_model = LinearRegression()
            prior_model.fit(np.arange(len(previous)).reshape(-1, 1), previous_expenses)
            regression_prediction = float(prior_model.predict([[len(previous)]])[0])
            weights = np.linspace(1, 2.5, len(previous))
            weighted_average = float(np.average(previous_expenses, weights=weights))
            predicted = round(max(0.0, (regression_prediction + weighted_average) / 2), -3)
        else:
            predicted = previous[-1]['expense']
        actual = month_data['expense']
        accuracy = max(0.0, 100.0 - abs(predicted - actual) / actual * 100.0) if actual > 0 else (100.0 if predicted == 0 else 0.0)
        accuracy_series.append({'ym': month_data['ym'], 'period': month_data['period'], 'accuracy': round(accuracy, 1)})

    history_days = sum(
        (cycle_bounds(item['year'], item['month'], start_day, end_day)[1] - cycle_bounds(item['year'], item['month'], start_day, end_day)[0]).days + 1
        for item in monthly_stats
    )
    history_total_income = sum(item['income'] for item in monthly_stats)
    history_total_expense = sum(item['expense'] for item in monthly_stats)
    history_count = len(monthly_stats)
    all_history_metrics = {
        'average_expense_per_month': round(history_total_expense / history_count) if history_count else 0,
        'average_expense_per_day': round(history_total_expense / history_days) if history_days else 0,
        'average_unspent_savings_per_month': round(sum(max(0.0, item['savings']) for item in monthly_stats) / history_count) if history_count else 0,
        'average_income_per_month': round(history_total_income / history_count) if history_count else 0,
        'safe_daily_spending': round(max(0.0, history_total_income - history_total_expense) / history_days) if history_days else 0,
        'periods_count': history_count,
        'accuracy_series': accuracy_series
    }

    # 3. STATISTICAL & MACHINE LEARNING MODELING
    trend_slope = 0.0
    trend_percent = 0.0
    trend_direction = "stabil"
    r2_score = 0.0
    std_err = 0.0

    model_data = past_months if len(past_months) >= 2 else monthly_stats
    num_historical_points = len(model_data)

    if num_historical_points >= 2:
        X = np.arange(num_historical_points).reshape(-1, 1)
        y_exp = np.array([m['expense'] for m in model_data])
        y_inc = np.array([m['income'] for m in model_data])

        model_exp = LinearRegression()
        model_exp.fit(X, y_exp)
        trend_slope = float(model_exp.coef_[0])
        r2_score = float(model_exp.score(X, y_exp))

        next_step_idx = num_historical_points
        regression_pred_exp = float(model_exp.predict([[next_step_idx]])[0])

        weights = np.linspace(1, 2.5, num_historical_points)
        weighted_avg_exp = float(np.average(y_exp, weights=weights))

        base_projected_exp = max(0.0, (regression_pred_exp * 0.5) + (weighted_avg_exp * 0.5))

        residuals = y_exp - model_exp.predict(X)
        std_err = float(np.std(residuals)) if len(residuals) > 1 else (base_projected_exp * 0.1)

        first_val = y_exp[0] if y_exp[0] > 0 else 1.0
        total_growth = (y_exp[-1] - first_val) / first_val
        trend_percent = round((total_growth / max(1, num_historical_points - 1)) * 100, 1)

        if trend_slope > 25000:
            trend_direction = "meningkat"
        elif trend_slope < -25000:
            trend_direction = "menurun"
        else:
            trend_direction = "stabil"

        if expected_next_income is not None and float(expected_next_income) > 0:
            projected_income = float(expected_next_income)
        else:
            valid_incomes = [inc for inc in y_inc if inc > 0]
            if valid_incomes:
                w_inc = np.linspace(1, 2, len(valid_incomes))
                projected_income = float(np.average(valid_incomes, weights=w_inc))
            else:
                projected_income = max(base_projected_exp * 1.25, 1000000.0)

    elif num_historical_points == 1:
        single_stat = model_data[0]
        base_projected_exp = single_stat['expense']
        std_err = base_projected_exp * 0.12
        projected_income = float(expected_next_income) if (expected_next_income and float(expected_next_income) > 0) else (single_stat['income'] if single_stat['income'] > 0 else base_projected_exp * 1.3)
        trend_direction = "baseline"
    else:
        base_projected_exp = cur_actual_expense + cur_planned_total
        std_err = base_projected_exp * 0.15
        projected_income = float(expected_next_income) if (expected_next_income and float(expected_next_income) > 0) else (cur_actual_income if cur_actual_income > 0 else base_projected_exp * 1.3)
        trend_direction = "data awal"

    # Final rounded projections
    final_forecast_expense = round(max(0.0, base_projected_exp), -3)
    projected_income = round(max(0.0, projected_income), -3)
    forecast_savings = max(0.0, projected_income - final_forecast_expense)
    savings_ratio = round((forecast_savings / projected_income * 100), 1) if projected_income > 0 else 0.0

    min_forecast_expense = max(0.0, round(final_forecast_expense - (1.28 * std_err), -3))
    max_forecast_expense = round(final_forecast_expense + (1.28 * std_err), -3)
    safe_daily_limit = round(final_forecast_expense / max(1, days_in_next_month), -2)

    # 4. Distribusi kategori
    df_exp_train = df_training[df_training['type'] == 'expense'] if not df_training.empty else pd.DataFrame()
    category_forecast = []
    if not df_exp_train.empty:
        cat_sums = df_exp_train.groupby('category')['amount'].sum()
        total_exp_all = cat_sums.sum()
        if total_exp_all > 0:
            for cat, amt in cat_sums.items():
                pct = amt / total_exp_all
                cat_amt = round(final_forecast_expense * pct, -3)
                category_forecast.append({
                    'category': cat,
                    'projected_amount': cat_amt,
                    'percentage': round(pct * 100, 1)
                })
    category_forecast = sorted(category_forecast, key=lambda x: x['projected_amount'], reverse=True)

    # 5. EVALUASI AKURASI HASIL FORECASTING DENGAN DATA BULAN DEPAN
    # Kondisi: ketika melihat bulan-bulan sebelumnya dan bulan depan sudah selesai atau akhir bulan
    accuracy_eval = {
        'can_evaluate': False,
        'is_completed': is_next_month_completed,
        'timing_status': timing_status,
        'target_month_name': f"{next_month_name} {next_year}",
        'accuracy_score': 0.0,
        'accuracy_grade': 'Belum Tersedia',
        'accuracy_color': 'muted',
        'status_message': '',
        'forecasted_expense': final_forecast_expense,
        'real_expense': real_next_expense,
        'diff_expense': 0.0,
        'abs_diff_expense': 0.0,
        'expense_accuracy': 0.0,
        'forecasted_savings': forecast_savings,
        'real_savings': real_next_savings,
        'diff_savings': 0.0,
        'savings_accuracy': 0.0,
        'real_income': real_next_income,
        'forecasted_income': projected_income,
        'real_tx_count': real_tx_count
    }

    if is_past_month and is_next_month_completed:
        if real_tx_count > 0:
            diff_exp = final_forecast_expense - real_next_expense
            abs_diff_exp = abs(diff_exp)
            if real_next_expense > 0:
                exp_err_pct = (abs_diff_exp / real_next_expense) * 100.0
                exp_acc = max(0.0, round(100.0 - exp_err_pct, 1))
            else:
                exp_acc = 100.0 if final_forecast_expense == 0 else 0.0

            diff_sav = forecast_savings - real_next_savings
            abs_diff_sav = abs(diff_sav)
            if real_next_savings > 0:
                sav_err_pct = (abs_diff_sav / real_next_savings) * 100.0
                sav_acc = max(0.0, round(100.0 - sav_err_pct, 1))
            else:
                sav_acc = 100.0 if forecast_savings == 0 else 50.0

            overall_acc = exp_acc
            if overall_acc >= 90:
                grade = "Sangat Akurat"
                col = "emerald"
            elif overall_acc >= 75:
                grade = "Akurat"
                col = "indigo"
            elif overall_acc >= 50:
                grade = "Cukup Akurat"
                col = "amber"
            else:
                grade = "Deviasi Tinggi"
                col = "rose"

            timing_text = "sudah selesai sepenuhnya" if timing_status == "selesai" else "telah mencapai akhir bulan"
            accuracy_eval.update({
                'can_evaluate': True,
                'accuracy_score': overall_acc,
                'accuracy_grade': grade,
                'accuracy_color': col,
                'status_message': f"Data bulan depan ({next_month_name} {next_year}) {timing_text}. Diverifikasi terhadap {real_tx_count} transaksi riil.",
                'diff_expense': diff_exp,
                'abs_diff_expense': abs_diff_exp,
                'expense_accuracy': exp_acc,
                'diff_savings': diff_sav,
                'savings_accuracy': sav_acc
            })
        else:
            accuracy_eval['status_message'] = f"Periode bulan depan ({next_month_name} {next_year}) telah berlalu, tetapi belum ada catatan transaksi riil yang terekam."
    elif is_past_month and not is_next_month_completed:
        accuracy_eval['status_message'] = f"Bulan depan ({next_month_name} {next_year}) sedang berjalan (tanggal {today.day}) dan belum akhir bulan. Evaluasi akurasi aktif saat data bulan selesai atau akhir bulan (tanggal 25+)."
    else:
        accuracy_eval['status_message'] = f"Saat ini sedang melihat bulan berjalan ({MONTH_NAMES_ID[cur_month]} {cur_year}). Gunakan navigator bulan di atas untuk melihat akurasi peramalan pada bulan-bulan sebelumnya."

    # 6. Narrative Insights
    insights = []
    if accuracy_eval['can_evaluate']:
        insights.append({
            'type': 'success' if accuracy_eval['accuracy_score'] >= 75 else 'warning',
            'title': f"Hasil Akurasi Model ({accuracy_eval['accuracy_grade']} - {accuracy_eval['accuracy_score']}%)",
            'message': f"Proyeksi pengeluaran untuk {next_month_name} {next_year} adalah Rp {final_forecast_expense:,.0f} vs Realisasi Riil Rp {real_next_expense:,.0f} (Selisih Rp {accuracy_eval['diff_expense']:+,.0f})."
        })

    if len(past_months) >= 2:
        insights.append({
            'type': 'info',
            'title': f'Analisis Data Historis {len(past_months)} Bulan Sebelumnya',
            'message': f'Model Scikit-Learn menganalisis {len(past_months)} bulan histori transaksi. Tren pengeluaran tercatat {trend_direction} ({trend_percent:+.1f}%/bulan) dengan pergeseran rata-rata Rp {abs(trend_slope):,.0f} per bulan.'
        })
    elif len(past_months) == 1:
        insights.append({
            'type': 'info',
            'title': 'Basis Data Historis 1 Bulan Sebelumnya',
            'message': f'Proyeksi mengacu pada 1 bulan historis ({past_months[0]["period"]}) serta aktivitas bulan acuan.'
        })

    if savings_ratio >= 25:
        insights.append({
            'type': 'success',
            'title': 'Kapasitas Tabungan Sehat',
            'message': f'Dengan proyeksi pemasukan Rp {projected_income:,.0f}, potensi tabungan bulan depan adalah Rp {forecast_savings:,.0f} ({savings_ratio}%).'
        })
    elif savings_ratio > 0:
        insights.append({
            'type': 'warning',
            'title': 'Margin Tabungan Perlu Dijaga',
            'message': f'Proyeksi sisa tabungan bulan depan sebesar Rp {forecast_savings:,.0f} ({savings_ratio}%). Pertahankan batas belanja harian aman.'
        })

    return {
        'status': 'success',
        'meta': {
            'analysis_date': today.isoformat(),
            'current_month': cur_month,
            'current_year': cur_year,
            'is_past_month': is_past_month,
            'next_month': next_month,
            'next_year': next_year,
            'next_month_name': next_month_name,
            'days_in_next_month': days_in_next_month,
            'start_day': start_day,
            'end_day': end_day,
            'next_period_start': next_start.isoformat(),
            'next_period_end': next_end.isoformat(),
            'all_time': all_time,
            'historical_months_count': len(past_months),
            'total_months_tracked': len(monthly_stats)
        },
        'accuracy_evaluation': accuracy_eval,
        'saved_input_log': log_info,
        'historical_analysis': {
            'months_analyzed_count': len(past_months),
            'historical_series': monthly_stats,
            'trend_slope': trend_slope,
            'trend_direction': trend_direction,
            'trend_percent': trend_percent,
            'model_name': 'Scikit-Learn Linear Regression + Weighted Moving Average',
            'r2_score': round(r2_score, 3)
        },
        'all_history_metrics': all_history_metrics,
        'forecast_next_month': {
            'projected_income': projected_income,
            'forecasted_expense': final_forecast_expense,
            'forecasted_savings': forecast_savings,
            'savings_ratio': savings_ratio,
            'safe_daily_limit': safe_daily_limit,
            'confidence_range': {
                'min': min_forecast_expense,
                'max': max_forecast_expense
            },
            'category_breakdown': category_forecast
        },
        'insights': insights
    }

def generate_empty_forecast(today, days_in_next_month, next_month_name, next_year, next_month, cur_year, cur_month, is_past_month, is_next_month_completed, timing_status, log_info):
    return {
        'status': 'success',
        'meta': {
            'analysis_date': today.isoformat(),
            'current_month': cur_month,
            'current_year': cur_year,
            'is_past_month': is_past_month,
            'next_month': next_month,
            'next_year': next_year,
            'next_month_name': next_month_name,
            'days_in_next_month': days_in_next_month,
            'historical_months_count': 0,
            'total_months_tracked': 0
        },
        'accuracy_evaluation': {
            'can_evaluate': False,
            'is_completed': is_next_month_completed,
            'timing_status': timing_status,
            'target_month_name': f"{next_month_name} {next_year}",
            'accuracy_score': 0.0,
            'accuracy_grade': 'Belum Ada Data',
            'accuracy_color': 'muted',
            'status_message': 'Belum ada data transaksi yang tercatat untuk menghitung akurasi peramalan.',
            'forecasted_expense': 0,
            'real_expense': 0,
            'diff_expense': 0,
            'abs_diff_expense': 0,
            'expense_accuracy': 0,
            'forecasted_savings': 0,
            'real_savings': 0,
            'diff_savings': 0,
            'savings_accuracy': 0,
            'real_income': 0,
            'forecasted_income': 0,
            'real_tx_count': 0
        },
        'saved_input_log': log_info,
        'historical_analysis': {
            'months_analyzed_count': 0,
            'historical_series': [],
            'trend_slope': 0,
            'trend_direction': 'belum ada data',
            'trend_percent': 0,
            'model_name': 'Scikit-Learn Linear Regression',
            'r2_score': 0
        },
        'all_history_metrics': {
            'average_expense_per_month': 0,
            'average_expense_per_day': 0,
            'average_unspent_savings_per_month': 0,
            'average_income_per_month': 0,
            'safe_daily_spending': 0,
            'periods_count': 0,
            'accuracy_series': []
        },
        'forecast_next_month': {
            'projected_income': log_info.get('amount', 0) if log_info.get('exists') else 0,
            'forecasted_expense': 0,
            'forecasted_savings': 0,
            'savings_ratio': 0,
            'safe_daily_limit': 0,
            'confidence_range': {'min': 0, 'max': 0},
            'category_breakdown': []
        },
        'insights': [{
            'type': 'info',
            'title': 'Belum Ada Data Transaksi',
            'message': 'Catat pemasukan & pengeluaran untuk mengaktifkan model forcasting regresi Python dan evaluasi akurasi.'
        }]
    }
