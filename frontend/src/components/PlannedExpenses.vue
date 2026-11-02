<template>
  <div class="fin-card planned-container" id="perencanaan">

    <div class="card-header">
      <div class="header-left">
        <div class="title-with-badge">
          <h3 class="card-title">{{ activeMode === 'finance' ? 'Rencana Pengeluaran Bulan Ini' : showTemplateView ? 'Template Pengeluaran' : 'Kebutuhan Bulanan' }}</h3>
          <span class="badge badge-planned">{{ activeMode === 'finance' ? plannedList.length : showTemplateView ? monthlyTemplates.length : monthlyNeeds.length }} {{ activeMode === 'finance' ? 'Rencana' : showTemplateView ? 'Template' : 'Kebutuhan' }}</span>
        </div>
        <p class="card-desc">
          {{ activeMode === 'finance' ? 'Catat rencana pengeluaran atau estimasi biaya tak terduga untuk menghitung sisa uang yang bisa ditabung secara akurat.' : showTemplateView ? 'Kelola template bernama yang berisi banyak kebutuhan untuk diterapkan ke bulan berjalan.' : 'Catat kebutuhan bulan ini dan kirim ke log transaksi saat benar-benar terjadi.' }}
        </p>
      </div>

      <div class="view-toggles">
        <button
          class="toggle-btn"
          :class="{ active: activeMode === 'finance' }"
          @click="setMode('finance')"
        >
          Rencana Pengeluaran
        </button>
        <button
          class="toggle-btn"
          :class="{ active: activeMode === 'wallet' }"
          @click="setMode('wallet')"
        >
          Kebutuhan Bulanan
        </button>
      </div>
    </div>

    <div class="card-header header-actions-row">
      <div class="header-actions-buttons">
        <button v-if="activeMode === 'finance'" @click="$emit('open-add-planned')" class="btn btn-primary btn-sm">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Tambah Kemungkinan
        </button>
        <div v-else-if="!showTemplateView" class="monthly-header-actions">
          <button class="btn btn-secondary btn-sm" :disabled="!isCurrentMonth" @click="openMonthlyForm">
            <span aria-hidden="true">+</span> Tambah Kebutuhan Bulanan
          </button>
          <button type="button" class="btn btn-primary btn-sm" @click="openTemplateView">
            Template
          </button>
        </div>
        <div v-else class="monthly-header-actions">
          <button type="button" class="btn btn-secondary btn-sm" @click="closeTemplateView">Kebutuhan Bulanan</button>
        </div>
      </div>
    </div>

    <div v-if="activeMode === 'finance'" class="impact-box finance-impact-box">
      <div class="impact-col">
        <span class="impact-label">Total Rencana Bulan Ini</span>
        <span class="impact-val text-planned">{{ formatRupiah(totalPlannedAmount) }}</span>
        <span class="impact-sub">Total seluruh kemungkinan rencana pengeluaran</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Perkiraan Total Sisa Uang Bulan Ini</span>
        <span class="impact-val text-savings">{{ formatRupiah(availableAfterExpensesAndNeeds - plannedImpactAmount) }}</span>
        <span class="impact-sub">Rencana non-tabungan dikurangi dari sisa dana</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Total Tabungan Akhir</span>
        <span class="impact-val text-income">{{ formatRupiah(totalSavingsAmount) }}</span>
        <span class="impact-sub">Saldo seluruh rekening - kebutuhan dan kemungkinan pengeluaran non-tabungan</span>
      </div>
    </div>

    <div v-else-if="!showTemplateView" class="impact-box monthly-summary">
      <div class="impact-col"><span class="impact-label">Total Semua Kebutuhan</span><span class="impact-val text-planned">{{ formatRupiah(monthlyTotal) }}</span><span class="impact-sub">Total pengeluaran x sisa transaksi</span></div>
      <div class="impact-divider"></div>
      <div class="impact-col"><span class="impact-label">Sudah Masuk Log</span><span class="impact-val text-income">{{ formatRupiah(monthlyCommitted) }}</span><span class="impact-sub">{{ monthlyCommittedCount }} transaksi</span></div>
      <div class="impact-divider"></div>
      <div class="impact-col"><span class="impact-label">Perkiraan Sisa Uang</span><span class="impact-val text-savings">{{ formatRupiah(availableAfterExpensesAndNeeds) }}</span><span class="impact-sub">Pemasukan - pengeluaran riil non-tabungan - kebutuhan non-tabungan</span></div>
    </div>

    <div v-if="activeMode === 'wallet' && !showTemplateView" class="wallet-chart">
      <div class="wallet-chart-header"><div><strong>Perkiraan Pengeluaran per Rekening</strong><small>Diambil dari sumber dana pada kebutuhan bulan ini.</small></div><span class="impact-val text-planned">{{ formatRupiah(walletSpendingTotal) }}</span></div>
      <div v-if="walletGroups.length" class="wallet-chart-list">
        <div v-for="wallet in walletGroups" :key="wallet.wallet" class="wallet-chart-row">
          <div class="wallet-chart-label"><span>{{ wallet.wallet }}</span><strong>{{ formatRupiah(wallet.amount) }}</strong></div>
          <div class="wallet-bar-track"><div class="wallet-bar" :style="{ width: `${wallet.percent}%` }"></div></div>
          <small>{{ wallet.percent }}% dari total pengeluaran</small>
        </div>
      </div>
      <p v-else class="template-empty">Belum ada sumber rekening untuk kebutuhan pengeluaran.</p>
    </div>

    <div v-if="activeMode === 'finance' && plannedList.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
      </div>
      <p class="empty-title">Belum ada kemungkinan pengeluaran</p>
      <p class="empty-sub">Tambahkan rencana pengeluaran seperti servis kendaraan, estimasi tagihan, atau belanja berkala.</p>
    </div>

    <div v-if="activeMode === 'finance' && plannedList.length" class="planned-grid">
      <div
        v-for="item in plannedList"
        :key="item.id"
        class="planned-item-card"
      >
        <div class="item-top">
          <div class="item-meta">
            <span class="item-cat">{{ item.category }}</span>
            <span class="prob-tag" :class="getProbClass(item.probability)">
              {{ item.probability || 100 }}% Kepastian
            </span>
          </div>
          <div class="item-actions">
            <button @click="$emit('edit-planned', item)" class="action-btn edit-btn" title="Edit rencana">Edit</button>
            <button
              @click="$emit('realize-planned', item)"
              class="action-btn check-btn"
              title="Realisasikan sebagai pengeluaran riil"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Realisasi
            </button>
            <button
              @click="$emit('delete-planned', item.id)"
              class="action-btn del-btn"
              title="Hapus rencana"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="item-title">{{ item.title }}</div>

        <div class="item-amount-row">
          <div>
            <span class="est-label">Estimasi:</span>
            <span class="est-amount">{{ formatRupiah(item.amount) }}</span>
          </div>
          <span class="item-date">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
              <line x1="16" x2="16" y1="2" y2="6"/>
              <line x1="8" x2="8" y1="2" y2="6"/>
              <line x1="3" x2="21" y1="10" y2="10"/>
            </svg>
            {{ formatDate(item.date) }}
          </span>
        </div>

        <div v-if="item.notes" class="item-notes">
          "{{ item.notes }}"
        </div>
      </div>
    </div>


    <div v-if="activeMode === 'wallet' && !showTemplateView && monthlyNeeds.length === 0" class="empty-state">
      <p class="empty-title">Belum ada template kebutuhan bulan ini</p>
      <p class="empty-sub">Tambahkan kebutuhan bulan aktif atau terapkan template reusable.</p>
    </div>

    <div v-if="activeMode === 'wallet' && !showTemplateView && monthlyNeeds.length" class="monthly-list">
      <div v-for="group in monthlyGroups" :key="group.category" class="monthly-group">
        <div class="group-heading"><strong>{{ group.category }}</strong><span>{{ formatRupiah(group.total) }}</span></div>
        <div v-for="item in group.items" :key="item.id" class="monthly-item-card">
          <div><strong>{{ item.title }}</strong><small>{{ formatTypeLabel(item.type) }} · {{ formatRupiah(item.amount) }} x {{ item.total_occurrences }} transaksi</small></div>
          <div class="monthly-item-total"><strong>{{ formatRupiah(Number(item.amount) * Number(item.remaining_occurrences)) }}</strong><small>{{ item.remaining_occurrences }} tersisa / {{ item.total_occurrences }} total</small></div>
          <button class="action-btn edit-btn" :disabled="!isCurrentMonth" @click="openMonthlyForm(item)">Edit</button>
          <button class="action-btn del-btn" :disabled="!isCurrentMonth" @click="$emit('delete-monthly', item.id)">Hapus</button>
          <input v-model.number="quantities[item.id]" class="quantity-input" type="number" min="1" :max="item.remaining_occurrences" :disabled="!item.remaining_occurrences" aria-label="Jumlah transaksi yang dilakukan">
          <button class="action-btn check-btn" :disabled="!isCurrentMonth || !item.remaining_occurrences" @click="$emit('realize-monthly', { item, quantity: quantities[item.id] || 1 })">+</button>

        </div>
      </div>
    </div>

    <div v-if="showMonthlyForm" class="modal-overlay">
      <div class="modal-dialog monthly-form">
        <div class="form-heading"><div><strong>{{ editingMonthly ? 'Edit Kebutuhan Bulanan' : 'Tambah Kebutuhan Bulanan' }}</strong><small>Data ini langsung masuk ke list bulan yang sedang berjalan.</small></div><button class="modal-close-btn" @click="closeMonthlyForm">×</button></div>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div class="monthly-form-grid">
          <label>Nama Pengeluaran<input v-model.trim="monthlyForm.title" class="form-input" placeholder="Contoh: Makan siang" required></label>
          <label>Harga Satuan<input :value="monthlyForm.amount" class="form-input" type="text" placeholder="Contoh: 25.000" required @input="formatRupiahInput($event, monthlyForm, 'amount')"></label>
          <label>Kategori<select v-model="monthlyForm.category" class="form-select"><option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option></select></label>
          <label v-if="editingMonthly">Sisa Berapa Kali Terjadi<input v-model.number="monthlyForm.remaining_occurrences" class="form-input" type="number" min="0" :max="monthlyForm.total_occurrences" placeholder="Contoh: 5" required><small>Sudah dilakukan: {{ Number(monthlyForm.total_occurrences || 0) - Number(monthlyForm.remaining_occurrences || 0) }} kali</small></label>
          <label v-else>Berapa Kali Terjadi<input v-model.number="monthlyForm.total_occurrences" class="form-input" type="number" min="1" placeholder="Contoh: 20" required></label>
          <label v-if="editingMonthly">Total Awal<input :value="monthlyForm.total_occurrences" class="form-input" type="number" disabled><small>Total awal tidak berubah saat sisa diedit.</small></label>
          <label>Sumber / Rekening<input v-model.trim="monthlyForm.wallet" class="form-input" placeholder="Contoh: BCA, Cash, Dana"></label>
        </div>
        <div class="form-actions"><button class="btn btn-secondary" @click="closeMonthlyForm">Batal</button><button class="btn btn-primary" @click="submitMonthlyForm">Simpan Kebutuhan</button></div>
      </div>
    </div>

    <div v-if="showTemplateForm" class="modal-overlay">
      <div class="modal-dialog template-form wide-modal">
        <div class="form-heading"><div><strong>{{ editingTemplate ? 'Edit Template' : 'Buat Template' }}</strong><small>{{ editingTemplate ? 'Perbarui item dan nama template yang sudah ada.' : 'Buat template baru dengan menambah item per kategori.' }}</small></div><button class="modal-close-btn" @click="closeTemplateForm">×</button></div>

        <span class="template-name-label">Nama Template</span>
        <input v-model.trim="templateForm.name" class="form-input" placeholder="Contoh: Kebutuhan Rumah" required>
        <p v-if="formError" class="form-error">{{ formError }}</p>

        <div class="template-summary">
          <div class="summary-row">
            <span>Total Item</span>
            <strong>{{ templateForm.items.length }}</strong>
          </div>
          <div class="summary-row">
            <span>Total Estimasi Pengeluaran</span>
            <strong class="text-planned">{{ formatRupiah(templateTotalExpense) }}</strong>
          </div>
          <div class="summary-row">
            <span>Estimasi Sisa Uang Bulan Ini</span>
            <strong :class="templateRemainingEstimate >= 0 ? 'text-savings' : 'text-expense'">{{ formatRupiah(templateRemainingEstimate) }}</strong>
          </div>
        </div>

        <div class="template-categories-layout">
          <div class="template-sidebar">
            <div class="sidebar-header">
              <h4>Kategori</h4>
              <span class="item-count">{{ totalTemplateItems }} item</span>
            </div>
            <div class="category-nav" v-for="cat in categories" :key="cat">
              <button
                type="button"
                class="category-nav-btn"
                :class="{ active: activeCategory === cat }"
                @click="activeCategory = cat"
              >
                <span class="cat-name">{{ cat }}</span>
                <span class="cat-count">{{ getCategoryItemCount(cat) }}</span>
              </button>
            </div>
          </div>

          <div class="template-main-content">
            <div class="panel-header">
              <h4>{{ activeCategory }}</h4>
              <span class="items-in-category">{{ getCategoryItems(activeCategory).length }} item</span>
            </div>

            <div class="category-items-panel">
              <button type="button" class="add-item-inline-btn" @click="addCategoryItem">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Tambah item ke {{ activeCategory }}
              </button>

              <div v-for="item in getCategoryItems(activeCategory)" :key="item.localId" class="template-item-card">
                <div class="item-header">
                  <span class="item-number">{{ getCategoryIndex(item) }}</span>
                  <button type="button" class="item-delete-btn" @click="removeTemplateItem(templateForm.items.indexOf(item))" title="Hapus item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>

                <div class="item-fields-grid">
                  <label class="field-wide">
                    <span>Nama kebutuhan</span>
                    <input v-model.trim="item.title" class="form-input" placeholder="Contoh: Makan siang" required>
                  </label>

                  <label>
                    <span>Harga Satuan</span>
                    <input :value="item.amount" class="form-input" type="text" placeholder="Contoh: 25.000" required @input="formatRupiahInput($event, item, 'amount')">
                  </label>

                  <label>
                    <span>Berapa Kali</span>
                    <input v-model.number="item.total_occurrences" class="form-input" type="number" min="1" placeholder="Contoh: 20" required>
                  </label>

                  <label class="field-wide">
                    <span>Sumber / Rekening</span>
                    <input v-model.trim="item.wallet" class="form-input" placeholder="Contoh: BCA, Cash, Dana">
                  </label>

                  <label v-if="item.type === 'transfer'" class="field-wide">
                    <span>Rekening Tujuan</span>
                    <input v-model.trim="item.transfer_to" class="form-input" placeholder="Contoh: Mandiri" required>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions"><button class="btn btn-secondary" @click="closeTemplateForm">Batal</button><button class="btn btn-primary" @click="submitTemplateForm">{{ editingTemplate ? 'Perbarui Template' : 'Simpan Template' }}</button></div>
      </div>
    </div>
  </div>

  <div v-if="showTemplateListModal" class="modal-overlay">
    <div class="modal-dialog template-form wide-modal template-list-modal">
      <div class="form-heading"><div><strong>Template Reusable</strong><small>Simpan sekali, terapkan ke bulan aktif kapan saja. Total Pemasukan bulan ini: <strong class="text-income">{{ formatRupiah(summary.total_income) }}</strong></small></div><button class="modal-close-btn" @click="closeTemplateView">×</button></div>

      <div class="template-header-actions">
        <span class="badge badge-planned">{{ monthlyTemplates.length }} Template</span>
        <button class="btn btn-primary btn-sm" @click="openTemplateForm()">+ Buat Template</button>
      </div>

      <div v-if="monthlyTemplates.length" class="template-grid">
        <div v-for="item in monthlyTemplates" :key="item.id" class="template-card">
          <div class="template-card-content">
            <strong class="template-card-title">{{ item.name }}</strong>
            <small class="template-card-meta">{{ item.items.length }} kebutuhan · {{ formatRupiah(templateTotal(item)) }}</small>
            <div class="template-card-estimate">
              <span class="est-label">Est. Sisa Uang:</span>
              <strong class="est-val" :class="templateRemaining(item) >= 0 ? 'text-savings' : 'text-expense'">
                {{ formatRupiah(templateRemaining(item)) }}
              </strong>
            </div>
          </div>
          <div class="template-actions">
            <button class="action-btn check-btn" :disabled="!isCurrentMonth" @click="$emit('apply-template', item.id)">Terapkan</button>
            <button class="action-btn edit-btn" @click="openTemplateForm(item)">Edit</button>
            <button class="action-btn edit-btn" @click="$emit('duplicate-template', item.id)" title="Duplikat template">Duplikat</button>
            <button class="action-btn del-btn" @click="$emit('delete-template', item.id)">Hapus</button>
          </div>
        </div>
      </div>
      <p v-else class="template-empty">Belum ada template reusable.</p>
    </div>
  </div>
