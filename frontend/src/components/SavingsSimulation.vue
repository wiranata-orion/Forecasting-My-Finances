<template>
  <section class="fin-card simulation-container" id="simulasi-tabungan">
    <div class="simulation-header">
      <div>
        <div class="simulation-kicker">
          <span class="simulation-icon" aria-hidden="true">↗</span>
          Simulasi Perencanaan
        </div>
        <h3 class="simulation-title">Simulasi Tabungan</h3>
        <p class="simulation-desc">
          Hitung perkiraan tabungan sampai bulan yang kamu tentukan berdasarkan template kebutuhan bulanan dan pengeluaran satu kali.
        </p>
      </div>
      <span class="badge badge-savings">Tanpa mengubah data transaksi</span>
    </div>

    <div class="simulation-form-grid">
      <label class="simulation-field">
        <span>Bulan target</span>
        <input
          v-model="targetMonth"
          class="form-input"
          type="month"
          :min="nextMonthKey"
          aria-label="Bulan target simulasi"
          @change="targetMonthTouched = true"
        >
        <small>{{ monthCount }} bulan dari periode terpilih</small>
      </label>
      <label class="simulation-field">
        <span>Saldo tabungan awal</span>
        <input
          class="form-input"
          type="text"
          inputmode="numeric"
          :value="formatMoneyInput(openingSavingsAmount)"
          aria-label="Saldo tabungan awal"
          @input="handleMoneyInput('openingSavingsInput', $event)"
        >
        <small>Otomatis dari Total Tabungan Akhir (bisa diedit).</small>
      </label>
      <label class="simulation-field">
        <span>Pemasukan per bulan</span>
        <input
          class="form-input"
          type="text"
          inputmode="numeric"
          :value="formatMoneyInput(monthlyIncomeAmount)"
          aria-label="Pemasukan per bulan"
          @input="handleMoneyInput('monthlyIncomeInput', $event)"
        >
        <small>Default dari proyeksi pemasukan otomatis.</small>
      </label>
      <label class="simulation-field">
        <span>Template kebutuhan bulanan</span>
        <select v-model="templateId" class="form-select" :disabled="!templateOptions.length" aria-label="Pilih template kebutuhan">
          <option value="">Pilih template kebutuhan</option>
          <option v-for="template in templateOptions" :key="template.value" :value="template.value">
            {{ template.label }} · {{ formatRupiah(template.amount) }}/bln (Est. sisa: {{ formatRupiah(template.remaining) }})
          </option>
        </select>
        <small>Template yang dipilih akan digunakan berulang setiap bulan dalam simulasi.</small>
      </label>
    </div>

    <div class="extra-expense-panel">
      <div class="extra-expense-heading">
        <div>
          <strong>Pengeluaran satu kali di bulan tertentu</strong>
          <small>Contoh: servis kendaraan di Februari atau liburan di Juni.</small>
        </div>
        <span class="badge badge-planned">{{ extraExpenses.length }} tambahan</span>
      </div>
      <div class="extra-expense-form">
        <input v-model.trim="expenseDraft.title" class="form-input" placeholder="Nama pengeluaran" aria-label="Nama pengeluaran tambahan">
        <input :value="formatMoneyInput(expenseDraft.amount)" class="form-input" type="text" inputmode="numeric" placeholder="Nominal" aria-label="Nominal pengeluaran tambahan" @input="handleDraftAmountInput($event)">
        <input v-model="expenseDraft.month" class="form-input" type="month" :min="nextMonthKey" :max="targetMonthForCalculation" aria-label="Bulan pengeluaran tambahan">
        <button class="btn btn-secondary btn-sm" type="button" @click="addExtraExpense">+ Tambahkan</button>
      </div>
      <p v-if="extraExpenseError" class="simulation-error">{{ extraExpenseError }}</p>
      <div v-if="extraExpenses.length" class="extra-expense-list">
        <div v-for="expense in sortedExtraExpenses" :key="expense.id" class="extra-expense-row">
          <span class="extra-expense-month">{{ formatMonthLabel(expense.month) }}</span>
          <span class="extra-expense-name">{{ expense.title }}</span>
          <strong>{{ formatRupiah(expense.amount) }}</strong>
          <button class="remove-expense-btn" type="button" title="Hapus pengeluaran tambahan" @click="removeExtraExpense(expense.id)">×</button>
        </div>
      </div>
      <p v-else class="simulation-empty">Belum ada pengeluaran khusus yang dijadwalkan.</p>
    </div>

    <div class="simulation-result-header">
      <div>
        <span class="simulation-result-label">Perkiraan tabungan akhir</span>
        <strong class="simulation-result-value" :class="finalSavings >= 0 ? 'text-savings' : 'text-expense'">{{ formatRupiah(finalSavings) }}</strong>
        <small>{{ formatMonthLabel(targetMonthForCalculation) }} · {{ finalSavings >= openingSavingsAmount ? 'bertambah' : 'berkurang' }} {{ formatRupiah(Math.abs(finalSavings - openingSavingsAmount)) }}</small>
      </div>
      <div class="simulation-summary-metrics">
        <div><span>Total pemasukan</span><strong class="text-income">{{ formatRupiah(totalSimulatedIncome) }}</strong></div>
        <div><span>Total pengeluaran</span><strong class="text-expense">{{ formatRupiah(totalSimulatedExpense) }}</strong></div>
        <div><span>Tabungan bersih</span><strong :class="netSavings >= 0 ? 'text-savings' : 'text-expense'">{{ formatRupiah(netSavings) }}</strong></div>
      </div>
    </div>

    <div class="simulation-table-wrap">
      <table class="simulation-table">
        <thead>
          <tr>
            <th>Bulan</th>
            <th>Pemasukan</th>
            <th>Pengeluaran</th>
            <th>Selisih / bulan</th>
            <th>Akumulasi tabungan</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in simulationRows" :key="row.month">
            <td>
              <strong>{{ formatMonthLabel(row.month) }}</strong>
              <small v-if="row.specialExpenses">{{ row.specialExpenses }} pengeluaran tambahan</small>
            </td>
            <td class="text-income">{{ formatRupiah(row.income) }}</td>
            <td class="text-expense">{{ formatRupiah(row.expense) }}</td>
            <td :class="row.net >= 0 ? 'text-savings' : 'text-expense'">{{ row.net >= 0 ? '+' : '' }}{{ formatRupiah(row.net) }}</td>
            <td><strong :class="row.balance >= 0 ? 'text-savings' : 'text-expense'">{{ formatRupiah(row.balance) }}</strong></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!simulationRows.length" class="simulation-empty">Pilih bulan target untuk melihat hasil simulasi.</p>
    <p class="simulation-note">Simulasi ini adalah estimasi. Template kebutuhan dianggap berulang setiap bulan, sedangkan pengeluaran tambahan hanya dibebankan pada bulan yang dipilih.</p>
  </section>
