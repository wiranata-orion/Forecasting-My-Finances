<template>
  <div class="fin-card donut-container">
    <div class="card-header">
      <div class="header-titles">
        <h3 class="card-title">Alokasi & Kapasitas Keuangan</h3>
        <p class="card-desc">Visualisasi alokasi keuangan & distribusi simpanan rekening</p>
      </div>
      <div class="view-toggles">
        <button
          class="toggle-btn"
          :class="{ active: activeMode === 'finance' }"
          @click="setMode('finance')"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
          Pemasukan / Pengeluaran
        </button>
        <button
          class="toggle-btn"
          :class="{ active: activeMode === 'wallet' }"
          @click="setMode('wallet')"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <rect x="2" y="5" width="20" height="14" rx="2"/>
            <line x1="2" y1="10" x2="22" y2="10"/>
          </svg>
          Uang Tersimpan
        </button>
      </div>
    </div>

    <div class="donut-content">
      <div class="chart-wrapper">
        <div class="canvas-container">
          <canvas ref="donutCanvas"></canvas>
          <div class="donut-center-info">
            <span class="center-label">{{ centerTitle }}</span>
            <span class="center-value">{{ formatRupiah(centerAmount) }}</span>
            <span class="center-sub">{{ centerSub }}</span>
          </div>
        </div>
      </div>

      <div class="legend-wrapper">
        <!-- Mode 1: Pemasukan / Pengeluaran -->
        <div v-if="activeMode === 'finance'" class="pool-legends">
          <div class="pool-total-box">
            <div class="total-label-row">
              <span class="total-tag">Total Kapasitas Dana Siklus</span>
              <span class="total-val">{{ formatRupiah(totalBasis) }}</span>
            </div>
            <div class="total-progress-track">
              <div
                class="prog-segment seg-savings"
                :style="{ width: savingsPct + '%' }"
                title="Sisa Tabungan"
              ></div>
              <div
                class="prog-segment seg-expense"
                :style="{ width: expensePct + '%' }"
                title="Pengeluaran Riil"
              ></div>
              <div
                class="prog-segment seg-planned"
                :style="{ width: plannedPct + '%' }"
                title="Kemungkinan Pengeluaran"
              ></div>
            </div>
            <p class="pool-hint">
              <span v-if="!isAllTime && (safeSummary.start_balance || safeSummary.carry_over_balance)">
                Sisa bulan lalu: {{ formatRupiah(safeSummary.start_balance || safeSummary.carry_over_balance) }} (diteruskan) ·
              </span>
              Saldo tersimpan saat ini di seluruh rekening: {{ formatRupiah(safeSummary.sisa_tabungan) }}.
            </p>
          </div>

          <div class="legend-row highlight-row" @mouseenter="hoverSegment(0)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-savings"></span>
              <div>
                <div class="legend-name">Total Uang Tersimpan</div>
                <div class="legend-sub">
                  <span v-if="!isAllTime && (safeSummary.start_balance || safeSummary.carry_over_balance)">
                    Diteruskan dari {{ formatRupiah(safeSummary.start_balance || safeSummary.carry_over_balance) }}
                  </span>
                  <span v-else>Saldo saat ini seluruh rekening</span>
                </div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-savings">{{ formatRupiah(safeSummary.sisa_tabungan) }}</span>
              <span class="legend-pct">{{ savingsPct }}%</span>
            </div>
          </div>

          <div class="legend-row" @mouseenter="hoverSegment(1)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-expense"></span>
              <div>
                <div class="legend-name">Pengeluaran Riil</div>
                <div class="legend-sub">Transaksi aktual terjadi</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-expense">{{ formatRupiah(safeSummary.total_expense) }}</span>
              <span class="legend-pct">{{ expensePct }}%</span>
            </div>
          </div>

          <div class="legend-row" @mouseenter="hoverSegment(2)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-planned"></span>
              <div>
                <div class="legend-name">Kemungkinan Pengeluaran</div>
                <div class="legend-sub">Rencana pengeluaran siklus</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-planned">{{ formatRupiah(safeSummary.total_planned) }}</span>
              <span class="legend-pct">{{ plannedPct }}%</span>
            </div>
          </div>
        </div>

        <!-- Mode 2: Uang Tersimpan (Distribusi Rekening) -->
        <div v-else class="wallet-legends">
          <div class="wallet-total-box">
            <span class="total-tag">Total Uang Tersimpan</span>
            <span class="total-val">{{ formatRupiah(walletTotal) }}</span>
          </div>

          <div v-if="walletItems.length === 0" class="empty-wallet-msg">
            Belum ada rekening/dompet tercatat.
          </div>

          <div
            v-for="(item, idx) in walletItems"
            :key="item.wallet"
            class="legend-row"
            @mouseenter="hoverWallet(item, idx)"
            @mouseleave="resetCenter"
          >
            <div class="legend-left">
              <span class="color-dot" :style="{ background: getWalletColor(idx) }"></span>
              <div>
                <div class="legend-name">{{ item.wallet }}</div>
                <div class="legend-sub">{{ getWalletPct(item.balance) }}% dari total</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt">{{ formatRupiah(item.balance) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js';