</template>

<script>
import { formatRupiah, formatDate, formatRupiahInput } from '../utils/formatters.js';

export default {
  name: 'PlannedExpenses',
  props: {
    plannedList: {
      type: Array,
      default: () => []
    },
    summary: {
      type: Object,
      required: true
    },
    monthlyNeeds: {
      type: Array,
      default: () => []
    },
    monthlyTemplates: {
      type: Array,
      default: () => []
    },
    transactions: {
      type: Array,
      default: () => []
    },
    savingsWallets: {
      type: Array,
      default: () => []
    },
    isCurrentMonth: {
      type: Boolean,
      default: true
    }
  },
  emits: ['open-add-planned', 'edit-planned', 'delete-planned', 'realize-planned', 'create-monthly', 'edit-monthly', 'delete-monthly', 'realize-monthly', 'create-template', 'edit-template', 'delete-template', 'apply-template', 'duplicate-template'],
  data() {
    return {
      activeMode: 'finance', showMonthlyForm: false, showTemplateForm: false, showTemplateListModal: false, editingMonthly: null, editingTemplate: null, quantities: {},
      activeCategory: 'Makanan & Kebutuhan',
      categories: ['Makanan & Kebutuhan', 'Transportasi', 'Tagihan & Utilitas', 'Hiburan & Gaya Hidup', 'Belanja Online', 'Kesehatan', 'Pendidikan', 'Lain-lain'],
      incomeCategories: ['Gaji & Upah'],
      monthlyForm: { title: '', amount: '', category: 'Makanan & Kebutuhan', total_occurrences: 1, remaining_occurrences: 1, type: 'expense', wallet: '' },
      showTemplateView: false,
      formError: '',
      templateForm: { name: '', items: [] }
    };
  },
  computed: {
    totalTemplateItems() {
      return this.templateForm.items.length;
    },
    templateTotalExpense() {
      return this.templateForm.items
        .filter(item => item.type === 'expense')
        .reduce((total, item) => total + (typeof item.amount === 'string' ? Number(item.amount.replace(/[^\d]/g, '')) : Number(item.amount || 0)) * Number(item.total_occurrences || 0), 0);
    },
    templateTotalIncome() {
      return this.templateForm.items
        .filter(item => item.type === 'income')
        .reduce((total, item) => total + (typeof item.amount === 'string' ? Number(item.amount.replace(/[^\d]/g, '')) : Number(item.amount || 0)) * Number(item.total_occurrences || 0), 0);
    },
    templateRemainingEstimate() {
      return Number(this.summary.total_income || 0) - this.templateTotalExpense;
    },
    totalPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => acc + (Number(cur.amount) || 0), 0);
    },
    plannedImpactAmount() {
      return this.plannedList.reduce((total, item) => {
        return this.isSavingsExpense(item) ? total : total + (Number(item.amount) || 0);
      }, 0);
    },
    weightedPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => {
        const prob = (Number(cur.probability) || 100) / 100;
        return acc + ((Number(cur.amount) || 0) * prob);
      }, 0);
    },
    monthlyTotal() {
      return this.monthlyNeeds.reduce((total, item) => {
        if (item.type !== 'expense' || this.isSavingsExpense(item)) return total;
        return total + Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
      }, 0);
    },
    monthlyCommitted() {
      return this.monthlyNeeds.reduce((total, item) => total + Number(item.amount || 0) * (Number(item.total_occurrences || 0) - Number(item.remaining_occurrences || 0)), 0);
    },
    monthlyCommittedCount() {
      return this.monthlyNeeds.reduce((total, item) => total + Number(item.total_occurrences || 0) - Number(item.remaining_occurrences || 0), 0);
    },
    monthlyNetImpact() {
      return this.monthlyNeeds.reduce((total, item) => {
        const amount = Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
        if (item.type === 'income') return total + amount;
        if (item.type === 'expense') return total - amount;
        return total;
      }, 0);
    },
    remainingAfterNeeds() {
      return this.availableAfterExpensesAndNeeds;
    },
    availableAfterExpensesAndNeeds() {
      const actualExpenses = this.transactions.reduce((total, item) => {
        if (item.type !== 'expense' || this.isSavingsExpense(item)) return total;
        return total + Number(item.amount || 0);
      }, 0);
      return Number(this.summary.total_income || 0) - actualExpenses - this.monthlyTotal;
    },
    totalSavingsAmount() {
      const accountBalances = Number(this.summary.sisa_tabungan || 0);
      return accountBalances - this.monthlyTotal - this.plannedImpactAmount;
    },
    walletSpendingTotal() {
      return this.monthlyNeeds.reduce((total, item) => {
        if (item.type !== 'expense') return total;
        return total + Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
      }, 0);
    },
    walletGroups() {
      const groups = this.monthlyNeeds.reduce((result, item) => {
        if (item.type !== 'expense') return result;
        const wallet = String(item.wallet || '').trim() || 'Tanpa Rekening';
        result[wallet] = (result[wallet] || 0) + Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
        return result;
      }, {});
      const total = this.walletSpendingTotal;
      return Object.entries(groups)
        .map(([wallet, amount]) => ({ wallet, amount, percent: total ? Math.round(amount / total * 100) : 0 }))
        .sort((first, second) => second.amount - first.amount);
    },
    monthlyGroups() {
      return Object.values(this.monthlyNeeds.reduce((groups, item) => {
        const category = item.category || 'Lain-lain';
        if (!groups[category]) groups[category] = { category, total: 0, items: [] };
        groups[category].items.push(item);
        groups[category].total += Number(item.amount || 0) * Number(item.remaining_occurrences || 0);
        return groups;
      }, {}));
    }
  },
  methods: {
    formatRupiah,
    formatDate,
    formatRupiahInput,
    isSavingsExpense(item) {
      if (item.savings_status === 'savings') return true;
      const wallet = String(item.wallet || '').trim();
      return Boolean(wallet) && this.savingsWallets.some(
        savingsWallet => String(savingsWallet).trim() === wallet
      );
    },
    getCategories(type) {
      if (type === 'income') return this.incomeCategories;
      if (type === 'transfer') return ['Pindah Dana'];
      return this.categories;
    },
    syncTemplateCategory(item) {
      const validCategories = this.getCategories(item.type);
      if (!validCategories.includes(item.category)) item.category = validCategories[0];
    },
    newTemplateItem() {
      return { localId: `item-${Date.now()}-${Math.random()}`, title: '', amount: '', category: this.categories[0], total_occurrences: 1, type: 'expense', wallet: '', transfer_to: '' };
    },
    formatTypeLabel(type) {
      if (type === 'income') return 'Pemasukan';
      if (type === 'transfer') return 'Transfer';
      return 'Pengeluaran';
    },
    templateTotal(template) {
      return (template.items || []).reduce((total, item) => {
        if (item.type && item.type !== 'expense') return total;
        return total + Number(item.amount || 0) * Number(item.total_occurrences || 0);
      }, 0);
    },
    calculateTemplateIncome(template) {
      return (template.items || []).reduce((total, item) => {
        if (item.type === 'income') return total + Number(item.amount || 0) * Number(item.total_occurrences || 0);
        return total;
      }, 0);
    },
    templateRemaining(template) {
      const totalIncome = Number(this.summary?.total_income || 0);
      return totalIncome + this.calculateTemplateIncome(template) - this.templateTotal(template);
    },
    getCategoryItems(category) {
      return this.templateForm.items.filter(item => item.category === category);
    },
    getCategoryItemCount(category) {
      return this.getCategoryItems(category).length;
    },
    getCategoryIndex(item) {
      const categoryItems = this.getCategoryItems(item.category);
      return categoryItems.indexOf(item) + 1;
    },
    addCategoryItem() {
      const newItem = this.newTemplateItem();
      newItem.category = this.activeCategory;
      this.templateForm.items.push(newItem);
    },
    getProbClass(prob) {
      if (prob >= 90) return 'prob-high';
      if (prob >= 60) return 'prob-med';
      return 'prob-low';
    },
    setMode(mode) {
      this.activeMode = mode;
      if (mode === 'finance') this.closeMonthlyForm();
    },
    openTemplateView() {
      this.closeMonthlyForm();
      this.showTemplateListModal = true;
    },
    closeTemplateView() {
      this.closeTemplateForm();
      this.showTemplateListModal = false;
    },
    openMonthlyForm(item = null) {
      this.closeTemplateForm();
      this.closeTemplateView();
      this.formError = '';
      this.editingMonthly = item;
      const base = item
        ? { type: 'expense', wallet: '', ...item }
        : { title: '', amount: '', category: this.categories[0], total_occurrences: 1, remaining_occurrences: 1, type: 'expense', wallet: '' };
      this.monthlyForm = { ...base, type: 'expense' };
      if (item && base.amount != null && base.amount !== '') {
        this.monthlyForm.amount = new Intl.NumberFormat('id-ID').format(Number(base.amount));
      }
      this.monthlyForm.category = this.categories.includes(this.monthlyForm.category)
        ? this.monthlyForm.category
        : this.categories[0];
      this.showMonthlyForm = true;
    },
    closeMonthlyForm() {
      this.showMonthlyForm = false;
      this.editingMonthly = null;
    },
    openTemplateForm(item = null) {
      this.closeMonthlyForm();
      this.closeTemplateView();
      this.formError = '';
      this.editingTemplate = item;
      this.activeCategory = 'Makanan & Kebutuhan';
      this.templateForm = item
        ? { name: item.name, items: item.items.map(templateItem => {
            const t = { type: 'expense', wallet: '', transfer_to: '', ...templateItem, localId: templateItem.id };
            if (t.amount != null && t.amount !== '') {
              t.amount = new Intl.NumberFormat('id-ID').format(Number(t.amount));
            }
            return t;
          }) }
        : { name: '', items: [] };
      this.templateForm.items.forEach(templateItem => this.syncTemplateCategory(templateItem));
      this.showTemplateForm = true;
    },
    closeTemplateForm() {
      this.showTemplateForm = false;
      this.editingTemplate = null;
      // Reopen template list modal if it was open
      if (!this.showTemplateListModal) {
        this.showTemplateListModal = true;
      }
    },
    submitMonthlyForm() {
      const remaining = Number(this.monthlyForm.remaining_occurrences);
      const total = Number(this.monthlyForm.total_occurrences);
      const amountValue = typeof this.monthlyForm.amount === 'string'
        ? Number(this.monthlyForm.amount.replace(/[^\d]/g, ''))
        : Number(this.monthlyForm.amount);
      if (!this.monthlyForm.title || amountValue <= 0 || total <= 0 || (this.editingMonthly && (remaining < 0 || remaining > total))) {
        this.formError = 'Nama, harga, dan jumlah transaksi wajib valid.';
        return;
      }
      if (!this.validateTransactionFields(this.monthlyForm)) return;
      const payload = { ...this.monthlyForm, amount: amountValue, remaining_occurrences: this.editingMonthly ? this.monthlyForm.remaining_occurrences : this.monthlyForm.total_occurrences };
      this.$emit(this.editingMonthly ? 'edit-monthly' : 'create-monthly', payload);
      this.closeMonthlyForm();
    },
    submitTemplateForm() {
      const validItems = this.templateForm.items.every(item => {
        const amountVal = typeof item.amount === 'string'
          ? Number(item.amount.replace(/[^\d]/g, ''))
          : Number(item.amount);
        return item.title && amountVal > 0 && Number(item.total_occurrences) > 0;
      });
      if (!this.templateForm.name || !validItems) {
        this.formError = 'Nama template, nama kebutuhan, harga, dan jumlah transaksi wajib diisi.';
        return;
      }
      if (!this.templateForm.items.every(item => this.validateTransactionFields(item))) return;
      this.$emit(this.editingTemplate ? 'edit-template' : 'create-template', {
        name: this.templateForm.name,
        items: this.templateForm.items.map(({ localId, ...item }) => ({
          ...item,
          amount: typeof item.amount === 'string'
            ? Number(item.amount.replace(/[^\d]/g, ''))
            : Number(item.amount)
        })),
        ...(this.editingTemplate ? { id: this.editingTemplate.id } : {})
      });
      this.closeTemplateForm();
    },
    validateTransactionFields(item) {
      if (!['income', 'expense', 'transfer'].includes(item.type)) {
        this.formError = 'Pilih jenis transaksi yang valid.';
        return false;
      }
      if (item.type === 'transfer' && (!String(item.wallet || '').trim() || !String(item.transfer_to || '').trim() || String(item.wallet).trim() === String(item.transfer_to).trim())) {
        this.formError = 'Transfer memerlukan rekening asal dan tujuan yang berbeda.';
        return false;
      }
      return true;
    },
    addTemplateItem() {
      this.templateForm.items.push(this.newTemplateItem());
    },
    removeTemplateItem(index) {
      this.templateForm.items.splice(index, 1);
    }
  }
};
</script>

