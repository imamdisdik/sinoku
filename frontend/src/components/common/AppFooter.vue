<template>
  <footer class="footer">
    <div class="container footer__inner">
      <span>© {{ year }} SINOKU — Sistem Evaluasi Mata Kuliah Budaya Tiongkok</span>
      <span class="footer__right">Berbasis CIPP &middot; Universitas Indonesia</span>
    </div>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<style scoped>
.footer {
  background: #1a365d;
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  padding: 16px 0;
  margin-top: auto;
}
.footer__inner {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
</style>
