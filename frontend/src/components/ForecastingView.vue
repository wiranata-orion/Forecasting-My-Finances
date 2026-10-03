<template>
  <div class="fin-card forecast-container" id="forcasting">
    <!-- Header with AI Badge & Single Log Input -->
    <div class="forecast-header">
      <div>
        <div class="header-tag-row">
          <span class="python-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M12 2a10 10 0 0 0-10 10c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.1-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
            </svg>
            Python ML Model (Scikit-Learn)
          </span>
          <span class="target-month-badge">
            Siklus Proyeksi: {{ forecastData?.meta?.next_month_name || 'Bulan Ini' }} {{ forecastData?.meta?.next_year || '' }}
          </span>
          <span v-if="isPastMonth" class="history-mode-pill">
            Mode History Lampau
          </span>
        </div>
        <h3 class="forecast-title">{{ isAllTime ? 'Analisis & Forecasting Seluruh History' : 'Forecasting Pengeluaran & Tabungan Bulan Terpilih' }}</h3>
        <p class="forecast-desc">
          Model regresi linier & analisis deret waktu di backend Python memproyeksikan estimasi pengeluaran dan jumlah sisa tabungan berdasarkan pola historis.
        </p>
      </div>

    </div>

    <!-- 4 Forecast Metric Cards -->
    <div class="forecast-cards-grid">
      <!-- 1. Proyeksi Pengeluaran -->
      <div class="f-card f-card-expense">
        <div class="f-card-top">
          <span class="f-label">Proyeksi Pengeluaran</span>
          <span class="f-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
              <polyline points="17 18 23 18 23 12"/>
            </svg>
          </span>
        </div>
        <div class="f-val text-expense">{{ formatRupiah(nextMonthData.forecasted_expense) }}</div>
        <div class="f-footer">
          <span class="f-sub">
            Rentang 95%: {{ formatRupiah(nextMonthData.confidence_range?.min) }} – {{ formatRupiah(nextMonthData.confidence_range?.max) }}
          </span>
        </div>
      </div>

      <!-- 2. Estimasi Yang Bisa Ditabung -->
      <div class="f-card f-card-savings">
        <div class="f-card-top">
          <span class="f-label">Estimasi Uang Bisa Ditabung</span>
          <span class="f-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
            </svg>
          </span>
        </div>
        <div class="f-val text-savings">{{ formatRupiah(nextMonthData.forecasted_savings) }}</div>
        <div class="f-footer">
          <span class="badge badge-savings">
            {{ nextMonthData.savings_ratio }}% Potensi Tabungan
          </span>
        </div>
      </div>

      <!-- 3. Batas Belanja Harian Aman -->
      <div class="f-card">
        <div class="f-card-top">
          <span class="f-label">Batas Belanja Harian Aman</span>
          <span class="f-icon text-muted">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </span>
        </div>
        <div class="f-val text-white">{{ formatRupiah(nextMonthData.safe_daily_limit) }}</div>
        <div class="f-footer">
          <span class="f-sub">Maksimal belanja/hari agar target tabungan tercapai</span>
        </div>
      </div>

      <!-- 4. Pemasukan Acuan -->
      <div class="f-card">
        <div class="f-card-top">
          <span class="f-label">Proyeksi Pemasukan Otomatis</span>
          <span class="f-icon text-income">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
              <polyline points="17 6 23 6 23 12"/>
            </svg>
          </span>
        </div>
        <div class="f-val text-income">{{ formatRupiah(nextMonthData.projected_income) }}</div>
        <div class="f-footer">
          <span class="f-sub">Dihitung dari pola pemasukan historis</span>
        </div>
      </div>
    </div>

    <section v-if="isAllTime" class="all-history-section">
      <div class="all-history-metrics">
        <div class="history-metric">
          <span class="history-metric-label">Rata-rata pengeluaran / siklus</span>
          <strong>{{ formatRupiah(allHistoryMetrics.average_expense_per_month) }}</strong>
        </div>
        <div class="history-metric">
          <span class="history-metric-label">Rata-rata pengeluaran / hari</span>
          <strong>{{ formatRupiah(allHistoryMetrics.average_expense_per_day) }}</strong>
        </div>
        <div class="history-metric">
          <span class="history-metric-label">Sisa bersih rata-rata / siklus</span>
          <strong>{{ formatRupiah(allHistoryMetrics.average_unspent_savings_per_month) }}</strong>
        </div>
        <div class="history-metric">
          <span class="history-metric-label">Rata-rata pemasukan / siklus</span>
          <strong>{{ formatRupiah(allHistoryMetrics.average_income_per_month) }}</strong>
        </div>
        <div class="history-metric">
          <span class="history-metric-label">Batas belanja aman / hari</span>
          <strong>{{ formatRupiah(allHistoryMetrics.safe_daily_spending) }}</strong>
        </div>
      </div>

      <div class="all-history-visuals">
        <section class="history-visual-panel">
          <h4>Tren Akurasi Forecast per Siklus</h4>
          <div v-if="allHistoryMetrics.accuracy_series?.length" class="accuracy-chart">
            <div v-for="item in allHistoryMetrics.accuracy_series" :key="item.ym" class="accuracy-column">
              <span class="accuracy-score">{{ item.accuracy }}%</span>
              <div class="accuracy-track">
                <div class="accuracy-bar" :style="{ height: `${item.accuracy}%` }"></div>
              </div>
              <span class="accuracy-period">{{ item.period }}</span>
            </div>
          </div>
          <p v-else class="history-chart-empty">Belum cukup siklus terdahulu untuk mengukur akurasi.</p>
        </section>

        <section class="history-visual-panel category-projection-panel">
          <h4>Proyeksi Distribusi Pengeluaran Global</h4>
          <div class="category-projection-layout">
            <div class="category-projection-donut" :style="categoryDonutStyle">
              <div class="category-donut-center">
                <span>Total proyeksi</span>
                <strong>{{ formatRupiah(nextMonthData.forecasted_expense) }}</strong>
              </div>
            </div>
            <div class="category-projection-legend">
              <div v-for="(item, index) in projectedCategories" :key="item.category" class="projection-legend-row">
                <span class="projection-legend-dot" :style="{ backgroundColor: categoryColor(index) }"></span>
                <span>{{ item.category }}</span>
                <strong>{{ item.percentage }}%</strong>
              </div>
            </div>
          </div>
        </section>
      </div>
    </section>

    <!-- SECTION: EVALUASI AKURASI HASIL FORECASTING TERHADAP PERIODE TERPILIH -->
    <!-- Aktif saat periode yang dipilih sudah selesai atau mencapai akhir siklus -->
    <div v-if="isPastMonth || accuracyData.is_completed" class="accuracy-section">
      <!-- Kasus A: Akurasi berhasil diverifikasi dengan data transaksi periode terpilih -->
      <div v-if="accuracyData.can_evaluate" class="accuracy-card verified-card">
        <div class="accuracy-card-header">
          <div class="acc-badge-row">
            <span class="acc-badge" :class="`acc-badge-${accuracyData.accuracy_color}`">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              Evaluasi Akurasi Hasil Forcasting
            </span>
            <span class="acc-target-pill">
              Target: {{ accuracyData.target_month_name }}
            </span>
            <span class="acc-status-pill" :class="`pill-${accuracyData.accuracy_color}`">
              {{ accuracyData.accuracy_grade }}
            </span>
          </div>
          <p class="acc-desc">
            Perbandingan tingkat ketepatan antara hasil ramalan AI dan data riil pada periode yang dipilih.
          </p>
        </div>

        <div class="accuracy-grid">
          <!-- Big Score Gauge Card -->
          <div class="acc-score-card">
            <div class="score-circle-wrapper" :class="`score-border-${accuracyData.accuracy_color}`">
              <div class="score-value">{{ accuracyData.accuracy_score }}%</div>
              <div class="score-label">Tingkat Akurasi</div>
            </div>
            <div class="score-subtext">
              Dihitung dari deviasi pengeluaran riil vs ramalan
            </div>
          </div>

          <!-- Comparison Details -->
          <div class="acc-comparison-card">
            <!-- Pengeluaran Comparison -->
            <div class="comp-row-item">
              <div class="comp-col-label">
                <div class="comp-title">Pengeluaran Periode Terpilih</div>
                <div class="comp-sub">Hasil ramalan vs terbelanjakan riil</div>
              </div>
              <div class="comp-values-group">
                <div class="comp-val-box">
                  <span class="comp-tag">Ramalan:</span>
                  <span class="comp-num">{{ formatRupiah(accuracyData.forecasted_expense) }}</span>
                </div>
                <div class="comp-arrow">→</div>
                <div class="comp-val-box">
                  <span class="comp-tag">Riil:</span>
                  <span class="comp-num text-expense">{{ formatRupiah(accuracyData.real_expense) }}</span>
                </div>
                <div class="comp-diff-badge" :class="accuracyData.diff_expense >= 0 ? 'diff-over' : 'diff-under'">
                  Selisih: {{ accuracyData.diff_expense >= 0 ? '+' : '' }}{{ formatRupiah(accuracyData.diff_expense) }}
                  ({{ accuracyData.expense_accuracy }}% tepat)
                </div>
              </div>
            </div>

            <div class="comp-divider"></div>

            <!-- Tabungan Comparison -->
            <div class="comp-row-item">
              <div class="comp-col-label">
                <div class="comp-title">Sisa Tabungan Bersih</div>
                <div class="comp-sub">Estimasi tabungan vs sisa riil</div>
              </div>
              <div class="comp-values-group">
                <div class="comp-val-box">
                  <span class="comp-tag">Ramalan:</span>
                  <span class="comp-num">{{ formatRupiah(accuracyData.forecasted_savings) }}</span>
                </div>
                <div class="comp-arrow">→</div>
                <div class="comp-val-box">
                  <span class="comp-tag">Riil:</span>
                  <span class="comp-num text-savings">{{ formatRupiah(accuracyData.real_savings) }}</span>
                </div>
                <div class="comp-diff-badge">
                  Selisih: {{ accuracyData.diff_savings >= 0 ? '+' : '' }}{{ formatRupiah(accuracyData.diff_savings) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="acc-card-footer">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>{{ accuracyData.status_message }}</span>
        </div>
      </div>

      <!-- Kasus B: Belum Bisa Dievaluasi (Belum akhir bulan / belum selesai) -->
      <div v-else class="accuracy-card pending-card">
        <div class="pending-icon-box">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="pending-content">
          <div class="pending-title-row">
            <span class="pending-title">Akurasi Peramalan: {{ accuracyData.target_month_name }}</span>
            <span class="pending-badge">Menunggu Data Periode Terpilih</span>
          </div>
          <p class="pending-desc">
            {{ accuracyData.status_message || 'Akurasi dapat dievaluasi ketika periode yang dipilih sudah selesai atau mencapai akhir siklus.' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Real Historical Data Analysis Section (Masa Lalu / Bulan-Bulan Sebelumnya) -->
    <div class="historical-analysis-section">
      <div class="section-top-row">
        <div>
          <div class="badge-history-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>Analisis Data Historis Bulan-Bulan Sebelumnya</span>
            <span class="months-count-badge">{{ historicalSeries.length }} Periode Tercatat</span>
          </div>
          <p class="history-subtext">
            Forcasting riil dihitung menggunakan data histori transaksi dari bulan-bulan sebelumnya dengan model regresi linier Scikit-Learn.
          </p>
        </div>

        <div class="trend-indicator-box">
          <span class="trend-label">Tren Historis Pengeluaran</span>
          <div class="trend-value-row">
            <span class="trend-direction-badge" :class="`trend-${historicalData.trend_direction}`">
              {{ formatTrendDirection(historicalData.trend_direction) }}
            </span>
            <span v-if="historicalData.trend_percent" class="trend-pct">
              {{ historicalData.trend_percent > 0 ? '+' : '' }}{{ historicalData.trend_percent }}% / bln
            </span>
          </div>
        </div>
      </div>

      <!-- Historical Monthly Timeline Cards -->
      <div v-if="historicalSeries.length > 0" class="history-cards-scroll">
        <div
          v-for="h in historicalSeries"
          :key="h.ym"
          class="history-month-card"
          :class="{ 'current-month-card': h.is_current }"
        >
          <div class="history-card-header">
            <span class="history-period">{{ h.period }}</span>
            <span v-if="h.is_current" class="history-tag-cur">Bulan Acuan</span>
            <span v-else class="history-tag-past">Data Lampau</span>
          </div>

          <div class="history-metrics-list">
            <div class="history-row">
              <span class="h-lbl">Pemasukan:</span>
              <span class="h-val text-income">{{ formatRupiah(h.income) }}</span>
            </div>
            <div class="history-row">
              <span class="h-lbl">Pengeluaran:</span>
              <span class="h-val text-expense">{{ formatRupiah(h.expense) }}</span>
            </div>
            <div class="history-row h-savings-row">
              <span class="h-lbl">Tabungan:</span>
              <span class="h-val" :class="h.savings >= 0 ? 'text-savings' : 'text-expense'">
                {{ formatRupiah(h.savings) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-history-box">
        <p>Belum ada rekaman bulan-bulan sebelumnya. Tambahkan transaksi untuk memperkaya basis analisa regresi deret waktu.</p>
      </div>
    </div>

    <!-- Category Breakdown & Insights Split -->
    <div class="forecast-details-split">
      <!-- Category projection bars -->
      <div class="forecast-sub-card">
        <h4 class="sub-card-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
            <line x1="3" x2="21" y1="9" y2="9"/>
            <line x1="9" x2="9" y1="21" y2="9"/>
          </svg>
          Proyeksi Distribusi Kategori
        </h4>

        <div class="category-total-row">
          <span>Total Proyeksi Seluruh Kategori</span>
          <strong>{{ formatRupiah(projectedCategoryTotal) }}</strong>
        </div>

        <div class="cat-bars-list">
          <div
            v-for="cat in nextMonthData.category_breakdown || []"
            :key="cat.category"
            class="cat-bar-item"
          >
            <div class="cat-bar-header">
              <span class="cat-name">{{ cat.category }}</span>
              <span class="cat-values">
                <strong>{{ formatRupiah(cat.projected_amount) }}</strong>
                <span class="cat-pct">({{ cat.percentage }}%)</span>
              </span>
            </div>
            <div class="cat-progress-track">
              <div
                class="cat-progress-fill"
                :style="{ width: Math.min(100, cat.percentage * 1.5) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Python Insights & Advice -->
      <div class="forecast-sub-card">
        <h4 class="sub-card-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
          Analisa Cerdas & Saran Keuangan (Python Engine)
        </h4>

        <div class="insights-list">
          <div
            v-for="(tip, idx) in forecastData?.insights || []"
            :key="idx"
            class="insight-item"
            :class="`insight-${tip.type}`"
          >
            <div class="insight-icon">
              <svg v-if="tip.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <svg v-else-if="tip.type === 'warning'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
            </div>
            <div class="insight-text">
              <div class="insight-title">{{ tip.title }}</div>
              <div class="insight-msg">{{ tip.message }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { formatRupiah } from '../utils/formatters.js';

export default {
  name: 'ForecastingView',
  props: {
    forecastData: {
      type: Object,
      default: () => ({})
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    selectedYear: {
      type: Number,
      default: () => new Date().getFullYear()
    },
    selectedMonth: {
      type: Number,
      default: () => new Date().getMonth() + 1
    },
    isPastMonth: {
      type: Boolean,
      default: false
    },
    isAllTime: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    nextMonthData() {
      return this.forecastData?.forecast_next_month || {};
    },
    historicalData() {
      return this.forecastData?.historical_analysis || {};
    },
    allHistoryMetrics() {
      return this.forecastData?.all_history_metrics || {};
    },
    projectedCategories() {
      return this.nextMonthData.category_breakdown || [];
    },
    projectedCategoryTotal() {
      return this.projectedCategories.reduce((total, item) => total + Number(item.projected_amount || 0), 0);
    },
    categoryDonutStyle() {
      const total = this.projectedCategories.reduce((sum, item) => sum + Number(item.projected_amount || 0), 0);
      if (!total) return { background: '#334155' };
      let current = 0;
      const stops = this.projectedCategories.map((item, index) => {
        const start = current;
        current += Number(item.projected_amount || 0) / total * 100;
        const end = index === this.projectedCategories.length - 1 ? 100 : current;
        return `${this.categoryColor(index)} ${start}% ${end}%`;
      });
      return { background: `conic-gradient(${stops.join(', ')})` };
    },
    historicalSeries() {
      return this.historicalData?.historical_series || [];
    },
    accuracyData() {
      return this.forecastData?.accuracy_evaluation || {};
    },
    savedLog() {
      return this.forecastData?.saved_input_log || {};
    },
    targetPeriodName() {
      return `${this.forecastData?.meta?.next_month_name || 'Bulan Ini'} ${this.forecastData?.meta?.next_year || ''}`;
    }
  },
  methods: {
    formatRupiah,
    categoryColor(index) {
      return ['#f43f5e', '#06b6d4', '#f59e0b', '#10b981', '#6366f1', '#ec4899', '#14b8a6', '#f97316'][index % 8];
    },
    formatTrendDirection(dir) {
      if (dir === 'meningkat') return '↗ Pengeluaran Naik';
      if (dir === 'menurun') return '↘ Pengeluaran Turun';
      return '→ Pengeluaran Stabil';
    },
  }
};
</script>

<style scoped>
.forecast-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
  background: linear-gradient(180deg, #161f33 0%, var(--bg-card) 100%);
  border: 1px solid rgba(99, 102, 241, 0.25);
  position: relative;
  overflow: hidden;
}

.forecast-container::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.forecast-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.header-tag-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.65rem;
  flex-wrap: wrap;
}

.python-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 8px;
}

.target-month-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.25rem 0.65rem;
  border-radius: 8px;
}

.history-mode-pill {
  font-size: 0.72rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.forecast-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.all-history-section {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  padding: 1.1rem 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.all-history-metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0.9rem;
}

.history-metric {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.55rem;
  padding-right: 0.7rem;
  border-right: 1px solid var(--border-color);
}

.history-metric-label {
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.35;
}

.history-metric strong {
  color: #fff;
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.all-history-visuals {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr);
  gap: 1.2rem;
}

.history-visual-panel {
  min-width: 0;
}

.history-visual-panel h4 {
  margin-bottom: 0.8rem;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.accuracy-chart {
  display: grid;
  grid-auto-columns: minmax(3.6rem, 1fr);
  grid-auto-flow: column;
  align-items: end;
  gap: 0.45rem;
  min-height: 145px;
  overflow-x: auto;
  padding: 0.25rem 0 0.5rem;
}

.accuracy-column {
  display: flex;
  min-width: 3.6rem;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
}

.accuracy-score {
  color: #fff;
  font-size: 0.68rem;
  font-variant-numeric: tabular-nums;
}

.accuracy-track {
  display: flex;
  width: 1.2rem;
  height: 90px;
  align-items: end;
  overflow: hidden;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.07);
}

.accuracy-bar {
  width: 100%;
  min-height: 2px;
  background: #10b981;
  border-radius: 4px 4px 0 0;
}

.accuracy-period {
  max-width: 4.5rem;
  color: var(--text-dim);
  font-size: 0.62rem;
  text-align: center;
}

.history-chart-empty {
  padding: 2rem 0;
  color: var(--text-dim);
  font-size: 0.75rem;
}

.category-projection-layout {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.category-projection-donut {
  display: grid;
  width: 9rem;
  min-width: 9rem;
  aspect-ratio: 1;
  place-items: center;
  border-radius: 50%;
}

.category-donut-center {
  display: flex;
  width: 66%;
  aspect-ratio: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bg-card);
  text-align: center;
}

.category-donut-center span {
  color: var(--text-dim);
  font-size: 0.58rem;
}

.category-donut-center strong {
  max-width: 95%;
  margin-top: 0.25rem;
  color: #fff;
  font-size: 0.66rem;
}

.category-projection-legend {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 0.45rem;
}

.projection-legend-row {
  display: grid;
  grid-template-columns: 0.5rem minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.projection-legend-row > span:nth-child(2) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.projection-legend-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
}

.projection-legend-row strong {
  color: #fff;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 900px) {
  .all-history-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .all-history-visuals {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .all-history-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .history-metric {
    padding: 0.35rem 0.5rem 0.35rem 0;
  }
  .category-projection-layout {
    align-items: flex-start;
    gap: 0.75rem;
  }
  .category-projection-donut {
    width: 7rem;
    min-width: 7rem;
  }
}

.forecast-desc {
  font-size: 0.825rem;
  color: var(--text-muted);
  max-width: 680px;
  margin-top: 0.25rem;
}

/* 1 Log Acuan Input/Display Box */
.income-simulator {
  display: flex;
  flex-direction: column;
  min-width: 280px;
}

.saved-log-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(99, 102, 241, 0.35);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}

.saved-log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.log-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: #34d399;
  background: rgba(52, 211, 153, 0.12);
  border: 1px solid rgba(52, 211, 153, 0.25);
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
}

.btn-edit-log {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-edit-log:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.4);
  color: #a5b4fc;
}

.saved-log-value {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.01em;
  margin: 0.15rem 0;
}

.saved-log-meta {
  font-size: 0.68rem;
  color: var(--text-dim);
}

.saved-log-meta strong {
  color: var(--text-muted);
}

.log-input-box {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  padding: 0.75rem 1rem;
  border-radius: 12px;
}

.sim-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
}

.sim-input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-prefix {
  font-size: 0.825rem;
  font-weight: 700;
  color: var(--text-dim);
}

.sim-input {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.4rem 0.75rem;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  width: 135px;
  outline: none;
}

.sim-input:focus {
  border-color: var(--primary);
}

.sim-hint {
  font-size: 0.65rem;
  color: var(--text-dim);
  font-style: italic;
  margin: 0;
}

/* 4 Forecast Metric Cards */
.forecast-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.f-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.5rem;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.f-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.15);
}

.f-card-expense {
  border-color: rgba(244, 63, 94, 0.3);
  background: linear-gradient(135deg, rgba(244, 63, 94, 0.05) 0%, var(--bg-card) 100%);
}

.f-card-savings {
  border-color: rgba(6, 182, 212, 0.3);
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.05) 0%, var(--bg-card) 100%);
}

