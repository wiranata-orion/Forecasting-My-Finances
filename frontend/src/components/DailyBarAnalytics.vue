<template>
  <div class="fin-card daily-bar-container">
    <div class="card-header">
      <div class="header-titles">
        <h3 class="card-title">Analitik Batang Pertanggal</h3>
        <p class="card-desc" v-if="activeMode === 'finance'">Perbandingan arus kas pemasukan dan pengeluaran per setiap tanggal</p>
        <p class="card-desc" v-else>Perubahan Total Tabungan Aktif harian (mulai dari saldo awal periode)</p>
      </div>

      <div class="header-controls">
        <div class="view-toggles">
          <button
            class="toggle-btn"
            :class="{ active: activeMode === 'finance' }"
            @click="setMode('finance')"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            Pengeluaran / Pemasukan
          </button>
          <button
            class="toggle-btn"
            :class="{ active: activeMode === 'wallet' }"
            @click="setMode('wallet')"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M3 7h18v13H3z"/>
              <path d="M7 7V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2"/>
              <path d="M12 11v5M9.5 13.5h5"/>
            </svg>
            Uang Tersimpan
          </button>
        </div>

        <div class="filter-pills">
          <button
            class="pill-btn"
            :class="{ active: timeFilter === 'all' }"
            @click="setTimeFilter('all')"
          >
            Semua
          </button>
          <template v-if="!isAllTime">
            <!-- Monthly mode: 7 Hari, 14 Hari -->
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
          </template>
          <template v-else>
            <!-- All-time mode: 6 Bulan, 1 Tahun -->
            <button
              class="pill-btn"
              :class="{ active: timeFilter === '6m' }"
              @click="setTimeFilter('6m')"
            >
              6 Bulan
            </button>
            <button
              class="pill-btn"
              :class="{ active: timeFilter === '1y' }"
              @click="setTimeFilter('1y')"
            >
              1 Tahun
            </button>
          </template>
        </div>

        <!-- Date Window Navigation (for 7d/14d modes) -->
        <div v-if="timeFilter !== 'all' && maxDateWindowOffset > 0" class="window-nav">
          <button
            class="nav-btn"
            :class="{ disabled: !canGoPrevWindow }"
            :disabled="!canGoPrevWindow"
            @click="prevWindow"
            aria-label="Jendela sebelumnya (lebih lama)"
            title="Jendela sebelumnya (lebih lama)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <span class="window-label">{{ currentWindowLabel }}</span>
          <button
            class="nav-btn"
            :class="{ disabled: !canGoNextWindow }"
            :disabled="!canGoNextWindow"
            @click="nextWindow"
            aria-label="Jendela berikutnya (lebih baru)"
            title="Jendela berikutnya (lebih baru)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Stats Row -->
    <div class="stats-ribbon" v-if="activeMode === 'finance'">
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

    <div class="stats-ribbon" v-else>
      <div class="ribbon-item">
        <span class="ribbon-label">Saldo Awal Periode</span>
        <span class="ribbon-val text-white">{{ formatRupiah(startBalance) }}</span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Saldo Akhir (Akhir Periode)</span>
        <span class="ribbon-val" :class="runningBalances.length ? (runningBalances[runningBalances.length - 1] >= 0 ? 'text-income' : 'text-expense') : 'text-white'">
          {{ runningBalances.length ? formatRupiah(runningBalances[runningBalances.length - 1]) : formatRupiah(startBalance) }}
        </span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Total Pemasukan Periode</span>
        <span class="ribbon-val text-income">{{ formatRupiah(filteredTotals.income) }}</span>
      </div>
      <div class="ribbon-divider"></div>
      <div class="ribbon-item">
        <span class="ribbon-label">Total Pengeluaran Periode</span>
        <span class="ribbon-val text-expense">{{ formatRupiah(filteredTotals.expense) }}</span>
      </div>
    </div>

    <!-- Chart Canvas -->
    <div class="chart-canvas-area"
         @touchstart.passive="handleTouchStart"
         @touchend.passive="handleTouchEnd"
         @touchcancel="touchStartX = null">
      <div v-if="processedDailyData.length === 0" class="empty-bar-state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        <p v-if="isAllTime">Belum ada data historis.</p>
        <p v-else>Belum ada data mutasi harian di bulan ini.</p>
        <span v-if="isAllTime">Data akan muncul setelah ada transaksi di periode manapun.</span>
        <span v-else>Tambahkan pemasukan atau pengeluaran untuk melihat grafik.</span>
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
  Legend,
  LineController,
  LineElement,
  PointElement,
  Filler
} from 'chart.js';
import { formatRupiah, formatDateShort } from '../utils/formatters.js';

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend, LineController, LineElement, PointElement, Filler);