</template>

<script>
import { formatRupiah } from '../utils/formatters.js';

function toMonthKey(year, month) {
  return `${year}-${String(month).padStart(2, '0')}`;
}

function parseMonthKey(value) {
  const [year, month] = String(value || '').split('-').map(Number);
  return Number.isFinite(year) && Number.isFinite(month) ? new Date(year, month - 1, 1) : null;
}

function addMonths(date, count) {
  return new Date(date.getFullYear(), date.getMonth() + count, 1);
}

export default {
  name: 'SavingsSimulation',
  props: {
    forecastData: { type: Object, default: () => ({}) },
    summary: { type: Object, default: () => ({}) },
    activeSavings: { type: Number, default: 0 },
    monthlyNeeds: { type: Array, default: () => [] },
    monthlyTemplates: { type: Array, default: () => [] },
    savingsWallets: { type: Array, default: () => [] },
    selectedYear: { type: Number, default: () => new Date().getFullYear() },
    selectedMonth: { type: Number, default: () => new Date().getMonth() + 1 }
  },
  data() {
    const next = addMonths(new Date(this.selectedYear, this.selectedMonth - 1, 1), 1);
    return {
      targetMonth: toMonthKey(next.getFullYear(), next.getMonth() + 1),
      targetMonthTouched: false,
      openingSavingsInput: null,
      monthlyIncomeInput: null,
      templateId: '',
      extraExpenses: [],
      expenseDraft: { title: '', amount: null, month: toMonthKey(next.getFullYear(), next.getMonth() + 1) },
      extraExpenseError: ''
    };
  },
  computed: {
    nextMonthKey() {
      const next = addMonths(new Date(this.selectedYear, this.selectedMonth - 1, 1), 1);
      return toMonthKey(next.getFullYear(), next.getMonth() + 1);
    },
    targetMonthForCalculation() {
      const selected = parseMonthKey(this.targetMonth);
      const next = parseMonthKey(this.nextMonthKey);
      if (!selected || !next || selected < next) return this.nextMonthKey;
      return this.targetMonth;
    },
    openingSavingsAmount() {
      if (this.openingSavingsInput !== null) return Number(this.openingSavingsInput) || 0;
      return Number(this.activeSavings) || 0;
    },
    monthlyIncomeAmount() {
      if (this.monthlyIncomeInput !== null) return Math.max(0, Number(this.monthlyIncomeInput) || 0);
      return Number(this.summary?.total_income) || 2250000;
    },
    baseExpenseAmount() {
      return 0;
    },
    templateOptions() {
      const options = [];
      const income = this.monthlyIncomeAmount;
      this.monthlyTemplates.forEach(template => {
        const amount = this.expenseItemsTotal(template.items || [], false);
        if (amount > 0) {
          options.push({
            value: `template-${template.id}`,
            label: template.name,
            amount,
            remaining: income - amount
          });
        }
      });
      return options;
    },
    selectedTemplateAmount() {
      return Number(this.templateOptions.find(item => item.value === this.templateId)?.amount || 0);
    },
    monthCount() {
      const start = parseMonthKey(this.nextMonthKey);
      const end = parseMonthKey(this.targetMonthForCalculation);
      if (!start || !end || end < start) return 1;
      return Math.max(1, (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth() + 1);
    },
    sortedExtraExpenses() {
      return [...this.extraExpenses].sort((a, b) => a.month.localeCompare(b.month));
    },
    simulationRows() {
      const rows = [];
      let balance = this.openingSavingsAmount;
      const start = parseMonthKey(this.nextMonthKey);
      for (let index = 0; index < this.monthCount; index += 1) {
        const date = addMonths(start, index);
        const month = toMonthKey(date.getFullYear(), date.getMonth() + 1);
        const scheduled = this.extraExpenses.filter(item => item.month === month);
        const extraAmount = scheduled.reduce((total, item) => total + Number(item.amount || 0), 0);
        const expense = this.selectedTemplateAmount + extraAmount;
        const income = this.monthlyIncomeAmount;
        const net = income - expense;
        balance += net;
        rows.push({ month, income, expense, net, balance, specialExpenses: scheduled.length });
      }
      return rows;
    },
    finalSavings() {
      return this.simulationRows.length ? this.simulationRows[this.simulationRows.length - 1].balance : this.openingSavingsAmount;
    },
    totalSimulatedIncome() {
      return this.simulationRows.reduce((total, row) => total + row.income, 0);
    },
    totalSimulatedExpense() {
      return this.simulationRows.reduce((total, row) => total + row.expense, 0);
    },
    netSavings() {
      return this.finalSavings - this.openingSavingsAmount;
    }
  },
  watch: {
    nextMonthKey(next) {
      if (!this.targetMonthTouched || this.targetMonth < next) this.targetMonth = next;
      if (!this.expenseDraft.month || this.expenseDraft.month < next) this.expenseDraft.month = next;
    },
    templateOptions(options) {
      if (this.templateId && !options.some(item => item.value === this.templateId)) this.templateId = '';
    },
    selectedMonth() {
      this.openingSavingsInput = null;
    },
    selectedYear() {
      this.openingSavingsInput = null;
    }
  },
  methods: {
    formatRupiah,
    formatMoneyInput(value) {
      const amount = Number(value);
      if (!Number.isFinite(amount) || amount === 0) return amount === 0 ? '0' : '';
      return new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(Math.round(amount));
    },
    parseMoneyInput(value) {
      const digits = String(value || '').replace(/\D/g, '');
      return digits ? Number(digits) : 0;
    },
    handleMoneyInput(field, event) {
      this[field] = this.parseMoneyInput(event.target.value);
      event.target.value = this.formatMoneyInput(this[field]);
    },
    handleDraftAmountInput(event) {
      this.expenseDraft.amount = this.parseMoneyInput(event.target.value);
      event.target.value = this.formatMoneyInput(this.expenseDraft.amount);
    },
    toNumber(value) {
      return value === '' ? 0 : Number(value) || 0;
    },
    formatMonthLabel(month) {
      const date = parseMonthKey(month);
      if (!date) return '-';
      return new Intl.DateTimeFormat('id-ID', { month: 'long', year: 'numeric' }).format(date);
    },
    isSavingsExpense(item) {
      if (item.savings_status === 'savings') return true;
      const wallet = String(item.wallet || '').trim();
      return Boolean(wallet) && this.savingsWallets.some(savingsWallet => String(savingsWallet).trim() === wallet);
    },
    expenseItemsTotal(items, useRemaining) {
      return items.reduce((total, item) => {
        if (item.type && item.type !== 'expense') return total;
        if (this.isSavingsExpense(item)) return total;
        const occurrences = useRemaining ? Number(item.remaining_occurrences ?? item.total_occurrences ?? 0) : Number(item.total_occurrences || 0);
        return total + Number(item.amount || 0) * occurrences;
      }, 0);
    },
    addExtraExpense() {
      this.extraExpenseError = '';
      const month = this.expenseDraft.month || this.nextMonthKey;
      if (!this.expenseDraft.title || Number(this.expenseDraft.amount) <= 0) {
        this.extraExpenseError = 'Nama dan nominal pengeluaran wajib diisi.';
        return;
      }
      if (month < this.nextMonthKey || month > this.targetMonthForCalculation) {
        this.extraExpenseError = 'Pilih bulan di dalam rentang simulasi.';
        return;
      }
      this.extraExpenses.push({ id: `extra-${Date.now()}-${Math.random()}`, title: this.expenseDraft.title, amount: Number(this.expenseDraft.amount), month });
      this.expenseDraft = { title: '', amount: null, month };
    },
    removeExtraExpense(id) {
      this.extraExpenses = this.extraExpenses.filter(item => item.id !== id);
    }
  }
};
</script>

<style scoped>
.simulation-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 2rem;
  background: linear-gradient(180deg, #122532 0%, var(--bg-card) 100%);
  border-color: rgba(6, 182, 212, 0.25);
}

.simulation-header,
.simulation-result-header,
.extra-expense-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.simulation-kicker {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--savings-text);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.simulation-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 7px;
  background: var(--savings-glow);
  font-size: 1rem;
}

