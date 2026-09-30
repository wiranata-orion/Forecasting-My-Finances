<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Tambah Kemungkinan Pengeluaran</h3>
        <button class="modal-close-btn" @click="$emit('close')">×</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="modal-body">
          <p class="modal-hint">
            Masukkan rencana pengeluaran untuk memperkirakan dampaknya terhadap uang sisa yang bisa Anda tabung bulan ini.
          </p>

          <!-- Judul Rencana -->
          <div class="form-group">
            <label class="form-label">Nama Rencana / Pos Pengeluaran</label>
            <input
              v-model="form.title"
              type="text"
              class="form-input"
              placeholder="Contoh: Servis rutin motor, Hadiah ultah teman"
              required
            />
          </div>

          <!-- Perkiraan Biaya -->
          <div class="form-group">
            <label class="form-label">Perkiraan Biaya (Rupiah)</label>
            <div class="currency-input-wrapper">
              <span class="currency-prefix">Rp</span>
              <input
                :value="formattedAmount"
                @input="handleAmountInput"
                type="text"
                inputmode="numeric"
                class="form-input currency-field"
                placeholder="Contoh: 350.000"
                required
              />
            </div>
          </div>

          <!-- Kategori -->
          <div class="form-group">
            <label class="form-label">Kategori</label>
            <select v-model="form.category" class="form-select">
              <option v-for="cat in categories" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>

          <!-- Probabilitas -->
          <div class="form-group">
            <div class="slider-header">
              <label class="form-label">Tingkat Kepastian / Probabilitas</label>
              <span class="slider-val">{{ form.probability }}%</span>
            </div>
            <input
              v-model.number="form.probability"
              type="range"
              min="10"
              max="100"
              step="5"
              class="range-slider"
            />
            <div class="slider-ticks">
              <span>Mungkin (50%)</span>
              <span>Sangat Mungkin (80%)</span>
              <span>Pasti (100%)</span>
            </div>
          </div>

          <!-- Estimasi Tanggal Rencana -->
          <div class="form-group">
            <label class="form-label">Estimasi Tanggal</label>
            <input
              v-model="form.date"
              type="date"
              class="form-input"
              required
            />
          </div>

          <!-- Catatan Tambahan -->
          <div class="form-group">
            <label class="form-label">Catatan Tambahan (Opsional)</label>
            <input
              v-model="form.notes"
              type="text"
              class="form-input"
              placeholder="Contoh: Jika dapat diskon, bisa lebih murah"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            Batal
          </button>
          <button type="submit" class="btn btn-primary">
            Simpan Rencana
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
const CATEGORIES = [
  'Transportasi',
  'Tagihan & Utilitas',
  'Makanan & Kebutuhan',
  'Hiburan & Gaya Hidup',
  'Belanja Online',
  'Kesehatan',
  'Pendidikan',
  'Lain-lain'
];

export default {
  name: 'AddPlannedModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'submit'],
  data() {
    const today = new Date().toISOString().split('T')[0];
    return {
      categories: CATEGORIES,
      rawAmount: '',
      form: {
        title: '',
        amount: null,
        category: CATEGORIES[0],
        probability: 90,
        date: today,
        notes: ''
      }
    };
  },
  computed: {
    formattedAmount() {
      if (!this.rawAmount) return '';
      const cleaned = this.rawAmount.replace(/\D/g, '');
      if (!cleaned) return '';
      return cleaned.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
  },
  methods: {
    handleAmountInput(event) {
      const raw = event.target.value.replace(/\D/g, '');
      this.rawAmount = raw;
      this.form.amount = raw ? parseInt(raw, 10) : null;
      this.$nextTick(() => {
        event.target.value = this.formattedAmount;
      });
    },
    handleSubmit() {
      if (!this.form.amount || this.form.amount <= 0) return;
      this.$emit('submit', { ...this.form });
      this.resetForm();
    },
    resetForm() {
      const today = new Date().toISOString().split('T')[0];
      this.rawAmount = '';
      this.form = {
        title: '',
        amount: null,
        category: CATEGORIES[0],
        probability: 90,
        date: today,
        notes: ''
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

.modal-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
  line-height: 1.4;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
}

.slider-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.slider-val {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--planned-text);
}

.range-slider {
  width: 100%;
  accent-color: var(--planned);
  cursor: pointer;
  margin: 0.4rem 0;
}

.slider-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--text-dim);
}
</style>