// Custom plugin for reference lines (start balance and zero line)
const referenceLinesPlugin = {
  id: 'referenceLines',
  afterDraw(chart) {
    const { ctx, scales, chartArea } = chart;
    const yScale = scales.y;

    // Access stored reference line data from chart options
    const refLines = chart.config.options.plugins?.referenceLines;
    if (!refLines) return;

    ctx.save();

    // Helper function to draw rounded rect (with fallback for older browsers)
    function drawRoundRect(ctx, x, y, width, height, radius) {
      if (typeof ctx.roundRect === 'function') {
        ctx.roundRect(x, y, width, height, radius);
      } else {
        // Fallback for older browsers
        const r = Math.min(radius, width / 2, height / 2);
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + width - r, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + r);
        ctx.lineTo(x + width, y + height - r);
        ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
        ctx.lineTo(x + r, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
      }
    }

    // Draw start balance line
    if (refLines.startBalance !== undefined && refLines.startBalance !== null) {
      const y = yScale.getPixelForValue(refLines.startBalance);
      if (y >= chartArea.top && y <= chartArea.bottom) {
        ctx.beginPath();
        ctx.moveTo(chartArea.left, y);
        ctx.lineTo(chartArea.right, y);
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.5)';
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 4]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw label
        const labelText = `Saldo Awal: ${formatRupiah(refLines.startBalance)}`;
        ctx.font = '600 10px "Plus Jakarta Sans", sans-serif';
        const textMetrics = ctx.measureText(labelText);
        const padding = 6;
        const labelWidth = textMetrics.width + padding * 2;
        const labelHeight = 20;
        const labelX = chartArea.left + 8;
        const labelY = y - 8;

        // Background
        ctx.fillStyle = 'rgba(6, 182, 212, 0.9)';
        ctx.beginPath();
        drawRoundRect(ctx, labelX, labelY - labelHeight, labelWidth, labelHeight, 4);
        ctx.fill();

        // Text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(labelText, labelX + padding, labelY - 5);
      }
    }

    // Draw zero line
    if (refLines.showZeroLine && refLines.minBalance < 0) {
      const y = yScale.getPixelForValue(0);
      if (y >= chartArea.top && y <= chartArea.bottom) {
        ctx.beginPath();
        ctx.moveTo(chartArea.left, y);
        ctx.lineTo(chartArea.right, y);
        ctx.strokeStyle = 'rgba(244, 63, 94, 0.3)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([6, 6]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    ctx.restore();
  }
};

Chart.register(referenceLinesPlugin);

