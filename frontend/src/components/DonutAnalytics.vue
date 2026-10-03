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
        <div v-if="activeMode === 'wallet'" class="savings-wallet-settings">
          <div class="settings-heading">
            <div>
              <div class="settings-title">Rekening Tabungan Aktif</div>
              <p class="settings-hint">{{ selectedSavingsWallets.length }} rekening dipilih sebagai tabungan.</p>
            </div>
            <button class="settings-toggle" @click="showSavingsSettings = !showSavingsSettings">
              {{ showSavingsSettings ? 'Sembunyikan' : 'Atur' }}
            </button>
          </div>
          <div v-if="showSavingsSettings">
            <div v-if="walletOptions.length" class="savings-wallet-options">
              <label v-for="wallet in walletOptions" :key="wallet" class="savings-wallet-option">
                <input v-model="selectedSavingsWallets" type="checkbox" :value="wallet">
                <span>{{ wallet }}</span>
              </label>
            </div>
            <p v-else class="settings-hint">Belum ada rekening di database.</p>
            <button class="btn btn-primary btn-sm" :disabled="isSavingWallets" @click="saveSavingsWallets">
              {{ isSavingWallets ? 'Menyimpan...' : 'Simpan Pengaturan' }}
            </button>
          </div>
        </div>
      </div>

      <div class="legend-wrapper">
        <!-- Mode 1: Pemasukan / Pengeluaran -->
        <div v-if="activeMode === 'finance'" class="pool-legends">
          <!-- Total Pemasukan Banner -->
          <div class="pool-total-box">
            <div class="total-label-row">
              <span class="total-tag">Total Alokasi Siklus</span>
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
              Saldo tersimpan adalah jumlah uang saat ini di seluruh rekening.
            </p>
          </div>

          <!-- Item 1: Total current funds -->
          <div class="legend-row highlight-row" @mouseenter="hoverSegment(0)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-savings"></span>
              <div>
                <div class="legend-name">Total Uang Tersimpan</div>
                <div class="legend-sub">Saldo saat ini seluruh rekening</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-savings">{{ formatRupiah(safeSummary.sisa_tabungan) }}</span>
              <span class="legend-pct">{{ savingsPct }}%</span>
            </div>
          </div>
          <!-- Item 2: Pengeluaran Riil -->
          <div class="legend-row" @mouseenter="hoverSegment(1)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-expense"></span>
              <div>
                <div class="legend-name">Pengeluaran Riil</div>
                <div class="legend-sub">Sudah terbelanjakan</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-expense">{{ formatRupiah(safeSummary.total_expense) }}</span>
              <span class="legend-pct">{{ expensePct }}%</span>
            </div>
          </div>

          <!-- Item 3: Kemungkinan Pengeluaran -->
          <div class="legend-row" @mouseenter="hoverSegment(2)" @mouseleave="resetCenter">
            <div class="legend-left">
              <span class="color-dot dot-planned"></span>
              <div>
                <div class="legend-name">Kemungkinan Pengeluaran</div>
                <div class="legend-sub">Rencana s.d akhir bulan</div>
              </div>
            </div>
            <div class="legend-right">
              <span class="legend-amt val-planned">{{ formatRupiah(safeSummary.total_planned) }}</span>
              <span class="legend-pct">{{ plannedPct }}%</span>
            </div>
          </div>

          <!-- Category Breakdown (compact, below the main items) -->
          <div v-if="categories && categories.length > 0" class="category-mini-section">
            <div class="cat-section-label">Rincian Kategori Pengeluaran</div>
            <div
              v-for="(cat, idx) in categories"
              :key="cat.category"
              class="cat-mini-row"
              @mouseenter="hoverCategory(idx)"
              @mouseleave="resetCenter"
            >
              <div class="cat-mini-left">
                <span
                  class="color-dot-sm"
                  :style="{ backgroundColor: getCategoryColor(idx) }"
                ></span>
                <span class="cat-mini-name">{{ cat.category }}</span>
              </div>
              <div class="cat-mini-right">
                <span class="cat-mini-amt">{{ formatRupiah(cat.amount) }}</span>
                <span class="cat-mini-pct">{{ getCategoryPct(cat.amount) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Mode 2: Uang Tersimpan (Wallet/Bank Distribution) -->
        <div v-else class="wallet-legends">
          <!-- Total Balance Banner -->
          <div class="pool-total-box wallet-total-box">
            <div class="total-label-row">
              <span class="total-tag">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: -2px; margin-right: 4px;">
                  <rect x="2" y="5" width="20" height="14" rx="2"/>
                  <line x1="2" y1="10" x2="22" y2="10"/>
                </svg>
                {{ isAllTime ? 'Total Saldo Tersimpan' : 'Mutasi Bersih Siklus' }}
              </span>
              <span class="total-val">{{ formatRupiah(walletTotal) }}</span>
            </div>
            <p class="pool-hint">
              {{ isAllTime ? 'Saldo akumulatif dari seluruh log transaksi.' : 'Hanya mutasi rekening pada siklus terpilih.' }}
            </p>
          </div>

          <div v-if="walletItems.length === 0" class="empty-cats">
            <p>Belum ada transaksi dengan sumber/tempat dana.</p>
            <p style="font-size: 0.72rem; color: var(--text-dim); margin-top: 0.25rem;">
              Saat Anda mencatat pemasukan/pengeluaran, pilih atau ketik nama tempat (misal: BCA, Dana, Cash).
            </p>
          </div>

          <div
            v-for="(item, idx) in walletItems"
            :key="item.wallet"
            class="legend-row"
            @mouseenter="hoverWallet(idx)"
            @mouseleave="resetCenter"
          >
            <div class="legend-left">
              <span
                class="color-dot"
                :style="{ backgroundColor: getWalletColor(idx) }"
              ></span>
              <div>
                <div class="legend-name">{{ item.wallet }}</div>
                <div class="legend-sub">{{ getWalletPct(item.balance) }}% dari total uang</div>
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

const CATEGORY_COLORS = [
  '#f43f5e', '#6366f1', '#f59e0b', '#06b6d4', '#10b981', '#ec4899', '#8b5cf6', '#64748b'
];

const WALLET_COLORS = [
  '#06b6d4', '#10b981', '#8b5cf6', '#f59e0b', '#3b82f6', '#ec4899', '#14b8a6', '#f97316'
];

export default {
  name: 'DonutAnalytics',
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
    savingsWallets: {
      type: Array,
      default: () => []
    },
    isAllTime: {
      type: Boolean,
      default: false
    }
  },
  emits: ['save-savings-wallets'],
  data() {
    return {
      activeMode: 'finance',
      chartInstance: null,
      selectedSavingsWallets: [],
      isSavingWallets: false,
      showSavingsSettings: false,
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
        savings_ratio: 0
      };
    },
    totalBasis() {
      return Math.max(1,
        (this.safeSummary.sisa_tabungan || 0)
        + (this.safeSummary.total_expense || 0)
        + (this.safeSummary.total_planned || 0)
      );
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
    walletOptions() {
      return Array.from(new Set(this.wallets.map(wallet => typeof wallet === 'string' ? wallet : wallet.name).filter(Boolean)));
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
    },
    savingsWallets: {
      immediate: true,
      handler(value) {
        this.selectedSavingsWallets = [...(value || [])];
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
      this.chartInstance.stop();
      this.chartInstance.destroy();
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
    saveSavingsWallets() {
      this.isSavingWallets = true;
      this.$emit('save-savings-wallets', [...this.selectedSavingsWallets]);
      this.isSavingWallets = false;
    },
    getCategoryColor(idx) {
      return CATEGORY_COLORS[idx % CATEGORY_COLORS.length];
    },
    getWalletColor(idx) {
      return WALLET_COLORS[idx % WALLET_COLORS.length];
    },
    getCategoryPct(amt) {
      const total = this.safeSummary.total_expense || 1;
      return Math.round((amt / total) * 100);
    },
    getWalletPct(amt) {
      if (!this.walletTotal || this.walletTotal <= 0) return 0;
      return Math.round((amt / this.walletTotal) * 100);
    },
    resetCenter() {
      if (this.activeMode === 'finance') {
        const s = this.safeSummary;
        if (!s.total_income && !s.total_expense && !s.sisa_tabungan) {
          this.centerTitle = 'Belum Ada Data';
          this.centerAmount = 0;
          this.centerSub = 'Tambahkan transaksi awal';
        } else {
          this.centerTitle = 'Total Uang Tersimpan';
          this.centerAmount = s.sisa_tabungan || 0;
          this.centerSub = 'Saldo saat ini seluruh rekening';
        }
      } else {
        this.centerTitle = this.isAllTime ? 'Total Saldo Tersimpan' : 'Mutasi Bersih Siklus';
        this.centerAmount = this.walletTotal;
        this.centerSub = `${this.walletItems.length} tempat`;
      }
    },
    hoverSegment(idx) {
      const s = this.safeSummary;
      if (idx === 0) {
        this.centerTitle = 'Total Uang Tersimpan';
        this.centerAmount = s.sisa_tabungan || 0;
        this.centerSub = 'Saldo saat ini seluruh rekening';
      } else if (idx === 1) {
        this.centerTitle = 'Pengeluaran Riil';
        this.centerAmount = s.total_expense || 0;
        this.centerSub = `${this.expensePct}% dari ringkasan periode`;
      } else if (idx === 2) {
        this.centerTitle = 'Kemungkinan Rencana';
        this.centerAmount = s.total_planned || 0;
        this.centerSub = `${this.plannedPct}% dari ringkasan periode`;
      }
    },
    hoverCategory(idx) {
      const item = this.categories[idx];
      if (item) {
        this.centerTitle = item.category;
        this.centerAmount = item.amount;
        this.centerSub = `${this.getCategoryPct(item.amount)}% dari pengeluaran`;
      }
    },
    hoverWallet(idx) {
      const item = this.walletItems[idx];
      if (item) {
        this.centerTitle = item.wallet;
        this.centerAmount = item.balance;
        this.centerSub = `${this.getWalletPct(item.balance)}% dari total`;
      }
    },
    renderChart() {
      if (this.chartInstance) {
        this.chartInstance.stop();
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      if (!this.$refs.donutCanvas) return;

      const ctx = this.$refs.donutCanvas.getContext('2d');
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
        // Wallet mode
        const items = this.walletItems;
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
    }
  }
};
</script>

<style scoped>
.donut-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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
}

.center-sub {
  font-size: 0.68rem;
  color: var(--text-dim);
}

.legend-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 420px;
  overflow-y: auto;
}

.pool-legends,
.wallet-legends {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.pool-total-box {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
  margin-bottom: 0.15rem;
}

.wallet-total-box {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-color: rgba(56, 189, 248, 0.2);
}

.savings-wallet-settings {
  width: 100%;
  max-width: 320px;
  margin-top: 0.75rem;
  padding: 0.8rem;
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 10px;
  background: rgba(16, 185, 129, 0.06);
}

.settings-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.settings-count {
  flex: 0 0 auto;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.14);
  color: var(--income-text);
  font-size: 0.65rem;
  font-weight: 700;
}

.settings-toggle {
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: 6px;
  padding: 0.3rem 0.55rem;
  background: rgba(16, 185, 129, 0.1);
  color: var(--income-text);
  font-size: 0.68rem;
  font-weight: 700;
  cursor: pointer;
}

.settings-toggle:hover {
  background: rgba(16, 185, 129, 0.2);
}

.settings-title {
  color: var(--text-main);
  font-size: 0.78rem;
  font-weight: 700;
}

.settings-hint {
  margin: 0.25rem 0 0.65rem;
  color: var(--text-dim);
  font-size: 0.68rem;
}

.savings-wallet-option {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0.35rem 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  cursor: pointer;
}

.savings-wallet-option input {
  accent-color: var(--income);
}

.savings-wallet-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.25rem 0.6rem;
}

.savings-wallet-settings .btn {
  width: 100%;
  margin-top: 0.65rem;
}

.total-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.total-tag {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
}

.total-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #ffffff;
}