<style scoped>
.planned-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  margin-top: 0.25rem;
}

.impact-box {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.1rem 1.5rem;
  gap: 1.25rem;
}

.finance-impact-box {
  grid-template-columns: 1fr auto 1fr auto 1fr;
}

.impact-col {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.impact-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  font-weight: 600;
}

.impact-val {
  font-size: 1.25rem;
  font-weight: 800;
  font-feature-settings: 'tnum' on;
}

.impact-sub {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.wallet-chart {
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
}

.wallet-chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.wallet-chart-header small {
  display: block;
  color: var(--text-dim);
  font-size: 0.72rem;
  margin-top: 0.25rem;
}

.wallet-chart-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1rem;
}

.wallet-chart-label {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.wallet-chart-label strong {
  color: var(--text-main);
}

.wallet-bar-track {
  height: 8px;
  margin-top: 0.35rem;
  background: var(--bg-input);
  border-radius: 999px;
  overflow: hidden;
}

.wallet-bar {
  height: 100%;
  min-width: 2px;
  background: linear-gradient(90deg, var(--primary), #22d3ee);
  border-radius: inherit;
}

.wallet-chart-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.wallet-chart-row small {
  display: block;
  color: var(--text-dim);
  font-size: 0.68rem;
  margin-top: 0.25rem;
}

.impact-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

.text-planned {
  color: var(--planned-text);
}
.text-savings {
  color: var(--savings-text);
}
.text-income {
  color: var(--income-text);
}
.text-expense {
  color: var(--expense-text, #f43f5e);
}

.empty-state {
  padding: 2.5rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed var(--border-color);
  border-radius: 14px;
}

.empty-icon {
  color: var(--text-dim);
  margin-bottom: 0.75rem;
}

.empty-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-main);
}

.empty-sub {
  font-size: 0.8rem;
  color: var(--text-dim);
  max-width: 420px;
  margin: 0.25rem auto 0;
}

.planned-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.planned-item-card {
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: all 0.2s ease;
}

.planned-item-card:hover {
  border-color: var(--border-light);
  transform: translateY(-2px);
}

.item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-cat {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.prob-tag {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.prob-high {
  background: rgba(244, 63, 94, 0.15);
  color: var(--expense-text);
}
.prob-med {
  background: rgba(245, 158, 11, 0.15);
  color: var(--planned-text);
}
.prob-low {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-muted);
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.edit-btn {
  background: rgba(56, 189, 248, 0.14);
  color: #38bdf8;
}

.edit-btn:hover {
  background: #0284c7;
  color: #fff;
}

.check-btn {
  background: rgba(16, 185, 129, 0.15);
  color: var(--income-text);
}
.check-btn:hover {
  background: var(--income);
  color: #fff;
}

.del-btn {
  background: rgba(244, 63, 94, 0.1);
  color: var(--expense-text);
  padding: 0.3rem;
}
.del-btn:hover {
  background: rgba(244, 63, 94, 0.25);
}

.item-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff;
}

.item-amount-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.est-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-right: 0.35rem;
}

.est-amount {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--planned-text);
}

