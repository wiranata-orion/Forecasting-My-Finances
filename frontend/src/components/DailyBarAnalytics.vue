<template>
  <div class="fin-card daily-bar-container">
    <div class="card-header">
      <div class="header-titles">
        <h3 class="card-title">Analitik Batang Pertanggal</h3>
        <p class="card-desc">Perbandingan arus kas pemasukan dan pengeluaran per setiap tanggal</p>
      </div>

      <div class="header-controls">
        <div class="legend-badges">
          <span class="indicator-badge income-ind">
            <span class="square income-sq"></span> Pemasukan
          </span>
          <span class="indicator-badge expense-ind">
            <span class="square expense-sq"></span> Pengeluaran
          </span>
        </div>

        <div class="filter-pills">
          <button
            class="pill-btn"
            :class="{ active: timeFilter === 'all' }"
            @click="setTimeFilter('all')"
          >
            Semua
          </button>
          <button
            class="pill-btn"
            :class="{ active: timeFilter === '7d' }"
            @click="setTimeFilter('7d')"
          >
            7 Hari
          </button>
          <button
            class="pill-btn"
            :class="{ active: timeFilter === '14d' }"
            @click="setTimeFilter('14d')"
          >
            14 Hari
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Stats Row -->
    <div class="stats-ribbon">
      <div class="ribbon-item">
        <span class="ribbon-label">Total Pemasukan Periode</span>
        <span class="ribbon-val text-income">{{ formatRupiah(filteredTotals.income) }}</span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Total Pengeluaran Periode</span>
        <span class="ribbon-val text-expense">{{ formatRupiah(filteredTotals.expense) }}</span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Rata-rata Pengeluaran / Hari</span>
        <span class="ribbon-val text-white">{{ formatRupiah(dailyAvgExpense) }}</span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Net Saldo Harian</span>
        <span class="ribbon-val" :class="filteredTotals.net >= 0 ? 'text-income' : 'text-expense'">
          {{ filteredTotals.net >= 0 ? '+' : '' }}{{ formatRupiah(filteredTotals.net) }}
        </span>
      </div>
    </div>

    <!-- Bar Chart Canvas -->
    <div class="chart-canvas-area">
      <div v-if="processedDailyData.length === 0" class="empty-bar-state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        <p>Belum ada data mutasi harian di bulan ini.</p>
        <span>Tambahkan pemasukan atau pengeluaran untuk melihat grafik batang pertanggal.</span>
      </div>
      <canvas v-else ref="barCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js';
