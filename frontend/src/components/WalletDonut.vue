<template>
  <div class="fin-card wallet-donut-container" id="distribusi-rekening">
    <!-- Header -->
    <div class="card-header">
      <div class="header-titles">
        <div class="title-with-badge">
          <h3 class="card-title">Distribusi Simpanan & Rekening</h3>
          <span class="badge badge-wallet">{{ activeWalletsCount }} Tempat Terdeteksi</span>
        </div>
        <p class="card-desc">
          Visualisasi posisi uang riil di bank, dompet digital, atau uang tunai yang tercatat dari log aktivitas.
        </p>
      </div>
    </div>

    <!-- Hero Card: Total Seluruh Uang Saya -->
    <div class="wealth-summary-card">
      <div class="wealth-info">
        <div class="wealth-label-row">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="5" width="20" height="14" rx="2"/>
            <line x1="2" y1="10" x2="22" y2="10"/>
          </svg>
          <span>Total Seluruh Uang Saya</span>
        </div>
        <div class="wealth-amount">{{ formatRupiah(totalBalance) }}</div>
        <div class="wealth-sub">
          Tersimpan dan tersebar di {{ activeWalletsCount }} rekening & pos keuangan
        </div>
      </div>
    </div>

    <!-- Donut Chart & Breakdown -->
    <div class="donut-content">
      <div class="chart-wrapper">
        <div class="canvas-container">
          <canvas ref="walletCanvas"></canvas>
          <div class="donut-center-info">
            <span class="center-label">{{ centerTitle }}</span>
            <span class="center-value">{{ formatRupiah(centerAmount) }}</span>
            <span class="center-sub">{{ centerSub }}</span>
          </div>
        </div>
      </div>

      <div class="legend-wrapper">
        <!-- Empty state if no wallets or 0 balances -->
        <div v-if="processedBalances.length === 0" class="empty-wallets">
          <div class="empty-icon-sm">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="2" y="5" width="20" height="14" rx="2"/>
              <line x1="2" y1="10" x2="22" y2="10"/>
            </svg>
          </div>
          <p class="empty-text">Belum ada transaksi dengan sumber/tempat dana</p>
          <p class="empty-subtext">
            Saat Anda mencatat pemasukan atau pengeluaran di Log Aktivitas, pilih atau ketik nama tempat (misal: BCA, Dana, Cash). Saldo otomatis tampil di sini.
          </p>
        </div>

        <!-- Wallets Breakdown Cards -->
        <div v-else class="wallet-list">
          <div
            v-for="(item, idx) in processedBalances"
            :key="item.wallet"
            class="wallet-row"
            @mouseenter="hoverWallet(idx)"
            @mouseleave="resetCenter"
          >
            <div class="wallet-row-left">
              <span
                class="wallet-dot"
                :style="{ backgroundColor: getWalletColor(idx) }"
              ></span>
              <div class="wallet-info">
                <span class="wallet-name">{{ item.wallet }}</span>
                <span class="wallet-pct">{{ getWalletPct(item.balance) }}% dari total uang</span>
              </div>
            </div>

            <div class="wallet-row-right">
              <span class="wallet-balance">{{ formatRupiah(item.balance) }}</span>
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
  '#06b6d4', // Cyan (Bank 1)
  '#10b981', // Emerald (Cash)
  '#8b5cf6', // Purple (E-Wallet 1)
  '#f59e0b', // Amber (E-Wallet 2)
  '#3b82f6', // Blue (Bank 2)
  '#ec4899', // Pink
  '#14b8a6', // Teal
  '#f97316'  // Orange
];

