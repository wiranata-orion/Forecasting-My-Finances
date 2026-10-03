<template>
  <div class="fin-card planned-container" id="perencanaan">

    <div class="card-header">
      <div>
        <div class="title-with-badge">
          <h3 class="card-title">{{ activeMode === 'finance' ? 'Rencana Pengeluaran Bulan Ini' : showTemplateView ? 'Template Pengeluaran' : 'Kebutuhan Bulanan' }}</h3>
          <span class="badge badge-planned">{{ activeMode === 'finance' ? plannedList.length : showTemplateView ? monthlyTemplates.length : monthlyNeeds.length }} {{ activeMode === 'finance' ? 'Rencana' : showTemplateView ? 'Template' : 'Kebutuhan' }}</span>
        </div>
        <p class="card-desc">
          {{ activeMode === 'finance' ? 'Catat rencana pengeluaran atau estimasi biaya tak terduga untuk menghitung sisa uang yang bisa ditabung secara akurat.' : showTemplateView ? 'Kelola template bernama yang berisi banyak kebutuhan untuk diterapkan ke bulan berjalan.' : 'Catat kebutuhan bulan ini dan kirim ke log transaksi saat benar-benar terjadi.' }}
        </p>
      </div>

      <button v-if="activeMode === 'finance'" @click="$emit('open-add-planned')" class="btn btn-primary btn-sm">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Tambah Kemungkinan
      </button>
      <div v-else-if="!showTemplateView" class="monthly-header-actions">
        <button class="btn btn-secondary btn-sm" :disabled="!isCurrentMonth" @click="openMonthlyForm()">
          <span aria-hidden="true">+</span> Tambah Kebutuhan Bulanan
        </button>
        <button class="btn btn-primary btn-sm" @click="showTemplateView = true">
          Template
        </button>
      </div>
      <div v-else class="monthly-header-actions">
        <button class="btn btn-secondary btn-sm" @click="showTemplateView = false">Kebutuhan Bulanan</button>
      </div>
    </div>
    <div class="card-header">
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

    <div v-if="activeMode === 'finance'" class="impact-box finance-impact-box">
      <div class="impact-col">
        <span class="impact-label">Total Rencana Bulan Ini</span>
        <span class="impact-val text-planned">{{ formatRupiah(totalPlannedAmount) }}</span>
        <span class="impact-sub">Total seluruh kemungkinan rencana pengeluaran</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Perkiraan Total Sisa Uang Bulan Ini</span>
        <span class="impact-val text-savings">{{ formatRupiah(availableAfterExpensesAndNeeds - totalPlannedAmount) }}</span>
        <span class="impact-sub">Total rencana dikurangi dari sisa dana</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Total Tabungan Akhir</span>
        <span class="impact-val text-income">{{ formatRupiah(totalSavingsAmount) }}</span>
        <span class="impact-sub">Saldo seluruh rekening - semua kebutuhan dan kemungkinan pengeluaran</span>
      </div>
    </div>

    <div v-else-if="!showTemplateView" class="impact-box monthly-summary">
      <div class="impact-col"><span class="impact-label">Total Semua Kebutuhan</span><span class="impact-val text-planned">{{ formatRupiah(monthlyTotal) }}</span><span class="impact-sub">Total pengeluaran x sisa transaksi</span></div>
      <div class="impact-divider"></div>
      <div class="impact-col"><span class="impact-label">Sudah Masuk Log</span><span class="impact-val text-income">{{ formatRupiah(monthlyCommitted) }}</span><span class="impact-sub">{{ monthlyCommittedCount }} transaksi</span></div>
      <div class="impact-divider"></div>
      <div class="impact-col"><span class="impact-label">Perkiraan Sisa Uang</span><span class="impact-val text-savings">{{ formatRupiah(availableAfterExpensesAndNeeds) }}</span><span class="impact-sub">Pemasukan - pengeluaran riil - semua kebutuhan</span></div>
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

    <div v-if="activeMode === 'wallet' && showTemplateView" class="template-panel">
      <div class="template-panel-header">
        <div><strong>Template Reusable</strong><small>Simpan sekali, terapkan ke bulan aktif kapan saja.</small></div>
        <div class="template-header-actions"><span class="badge badge-planned">{{ monthlyTemplates.length }} Template</span><button class="btn btn-primary btn-sm" @click="openTemplateForm()">+ Buat Template</button></div>
      </div>
      <div v-if="monthlyTemplates.length" class="template-grid">
        <div v-for="item in monthlyTemplates" :key="item.id" class="template-card">
          <div><strong>{{ item.name }}</strong><small>{{ item.items.length }} kebutuhan · {{ formatRupiah(templateTotal(item)) }}</small></div>
          <div class="template-actions">
            <button class="action-btn check-btn" :disabled="!isCurrentMonth" @click="$emit('apply-template', item.id)">Terapkan</button>
            <button class="action-btn edit-btn" @click="openTemplateForm(item)">Edit</button>
            <button class="action-btn del-btn" @click="$emit('delete-template', item.id)">Hapus</button>
          </div>
        </div>
      </div>
      <p v-else class="template-empty">Belum ada template reusable.</p>
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
        <div class="monthly-type-toggle">
          <button type="button" :class="{ active: monthlyForm.type === 'income' }" @click="setMonthlyType('income')">Pemasukan (+)</button>
          <button type="button" :class="{ active: monthlyForm.type === 'expense' }" @click="setMonthlyType('expense')">Pengeluaran (-)</button>
          <button type="button" :class="{ active: monthlyForm.type === 'transfer' }" @click="setMonthlyType('transfer')">Transfer</button>
        </div>
        <div class="monthly-form-grid">
          <label>Nama Pengeluaran<input v-model.trim="monthlyForm.title" class="form-input" placeholder="Contoh: Makan siang" required></label>
          <label>Harga Satuan<input v-model.number="monthlyForm.amount" class="form-input" type="number" min="1" placeholder="Contoh: 25000" required></label>
          <label>Kategori<select v-model="monthlyForm.category" class="form-select"><option v-for="cat in getCategories(monthlyForm.type)" :key="cat" :value="cat">{{ cat }}</option></select></label>
          <label v-if="editingMonthly">Sisa Berapa Kali Terjadi<input v-model.number="monthlyForm.remaining_occurrences" class="form-input" type="number" min="0" :max="monthlyForm.total_occurrences" placeholder="Contoh: 5" required><small>Sudah dilakukan: {{ Number(monthlyForm.total_occurrences || 0) - Number(monthlyForm.remaining_occurrences || 0) }} kali</small></label>
          <label v-else>Berapa Kali Terjadi<input v-model.number="monthlyForm.total_occurrences" class="form-input" type="number" min="1" placeholder="Contoh: 20" required></label>
          <label v-if="editingMonthly">Total Awal<input :value="monthlyForm.total_occurrences" class="form-input" type="number" disabled><small>Total awal tidak berubah saat sisa diedit.</small></label>
          <label>Sumber / Rekening<input v-model.trim="monthlyForm.wallet" class="form-input" placeholder="Contoh: BCA, Cash, Dana"></label>
          <label v-if="monthlyForm.type === 'transfer'">Rekening Tujuan<input v-model.trim="monthlyForm.transfer_to" class="form-input" placeholder="Contoh: Mandiri" required></label>
        </div>
        <div class="form-actions"><button class="btn btn-secondary" @click="closeMonthlyForm">Batal</button><button class="btn btn-primary" @click="submitMonthlyForm">Simpan Kebutuhan</button></div>
      </div>
    </div>

    <div v-if="showTemplateForm" class="modal-overlay">
      <div class="modal-dialog monthly-form template-form">
        <div class="form-heading"><div><strong>{{ editingTemplate ? 'Edit Template' : 'Buat Template' }}</strong><small>Satu template dapat berisi banyak kebutuhan dan tidak masuk bulan aktif sebelum diterapkan.</small></div><button class="modal-close-btn" @click="closeTemplateForm">×</button></div>
        <label class="template-name-field">Nama Template<input v-model.trim="templateForm.name" class="form-input" placeholder="Contoh: Kebutuhan Rumah" required></label>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <div class="template-item-editor">
          <div v-for="(item, index) in templateForm.items" :key="item.localId" class="template-item-row">
            <div class="template-item-heading"><strong>Item {{ index + 1 }}</strong><button v-if="templateForm.items.length > 1" class="action-btn del-btn" @click="removeTemplateItem(index)">Hapus item</button></div>
            <div class="template-item-grid">
              <label class="template-field-wide">Nama kebutuhan<input v-model.trim="item.title" class="form-input" placeholder="Contoh: Makan siang" required></label>
              <label>Jenis transaksi<select v-model="item.type" class="form-select" @change="syncTemplateCategory(item)"><option value="expense">Pengeluaran</option><option value="income">Pemasukan</option><option value="transfer">Transfer</option></select></label>
              <label>Kategori<select v-model="item.category" class="form-select"><option v-for="cat in getCategories(item.type)" :key="cat" :value="cat">{{ cat }}</option></select></label>
              <label>Harga Satuan<input v-model.number="item.amount" class="form-input" type="number" min="1" placeholder="Contoh: 25000" required></label>
              <label>Berapa Kali Terjadi<input v-model.number="item.total_occurrences" class="form-input" type="number" min="1" placeholder="Contoh: 20" required></label>
              <label class="template-field-wide">Sumber / Rekening<input v-model.trim="item.wallet" class="form-input" placeholder="Contoh: BCA, Cash, Dana"></label>
              <label v-if="item.type === 'transfer'" class="template-field-wide">Rekening Tujuan<input v-model.trim="item.transfer_to" class="form-input" placeholder="Contoh: Mandiri" required></label>
            </div>
          </div>
        </div>
        <button class="btn btn-secondary add-item-btn" @click="addTemplateItem">+ Tambah Item</button>
        <div class="form-actions"><button class="btn btn-secondary" @click="closeTemplateForm">Batal</button><button class="btn btn-primary" @click="submitTemplateForm">Simpan Template</button></div>
      </div>
    </div>
  </div>