import { formatRupiah, formatDateShort } from '../utils/formatters.js';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default {
  name: 'DailyBarAnalytics',
  props: {
    dailyData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chartInstance: null,
      timeFilter: 'all' // 'all', '7d', '14d'
    };
  },
  computed: {
    processedDailyData() {
      if (!this.dailyData || this.dailyData.length === 0) return [];
      const sorted = [...this.dailyData].sort((a, b) => a.date.localeCompare(b.date));
      if (this.timeFilter === '7d') {
        return sorted.slice(-7);
      }
      if (this.timeFilter === '14d') {
        return sorted.slice(-14);
      }
      return sorted;
    },
    filteredTotals() {
      let income = 0;
      let expense = 0;
      this.processedDailyData.forEach(d => {
        income += (d.income || 0);
        expense += (d.expense || 0);
      });
      return {
        income,
        expense,
        net: income - expense
      };
    },
    dailyAvgExpense() {
      const count = this.processedDailyData.length || 1;
      return Math.round(this.filteredTotals.expense / count);
    }
  },
  watch: {
    dailyData: {
      deep: true,
      handler() {
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.renderChart();
    });
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.stop();
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  },
  methods: {
    formatRupiah,
    formatDateShort,
    setTimeFilter(filter) {
      this.timeFilter = filter;
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    renderChart() {
      this.$nextTick(() => {
        if (this.chartInstance) {
          this.chartInstance.stop();
          this.chartInstance.destroy();
          this.chartInstance = null;
        }
        if (!this.$refs.barCanvas) return;

        const dataItems = this.processedDailyData;
        if (!dataItems || dataItems.length === 0) {
          return;
        }

        const ctx = this.$refs.barCanvas.getContext('2d');
        if (!ctx) return;

        // Extract labels and dataset values
        const labels = dataItems.map(d => formatDateShort(d.date));
        const incomeValues = dataItems.map(d => d.income || 0);
        const expenseValues = dataItems.map(d => d.expense || 0);

        this.chartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'Pemasukan',
                data: incomeValues,
                backgroundColor: '#10b981',
                borderRadius: 6,
                barPercentage: 0.65,
                categoryPercentage: 0.7
              },
              {
                label: 'Pengeluaran',
                data: expenseValues,
                backgroundColor: '#f43f5e',
                borderRadius: 6,
                barPercentage: 0.65,
                categoryPercentage: 0.7
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: '#161e33',
                titleColor: '#f1f5f9',
                bodyColor: '#94a3b8',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 12,
                callbacks: {
                  title: (items) => {
                    if (!items || !items.length) return '';
                    const idx = items[0].dataIndex;
                    return `Tanggal: ${dataItems[idx]?.date || ''}`;
                  },
                  label: (context) => {
                    const label = context.dataset.label || '';
                    const val = context.raw || 0;
                    return ` ${label}: ${formatRupiah(val)}`;
                  },
                  afterBody: (items) => {
                    if (!items || !items.length) return '';
                    const idx = items[0].dataIndex;
                    const inc = incomeValues[idx] || 0;
                    const exp = expenseValues[idx] || 0;
                    const net = inc - exp;
                    return `\n Net Harian: ${net >= 0 ? '+' : ''}${formatRupiah(net)}`;
                  }
                }
              }
            },
            scales: {
              x: {
                grid: {
                  color: 'rgba(255, 255, 255, 0.04)',
                  drawBorder: false
                },
                ticks: {
                  color: '#94a3b8',
                  font: {
                    size: 11,
                    family: "'Plus Jakarta Sans', sans-serif"
                  }
                }
              },
              y: {
                grid: {
                  color: 'rgba(255, 255, 255, 0.05)',
                  drawBorder: false
                },
                ticks: {
                  color: '#64748b',
                  font: {
                    size: 11,
                    family: "'Plus Jakarta Sans', sans-serif"
                  },
                  callback: (val) => {
                    if (val >= 1000000) return `Rp ${(val / 1000000).toFixed(1)}jt`;
                    if (val >= 1000) return `Rp ${(val / 1000).toFixed(0)}rb`;
                    return `Rp ${val}`;
                  }
                }
              }
            }
          }
        });
      });
    }
  }
};
</script>

<style scoped>
.daily-bar-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.card-desc {
  font-size: 0.8rem;
  color: var(--text-dim);
  margin-top: 0.15rem;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.legend-badges {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.indicator-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}

.square {
  width: 9px;
  height: 9px;
  border-radius: 2px;
}
.income-sq {
  background: var(--income);
}
.expense-sq {
  background: var(--expense);
}

.filter-pills {
  display: flex;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  padding: 0.2rem;
  border-radius: 8px;
}

.pill-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn.active {
  background: var(--bg-card);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}

.stats-ribbon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.85rem 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.ribbon-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.ribbon-label {
  font-size: 0.72rem;
  color: var(--text-dim);
  font-weight: 500;
}

.ribbon-val {
  font-size: 0.95rem;
  font-weight: 700;
}

.ribbon-divider {
  width: 1px;
  height: 28px;
  background: var(--border-color);
}

.text-income {
  color: var(--income-text);
}
.text-expense {
  color: var(--expense-text);
}
.text-white {
  color: #ffffff;
}

.chart-canvas-area {
  position: relative;
  width: 100%;
  height: 260px;
}

.chart-canvas-area canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.empty-bar-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  text-align: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.015);
  border: 1px dashed var(--border-color);
  border-radius: 12px;
}

.empty-bar-state p {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
}

.empty-bar-state span {
  font-size: 0.775rem;
}
</style>