.simulation-title {
  margin-top: 0.35rem;
  color: #fff;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.simulation-desc {
  max-width: 720px;
  margin-top: 0.3rem;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.simulation-form-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.8rem;
}

.simulation-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 700;
}

.simulation-field small,
.simulation-check-row small,
.extra-expense-heading small,
.simulation-result-header small,
.extra-expense-row small {
  color: var(--text-dim);
  font-size: 0.7rem;
  font-weight: 500;
}

.simulation-options,
.extra-expense-panel {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 13px;
  background: rgba(14, 20, 36, 0.65);
}

.simulation-options {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.simulation-template-copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 250px;
  color: var(--text-main);
  font-size: 0.8rem;
}

.template-select {
  flex: 1;
  min-width: 250px;
}

.extra-expense-heading strong {
  display: block;
  color: var(--text-main);
  font-size: 0.82rem;
}

.extra-expense-heading small {
  display: block;
  margin-top: 0.2rem;
}

.extra-expense-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr auto;
  gap: 0.6rem;
  margin-top: 0.85rem;
}

.simulation-error {
  margin-top: 0.55rem;
  color: var(--expense-text);
  font-size: 0.73rem;
}

.extra-expense-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin-top: 0.85rem;
}

.extra-expense-row {
  display: grid;
  grid-template-columns: 145px 1fr auto 26px;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.035);
  color: var(--text-muted);
  font-size: 0.76rem;
}