export default {
  name: 'WalletDonut',
  props: {
    wallets: {
      type: Array,
      default: () => []
    },
    balances: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chartInstance: null,
      centerTitle: 'Total Seluruh Uang',
      centerAmount: 0,
      centerSub: 'Semua Tempat'
    };
  },
  computed: {
    totalBalance() {
      if (!this.balances || this.balances.length === 0) return 0;
      return this.balances.reduce((acc, curr) => acc + (curr.balance || 0), 0);
    },
    processedBalances() {
      if (!this.balances || this.balances.length === 0) {
        return [];
      }
      return this.balances;
    },
    activeWalletsCount() {
      return this.processedBalances.length;
    }
  },
  watch: {
    balances: {
      deep: true,
      handler() {
        this.resetCenter();
        this.$nextTick(() => {
          this.renderChart();
        });
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
      this.chartInstance.destroy();
    }
  },
  methods: {
    formatRupiah,
    getWalletColor(idx) {
      return WALLET_COLORS[idx % WALLET_COLORS.length];
    },
    getWalletPct(amt) {
      if (!this.totalBalance || this.totalBalance <= 0) return 0;
      return Math.round((amt / this.totalBalance) * 100);
    },
    resetCenter() {
      this.centerTitle = 'Total Seluruh Uang';
      this.centerAmount = this.totalBalance;
      this.centerSub = 'Semua Tempat';
    },
    hoverWallet(idx) {
      const item = this.processedBalances[idx];
      if (!item) return;
      this.centerTitle = item.wallet;
      this.centerAmount = item.balance;
      this.centerSub = `${this.getWalletPct(item.balance)}% dari total`;
    },
    renderChart() {
      if (!this.$refs.walletCanvas) return;

      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }

      const items = this.processedBalances.filter(b => b.balance > 0);

      let labels = [];
      let data = [];
      let bgColors = [];

      if (items.length === 0) {
        labels = ['Belum ada saldo'];
        data = [1];
        bgColors = ['rgba(255, 255, 255, 0.05)'];
      } else {
        labels = items.map(i => i.wallet);
        data = items.map(i => i.balance);
        bgColors = items.map((_, idx) => this.getWalletColor(idx));
      }

      const ctx = this.$refs.walletCanvas.getContext('2d');
      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [
            {
              data,
              backgroundColor: bgColors,
              borderColor: '#0f172a',
              borderWidth: 3,
              hoverBorderWidth: 4,
              hoverBorderColor: '#ffffff',
              borderRadius: 6,
              spacing: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '74%',
          animation: {
            duration: 600,
            easing: 'easeOutQuart'
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              enabled: items.length > 0,
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              titleColor: '#ffffff',
              bodyColor: '#cbd5e1',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              padding: 10,
              cornerRadius: 8,
              callbacks: {
                label: (ctxItem) => {
                  const val = ctxItem.parsed;
                  const pct = this.getWalletPct(val);
                  return ` ${formatRupiah(val)} (${pct}%)`;
                }
              }
            }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.wallet-donut-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.badge-wallet {
  font-size: 0.72rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
}

/* Wealth Summary Hero Card */
.wealth-summary-card {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(99, 102, 241, 0.08) 100%);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.wealth-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.wealth-label-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.wealth-amount {
  font-size: 1.65rem;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: -0.02em;
  font-feature-settings: 'tnum' on;
}

.wealth-sub {
  font-size: 0.75rem;
  color: var(--text-dim);
}

/* Donut Content */
.donut-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1;
}

.chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.25rem 0;
}

.canvas-container {
  position: relative;
  width: 210px;
  height: 210px;
}

.donut-center-info {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 140px;
}

.center-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
}

.center-value {
  font-size: 1.05rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.15rem 0;
  line-height: 1.2;
}

.center-sub {
  font-size: 0.68rem;
  color: #38bdf8;
  font-weight: 500;
}

/* Legend Wrapper */
.legend-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

/* Empty Wallets State */
.empty-wallets {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.75rem 1rem;
  background: rgba(255, 255, 255, 0.015);
  border: 1px dashed var(--border-color);
  border-radius: 12px;
  gap: 0.4rem;
}

.empty-icon-sm {
  color: var(--text-dim);
  margin-bottom: 0.2rem;
}

.empty-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.empty-subtext {
  font-size: 0.75rem;
  color: var(--text-dim);
  max-width: 280px;
  line-height: 1.35;
}

/* Wallet List */
.wallet-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.wallet-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem 0.85rem;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.wallet-row:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-light);
  transform: translateX(2px);
}

.wallet-row-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.wallet-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.wallet-info {
  display: flex;
  flex-direction: column;
}

.wallet-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
}

.wallet-pct {
  font-size: 0.7rem;
  color: var(--text-dim);
}

.wallet-row-right {
  display: flex;
  align-items: center;
}

.wallet-balance {
  font-size: 0.9rem;
  font-weight: 700;
  color: #ffffff;
}
</style>