export default {
  name: 'DailyBarAnalytics',
  props: {
    dailyData: {
      type: Array,
      default: () => []
    },
    monthlyData: {
      type: Array,
      default: () => []
    },
    startBalance: {
      type: Number,
      default: 0
    },
    isAllTime: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      chartInstance: null,
      timeFilter: 'all', // 'all', '7d', '14d', '6m', '1y'
      activeMode: 'finance', // 'finance' = Pengeluaran/Pemasukan, 'wallet' = Uang Tersimpan
      dateWindowOffset: 0, // 0 = most recent window, 1 = previous window, etc.
      touchStartX: null // for swipe gestures
    };
  },
  computed: {
    // Returns the appropriate data source based on mode
    sourceData() {
      return this.isAllTime ? this.monthlyData : this.dailyData;
    },
    // Returns the date key field name for the current data source
    dateKey() {
      return this.isAllTime ? 'month' : 'date';
    },
    // Returns the label field name for the current data source
    labelKey() {
      return this.isAllTime ? 'month_label' : 'date';
    },
    windowSize() {
      // Returns the window size in data points based on the current time filter
      // For monthly mode (isAllTime), these are months; for daily mode, these are days
      switch (this.timeFilter) {
        case '7d': return 7;
        case '14d': return 14;
        case '6m': return 6;  // 6 months
        case '1y': return 12; // 12 months
        default: return 0;
      }
    },
    processedDailyData() {
      const data = this.sourceData;
      if (!data || data.length === 0) return [];

      const key = this.dateKey;
      const sorted = [...data].sort((a, b) => a[key].localeCompare(b[key]));

      if (this.timeFilter === 'all') {
        return sorted;
      }

      // For all time-based filters, implement windowed pagination
      const windowSize = this.windowSize;
      if (!windowSize) return sorted;

      const totalItems = sorted.length;
      const maxOffset = Math.max(0, totalItems - windowSize);

      // Clamp offset to valid range
      const clampedOffset = Math.min(Math.max(0, this.dateWindowOffset), maxOffset);

      // Calculate slice indices
      // Offset 0 = last windowSize items (most recent)
      // Offset 1 = previous windowSize items, etc.
      const endIndex = totalItems - clampedOffset;
      const startIndex = Math.max(0, endIndex - windowSize);

      return sorted.slice(startIndex, endIndex);
    },
    maxDateWindowOffset() {
      const data = this.sourceData;
      if (!data || data.length === 0) return 0;
      if (this.timeFilter === 'all') return 0;
      const windowSize = this.windowSize;
      if (!windowSize) return 0;
      const totalItems = data.length;
      return Math.max(0, totalItems - windowSize);
    },
    currentWindowLabel() {
      if (this.timeFilter === 'all' || !this.processedDailyData.length) return '';
      const first = this.processedDailyData[0];
      const last = this.processedDailyData[this.processedDailyData.length - 1];
      if (!first || !last) return '';

      const labelKey = this.labelKey;
      if (this.isAllTime) {
        // For monthly data, use month_label directly
        if (first[labelKey] === last[labelKey]) {
          return first[labelKey];
        }
        return `${first[labelKey]} - ${last[labelKey]}`;
      } else {
        // For daily data, format the dates
        const firstDate = new Date(first.date + 'T00:00:00');
        const lastDate = new Date(last.date + 'T00:00:00');
        const formatter = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short' });
        if (first.date === last.date) {
          return formatter.format(firstDate);
        }
        return `${formatter.format(firstDate)} - ${formatter.format(lastDate)}`;
      }
    },
    canGoPrevWindow() {
      return this.timeFilter !== 'all' && this.dateWindowOffset < this.maxDateWindowOffset;
    },
    canGoNextWindow() {
      return this.timeFilter !== 'all' && this.dateWindowOffset > 0;
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
    },
    runningBalances() {
      // Calculate running balance for "Uang Tersimpan" mode
      // Start with startBalance, then add income and subtract expense for each day
      const balances = [];
      let running = this.startBalance || 0;
      this.processedDailyData.forEach(d => {
        running += (d.income || 0) - (d.expense || 0);
        balances.push(running);
      });
      return balances;
    }
  },
  watch: {
    dailyData: {
      deep: true,
      handler() {
        // Reset window when data changes (e.g., period changed)
        this.dateWindowOffset = 0;
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    },
    activeMode() {
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    startBalance() {
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    timeFilter() {
      // Reset window offset when time filter changes
      this.dateWindowOffset = 0;
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    dateWindowOffset() {
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    isAllTime(newVal) {
      // Reset time filter when switching between monthly/all-time modes
      this.timeFilter = 'all';
      this.dateWindowOffset = 0;
      this.$nextTick(() => {
        this.renderChart();
      });
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
    setMode(mode) {
      this.activeMode = mode;
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    setTimeFilter(filter) {
      this.timeFilter = filter;
      // Reset window offset when changing time filter
      this.dateWindowOffset = 0;
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    prevWindow() {
      if (this.canGoPrevWindow) {
        this.dateWindowOffset++;
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    },
    nextWindow() {
      if (this.canGoNextWindow) {
        this.dateWindowOffset--;
        this.$nextTick(() => {
          this.renderChart();
        });
      }
    },
    resetWindow() {
      this.dateWindowOffset = 0;
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    handleTouchStart(e) {
      this.touchStartX = e.touches[0].clientX;
    },
    handleTouchEnd(e) {
      if (this.touchStartX === null) return;
      const touchEndX = e.changedTouches[0].clientX;
      const diff = touchEndX - this.touchStartX;
      const threshold = 50; // minimum swipe distance

      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          // Swipe right - go to next window (more recent)
          this.nextWindow();
        } else {
          // Swipe left - go to previous window (older)
          this.prevWindow();
        }
      }
      this.touchStartX = null;
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
        // For monthly data (isAllTime), use month_label; for daily data, use formatDateShort
        const labels = this.isAllTime
          ? dataItems.map(d => d.month_label)
          : dataItems.map(d => formatDateShort(d.date));
        const incomeValues = dataItems.map(d => d.income || 0);
        const expenseValues = dataItems.map(d => d.expense || 0);

        if (this.activeMode === 'finance') {
          // Bar chart: Pengeluaran / Pemasukan
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
                      const item = dataItems[idx];
                      if (!item) return '';
                      // For monthly data, show month label; for daily data, show date
                      const label = this.isAllTime ? (item.month_label || item.month) : (item.date || '');
                      return `Periode: ${label}`;
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
                      const prefix = this.isAllTime ? 'Net Bulanan' : 'Net Harian';
                      return `\n ${prefix}: ${net >= 0 ? '+' : ''}${formatRupiah(net)}`;
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
        } else {
          // Line chart: Uang Tersimpan (running savings balance) - Enhanced styling
          const runningBalances = this.runningBalances;
          const chartHeight = 260; // Match chart-canvas-area height

          // Create gradient fill for the area under the line
          const gradient = ctx.createLinearGradient(0, 0, 0, chartHeight);
          gradient.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
          gradient.addColorStop(0.5, 'rgba(6, 182, 212, 0.15)');
          gradient.addColorStop(1, 'rgba(6, 182, 212, 0.02)');

          // Calculate point colors based on daily net change (green for positive, red for negative)
          const pointColors = runningBalances.map((balance, idx) => {
            if (idx === 0) return '#06b6d4'; // First point uses main color
            const prevBalance = runningBalances[idx - 1];
            const change = balance - prevBalance;
            return change >= 0 ? '#10b981' : '#f43f5e';
          });

          // Prepare annotation data for reference lines
          const startBalance = this.startBalance || 0;
          const minBalance = Math.min(...runningBalances, startBalance, 0);
          const maxBalance = Math.max(...runningBalances, startBalance);

          this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
              labels,
              datasets: [
                {
                  label: 'Total Tabungan Aktif',
                  data: runningBalances,
                  borderColor: '#06b6d4',
                  backgroundColor: gradient,
                  borderWidth: 4,
                  fill: true,
                  tension: 0.4,
                  pointRadius: 5,
                  pointHoverRadius: 8,
                  pointBackgroundColor: pointColors,
                  pointBorderColor: '#ffffff',
                  pointBorderWidth: 2.5,
                  pointHitRadius: 12
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              interaction: {
                mode: 'index',
                intersect: false
              },
              plugins: {
                legend: {
                  display: false
                },
                tooltip: {
                  backgroundColor: '#161e33',
                  titleColor: '#f1f5f9',
                  bodyColor: '#94a3b8',
                  borderColor: 'rgba(6, 182, 212, 0.3)',
                  borderWidth: 1.5,
                  padding: 14,
                  cornerRadius: 10,
                  displayColors: false,
                  callbacks: {
                    title: (items) => {
                      if (!items || !items.length) return '';
                      const idx = items[0].dataIndex;
                      const item = dataItems[idx];
                      if (!item) return '';
                      // For monthly data, show month label; for daily data, show date
                      const label = this.isAllTime ? (item.month_label || item.month) : (item.date || '');
                      return `Periode: ${label}`;
                    },
                    label: (context) => {
                      const val = context.raw || 0;
                      return `  Total Tabungan: ${formatRupiah(val)}`;
                    },
                    afterBody: (items) => {
                      if (!items || !items.length) return '';
                      const idx = items[0].dataIndex;
                      const inc = incomeValues[idx] || 0;
                      const exp = expenseValues[idx] || 0;
                      const net = inc - exp;
                      const netLabel = net >= 0 ? '▲  Naik' : '▼  Turun';
                      const periodPrefix = this.isAllTime ? 'Bulanan' : 'Harian';

                      // Calculate change from previous period
                      let changeStr = '';
                      if (idx > 0 && runningBalances.length > 1) {
                        const prevBalance = runningBalances[idx - 1];
                        const currBalance = runningBalances[idx];
                        const change = currBalance - prevBalance;
                        const pct = prevBalance !== 0 ? ((change / Math.abs(prevBalance)) * 100).toFixed(1) : '0';
                        const arrow = change >= 0 ? '▲' : '▼';
                        changeStr = `\n Perubahan ${periodPrefix.toLowerCase()}: ${arrow} ${formatRupiah(Math.abs(change))} (${pct}%)`;
                      }

                      return ` ${netLabel} ${periodPrefix.toLowerCase()}: ${net >= 0 ? '+' : ''}${formatRupiah(net)}`
                        + `\n Pemasukan: ${formatRupiah(inc)}`
                        + `\n Pengeluaran: ${formatRupiah(exp)}`
                        + changeStr;
                    }
                  }
                },
                // Custom plugin for reference lines
                referenceLines: {
                  startBalance: startBalance,
                  showZeroLine: true,
                  minBalance: minBalance
                }
              },
              animation: {
                duration: 800,
                easing: 'easeOutQuart',
                animateScale: true
              },
              scales: {
                x: {
                  grid: {
                    color: 'rgba(255, 255, 255, 0.03)',
                    drawBorder: false,
                    drawTicks: false
                  },
                  ticks: {
                    color: '#94a3b8',
                    font: {
                      size: 11,
                      family: "'Plus Jakarta Sans', sans-serif"
                    },
                    maxRotation: 0,
                    autoSkip: true,
                    maxTicksLimit: 10
                  }
                },
                y: {
                  grid: {
                    color: (ctx) => {
                      // Highlight zero line
                      if (ctx.tick.value === 0) return 'rgba(244, 63, 94, 0.15)';
                      return 'rgba(255, 255, 255, 0.04)';
                    },
                    drawBorder: false,
                    drawTicks: false
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
                    },
                    // Add padding for gradient visibility
                    padding: 10,
                    // Ensure zero is included if balances cross it
                    includeBounds: true
                  },
                  // Add extra space at top for gradient
                  suggestedMax: maxBalance > 0 ? maxBalance * 1.15 : undefined,
                  suggestedMin: minBalance < 0 ? minBalance * 1.15 : (startBalance > 0 ? 0 : undefined)
                }
              }
            }
          });
        }
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

/* Window Navigation Styles */
.window-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.nav-btn.disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
}

.window-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  min-width: 120px;
  text-align: center;
}
</style>
