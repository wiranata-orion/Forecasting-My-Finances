<template>
  <div class="fin-card planned-container" id="perencanaan">
    <div class="card-header">
      <div>
        <div class="title-with-badge">
          <h3 class="card-title">Kemungkinan Pengeluaran Bulan Ini</h3>
          <span class="badge badge-planned">{{ plannedList.length }} Rencana</span>
        </div>
        <p class="card-desc">
          Catat rencana pengeluaran atau estimasi biaya tak terduga untuk menghitung sisa uang yang bisa ditabung secara akurat.
        </p>
      </div>

      <button @click="$emit('open-add-planned')" class="btn btn-primary btn-sm">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Tambah Kemungkinan
      </button>
    </div>

    <!-- Impact & Simulation Box -->
    <div class="impact-box">
      <div class="impact-col">
        <span class="impact-label">Total Rencana Bulan Ini</span>
        <span class="impact-val text-planned">{{ formatRupiah(totalPlannedAmount) }}</span>
        <span class="impact-sub">Tertimbang probabilitas: {{ formatRupiah(weightedPlannedAmount) }}</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Sisa Tabungan Saat Ini</span>
        <span class="impact-val text-savings">{{ formatRupiah(summary.sisa_tabungan) }}</span>
        <span class="impact-sub">{{ summary.savings_ratio }}% dari total pemasukan</span>
      </div>

      <div class="impact-divider"></div>

      <div class="impact-col">
        <span class="impact-label">Potensi Tabungan Jika Dihemat</span>
        <span class="impact-val text-income">{{ formatRupiah(summary.sisa_tabungan + totalPlannedAmount) }}</span>
        <span class="impact-sub">Jika seluruh rencana dapat ditekan</span>
      </div>
    </div>

    <!-- List of Planned Items -->
    <div v-if="plannedList.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
      </div>
      <p class="empty-title">Belum ada kemungkinan pengeluaran</p>
      <p class="empty-sub">Tambahkan rencana pengeluaran seperti servis kendaraan, estimasi tagihan, atau belanja berkala.</p>
    </div>

    <div v-else class="planned-grid">
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
    }
  },
  emits: ['open-add-planned', 'delete-planned', 'realize-planned'],
  computed: {
    totalPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => acc + (Number(cur.amount) || 0), 0);
    },
    weightedPlannedAmount() {
      return this.plannedList.reduce((acc, cur) => {
        const prob = (Number(cur.probability) || 100) / 100;
        return acc + ((Number(cur.amount) || 0) * prob);
      }, 0);
    }
  },
  methods: {
    formatRupiah,
    formatDate,
    getProbClass(prob) {
      if (prob >= 90) return 'prob-high';
      if (prob >= 60) return 'prob-med';
      return 'prob-low';
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

@media (max-width: 800px) {
  .impact-box {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .impact-divider {
    display: none;
  }
}
</style>
