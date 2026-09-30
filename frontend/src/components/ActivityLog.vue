<template>
  <div class="fin-card activity-container" id="log-aktivitas">
    <div class="log-header">
      <div>
        <div class="title-row">
          <h3 class="card-title">Log Aktivitas Transaksi</h3>
          <span class="badge badge-savings">{{ filteredTransactions.length }} Catatan</span>
        </div>
        <p class="card-desc">Riwayat lengkap mutasi kas pemasukan dan pengeluaran terkini</p>
      </div>

      <div class="log-top-actions">
        <!-- Search bar -->
        <div class="search-box">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cari transaksi atau kategori..."
            class="search-input"
          />
          <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''">×</button>
        </div>

        <!-- Filter tabs -->
        <div class="filter-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeFilter === 'all' }"
            @click="activeFilter = 'all'"
          >
            Semua
          </button>
          <button
            class="tab-btn tab-inc"
            :class="{ active: activeFilter === 'income' }"
            @click="activeFilter = 'income'"
          >
            Pemasukan
          </button>
          <button
            class="tab-btn tab-exp"
            :class="{ active: activeFilter === 'expense' }"
            @click="activeFilter = 'expense'"
          >
            Pengeluaran
          </button>
          <button
            class="tab-btn tab-trans"
            :class="{ active: activeFilter === 'transfer' }"
            @click="activeFilter = 'transfer'"
          >
            Transfer
          </button>
        </div>

        <button @click="$emit('open-add-transaction')" class="btn btn-primary btn-sm">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Tambah Transaksi
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="filteredTransactions.length === 0" class="empty-log">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>Tidak ada transaksi yang cocok dengan filter "{{ activeFilter }}" atau kata kunci "{{ searchQuery }}"</p>
    </div>

    <!-- Transaction Table -->
    <div v-else class="table-wrapper">
      <table class="activity-table">
        <thead>
          <tr>
            <th class="th-date">Tanggal</th>
            <th class="th-type">Tipe</th>
            <th class="th-cat">Kategori</th>
            <th class="th-wallet">Tempat / Akun</th>
            <th class="th-desc">Keterangan</th>
            <th class="th-amt text-right">Jumlah</th>
            <th class="th-action text-right">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="tx in filteredTransactions"
            :key="tx.id"
            class="tx-row"
          >
            <td class="td-date">
              <span class="date-text">{{ formatDate(tx.date) }}</span>
            </td>
            <td class="td-type">
              <span
                class="badge"
                :class="getTypeBadgeClass(tx.type)"
              >
                {{ formatTypeLabel(tx.type) }}
              </span>
            </td>
            <td class="td-cat">
              <span class="cat-pill">
                {{ tx.category || 'Lainnya' }}
                <template v-if="tx.savings_status">· {{ tx.savings_status === 'savings' ? 'Tabungan' : 'Bukan Tabungan' }}</template>
              </span>
            </td>
            <td class="td-wallet">
              <span v-if="tx.wallet" class="wallet-pill">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="5" width="20" height="14" rx="2"/>
                  <line x1="2" y1="10" x2="22" y2="10"/>
                </svg>
                {{ tx.wallet }}<template v-if="tx.type === 'transfer' && tx.transfer_to"> → {{ tx.transfer_to }}</template>
              </span>
              <span v-else class="text-dim-dash">-</span>
            </td>
            <td class="td-desc">
              <span class="desc-text">{{ tx.description }}</span>
            </td>
            <td class="td-amt text-right">
              <span
                class="amt-text"
                :class="tx.type === 'transfer' ? 'amt-transfer' : isPositiveType(tx.type) ? 'amt-inc' : 'amt-exp'"
              >
                {{ tx.type === 'transfer' ? '' : isPositiveType(tx.type) ? '+' : '-' }}{{ formatRupiah(tx.amount) }}
              </span>
            </td>
            <td class="td-action text-right">
              <button
                @click="$emit('edit-transaction', tx)"
                class="edit-row-btn"
                title="Edit transaksi ini"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 20h9"/>
                  <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>
                </svg>
              </button>
              <button
                @click="$emit('delete-transaction', tx.id)"
                class="del-row-btn"
                title="Hapus transaksi ini"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { formatRupiah, formatDate } from '../utils/formatters.js';