.f-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.f-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

.f-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.f-val {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.f-footer {
  font-size: 0.72rem;
  color: var(--text-dim);
}

.f-sub {
  font-size: 0.7rem;
  color: var(--text-dim);
}

/* ========================================================
   SECTION: EVALUASI AKURASI HASIL PERAMALAN (VERIFIED / PENDING)
   ======================================================== */
.accuracy-section {
  display: flex;
  flex-direction: column;
  margin: 0.25rem 0;
}

.accuracy-card {
  border-radius: 14px;
  padding: 1.25rem 1.4rem;
  position: relative;
  overflow: hidden;
  transition: all 0.2s ease;
}

.verified-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(15, 23, 42, 0.85) 100%);
  border: 1px solid rgba(16, 185, 129, 0.35);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.accuracy-card-header {
  margin-bottom: 1rem;
}

.acc-badge-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.acc-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 8px;
}

.acc-badge-emerald {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}
.acc-badge-indigo {
  background: rgba(99, 102, 241, 0.18);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.35);
}
.acc-badge-amber {
  background: rgba(245, 158, 11, 0.18);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}
.acc-badge-rose {
  background: rgba(244, 63, 94, 0.18);
  color: #fb7185;
  border: 1px solid rgba(244, 63, 94, 0.35);
}
.acc-badge-muted {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
}

