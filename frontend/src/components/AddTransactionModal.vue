<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">{{ transaction ? 'Edit Transaksi' : 'Tambah Transaksi Baru' }}</h3>
        <button class="modal-close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="modal-body">
          <!-- Type selector -->
          <div class="type-toggle-group">
            <button
              type="button"
              class="type-btn"
              :class="{ 'active-income': form.type === 'income' }"
              @click="form.type = 'income'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="19" x2="12" y2="5"/>
                <polyline points="5 12 12 5 19 12"/>
              </svg>
              Pemasukan (+)
            </button>
            <button
              type="button"
              class="type-btn"
              :class="{ 'active-transfer': form.type === 'transfer' }"
              @click="form.type = 'transfer'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M4 7h13l-3-3"/>
                <path d="M20 17H7l3 3"/>
              </svg>
              Transfer
            </button>
            <button
              type="button"
              class="type-btn"
              :class="{ 'active-expense': form.type === 'expense' }"
              @click="form.type = 'expense'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <polyline points="19 12 12 19 5 12"/>
              </svg>
              Pengeluaran (-)
            </button>
          </div>

          <!-- Nominal (Rupiah) with dot formatting -->
          <div class="form-group">
            <label class="form-label">Nominal (Rupiah)</label>
            <div class="currency-input-wrapper">
              <span class="currency-prefix">Rp</span>
              <input
                :value="formattedAmount"
                @input="handleAmountInput"
                type="text"
                inputmode="numeric"
                class="form-input currency-field"
                placeholder="Contoh: 1.200.000"
                required
              />
            </div>
          </div>

          <!-- Keterangan / Deskripsi -->
          <div class="form-group">
            <label class="form-label">Keterangan / Catatan</label>
            <input
              v-model="form.description"
              type="text"
              class="form-input"
              placeholder="Contoh: Makan siang nasi padang"
              required
            />
          </div>

          <!-- Kategori -->
          <div class="form-group">
            <label class="form-label">Kategori</label>
            <select v-model="form.category" class="form-select">
              <option v-for="cat in availableCategories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Alokasi</label>
            <select v-model="form.savings_status" class="form-select">
              <option value="non_savings">Bukan Tabungan</option>
              <option value="savings">Tabungan</option>
            </select>
          </div>

          <!-- Wallet / Sumber Dana -->
          <!-- Sumber / Tempat Dana (Bank / Dompet / Cash) -->
          <div class="form-group">
            <div class="label-with-hint">
              <label class="form-label">{{ form.type === 'transfer' ? 'Rekening Asal' : 'Sumber / Tempat Dana' }}</label>
              <span class="hint-small">Bebas ketik nama bank, e-wallet, atau cash</span>
            </div>
            <input
              v-model="form.wallet"
              type="text"
              class="form-input"
              placeholder="Ketik nama bank/tempat (cth: BCA, Mandiri, Cash, Dana...)"
              list="wallet-suggestions"
            />
            <datalist id="wallet-suggestions">
              <option v-for="w in allWalletSuggestions" :key="w" :value="w" />
            </datalist>

            <!-- Quick Suggestion Chips -->
            <div class="wallet-chips-row">
              <button
                v-for="chip in quickChips"
                :key="chip"
                type="button"
                class="wallet-chip"
                :class="{ active: form.wallet.toLowerCase() === chip.toLowerCase() }"
                @click="form.wallet = chip"
              >
                {{ chip }}
              </button>
            </div>
          </div>

          <div v-if="form.type === 'transfer'" class="form-group">
            <label class="form-label">Rekening Tujuan</label>
            <input
              v-model="form.transfer_to"
              type="text"
              class="form-input"
              placeholder="Pilih atau ketik rekening tujuan"
              list="wallet-suggestions"
              required
            />
          </div>

          <!-- Tanggal -->
          <div class="form-group">
            <label class="form-label">Tanggal Transaksi</label>
            <input
              v-model="form.date"
              type="date"
              class="form-input"
              required
            />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            Batal
          </button>
          <button
            type="submit"
            class="btn"
            :class="form.type === 'income' ? 'btn-success' : form.type === 'transfer' ? 'btn-secondary' : 'btn-primary'"
            :disabled="isSubmitting"
          >
            {{ form.type === 'income' ? 'Simpan Pemasukan' : form.type === 'transfer' ? 'Simpan Transfer' : 'Simpan Pengeluaran' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { fetchWallets } from '../services/api.js';

const EXPENSE_CATEGORIES = [
  'Makanan & Kebutuhan',
  'Transportasi',
  'Tagihan & Utilitas',
  'Hiburan & Gaya Hidup',
  'Belanja Online',
  'Kesehatan',
  'Pendidikan',
  'Lain-lain'
];

const INCOME_CATEGORIES = [
  'Gaji & Upah'
];

export default {
  name: 'AddTransactionModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    transaction: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'submit'],
  data() {
    const today = new Date().toISOString().split('T')[0];
    return {
      isSubmitting: false,
      isLoadingTransaction: false,
      wallets: [],
      rawAmount: '',
      form: {
        type: 'expense',
        amount: null,
        description: '',
        category: 'Makanan & Kebutuhan',
        wallet: '',
        transfer_to: '',
        savings_status: 'non_savings',
        date: today
      }
    };
  },
  computed: {
    availableCategories() {
      if (this.form.type === 'income') {
        const existingCategory = this.transaction?.category;
        return existingCategory && !INCOME_CATEGORIES.includes(existingCategory)
          ? [...INCOME_CATEGORIES, existingCategory]
          : INCOME_CATEGORIES;
      }
      if (this.form.type === 'transfer') return ['Pindah Dana'];
      return EXPENSE_CATEGORIES;
    },
    formattedAmount() {
      if (!this.rawAmount) return '';
      return this.formatWithDots(this.rawAmount);
    },
    quickChips() {
      return ['Cash', 'BCA', 'Mandiri', 'GoPay', 'Dana', 'Bank Jago'];
    },
    allWalletSuggestions() {
      const fromDb = this.wallets.map(w => w.name);
      return Array.from(new Set([...this.quickChips, ...fromDb]));
    }
  },
  watch: {
    'form.type'(newType) {
      if (this.isLoadingTransaction) {
        this.isLoadingTransaction = false;
        return;
      }
      this.form.category = newType === 'income'
        ? INCOME_CATEGORIES[0]
        : newType === 'transfer'
          ? 'Pindah Dana'
          : EXPENSE_CATEGORIES[0];
    },
    isOpen(val) {
      if (val) {
        this.loadWallets();
        if (this.transaction) {
          this.loadTransaction(this.transaction);
        } else {
          this.resetForm();
        }
      }
    }
  },
  methods: {
    formatWithDots(numStr) {
      // Format number string with dots as thousand separator
      const cleaned = numStr.replace(/\D/g, '');
      if (!cleaned) return '';
      return cleaned.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    },

    handleAmountInput(event) {
      // Strip all non-digits, store raw number
      const raw = event.target.value.replace(/\D/g, '');
      this.rawAmount = raw;
      this.form.amount = raw ? parseInt(raw, 10) : null;

      // Update the display value with formatting
      this.$nextTick(() => {
        event.target.value = this.formattedAmount;
      });
    },

    async loadWallets() {
      try {
        this.wallets = await fetchWallets();
      } catch (e) {
        console.error('Failed to load wallets:', e);
      }
    },

    loadTransaction(transaction) {
      this.isLoadingTransaction = true;
      this.rawAmount = String(Math.round(Number(transaction.amount || 0)));
      this.form = {
        type: transaction.type === 'transfer_in' ? 'transfer' : transaction.type,
        amount: Number(transaction.amount || 0),
        description: transaction.description || '',
        category: transaction.type === 'transfer' || transaction.type === 'transfer_in'
          ? 'Pindah Dana'
          : transaction.category || 'Lain-lain',
        wallet: transaction.wallet || '',
        transfer_to: transaction.transfer_to || '',
        savings_status: transaction.savings_status || 'non_savings',
        date: String(transaction.date || new Date().toISOString()).slice(0, 10)
      };
      this.$nextTick(() => {
        this.isLoadingTransaction = false;
      });
    },

    handleSubmit() {
      if (!this.form.amount || this.form.amount <= 0) return;
      if (this.form.type === 'transfer' && (!this.form.wallet.trim() || !this.form.transfer_to.trim() || this.form.wallet.trim() === this.form.transfer_to.trim())) return;
      this.$emit('submit', { ...this.form });
      this.resetForm();
    },

    resetForm() {
      const today = new Date().toISOString().split('T')[0];
      this.rawAmount = '';
      this.form = {
        type: 'expense',
        amount: null,
        description: '',
        category: EXPENSE_CATEGORIES[0],
        wallet: '',
        transfer_to: '',
        savings_status: 'non_savings',
        date: today
      };
    }
  }
};
</script>

<style scoped>
.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
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

.type-toggle-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  background: var(--bg-input);
  padding: 0.35rem;
  border-radius: 12px;
}

.type-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem;
  border-radius: 9px;
  background: transparent;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.active-income {
  background: var(--income);
  color: #fff;
  box-shadow: 0 2px 10px rgba(16, 185, 129, 0.35);
}

.active-expense {
  background: var(--expense);
  color: #fff;
  box-shadow: 0 2px 10px rgba(244, 63, 94, 0.35);
}

.active-transfer {
  background: #0284c7;
  color: #fff;
}

/* Currency Input */
.currency-input-wrapper {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s ease;
}

.currency-input-wrapper:focus-within {
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.15);
}

.currency-prefix {
  padding: 0.6rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.03);
  border-right: 1px solid var(--border-color);
  white-space: nowrap;
}

.currency-field {
  border: none !important;
  background: transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.currency-field:focus {
  box-shadow: none !important;
}

/* Wallet Input and Chips */
.label-with-hint {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.35rem;
}

.hint-small {
  font-size: 0.7rem;
  color: var(--text-dim);
}

.wallet-chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.5rem;
}

.wallet-chip {
  background: var(--bg-card-subtle);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.wallet-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.wallet-chip.active {
  background: rgba(56, 189, 248, 0.18);
  border-color: #38bdf8;
  color: #38bdf8;
  font-weight: 700;
}
</style>