</template>

<script>
import { formatRupiah, formatDate } from '../utils/formatters.js';

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
  emits: ['open-add-planned', 'edit-planned', 'delete-planned', 'realize-planned', 'create-monthly', 'edit-monthly', 'delete-monthly', 'realize-monthly', 'create-template', 'edit-template', 'delete-template', 'apply-template'],
  data() {
    return {
      activeMode: 'finance', showMonthlyForm: false, showTemplateForm: false, editingMonthly: null, editingTemplate: null, quantities: {},
      categories: ['Makanan & Kebutuhan', 'Transportasi', 'Tagihan & Utilitas', 'Hiburan & Gaya Hidup', 'Belanja Online', 'Kesehatan', 'Pendidikan', 'Lain-lain'],
      incomeCategories: ['Gaji & Upah'],
      monthlyForm: { title: '', amount: null, category: 'Makanan & Kebutuhan', total_occurrences: 1, remaining_occurrences: 1, type: 'expense', wallet: '', transfer_to: '' },
      showTemplateView: false,
      formError: '',
      templateForm: { name: '', items: [{ localId: 'initial-item', title: '', amount: null, category: 'Makanan & Kebutuhan', total_occurrences: 1, type: 'expense', wallet: '', transfer_to: '' }] }
    };
  },
  computed: {
    totalPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => acc + (Number(cur.amount) || 0), 0);
    },
    weightedPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => {
        const prob = (Number(cur.probability) || 100) / 100;
        return acc + ((Number(cur.amount) || 0) * prob);
      }, 0);
    },
    monthlyTotal() {
      return this.monthlyNeeds.reduce((total, item) => {
        if (item.type !== 'expense') return total;
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
      return Number(this.summary.total_income || 0) - Number(this.summary.total_expense || 0) - this.monthlyTotal;
    },
    totalSavingsAmount() {
      const accountBalances = Number(this.summary.sisa_tabungan || 0);
      return accountBalances - this.monthlyTotal - this.totalPlannedAmount;
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
    getCategories(type) {
      if (type === 'income') return this.incomeCategories;
      if (type === 'transfer') return ['Pindah Dana'];
      return this.categories;
    },
    setMonthlyType(type) {
      this.monthlyForm.type = type;
      this.monthlyForm.category = this.getCategories(type)[0];
    },
    syncTemplateCategory(item) {
      const validCategories = this.getCategories(item.type);
      if (!validCategories.includes(item.category)) item.category = validCategories[0];
    },
    newTemplateItem() {
      return { localId: `item-${Date.now()}-${Math.random()}`, title: '', amount: null, category: this.categories[0], total_occurrences: 1, type: 'expense', wallet: '', transfer_to: '' };
    },
    formatTypeLabel(type) {
      if (type === 'income') return 'Pemasukan';
      if (type === 'transfer') return 'Transfer';
      return 'Pengeluaran';
    },
    templateTotal(template) {
      return (template.items || []).reduce((total, item) => total + Number(item.amount || 0) * Number(item.total_occurrences || 0), 0);
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
    openMonthlyForm(item = null) {
      this.closeTemplateForm();
      this.formError = '';
      this.editingMonthly = item;
      this.monthlyForm = item ? { type: 'expense', wallet: '', transfer_to: '', ...item } : { title: '', amount: null, category: this.categories[0], total_occurrences: 1, remaining_occurrences: 1, type: 'expense', wallet: '', transfer_to: '' };
      this.monthlyForm.category = this.getCategories(this.monthlyForm.type).includes(this.monthlyForm.category)
        ? this.monthlyForm.category
        : this.getCategories(this.monthlyForm.type)[0];
      this.showMonthlyForm = true;
    },
    closeMonthlyForm() {
      this.showMonthlyForm = false;
      this.editingMonthly = null;
    },
    openTemplateForm(item = null) {
      this.closeMonthlyForm();
      this.formError = '';
      this.editingTemplate = item;
      this.templateForm = item
        ? { name: item.name, items: item.items.map(templateItem => ({ type: 'expense', wallet: '', transfer_to: '', ...templateItem, localId: templateItem.id })) }
        : { name: '', items: [this.newTemplateItem()] };
      this.templateForm.items.forEach(templateItem => this.syncTemplateCategory(templateItem));
      this.showTemplateForm = true;
    },
    closeTemplateForm() {
      this.showTemplateForm = false;
      this.editingTemplate = null;
    },
    submitMonthlyForm() {
      const remaining = Number(this.monthlyForm.remaining_occurrences);
      const total = Number(this.monthlyForm.total_occurrences);
      if (!this.monthlyForm.title || Number(this.monthlyForm.amount) <= 0 || total <= 0 || (this.editingMonthly && (remaining < 0 || remaining > total))) {
        this.formError = 'Nama, harga, dan jumlah transaksi wajib valid.';
        return;
      }
      if (!this.validateTransactionFields(this.monthlyForm)) return;
      const payload = { ...this.monthlyForm, remaining_occurrences: this.editingMonthly ? this.monthlyForm.remaining_occurrences : this.monthlyForm.total_occurrences };
      this.$emit(this.editingMonthly ? 'edit-monthly' : 'create-monthly', payload);
      this.closeMonthlyForm();
    },
    submitTemplateForm() {
      const validItems = this.templateForm.items.every(item => item.title && Number(item.amount) > 0 && Number(item.total_occurrences) > 0);
      if (!this.templateForm.name || !validItems) {
        this.formError = 'Nama template, nama kebutuhan, harga, dan jumlah transaksi wajib diisi.';
        return;
      }
      if (!this.templateForm.items.every(item => this.validateTransactionFields(item))) return;
      this.$emit(this.editingTemplate ? 'edit-template' : 'create-template', {
        name: this.templateForm.name,
        items: this.templateForm.items.map(({ localId, ...item }) => item),
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

.modal-close-btn {
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-close-btn:hover {
  color: #fff;
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

.template-name-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
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

.template-item-grid label,
.template-name-field {
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
</style>