.item-date {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: var(--text-dim);
}

.item-notes {
  font-size: 0.75rem;
  color: var(--text-dim);
  font-style: italic;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.4rem 0.65rem;
  border-radius: 6px;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

.template-form {
  transform: translateY(-2rem);
}

.modal-dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.25s ease;
}

.wide-modal {
  max-width: 1000px;
}

.form-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
}

.form-heading strong {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}

.form-heading small {
  color: var(--text-dim);
  font-size: 0.75rem;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  padding: 0.25rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.modal-close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.form-error {
  margin: 0.75rem 1.25rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid rgba(244, 63, 94, 0.35);
  border-radius: 8px;
  background: rgba(244, 63, 94, 0.1);
  color: var(--expense-text);
  font-size: 0.78rem;
}

.monthly-form,
.template-form {
  padding: 1.25rem;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.view-toggles {
  display: flex;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  padding: 0.2rem;
  border-radius: 10px;
  gap: 0;
}

.header-actions-row {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  margin-top: 0.5rem;
}

.header-actions-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.monthly-header-actions,
.template-actions,
.form-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.template-panel,
.monthly-form {
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
}

.template-panel-header,
.form-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.template-header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.template-panel-header small,
.form-heading small,
.template-card small,
.monthly-item-card small {
  display: block;
  color: var(--text-dim);
  font-size: 0.72rem;
  margin-top: 0.25rem;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
  margin-top: 0.85rem;
}

.template-card,
.monthly-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 9px;
  padding: 0.75rem;
}

.template-card-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.template-card-title {
  color: #ffffff;
  font-size: 0.95rem;
}

.template-card-meta {
  color: var(--text-dim);
  font-size: 0.72rem;
}

.template-card-estimate {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.35rem;
  font-size: 0.78rem;
  flex-wrap: wrap;
}

.template-card-estimate .est-label {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.template-card-estimate .est-val {
  font-size: 0.82rem;
  font-weight: 700;
}

.template-empty {
  color: var(--text-dim);
  font-size: 0.8rem;
  margin: 0.85rem 0 0;
}

.monthly-group {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: 1rem;
}

.group-heading {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.monthly-item-total {
  text-align: right;
  margin-left: auto;
}

.quantity-input {
  width: 4.5rem;
  padding: 0.45rem;
  color: #fff;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 7px;
}

.monthly-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.template-name-label {
  display: block;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 0.5rem;
  margin-bottom: 0.35rem;
  padding-left: 1.25rem;
}

.template-item-editor {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 45vh;
  overflow-y: auto;
}

.template-item-row {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.template-item-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-main);
  font-size: 0.85rem;
}

.template-item-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.template-item-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.template-field-wide {
  grid-column: 1 / -1;
}

.add-item-btn {
  align-self: flex-start;
}

.monthly-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.monthly-type-toggle {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.4rem;
  background: var(--bg-input);
  padding: 0.3rem;
  border-radius: 9px;
}

.monthly-type-toggle button {
  border: none;
  border-radius: 7px;
  padding: 0.55rem 0.4rem;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.monthly-type-toggle button.active {
  background: var(--primary);
  color: #fff;
}

.monthly-form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.form-actions {
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.form-error {
  margin: 0;
  padding: 0.65rem 0.8rem;
  border: 1px solid rgba(244, 63, 94, 0.35);
  border-radius: 8px;
  background: rgba(244, 63, 94, 0.1);
  color: var(--expense-text);
  font-size: 0.78rem;
}


@media (max-width: 800px) {
  .impact-box {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .impact-divider {
    display: none;
  }
  .monthly-form-grid {
    grid-template-columns: 1fr;
  }
  .monthly-item-card {
    align-items: flex-start;
    flex-wrap: wrap;
  }
  .template-item-row {
    padding: 0.8rem;
  }
  .template-item-grid {
    grid-template-columns: 1fr;
  }
  .template-field-wide {
    grid-column: auto;
  }
}

/* Wide Modal for Template Form */
.wide-modal {
  max-width: 1000px;
  width: 95vw;
}

/* Template List Modal */
.template-list-modal {
  max-height: 90vh;
  overflow-y: auto;
}

.template-list-modal .form-heading {
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.template-list-modal .template-header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  flex-wrap: wrap;
  padding: 0 1.25rem;
  margin-bottom: 0.5rem;
}

.template-list-modal .template-grid {
  padding: 0 1.25rem 1.25rem;
  max-height: 60vh;
  overflow-y: auto;
}

.template-list-modal .template-card {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 9px;
  padding: 0.75rem;
}

.template-list-modal .template-empty {
  padding: 2rem;
  text-align: center;
  color: var(--text-dim);
}

.template-list-modal .template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

/* Template Categories Layout */
.template-categories-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1.5rem;
  margin-top: 1rem;
  min-height: 500px;
}

.template-sidebar {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: fit-content;
  max-height: 600px;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
}

.item-count {
  font-size: 0.7rem;
  color: var(--text-dim);
  background: rgba(255,255,255,0.05);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.category-nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.category-nav-btn {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.75rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  width: 100%;
}

.category-nav-btn:hover {
  background: rgba(255,255,255,0.05);
  border-color: var(--border-color);
  color: var(--text-main);
}

.category-nav-btn.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
}

.cat-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-count {
  font-size: 0.65rem;
  color: var(--text-dim);
  background: rgba(255,255,255,0.05);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
}

.template-main-content {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.25rem;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  padding-bottom: 100px;
}

.empty-template-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 0.75rem;
  color: var(--text-dim);
  text-align: left;
  padding: 2rem;
  width: 100%;
}

.empty-template-state svg {
  color: var(--text-dim);
}

.empty-template-state p {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-muted);
}

.empty-template-state small {
  font-size: 0.75rem;
}

.category-items-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.category-items-panel .empty-template-state {
  grid-column: 1 / -1;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.75rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h4 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.items-in-category {
  font-size: 0.7rem;
  color: var(--text-dim);
  background: rgba(255,255,255,0.05);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  white-space: nowrap;
}

.template-item-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 280px;
  box-sizing: border-box;
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-shrink: 0;
}

.item-number {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-dim);
  background: rgba(255,255,255,0.05);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  flex-shrink: 0;
}

.item-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.item-delete-btn:hover {
  background: rgba(244, 63, 94, 0.15);
  color: var(--expense-text);
}

.item-fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.6rem;
  flex: 1;
}

