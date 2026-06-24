<template>
  <nav class="navbar">
    <div class="container navbar__inner">
      <RouterLink to="/" class="navbar__brand" @click="closeMenu">
        <span class="brand-icon">汉</span>
        <span>SINOKU</span>
      </RouterLink>

      <button class="navbar__hamburger" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="Menu">
        {{ menuOpen ? '✕' : '☰' }}
      </button>

      <div class="navbar__links" :class="{ open: menuOpen }">
        <RouterLink to="/" class="navbar__link" @click="closeMenu">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/survey" class="navbar__link" @click="closeMenu">{{ t('nav.survey') }}</RouterLink>
        <RouterLink to="/result" class="navbar__link" @click="closeMenu">{{ t('nav.result') }}</RouterLink>
        <RouterLink to="/login" class="navbar__link navbar__link--cta" v-if="!auth.isLoggedIn" @click="closeMenu">
          {{ t('nav.login') }}
        </RouterLink>
        <RouterLink to="/admin" class="navbar__link navbar__link--cta" v-else @click="closeMenu">Dashboard</RouterLink>
        <LanguageToggle />
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LanguageToggle from './LanguageToggle.vue'

const { t } = useI18n()
const auth = useAuthStore()
const route = useRoute()

const menuOpen = ref(false)
function closeMenu() { menuOpen.value = false }
// Tutup menu otomatis saat pindah halaman
watch(() => route.path, closeMenu)
</script>

<style scoped>
.navbar {
  background: #1a365d;
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.15);
}
.navbar__inner { display: flex; align-items: center; justify-content: space-between; height: 60px; }
.navbar__brand { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 800; color: #fff; }
.brand-icon { background: #3182ce; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.navbar__links { display: flex; align-items: center; gap: 8px; }
.navbar__link { padding: 7px 14px; border-radius: 6px; font-size: 13px; color: rgba(255,255,255,.85); transition: all .15s; }
.navbar__link:hover, .navbar__link.router-link-active { background: rgba(255,255,255,.1); color: #fff; }
.navbar__link--cta { background: #3182ce; color: #fff !important; }
.navbar__link--cta:hover { background: #2c5282 !important; }

/* Tombol hamburger: hanya tampil di mobile */
.navbar__hamburger {
  display: none;
  background: none; border: none; color: #fff;
  font-size: 22px; line-height: 1; cursor: pointer; padding: 6px 8px;
}

@media (max-width: 768px) {
  .navbar__hamburger { display: block; }
  .navbar__links {
    display: none;
    position: absolute; top: 60px; left: 0; right: 0;
    flex-direction: column; align-items: stretch; gap: 4px;
    background: #1a365d; padding: 10px 16px 16px;
    box-shadow: 0 8px 16px rgba(0,0,0,.25);
    border-top: 1px solid rgba(255,255,255,.08);
  }
  .navbar__links.open { display: flex; }
  .navbar__link { padding: 12px 10px; font-size: 14px; }
}
</style>