.acc-target-pill {
  font-size: 0.72rem;
  font-weight: 600;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.acc-status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.pill-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.pill-indigo { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; }
.pill-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.pill-rose { background: rgba(244, 63, 94, 0.15); color: #fb7185; }

.acc-desc {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
}

.accuracy-grid {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1.25rem;
  align-items: stretch;
}

.acc-score-card {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
}

.score-circle-wrapper {
  width: 105px;
  height: 105px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 3px solid #10b981;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, transparent 70%);
  margin-bottom: 0.6rem;
}

.score-border-emerald { border-color: #10b981; }
.score-border-indigo { border-color: #6366f1; }
.score-border-amber { border-color: #f59e0b; }
.score-border-rose { border-color: #f43f5e; }

.score-value {
  font-size: 1.55rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.score-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.score-subtext {
  font-size: 0.68rem;
  color: var(--text-dim);
  line-height: 1.3;
}

.acc-comparison-card {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 0.75rem;
}

.comp-row-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.comp-col-label {
  min-width: 170px;
}

.comp-title {
  font-size: 0.825rem;
  font-weight: 700;
  color: #ffffff;
}

.comp-sub {
  font-size: 0.68rem;
  color: var(--text-dim);
}

.comp-values-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.comp-val-box {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  font-size: 0.78rem;
}

.comp-tag {
  color: var(--text-dim);
  font-size: 0.7rem;
}

.comp-num {
  font-weight: 700;
}

.comp-arrow {
  color: var(--text-dim);
  font-size: 0.85rem;
}

.comp-diff-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

.comp-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
}

.acc-card-footer {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.85rem;
  padding-top: 0.65rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.72rem;
  color: var(--text-dim);
}

/* Pending Card (When next month is still running or not yet end of month) */
.pending-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px dashed rgba(255, 255, 255, 0.15);
}

.pending-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.pending-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.pending-title-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.pending-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
}

.pending-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.12);
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.pending-desc {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin: 0;
}

/* Historical Timeline & Cards */
.historical-analysis-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.25rem 1.4rem;
}

.section-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.badge-history-title {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.35rem;
}

.months-count-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.history-subtext {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin: 0;
}

.trend-indicator-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.trend-label {
  font-size: 0.68rem;
  color: var(--text-dim);
  font-weight: 600;
}

.trend-value-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.trend-direction-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.trend-meningkat {
  background: rgba(244, 63, 94, 0.12);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.25);
}

.trend-menurun {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.trend-stabil,
.trend-baseline,
.trend-data\ awal {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

.trend-pct {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
}

.history-cards-scroll {
  display: flex;
  gap: 0.85rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.history-month-card {
  min-width: 175px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.current-month-card {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(99, 102, 241, 0.05);
}

.history-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.history-period {
  font-size: 0.75rem;
  font-weight: 700;
  color: #ffffff;
}

.history-tag-cur {
  font-size: 0.62rem;
  font-weight: 700;
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.2);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.history-tag-past {
  font-size: 0.62rem;
  color: var(--text-dim);
}

.history-metrics-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
}

.h-lbl {
  color: var(--text-dim);
}

.h-val {
  font-weight: 700;
}

.h-savings-row {
  padding-top: 0.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.empty-history-box {
  padding: 1.5rem;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.8rem;
}

/* Category Breakdown & Insights Split */
.forecast-details-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.forecast-sub-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.sub-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
}

.category-total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.7rem 0.8rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 9px;
  background: rgba(99, 102, 241, 0.08);
  color: var(--text-muted);
  font-size: 0.75rem;
}

.category-total-row strong {
  color: var(--planned-text);
  font-size: 0.95rem;
}

.cat-bars-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.cat-bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.cat-bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
}

.cat-name {
  color: var(--text-muted);
  font-weight: 600;
}

.cat-values strong {
  color: #ffffff;
}

.cat-pct {
  color: var(--text-dim);
  margin-left: 0.25rem;
}

.cat-progress-track {
  height: 5px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.cat-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
  border-radius: 8px;
  transition: width 0.3s ease;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  padding: 0.75rem 0.85rem;
  border-radius: 10px;
  font-size: 0.75rem;
}

.insight-icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.insight-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.insight-title {
  font-weight: 700;
  color: #ffffff;
}

.insight-msg {
  color: var(--text-muted);
  line-height: 1.35;
}

.insight-info {
  background: rgba(56, 189, 248, 0.06);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: #38bdf8;
}

.insight-success {
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.insight-warning {
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.insight-danger {
  background: rgba(244, 63, 94, 0.06);
  border: 1px solid rgba(244, 63, 94, 0.2);
  color: #f43f5e;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .forecast-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .forecast-details-split {
    grid-template-columns: 1fr;
  }
  .accuracy-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .forecast-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
