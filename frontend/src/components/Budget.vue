<template>
  <div class="budget-redirect">
    <div class="fin-card redirect-box">
      <h2>Modul Anggaran & Perencanaan</h2>
      <p>Modul perencanaan dan kemungkinan pengeluaran kini terintegrasi langsung di dashboard utama.</p>
      <router-link to="/#perencanaan" class="btn btn-primary">
        Buka Perencanaan di Dashboard
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Budget',
  mounted() {
    this.$router.replace('/#perencanaan');
  }
};
</script>

<style scoped>
.budget-redirect {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
}
.redirect-box {
  max-width: 480px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}
</style>