export default {
  name: 'ActivityLog',
  props: {
    transactions: {
      type: Array,
      default: () => []
    }
  },
  emits: ['open-add-transaction', 'edit-transaction', 'delete-transaction'],
  data() {
    return {
      searchQuery: '',
      activeFilter: 'all' // 'all', 'income', 'expense'
    };
  },
  computed: {
    filteredTransactions() {
      let list = [...this.transactions];

      // Filter by type
      if (this.activeFilter === 'income') {
        list = list.filter(t => t.type === 'income');
      } else if (this.activeFilter === 'expense') {
        list = list.filter(t => t.type === 'expense');
      } else if (this.activeFilter === 'transfer') {
        list = list.filter(t => t.type === 'transfer' || t.type === 'transfer_in');
      }

      // Filter by search query
      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase();
        list = list.filter(t =>
          (t.description || '').toLowerCase().includes(q) ||
          (t.category || '').toLowerCase().includes(q) ||
          (t.wallet || '').toLowerCase().includes(q) ||
          (t.transfer_to || '').toLowerCase().includes(q)
        );
      }

      return list;
    }
  },
  methods: {
    formatRupiah,
    formatDate,
    getTypeBadgeClass(type) {
      if (type === 'income') return 'badge-income';
      if (type === 'expense') return 'badge-expense';
      if (type === 'transfer') return 'badge-transfer-out';
      if (type === 'transfer_in') return 'badge-transfer-in';
      return 'badge-transfer-out';
    },
    formatTypeLabel(type) {
      if (type === 'income') return 'Masuk';
      if (type === 'expense') return 'Keluar';
      if (type === 'transfer') return 'Transfer';
      if (type === 'transfer_in') return 'Transfer Masuk';
      return 'Transfer Keluar';
    },
    isPositiveType(type) {
      return type === 'income' || type === 'transfer_in';
    }
  }
};
</script>

<style scoped>
.activity-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 3rem;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-row {
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
  margin-top: 0.2rem;
}

.log-top-actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  color: var(--text-dim);
  pointer-events: none;
}

.search-input {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.5rem 2rem 0.5rem 2.4rem;
  font-size: 0.825rem;
  color: #fff;
  width: 220px;
  outline: none;
  transition: all 0.2s ease;
}
.search-input:focus {
  border-color: var(--primary);
  width: 260px;
}

.clear-search-btn {
  position: absolute;
  right: 0.6rem;
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 1.1rem;
  cursor: pointer;
}

.filter-tabs {
  display: flex;
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  padding: 0.2rem;
  border-radius: 8px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.775rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: var(--bg-card);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}

.tab-btn.active.tab-inc {
  color: var(--income-text);
}
.tab-btn.active.tab-exp {
  color: var(--expense-text);
}
.tab-btn.active.tab-trans {
  color: #38bdf8;
}

.empty-log {
  padding: 3rem 1.5rem;
  text-align: center;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}

.table-wrapper {
  overflow-x: auto;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.activity-table th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-color);
}

.activity-table td {
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  vertical-align: middle;
}

.tx-row:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.date-text {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.cat-pill {
  display: inline-block;
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  color: var(--text-muted);
}

.wallet-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #38bdf8;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  white-space: nowrap;
}

.text-dim-dash {
  color: var(--text-dim);
  font-size: 0.85rem;
}

.desc-text {
  font-weight: 600;
  color: #ffffff;
}

.amt-text {
  font-weight: 700;
  font-feature-settings: 'tnum' on;
  font-size: 0.95rem;
}

.amt-inc {
  color: var(--income-text);
}
.amt-exp {
  color: var(--expense-text);
}

.text-right {
  text-align: right;
}

.del-row-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-dim);
  padding: 0.35rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.edit-row-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-dim);
  padding: 0.35rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.edit-row-btn:hover {
  background: rgba(6, 182, 212, 0.12);
  color: #22d3ee;
  border-color: rgba(6, 182, 212, 0.25);
}

.del-row-btn:hover {
  background: rgba(244, 63, 94, 0.15);
  color: var(--expense-text);
  border-color: rgba(244, 63, 94, 0.3);
}
</style>
