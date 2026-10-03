<template>
  <div class="dashboard-page">
    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="toast.show" class="toast-notification" :class="`toast-${toast.type}`">
        <span class="toast-icon">
          <svg v-if="toast.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </span>
        <span>{{ toast.message }}</span>
      </div>
    </transition>

    <main class="main-content">
      <!-- Sticky Top Header with Month Navigator + History Toggle -->
      <header class="dashboard-header">
        <div class="header-left">
          <!-- All History / Monthly toggle -->
          <div class="view-mode-toggle">
            <button
              class="mode-btn"
              :class="{ active: !isAllTime }"
              @click="setViewMode(false)"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                <line x1="16" x2="16" y1="2" y2="6"/>
                <line x1="8" x2="8" y1="2" y2="6"/>
                <line x1="3" x2="21" y1="10" y2="10"/>
              </svg>
              Bulanan
            </button>
            <button
              class="mode-btn"
              :class="{ active: isAllTime }"
              @click="setViewMode(true)"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              Seluruh History
            </button>
          </div>
        </div>

        <!-- FITUR LIHAT BULAN SEBELUMNYA / BULAN INI (DI TENGAH) -->
        <div class="header-center">
          <div class="month-navigator" :class="{ 'nav-disabled': isAllTime }">
            <button
              class="nav-month-btn"
              :disabled="isAllTime"
              @click="changeMonth(-1)"
              title="Lihat Bulan Sebelumnya"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>

            <div class="month-display-box">
              <span class="month-calendar-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                  <line x1="16" x2="16" y1="2" y2="6"/>
                  <line x1="8" x2="8" y1="2" y2="6"/>
                  <line x1="3" x2="21" y1="10" y2="10"/>
                </svg>
              </span>
              <span class="month-label">{{ isAllTime ? 'Seluruh Data' : currentMonthLabel }}</span>
              <span v-if="!isAllTime" class="cycle-range">
                <span>Mulai</span> {{ cycleStartLabel }}
                <span>Selesai</span> {{ cycleEndLabel }}
              </span>
              <span v-if="!isAllTime && isViewingCurrentMonth" class="current-badge">Siklus Aktif</span>
              <button
                v-else-if="!isAllTime"
                class="btn-return-today"
                @click="resetToCurrentMonth"
                title="Kembali ke Bulan Sekarang"
              >
                Kembali
              </button>
            </div>

            <button
              class="nav-month-btn"
              :class="{ 'btn-disabled': isViewingCurrentMonth || isAllTime }"
              :disabled="isViewingCurrentMonth || isAllTime"
              @click="changeMonth(1)"
              :title="isViewingCurrentMonth ? 'Bulan berikutnya belum ada' : 'Lihat Bulan Berikutnya'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="!isAllTime" class="header-actions">
          <label class="cutoff-control">
            <span>Mulai</span>
            <input
              v-model="periodStart"
              type="date"
              aria-label="Tanggal mulai"
              @change="saveCyclePeriod"
            />
          </label>
          <label class="cutoff-control">
            <span>Selesai</span>
            <input
              v-model="periodEnd"
              type="date"
              aria-label="Tanggal selesai"
              @change="saveCyclePeriod"
            />
          </label>
        </div>
      </header>

      <!-- Section 1: Overview Summary Cards -->
      <OverviewCards
        :month-label="isAllTime ? 'Seluruh History' : currentMonthLabel"
        :summary="overviewSummary"
        :transaction-count="summary.transaction_count"
        :planned-count="overviewPlannedCount"
        :total-savings="activeSavingsAmount"
      />

      <!-- Section 2: Charts Row (Donut Analytics + Daily Bar Analytics) -->
      <section class="charts-grid" id="grafik">
        <DonutAnalytics
          :summary="summary.current_month"
          :categories="summary.categories"
          :wallet-balances="walletBalances"
          :wallets="wallets"
          :savings-wallets="savingsWallets"
          :is-all-time="isAllTime"
          @save-savings-wallets="handleSaveSavingsWallets"
        />

        <DailyBarAnalytics
          :daily-data="summary.daily_analytics"
        />
      </section>

      <!-- Section 3: Kemungkinan Pengeluaran (full width) -->
      <PlannedExpenses
        v-if="!isAllTime"
        :planned-list="filteredPlannedList"
        :summary="summary.current_month"
        :transactions="filteredTransactions"
        @open-add-planned="isAddPlanOpen = true"
        @edit-planned="handleEditPlanned"
        @delete-planned="handleDeletePlanned"
        @realize-planned="handleRealizePlanned"
        :monthly-needs="monthlyNeeds"
        :monthly-templates="monthlyTemplates"
        :savings-wallets="savingsWallets"
        @create-monthly="handleCreateMonthly"
        @edit-monthly="handleEditMonthly"
        @delete-monthly="handleDeleteMonthly"
        @realize-monthly="handleRealizeMonthly"
        @create-template="handleCreateTemplate"
        @edit-template="handleEditTemplate"
        @delete-template="handleDeleteTemplate"
        @apply-template="handleApplyTemplate"
        :is-current-month="isViewingCurrentMonth"
      />

      <!-- Section 4: Python Machine Learning Forecasting View (hidden in all-time mode) -->
      <ForecastingView
        :forecast-data="forecastData"
        :is-loading="isForecastLoading"
        :selected-year="selectedYear"
        :selected-month="selectedMonth"
        :is-past-month="!isViewingCurrentMonth"
        :is-all-time="isAllTime"
        @recalculate-forecast="handleRecalculateForecast"
      />

      <!-- Section 5: Activity Log (Log Aktivitas Pengeluaran & Pemasukan) -->
      <ActivityLog
        :transactions="filteredTransactions"
        :month-label="isAllTime ? 'Seluruh History' : currentMonthLabel"
        @open-add-transaction="isAddTxOpen = true"
        @edit-transaction="handleEditTransaction"
        @delete-transaction="handleDeleteTransaction"
      />
    </main>

    <!-- Modals -->
    <AddTransactionModal
      :is-open="isAddTxOpen"
      :transaction="editingTransaction"
      @close="closeTransactionModal"
      @submit="handleSaveTransaction"
    />

    <AddPlannedModal
      :is-open="isAddPlanOpen"
      :plan="editingPlanned"
      @close="closePlannedModal"
      @submit="handleAddPlanned"
    />
  </div>
