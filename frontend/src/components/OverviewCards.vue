<template>
  <div class="overview-grid">
    <!-- Card 1: Total Pemasukan -->
    <div class="fin-card metric-card income-card">
      <div class="card-top">
        <span class="metric-label">Total Pemasukan · {{ monthLabel }}</span>
        <div class="metric-icon-wrap income-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
        </div>
      </div>
      <div class="metric-value">{{ formatRupiah(summary.total_income) }}</div>
      <div class="card-footer">
        <span class="badge badge-income">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="19" x2="12" y2="5"/>
            <polyline points="5 12 12 5 19 12"/>
          </svg>
          Arus Masuk
        </span>
        <span class="sub-text">Memperbesar kapasitas donat</span>
      </div>
    </div>

    <!-- Card 2: Pengeluaran Riil -->
    <div class="fin-card metric-card expense-card">
      <div class="card-top">
        <span class="metric-label">Pengeluaran Riil · {{ monthLabel }}</span>
        <div class="metric-icon-wrap expense-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
        </div>
      </div>
      <div class="metric-value">{{ formatRupiah(summary.total_expense) }}</div>
      <div class="card-footer">
        <span class="badge badge-expense">
          {{ calculateExpensePercent() }}% dari Pemasukan
        </span>
        <span class="sub-text">{{ transactionCount }} transaksi tercatat</span>
      </div>
    </div>

    <!-- Card 3: Kemungkinan Pengeluaran -->
    <div class="fin-card metric-card planned-card">
      <div class="card-top">
        <span class="metric-label">Kemungkinan Pengeluaran</span>
        <div class="metric-icon-wrap planned-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
      </div>
      <div class="metric-value">{{ formatRupiah(summary.total_planned) }}</div>
      <div class="card-footer">
        <span class="badge badge-planned">
          {{ plannedCount }} Rencana Aktif
        </span>
        <span class="sub-text">Estimasi s.d akhir bulan</span>
      </div>
    </div>

    <!-- Card 4: Total uang yang saat ini tersimpan di rekening -->
    <div class="fin-card metric-card savings-card">
      <div class="card-top">
        <span class="metric-label">Total Uang Tersimpan</span>
        <div class="metric-icon-wrap savings-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
          </svg>
        </div>
      </div>
      <div class="metric-value highlight-savings">{{ formatRupiah(summary.sisa_tabungan) }}</div>
      <div class="card-footer">
        <span class="badge badge-savings">
          Saldo seluruh rekening
        </span>
        <span class="sub-text">Dihitung dari mutasi saldo</span>
      </div>
    </div>

    <!-- Card 5: Estimasi total tabungan aktif -->
    <div class="fin-card metric-card savings-forecast-card">
      <div class="card-top">
        <span class="metric-label">Total Tabungan Aktif</span>
        <div class="metric-icon-wrap savings-forecast-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M3 7h18v13H3z"/>
            <path d="M7 7V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2"/>
            <path d="M12 11v5M9.5 13.5h5"/>
          </svg>
        </div>
      </div>
      <div class="metric-value highlight-savings">{{ formatRupiah(totalSavings) }}</div>
      <div class="card-footer">
        <span class="badge badge-savings">Sisa + alokasi tabungan</span>
        <span class="sub-text">Aktif saja</span>
      </div>
    </div>
  </div>
</template>

<script>
import { formatRupiah } from '../utils/formatters.js';

export default {
  name: 'OverviewCards',
  props: {
    monthLabel: {
      type: String,
      default: 'Bulan Ini'
    },
    summary: {
      type: Object,
      default: () => ({
        total_income: 0,
        total_expense: 0,
        total_planned: 0,
        sisa_tabungan: 0,
        savings_ratio: 0
      })
    },
    transactionCount: {
      type: Number,
      default: 0
    },
    plannedCount: {
      type: Number,
      default: 0
    },
    totalSavings: {
      type: Number,
      default: 0
    }
  },
  methods: {
    formatRupiah,
    calculateExpensePercent() {
      if (!this.summary.total_income || this.summary.total_income === 0) return 0;
      return Math.round((this.summary.total_expense / this.summary.total_income) * 100);
    }
  }
};
</script>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.metric-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.35rem 1.4rem;
  border-radius: 18px;
  background: var(--bg-card);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.85rem;
}

.metric-label {
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--text-muted);
}

.metric-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.income-icon {
  background: var(--income-glow);
  color: var(--income);
}
.expense-icon {
  background: var(--expense-glow);
  color: var(--expense);
}
.planned-icon {
  background: var(--planned-glow);
  color: var(--planned);
}
.savings-icon {
  background: var(--savings-glow);
  color: var(--savings);
}
.savings-forecast-icon {
  background: rgba(34, 197, 94, 0.14);
  color: #22c55e;
}

.metric-value {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #ffffff;
  margin-bottom: 0.85rem;
  font-feature-settings: 'tnum' on, 'lnum' on;
}

.highlight-savings {
  color: var(--savings-text);
  text-shadow: 0 0 20px rgba(6, 182, 212, 0.25);
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.sub-text {
  font-size: 0.75rem;
  color: var(--text-dim);
}

.status-good {
  color: var(--income-text);
  font-weight: 600;
}
.status-warn {
  color: var(--planned-text);
  font-weight: 600;
}
.status-alert {
  color: var(--expense-text);
  font-weight: 600;
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