import { formatRupiah } from '../utils/formatters.js';

Chart.register(DoughnutController, ArcElement, Tooltip, Legend);

const WALLET_COLORS = [
  '#06b6d4', '#10b981', '#8b5cf6', '#f59e0b', '#3b82f6', '#ec4899', '#14b8a6', '#f97316'
];

export default {
  name: 'DonutChart',
  props: {
    summary: {
      type: Object,
      required: true
    },
    categories: {
      type: Array,
      default: () => []
    },
    walletBalances: {
      type: Array,
      default: () => []
    },
    wallets: {
      type: Array,
      default: () => []
    },
    isAllTime: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeMode: 'finance',
      chartInstance: null,
      centerTitle: 'Sisa Tabungan',
      centerAmount: 0,
      centerSub: 'Siap dialokasikan'
    };
  },
  computed: {
    safeSummary() {
      return this.summary || {
        total_income: 0,
        total_expense: 0,
        total_planned: 0,
        sisa_tabungan: 0,
        start_balance: 0,
        carry_over_balance: 0,
        savings_ratio: 0
      };
    },
    totalBasis() {
      if (this.isAllTime) {
        return Math.max(1, (this.safeSummary.sisa_tabungan || 0) + (this.safeSummary.total_expense || 0));
      }
      const startBalance = Number(this.safeSummary.start_balance ?? this.safeSummary.carry_over_balance ?? 0);
      const income = Number(this.safeSummary.total_income || 0);
      const capacity = startBalance + income;
      return Math.max(1, capacity > 0 ? capacity : ((this.safeSummary.sisa_tabungan || 0) + (this.safeSummary.total_expense || 0)));
    },
    savingsPct() {
      return Math.round(((this.safeSummary.sisa_tabungan || 0) / this.totalBasis) * 100);
    },
    expensePct() {
      return Math.round(((this.safeSummary.total_expense || 0) / this.totalBasis) * 100);
    },
    plannedPct() {
      return Math.round(((this.safeSummary.total_planned || 0) / this.totalBasis) * 100);
    },
    walletItems() {
      if (!this.walletBalances || this.walletBalances.length === 0) return [];
      return this.walletBalances;
    },
    walletTotal() {
      return this.walletItems.reduce((acc, cur) => acc + (cur.balance || 0), 0);
    }
  },
  watch: {
    summary: {
      deep: true,
      handler() {
        this.resetCenter();
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    },
    categories: {
      deep: true,
      handler() {
        if (this.activeMode === 'finance') {
          this.$nextTick(() => {
            this.renderChart();
          });
        }
      }
    },
    walletBalances: {
      deep: true,
      handler() {
        if (this.activeMode === 'wallet') {
          this.resetCenter();
          this.$nextTick(() => {
            this.renderChart();
          });
        }
      }
    }
  },
  mounted() {
    this.resetCenter();
    this.$nextTick(() => {
      this.renderChart();
    });
  },
  beforeUnmount() {
    if (this.chartInstance) {
      try {
        this.chartInstance.stop();
        this.chartInstance.destroy();
      } catch (e) {
        // ignore
      }
      this.chartInstance = null;
    }
  },
  methods: {
    formatRupiah,
    setMode(mode) {
      this.activeMode = mode;
      this.resetCenter();
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    resetCenter() {
      if (this.activeMode === 'finance') {
        this.centerTitle = 'Sisa Tabungan';
        this.centerAmount = this.safeSummary.sisa_tabungan || 0;
        this.centerSub = 'Saldo saat ini seluruh rekening';
      } else {
        this.centerTitle = 'Total Saldo';
        this.centerAmount = this.walletTotal;
        this.centerSub = `${this.walletItems.length} Rekening Aktif`;
      }
    },
    hoverSegment(idx) {
      if (this.activeMode !== 'finance') return;
      const s = this.safeSummary;
      if (idx === 0) {
        this.centerTitle = 'Sisa Tabungan';
        this.centerAmount = s.sisa_tabungan || 0;
        this.centerSub = `${this.savingsPct}% dari kapasitas`;
      } else if (idx === 1) {
        this.centerTitle = 'Pengeluaran Riil';
        this.centerAmount = s.total_expense || 0;
        this.centerSub = `${this.expensePct}% dari kapasitas`;
      } else if (idx === 2) {
        this.centerTitle = 'Rencana Belanja';
        this.centerAmount = s.total_planned || 0;
        this.centerSub = `${this.plannedPct}% dari kapasitas`;
      }
    },
    getWalletColor(idx) {
      return WALLET_COLORS[idx % WALLET_COLORS.length];
    },
    getWalletPct(amt) {
      if (!this.walletTotal) return 0;
      return Math.round(((amt || 0) / this.walletTotal) * 100);
    },
    hoverWallet(item) {
      if (this.activeMode !== 'wallet') return;
      this.centerTitle = item.wallet;
      this.centerAmount = item.balance;
      this.centerSub = `${this.getWalletPct(item.balance)}% dari total`;
    },
    renderChart() {
      if (this.chartInstance) {
        try {
          this.chartInstance.stop();
          this.chartInstance.destroy();
        } catch (e) {
          // ignore
        }
        this.chartInstance = null;
      }
      if (!this.$refs.donutCanvas) return;

      const canvas = this.$refs.donutCanvas;
      const ctx = canvas && canvas.getContext('2d');
      if (!ctx) return;

      let labels = [];
      let data = [];
      let backgroundColors = [];
      let borderColors = [];

      if (this.activeMode === 'finance') {
        const s = this.safeSummary;
        labels = ['Sisa Ditabung', 'Pengeluaran Riil', 'Kemungkinan Pengeluaran'];
        data = [
          Math.max(0, s.sisa_tabungan || 0),
          Math.max(0, s.total_expense || 0),
          Math.max(0, s.total_planned || 0)
        ];
        if (data.every(v => v === 0)) {
          data = [1];
          labels = ['Belum ada data'];
          backgroundColors = ['rgba(255,255,255,0.06)'];
          borderColors = ['transparent'];
        } else {
          backgroundColors = [
            '#06b6d4',
            '#f43f5e',
            '#f59e0b'
          ];
          borderColors = ['#141b2d', '#141b2d', '#141b2d'];
        }
      } else {
        const items = this.walletItems.filter(i => (i.balance || 0) > 0);
        if (items.length === 0) {
          labels = ['Belum ada saldo'];
          data = [1];
          backgroundColors = ['rgba(255,255,255,0.06)'];
          borderColors = ['transparent'];
        } else {
          labels = items.map(i => i.wallet);
          data = items.map(i => i.balance);
          backgroundColors = items.map((_, idx) => this.getWalletColor(idx));
          borderColors = items.map(() => '#141b2d');
        }
      }

      try {
        this.chartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels,
            datasets: [{
              data,
              backgroundColor: backgroundColors,
              borderColor: borderColors,
              borderWidth: 3,
              hoverOffset: 6,
              borderRadius: 6,
              spacing: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '76%',
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
                boxPadding: 6,
                callbacks: {
                  label: (context) => {
                    const val = context.raw || 0;
                    return ` ${context.label}: ${formatRupiah(val)}`;
                  }
                }
              }
            },
            animation: {
              animateRotate: true,
              animateScale: true,
              duration: 600
            }
          }
        });
      } catch (err) {
        console.error('[DonutChart] Error creating chart instance:', err);
      }
    }
  }
};
</script>