</template>

<script>
import OverviewCards from './OverviewCards.vue';
import DonutAnalytics from './DonutAnalytics.vue';
import DailyBarAnalytics from './DailyBarAnalytics.vue';
import PlannedExpenses from './PlannedExpenses.vue';
import ForecastingView from './ForecastingView.vue';
import ActivityLog from './ActivityLog.vue';
import AddTransactionModal from './AddTransactionModal.vue';
import AddPlannedModal from './AddPlannedModal.vue';

import {
  fetchHealth,
  fetchSummary,
  fetchTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  fetchPlanned,
  createPlanned,
  updatePlanned,
  deletePlanned,
  fetchMonthlyNeeds,
  createMonthlyNeed,
  updateMonthlyNeed,
  deleteMonthlyNeed,
  realizeMonthlyNeed,
  fetchMonthlyTemplates,
  createMonthlyTemplate,
  updateMonthlyTemplate,
  deleteMonthlyTemplate,
  applyMonthlyTemplate,
  runForecast,
  fetchWallets,
  fetchCutoffDays,
  updateCutoffDays,
  fetchCyclePeriod,
  updateCyclePeriod,
  fetchSavingsWallets,
  updateSavingsWallets
} from '../services/api.js';

function getActiveCycle(startDay, endDay, today = new Date()) {
  let year = today.getFullYear();
  let month = today.getMonth() + 1;
  const monthLength = new Date(year, month, 0).getDate();
  const actualStartDay = Math.min(startDay, monthLength);
  const actualEndDay = Math.min(endDay, monthLength);
  if (startDay > endDay && today.getDate() >= actualStartDay) {
    month += 1;
    if (month > 12) {
      month = 1;
      year += 1;
    }
  } else if (startDay <= endDay && today.getDate() < actualStartDay) {
    month -= 1;
    if (month < 1) {
      month = 12;
      year -= 1;
    }
  } else if (startDay <= endDay && today.getDate() > actualEndDay) {
    month += 1;
    if (month > 12) {
      month = 1;
      year += 1;
    }
  }
  return { year, month };
}

