const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchSummary(year = null, month = null, isAllTime = false) {
  let url = `${API_BASE}/summary`;
  if (isAllTime) {
    url += `?all=true`;
  } else if (year && month) {
    url += `?year=${year}&month=${month}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error('Gagal mengambil ringkasan keuangan');
  return res.json();
}

export async function fetchTransactions() {
  const res = await fetch(`${API_BASE}/transactions`);
  if (!res.ok) throw new Error('Gagal mengambil daftar transaksi');
  return res.json();
}

export async function createTransaction(txData) {
  const res = await fetch(`${API_BASE}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan transaksi');
  }
  return res.json();
}

export async function updateTransaction(id, txData) {
  const res = await fetch(`${API_BASE}/transactions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal memperbarui transaksi');
  }
  return res.json();
}

export async function deleteTransaction(id) {
  const res = await fetch(`${API_BASE}/transactions/${id}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Gagal menghapus transaksi');
  return res.json();
}

export async function fetchPlanned() {
  const res = await fetch(`${API_BASE}/planned`);
  if (!res.ok) throw new Error('Gagal mengambil kemungkinan pengeluaran');
  return res.json();
}

export async function createPlanned(planData) {
  const res = await fetch(`${API_BASE}/planned`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(planData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan rencana pengeluaran');
  }
  return res.json();
}

export async function deletePlanned(id) {
  const res = await fetch(`${API_BASE}/planned/${id}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Gagal menghapus rencana');
  return res.json();
}

export async function updatePlanned(id, planData) {
  const res = await fetch(`${API_BASE}/planned/${id}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(planData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal memperbarui rencana pengeluaran');
  }
  return res.json();
}

export async function fetchMonthlyNeeds(year, month) {
  const res = await fetch(`${API_BASE}/monthly-needs?year=${year}&month=${month}`);
  if (!res.ok) throw new Error('Gagal mengambil kebutuhan bulanan');
  return res.json();
}

export async function createMonthlyNeed(item) {
  const res = await fetch(`${API_BASE}/monthly-needs`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(item)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan kebutuhan bulanan');
  }
  return res.json();
}

export async function updateMonthlyNeed(id, item) {
  const res = await fetch(`${API_BASE}/monthly-needs/${id}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(item)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal memperbarui kebutuhan bulanan');
  }
  return res.json();
}

export async function deleteMonthlyNeed(id) {
  const res = await fetch(`${API_BASE}/monthly-needs/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus kebutuhan bulanan');
  return res.json();
}

export async function realizeMonthlyNeed(id, year, month, quantity, wallet = '') {
  const res = await fetch(`${API_BASE}/monthly-needs/${id}/realize`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ year, month, quantity, wallet })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal mengirim kebutuhan ke log transaksi');
  }
  return res.json();
}

export async function fetchMonthlyTemplates() {
  const res = await fetch(`${API_BASE}/monthly-templates`);
  if (!res.ok) throw new Error('Gagal mengambil template kebutuhan');
  return res.json();
}

export async function createMonthlyTemplate(item) {
  const res = await fetch(`${API_BASE}/monthly-templates`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(item)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan template kebutuhan');
  }
  return res.json();
}

export async function updateMonthlyTemplate(id, item) {
  const res = await fetch(`${API_BASE}/monthly-templates/${id}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(item)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal memperbarui template kebutuhan');
  }
  return res.json();
}

export async function deleteMonthlyTemplate(id) {
  const res = await fetch(`${API_BASE}/monthly-templates/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus template kebutuhan');
  return res.json();
}

export async function applyMonthlyTemplate(id, year, month, force = false) {
  const res = await fetch(`${API_BASE}/monthly-templates/${id}/apply`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ year, month, force })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const error = new Error(err.error || 'Gagal menerapkan template kebutuhan');
    error.requiresConfirmation = Boolean(err.requires_confirmation);
    throw error;
  }
  return res.json();
}

export async function runForecast(year = null, month = null, expectedIncome = null, isSavingLog = false, allTime = false) {
  const payload = {};
  if (year) payload.year = year;
  if (month) payload.month = month;
  payload.all_time = allTime;
  if (expectedIncome !== null && expectedIncome !== undefined && expectedIncome !== '') {
    payload.expected_income = Number(expectedIncome);
  }
  if (isSavingLog) {
    payload.is_saving_log = true;
  }
  const res = await fetch(`${API_BASE}/forecast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Gagal menjalankan Python forcasting model');
  return res.json();
}

export async function clearAllData() {
  const res = await fetch(`${API_BASE}/clear-all`, { method: 'POST' });
  if (!res.ok) throw new Error('Gagal mengosongkan data');
  return res.json();
}

export async function fetchWallets() {
  const res = await fetch(`${API_BASE}/wallets`);
  if (!res.ok) throw new Error('Gagal mengambil daftar wallet');
  return res.json();
}

export async function createWallet(name) {
  const res = await fetch(`${API_BASE}/wallets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal membuat wallet baru');
  }
  return res.json();
}

export async function deleteWallet(id) {
  const res = await fetch(`${API_BASE}/wallets/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Gagal menghapus wallet');
  return res.json();
}

export async function fetchWalletBalances(year = null, month = null, allTime = false) {
  const params = new URLSearchParams();
  if (allTime) {
    params.set('all', 'true');
  } else {
    if (year) params.set('year', year);
    if (month) params.set('month', month);
  }
  const query = params.toString();
  const res = await fetch(`${API_BASE}/wallet-balances${query ? `?${query}` : ''}`);
  if (!res.ok) throw new Error('Gagal mengambil saldo wallet');
  return res.json();
}

export async function fetchCutoffDays() {
  const res = await fetch(`${API_BASE}/settings/cutoff-day`);
  if (!res.ok) throw new Error('Gagal mengambil periode cut-off');
  const data = await res.json();
  return {
    start_day: Number(data.start_day),
    end_day: Number(data.end_day)
  };
}

export async function updateCutoffDays(startDay, endDay) {
  const res = await fetch(`${API_BASE}/settings/cutoff-day`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_day: Number(startDay), end_day: Number(endDay) })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan periode cut-off');
  }
  const data = await res.json();
  return {
    start_day: Number(data.start_day),
    end_day: Number(data.end_day)
  };
}

export async function fetchCyclePeriod(year, month) {
  const res = await fetch(`${API_BASE}/settings/cycle-period?year=${year}&month=${month}`);
  if (!res.ok) throw new Error('Gagal mengambil periode bulan');
  return res.json();
}

export async function updateCyclePeriod(year, month, start, end) {
  const res = await fetch(`${API_BASE}/settings/cycle-period`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ year, month, start, end })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal menyimpan periode bulan');
  }
  return res.json();
}

export async function fetchSavingsWallets() {
  const res = await fetch(`${API_BASE}/settings/savings-wallets`);
  if (!res.ok) throw new Error('Gagal mengambil pengaturan rekening tabungan');
  return res.json();
}

export async function updateSavingsWallets(wallets) {
  const res = await fetch(`${API_BASE}/settings/savings-wallets`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallets })
  });
  if (!res.ok) throw new Error('Gagal menyimpan pengaturan rekening tabungan');
  return res.json();
}

export async function updateWalletInitialBalance(id, amount) {
  const res = await fetch(`${API_BASE}/wallets/${id}/initial-balance`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ initial_balance: Number(amount) })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Gagal memperbarui saldo awal rekening');
  }
  return res.json();
}