<style scoped>
.donut-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-width: 0;
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.card-desc {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-top: 0.1rem;
}

.view-toggles {
  display: flex;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  padding: 0.2rem;
  border-radius: 10px;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.toggle-btn.active {
  background: var(--bg-card);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.donut-content {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  align-items: start;
  gap: 1.5rem;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.canvas-container {
  position: relative;
  width: 240px;
  height: 240px;
}

.canvas-container canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.donut-center-info {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  text-align: center;
  padding: 1rem;
}

.center-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.center-value {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
  margin: 0.2rem 0;
  line-height: 1.2;
}

.center-sub {
  font-size: 0.68rem;
  color: var(--text-dim);
}

.legend-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.pool-legends, .wallet-legends {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.pool-total-box, .wallet-total-box {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.35rem;
}

.total-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.total-tag {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.total-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #ffffff;
}

.total-progress-track {
  height: 6px;
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 99px;
  display: flex;
  overflow: hidden;
  gap: 2px;
}

.prog-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.seg-savings {
  background: #06b6d4;
}
.seg-expense {
  background: #f43f5e;
}
.seg-planned {
  background: #f59e0b;
}

.pool-hint {
  font-size: 0.67rem;
  color: var(--text-dim);
  margin-top: 0.4rem;
  line-height: 1.35;
}

.legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.45rem 0.65rem;
  border-radius: 8px;
  background: var(--bg-card-subtle);
  border: 1px solid transparent;
  transition: all 0.15s ease;
  cursor: pointer;
}

.legend-row:hover {
  background: var(--bg-hover);
  border-color: var(--border-color);
}

.highlight-row {
  border-color: rgba(6, 182, 212, 0.2);
  background: rgba(6, 182, 212, 0.04);
}

.legend-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-savings {
  background: #06b6d4;
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);
}
.dot-expense {
  background: #f43f5e;
  box-shadow: 0 0 8px rgba(244, 63, 94, 0.5);
}
.dot-planned {
  background: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
}

.legend-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.2;
}

.legend-sub {
  font-size: 0.66rem;
  color: var(--text-dim);
}

.legend-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-amt {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-main);
}

.val-savings {
  color: #06b6d4;
}
.val-expense {
  color: #f43f5e;
}
.val-planned {
  color: #f59e0b;
}

.legend-pct {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
}

.empty-wallet-msg {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-align: center;
  padding: 1rem;
}

@media (max-width: 640px) {
  .donut-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>