function getCycleBounds(year, month, startDay, endDay) {
  if (startDay > endDay) {
    const previousMonthLength = new Date(year, month - 1, 0).getDate();
    const currentMonthLength = new Date(year, month, 0).getDate();
    return {
      start: new Date(year, month - 2, Math.min(startDay, previousMonthLength)),
      end: new Date(year, month - 1, Math.min(endDay, currentMonthLength))
    };
  }
  const currentMonthLastDay = new Date(year, month, 0).getDate();
  return {
    start: new Date(year, month - 1, Math.min(startDay, currentMonthLastDay)),
    end: new Date(year, month - 1, Math.min(endDay, currentMonthLastDay))
  };
}

function toISODate(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export default {
  name: 'Home',
  components: {
    OverviewCards,
    DonutAnalytics,
    DailyBarAnalytics,
    PlannedExpenses,
    ForecastingView,
    ActivityLog,
    AddTransactionModal,
    AddPlannedModal
  },
  data() {
    const today = new Date();
    const cycle = getActiveCycle(24, 23, today);
    return {
      selectedYear: cycle.year,
      selectedMonth: cycle.month,
      startDay: 24,
      endDay: 23,
      periodStart: '',
      periodEnd: '',
      isAllTime: false,

      isBackendOnline: true,
      isAddTxOpen: false,
      editingTransaction: null,
      isAddPlanOpen: false,
      editingPlanned: null,
      isForecastLoading: false,

      summary: {
        current_month: {
          total_income: 0,
          total_expense: 0,
          total_planned: 0,
          sisa_tabungan: 0,
          savings_ratio: 0
        },
        daily_analytics: [],
        categories: [],
        transaction_count: 0,
        planned_count: 0
      },

      transactions: [],
      plannedList: [],
      monthlyNeeds: [],
      monthlyTemplates: [],
      wallets: [],
      savingsWallets: [],
      walletBalances: [],
      forecastData: null,

      toast: {
        show: false,
        message: '',
        type: 'success',
        timer: null
      }
    };
  },
  computed: {
    isViewingCurrentMonth() {
      const current = getActiveCycle(this.startDay, this.endDay);
      return this.selectedYear === current.year && this.selectedMonth === current.month;
    },
    currentMonthLabel() {
      const monthNames = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
      ];
      return `${monthNames[this.selectedMonth] || ''} ${this.selectedYear}`;
    },
    cycleStartLabel() {
      const formatter = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short' });
      return this.periodStart ? formatter.format(new Date(`${this.periodStart}T00:00:00`)) : '-';
    },
    cycleEndLabel() {
      const formatter = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short' });
      return this.periodEnd ? formatter.format(new Date(`${this.periodEnd}T00:00:00`)) : '-';
    },
    filteredPlannedList() {
      if (this.isAllTime) return this.plannedList;
      const start = new Date(`${this.periodStart}T00:00:00`);
      const end = new Date(`${this.periodEnd}T00:00:00`);
      const startDate = toISODate(start);
      const endDate = toISODate(end);
      return this.plannedList.filter(item => item.date >= startDate && item.date <= endDate);
    },
    filteredTransactions() {
      if (this.isAllTime) {
        return this.transactions;
      }
      const start = new Date(`${this.periodStart}T00:00:00`);
      const end = new Date(`${this.periodEnd}T00:00:00`);
      const startDate = toISODate(start);
      const endDate = toISODate(end);
      return this.transactions.filter(tx => {
        if (!tx.date) return false;
        const transactionDate = tx.date.slice(0, 10);
        if (this.isViewingCurrentMonth && transactionDate > toISODate(new Date())) return false;
        return transactionDate >= startDate && transactionDate <= endDate;
      });
    },
    overviewMonthlyTotal() {
      if (this.isAllTime) return 0;
      return this.monthlyNeeds.reduce((total, item) => {
        if (item.type && item.type !== 'expense') return total;
        return total + Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
      }, 0);
    },
    overviewPlannedTotal() {
      if (this.isAllTime) return Number(this.summary.current_month.total_planned || 0);
      const plannedTotal = this.filteredPlannedList.reduce((total, item) => total + Number(item.amount || 0), 0);
      return plannedTotal + this.overviewMonthlyTotal;
    },
    overviewSummary() {
      return {
        ...this.summary.current_month,
        total_planned: this.overviewPlannedTotal
      };
    },
    overviewPlannedCount() {
      return this.isAllTime ? this.summary.planned_count : this.filteredPlannedList.length + this.monthlyNeeds.length;
    },
    overviewTotalSavings() {
      return Number(this.summary.current_month.sisa_tabungan || 0)
        - Number(this.overviewPlannedTotal || 0);
    },
    activeSavingsAmount() {
      const activeWallets = new Set(this.savingsWallets.map(wallet => String(wallet).trim()));
      if (!activeWallets.size) return 0;
      return this.filteredTransactions.reduce((total, tx) => {
        const wallet = String(tx.wallet || '').trim();
        const transferTo = String(tx.transfer_to || '').trim();
        const amount = Number(tx.amount || 0);
        if (tx.type === 'transfer') {
          return total - (activeWallets.has(wallet) ? amount : 0) + (activeWallets.has(transferTo) ? amount : 0);
        }
        if (!activeWallets.has(wallet)) return total;
        if (tx.type === 'income') return total + amount;
        if (tx.type === 'expense' && tx.savings_status === 'savings') return total - amount;
        return total;
      }, 0);
    }
  },
  async mounted() {
    await this.checkBackend();
    try {
      const cutoffDays = await fetchCutoffDays();
      this.startDay = cutoffDays.start_day;
      this.endDay = cutoffDays.end_day;
      const cycle = getActiveCycle(this.startDay, this.endDay);
      this.selectedYear = cycle.year;
      this.selectedMonth = cycle.month;
      await this.loadCyclePeriod();
    } catch (err) {
      console.error('Error loading payday cut-off:', err);
    }
    await this.refreshAllData();
  },
  methods: {
    showToast(message, type = 'success') {
      if (this.toast.timer) clearTimeout(this.toast.timer);
      this.toast.message = message;
      this.toast.type = type;
      this.toast.show = true;
      this.toast.timer = setTimeout(() => {
        this.toast.show = false;
      }, 3500);
    },

    async checkBackend() {
      try {
        await fetchHealth();
        this.isBackendOnline = true;
      } catch (e) {
        this.isBackendOnline = false;
      }
    },

    async setViewMode(allTime) {
      const savedScroll = window.scrollY;
      this.isAllTime = allTime;
      await this.refreshAllData();
      this.$nextTick(() => {
        window.scrollTo({ top: savedScroll, behavior: 'instant' });
      });
    },

    async changeMonth(offset) {
      if (this.isAllTime) return;
      const savedScroll = window.scrollY;
      let m = this.selectedMonth + offset;
      let y = this.selectedYear;
      if (m < 1) {
        m = 12;
        y -= 1;
      } else if (m > 12) {
        m = 1;
        y += 1;
      }
      const current = getActiveCycle(this.startDay, this.endDay);
      if (y > current.year || (y === current.year && m > current.month)) {
        return; // Guard against future dates
      }
      this.selectedMonth = m;
      this.selectedYear = y;
      await this.loadCyclePeriod();
      await this.refreshAllData();
      this.$nextTick(() => {
        window.scrollTo({ top: savedScroll, behavior: 'instant' });
      });
    },

    async resetToCurrentMonth() {
      const savedScroll = window.scrollY;
      const current = getActiveCycle(this.startDay, this.endDay);
      this.selectedYear = current.year;
      this.selectedMonth = current.month;
      this.isAllTime = false;
      await this.loadCyclePeriod();
      await this.refreshAllData();
      this.$nextTick(() => {
        window.scrollTo({ top: savedScroll, behavior: 'instant' });
      });
    },

    async refreshSummary() {
      try {
        this.summary = await fetchSummary(this.selectedYear, this.selectedMonth, this.isAllTime);
        this.walletBalances = this.summary.wallet_balances || [];
      } catch (err) {
        console.error('Error fetching summary:', err);
      }
    },

    async refreshForecast(simulatedIncome = null, isSavingLog = false) {
      this.isForecastLoading = true;
      try {
        const fcRes = await runForecast(this.selectedYear, this.selectedMonth, simulatedIncome, isSavingLog, this.isAllTime);
        this.forecastData = fcRes;
      } catch (err) {
        console.error('Error fetching forecast:', err);
      } finally {
        this.isForecastLoading = false;
      }
    },

    async refreshAllData() {
      try {
        const [sumRes, txRes, planRes, monthlyRes, templateRes, walletRes, savingsRes, fcRes] = await Promise.all([
          fetchSummary(this.selectedYear, this.selectedMonth, this.isAllTime),
          fetchTransactions(),
          fetchPlanned(),
          fetchMonthlyNeeds(this.selectedYear, this.selectedMonth),
          fetchMonthlyTemplates(),
          fetchWallets(),
          fetchSavingsWallets(),
          runForecast(this.selectedYear, this.selectedMonth, null, false, this.isAllTime)
        ]);
        this.summary = sumRes;
        this.transactions = txRes;
        this.plannedList = planRes;
        this.monthlyNeeds = monthlyRes;
        this.monthlyTemplates = templateRes;
        this.wallets = walletRes;
        this.savingsWallets = savingsRes.wallets || [];
        this.forecastData = fcRes;
        this.walletBalances = sumRes.wallet_balances || [];
        this.isBackendOnline = true;
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        this.isBackendOnline = false;
      }
    },

    async handleSaveTransaction(txData) {
      try {
        if (this.editingTransaction) {
          await updateTransaction(this.editingTransaction.id, txData);
        } else {
          await createTransaction(txData);
        }
        this.isAddTxOpen = false;
        this.showToast(this.editingTransaction ? 'Transaksi berhasil diperbarui' : 'Transaksi baru berhasil ditambahkan');
        this.editingTransaction = null;
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menambahkan transaksi', 'error');
      }
    },

    handleEditTransaction(transaction) {
      this.editingTransaction = { ...transaction };
      this.isAddTxOpen = true;
    },

    closeTransactionModal() {
      this.isAddTxOpen = false;
      this.editingTransaction = null;
    },

    async handleDeleteTransaction(id) {
      if (!confirm('Yakin ingin menghapus transaksi ini?')) return;
      try {
        await deleteTransaction(id);
        this.showToast('Transaksi telah dihapus');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menghapus transaksi', 'error');
      }
    },

    async handleAddPlanned(planData) {
      try {
        const wasEditing = Boolean(this.editingPlanned);
        if (wasEditing) {
          await updatePlanned(this.editingPlanned.id, planData);
        } else {
          await createPlanned(planData);
        }
        this.isAddPlanOpen = false;
        this.editingPlanned = null;
        this.showToast(wasEditing ? 'Rencana pengeluaran diperbarui' : 'Rencana pengeluaran berhasil disimpan');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menambahkan rencana', 'error');
      }
    },

    handleEditPlanned(item) {
      this.editingPlanned = { ...item };
      this.isAddPlanOpen = true;
    },

    closePlannedModal() {
      this.isAddPlanOpen = false;
      this.editingPlanned = null;
    },

    async handleDeletePlanned(id) {
      if (!confirm('Hapus rencana kemungkinan pengeluaran ini?')) return;
      try {
        await deletePlanned(id);
        this.showToast('Rencana pengeluaran telah dihapus');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menghapus rencana', 'error');
      }
    },

    async handleCreateMonthly(item) {
      try {
        await createMonthlyNeed({ ...item, year: this.selectedYear, month: this.selectedMonth });
        this.showToast('Template kebutuhan bulanan disimpan');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menyimpan template', 'error');
      }
    },

    async handleEditMonthly(item) {
      try {
        await updateMonthlyNeed(item.id, { ...item, year: this.selectedYear, month: this.selectedMonth });
        this.showToast('Template kebutuhan diperbarui');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal memperbarui template', 'error');
      }
    },

    async handleDeleteMonthly(id) {
      if (!confirm('Hapus template kebutuhan bulanan ini?')) return;
      try {
        await deleteMonthlyNeed(id);
        this.showToast('Template kebutuhan dihapus');
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal menghapus template', 'error');
      }
    },

    async handleRealizeMonthly({ item, quantity }) {
      try {
        await realizeMonthlyNeed(item.id, this.selectedYear, this.selectedMonth, Number(quantity) || 1);
        this.showToast(`${quantity} transaksi ${item.title} masuk ke log`);
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal mengirim template ke log', 'error');
      }
    },

    async handleCreateTemplate(item) {
      try {
        await createMonthlyTemplate(item);
        this.showToast('Template kebutuhan reusable disimpan');
        this.monthlyTemplates = await fetchMonthlyTemplates();
      } catch (err) {
        this.showToast(err.message || 'Gagal menyimpan template', 'error');
      }
    },

    async handleEditTemplate(item) {
      try {
        await updateMonthlyTemplate(item.id, item);
        this.showToast('Template kebutuhan diperbarui');
        this.monthlyTemplates = await fetchMonthlyTemplates();
      } catch (err) {
        this.showToast(err.message || 'Gagal memperbarui template', 'error');
      }
    },

    async handleDeleteTemplate(id) {
      if (!confirm('Hapus template reusable ini?')) return;
      try {
        await deleteMonthlyTemplate(id);
        this.showToast('Template kebutuhan dihapus');
        this.monthlyTemplates = await fetchMonthlyTemplates();
      } catch (err) {
        this.showToast(err.message || 'Gagal menghapus template', 'error');
      }
    },

    async handleSaveSavingsWallets(wallets) {
      try {
        const result = await updateSavingsWallets(wallets);
        this.savingsWallets = result.wallets || [];
        this.showToast('Pengaturan rekening tabungan disimpan');
      } catch (err) {
        this.showToast(err.message || 'Gagal menyimpan rekening tabungan', 'error');
      }
    },

    async handleApplyTemplate(id) {
      try {
        await applyMonthlyTemplate(id, this.selectedYear, this.selectedMonth);
        this.showToast('Template diterapkan ke kebutuhan bulan ini');
        await this.refreshAllData();
      } catch (err) {
        if (err.requiresConfirmation && confirm('Bulan ini sudah memiliki list kebutuhan. Tambahkan isi template ke list yang sudah ada?')) {
          try {
            await applyMonthlyTemplate(id, this.selectedYear, this.selectedMonth, true);
            this.showToast('Isi template ditambahkan ke list kebutuhan bulan ini');
            await this.refreshAllData();
          } catch (applyError) {
            this.showToast(applyError.message || 'Gagal menambahkan template', 'error');
          }
          return;
        }
        this.showToast(err.message || 'Gagal menerapkan template', 'error');
      }
    },

    async handleRealizePlanned(item) {
      try {
        await createTransaction({
          amount: item.amount,
          description: item.title,
          category: item.category,
          wallet: item.wallet || '',
          date: new Date().toISOString().split('T')[0],
          type: 'expense'
        });
        await deletePlanned(item.id);
        this.showToast(`"${item.title}" berhasil direalisasikan ke pengeluaran riil!`);
        await this.refreshAllData();
      } catch (err) {
        this.showToast(err.message || 'Gagal merealisasikan rencana', 'error');
      }
    },

    async handleRecalculateForecast(payload) {
      this.isForecastLoading = true;
      try {
        let simulatedIncome = null;
        let isSavingLog = false;
        if (typeof payload === 'object' && payload !== null) {
          simulatedIncome = payload.simulatedIncome;
          isSavingLog = payload.isSavingLog ?? true;
        } else {
          simulatedIncome = payload;
          isSavingLog = true;
        }
        const fcRes = await runForecast(this.selectedYear, this.selectedMonth, simulatedIncome, isSavingLog, this.isAllTime);
        this.forecastData = fcRes;
        this.showToast(isSavingLog ? 'Log nilai acuan bulan depan berhasil disimpan & peramalan diperbarui!' : 'Peramalan berhasil dihitung ulang!');
      } catch (err) {
        this.showToast(err.message || 'Gagal menghitung forcasting', 'error');
      } finally {
        this.isForecastLoading = false;
      }
    },
    async loadCyclePeriod() {
      try {
        const period = await fetchCyclePeriod(this.selectedYear, this.selectedMonth);
        this.periodStart = period.start;
        this.periodEnd = period.end;
      } catch (err) {
        console.error('Error loading cycle period:', err);
      }
    },
    async saveCyclePeriod() {
      const previousStart = this.periodStart;
      const previousEnd = this.periodEnd;
      if (!this.periodStart || !this.periodEnd || this.periodStart > this.periodEnd) {
        await this.loadCyclePeriod();
        this.showToast('Tanggal mulai dan selesai harus valid', 'error');
        return;
      }
      try {
        const saved = await updateCyclePeriod(this.selectedYear, this.selectedMonth, this.periodStart, this.periodEnd);
        this.periodStart = saved.start;
        this.periodEnd = saved.end;
        await this.refreshAllData();
        this.showToast(`Periode ${this.currentMonthLabel} disimpan`);
      } catch (err) {
        this.periodStart = previousStart;
        this.periodEnd = previousEnd;
        this.showToast(err.message || 'Gagal menyimpan periode', 'error');
      }
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  max-width: 1360px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1.75rem 4rem;
  display: flex;
  flex-direction: column;
}

/* Sticky Top Header that follows user scroll */
.dashboard-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  padding: 0.65rem 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(10, 13, 20, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.header-left {
  display: flex;
  align-items: center;
  justify-self: start;
}

/* View Mode Toggle (Bulanan / Seluruh History) */
.view-mode-toggle {
  display: flex;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 0.2rem;
  border-radius: 10px;
}

.mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.mode-btn.active {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.mode-btn:not(.active):hover {
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.04);
}

/* Month Navigator Center Styling */
.header-center {
  display: flex;
  justify-content: center;
  align-items: center;
  justify-self: center;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  justify-self: end;
}

.cutoff-control {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 700;
}

.cutoff-control select {
  min-width: 3.5rem;
  padding: 0.45rem 0.6rem;
  color: #fff;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 7px;
}

.cutoff-control input {
  width: 4.2rem;
  padding: 0.45rem 0.5rem;
  color: #fff;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 7px;
  font-size: 0.8rem;
}

.cycle-range {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--text-dim);
  font-size: 0.68rem;
  white-space: nowrap;
}

.cycle-range span {
  color: var(--text-muted);
  font-weight: 700;
}

.month-navigator {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 0.25rem 0.4rem;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: opacity 0.2s ease;
}

.month-navigator.nav-disabled {
  opacity: 0.5;
  pointer-events: none;
}

.nav-month-btn {
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-month-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-color: var(--border-light);
  transform: scale(1.05);
}

.nav-month-btn:disabled,
.nav-month-btn.btn-disabled {
  opacity: 0.25;
  cursor: not-allowed;
  pointer-events: none;
  transform: none !important;
}

.month-display-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.2rem 0.6rem;
}

.month-calendar-icon {
  color: #818cf8;
  display: flex;
  align-items: center;
}

.month-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.current-badge {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--income-text);
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 0.1rem 0.4rem;
  border-radius: 5px;
}

.btn-return-today {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-return-today:hover {
  background: rgba(99, 102, 241, 0.3);
  color: #ffffff;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

/* Toast */
.toast-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.15rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(8px);
}

.toast-success {
  background: rgba(16, 185, 129, 0.9);
  color: #ffffff;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.toast-error {
  background: rgba(244, 63, 94, 0.9);
  color: #ffffff;
  border: 1px solid rgba(244, 63, 94, 0.4);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.95);
}

@media (max-width: 1100px) {
  .dashboard-header {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  .header-left, .header-center, .header-actions {
    justify-content: center;
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
  .main-content {
    padding: 1rem 0.85rem 3rem;
  }
}
</style>