.total-progress-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  display: flex;
  overflow: hidden;
  margin-bottom: 0.35rem;
}

.prog-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.seg-savings { background: #06b6d4; }
.seg-expense { background: #f43f5e; }
.seg-planned { background: #f59e0b; }

.pool-hint {
  font-size: 0.65rem;
  color: var(--text-dim);
  font-style: italic;
}

.legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.legend-row:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-color);
}

.legend-row.highlight-row {
  background: rgba(6, 182, 212, 0.06);
  border-color: rgba(6, 182, 212, 0.2);
}

.legend-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
}

.color-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-savings {
  background: #06b6d4;
  box-shadow: 0 0 6px rgba(6, 182, 212, 0.4);
}
.dot-expense {
  background: #f43f5e;
  box-shadow: 0 0 6px rgba(244, 63, 94, 0.4);
}
.dot-planned {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
}

.legend-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.legend-sub {
  font-size: 0.65rem;
  color: var(--text-dim);
}

.legend-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
  gap: 2px;
}

.legend-amt {
  font-size: 0.8rem;
  font-weight: 700;
  color: #ffffff;
}

.val-savings { color: var(--savings-text); }
.val-expense { color: var(--expense-text); }
.val-planned { color: var(--planned-text); }

.legend-pct {
  font-size: 0.65rem;
  color: var(--text-dim);
}

/* Category mini breakdown inside finance mode */
.category-mini-section {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.cat-section-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
}

.cat-mini-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.35rem 0.5rem;
  margin-bottom: 2px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.cat-mini-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.cat-mini-left {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.color-dot-sm {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.cat-mini-name {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
}

.cat-mini-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cat-mini-amt {
  font-size: 0.72rem;
  font-weight: 700;
  color: #ffffff;
}

.cat-mini-pct {
  font-size: 0.65rem;
  color: var(--text-dim);
}

.empty-cats {
  padding: 1.25rem;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.8rem;
}

@media (max-width: 900px) {
  .donut-content {
    grid-template-columns: 1fr;
  }
}
</style>