.extra-expense-month {
  color: var(--planned-text);
  font-size: 0.72rem;
  font-weight: 700;
}

.extra-expense-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.extra-expense-row strong {
  color: var(--expense-text);
  font-size: 0.78rem;
}

.remove-expense-btn {
  border: 0;
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 1.15rem;
  line-height: 1;
}

.remove-expense-btn:hover {
  color: var(--expense-text);
}

.simulation-empty {
  color: var(--text-dim);
  font-size: 0.75rem;
}

.simulation-result-header {
  align-items: center;
  padding: 1rem;
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 13px;
  background: linear-gradient(110deg, rgba(6, 182, 212, 0.1), rgba(99, 102, 241, 0.08));
}

.simulation-result-label {
  display: block;
  color: var(--text-muted);
  font-size: 0.74rem;
  font-weight: 700;
}

.simulation-result-value {
  display: block;
  margin: 0.2rem 0;
  font-size: 1.65rem;
  font-weight: 850;
  letter-spacing: -0.04em;
}

.simulation-summary-metrics {
  display: flex;
  gap: 1.4rem;
  flex-wrap: wrap;
}

.simulation-summary-metrics div {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.simulation-summary-metrics span {
  color: var(--text-dim);
  font-size: 0.7rem;
}

.simulation-summary-metrics strong {
  font-size: 0.86rem;
}

.simulation-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.simulation-table {
  width: 100%;
  min-width: 670px;
  border-collapse: collapse;
  font-size: 0.78rem;
}

.simulation-table th,
.simulation-table td {
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid var(--border-color);
  text-align: right;
  white-space: nowrap;
}

.simulation-table th:first-child,
.simulation-table td:first-child {
  text-align: left;
}

.simulation-table th {
  color: var(--text-dim);
  background: rgba(255, 255, 255, 0.025);
  font-size: 0.7rem;
  font-weight: 700;
}

.simulation-table tbody tr:last-child td {
  border-bottom: 0;
}

.simulation-table td:first-child {
  color: var(--text-main);
}

.simulation-table td:first-child small {
  display: block;
  margin-top: 0.15rem;
  color: var(--planned-text);
  font-size: 0.66rem;
}

.simulation-note {
  color: var(--text-dim);
  font-size: 0.7rem;
}

@media (max-width: 900px) {
  .simulation-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .extra-expense-form {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
  .simulation-form-grid {
    grid-template-columns: 1fr;
  }

  .extra-expense-form {
    grid-template-columns: 1fr;
  }

  .extra-expense-row {
    grid-template-columns: 1fr auto 26px;
  }

  .extra-expense-month {
    grid-column: 1 / -1;
  }

  .simulation-summary-metrics {
    width: 100%;
    justify-content: space-between;
    gap: 0.7rem;
  }
}
</style>