.item-fields-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 600;
  min-width: 0;
}

.item-fields-grid label.field-wide {
  grid-column: 1 / -1;
}

.item-fields-grid input,
.item-fields-grid select {
  padding: 0.45rem 0.6rem;
  font-size: 0.78rem;
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
}

.add-item-inline-btn {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0;
  padding: 0.7rem 1.5rem;
  background: rgba(56, 189, 248, 0.1);
  border: 1px dashed rgba(56, 189, 248, 0.3);
  border-radius: 8px;
  color: #38bdf8;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
}

.add-item-inline-btn:hover {
  background: rgba(56, 189, 248, 0.2);
  border-color: rgba(56, 189, 248, 0.5);
}

/* Template Summary */
.template-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  margin-top: 1rem;
}

.summary-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  text-align: center;
}

.summary-row span {
  font-size: 0.7rem;
  color: var(--text-dim);
  font-weight: 600;
}

.summary-row strong {
  font-size: 0.95rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .category-items-panel {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .category-items-panel {
    grid-template-columns: repeat(2, 1fr);
  }
  .item-fields-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .template-categories-layout {
    grid-template-columns: 1fr;
  }
  .template-sidebar {
    max-height: 200px;
    order: 2;
  }
  .template-main-content {
    order: 1;
  }
  .item-fields-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .item-fields-grid label.field-wide {
    grid-column: 1 / -1;
  }
  .template-summary {
    grid-template-columns: repeat(3, 1fr);
  }
  .category-items-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .item-fields-grid {
    grid-template-columns: 1fr;
  }
  .template-summary {
    grid-template-columns: 1fr;
  }
}
</style>
