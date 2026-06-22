<template>
  <div v-if="isAdmin" class="admin-layout">
    <AppSidebar />
    <!-- Topbar mobile dengan tombol hamburger -->
    <div class="mobile-topbar">
      <button class="hamburger" @click="ui.toggleSidebarMobile()" aria-label="Menu">&#9776;</button>
      <span class="mobile-brand">汉 SINOKU</span>
    </div>
    <main class="admin-main" :class="{ collapsed: ui.sidebarCollapsed }">
      <router-view />
    </main>
  </div>
  <div v-else class="public-layout">
    <AppNavbar />
    <router-view />
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'

const route = useRoute()
const ui = useUiStore()
const isAdmin = computed(() => route.path.startsWith('/admin'))
// Tutup drawer mobile setiap pindah halaman
watch(() => route.path, () => ui.closeSidebarMobile())
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f7fafc; }
.admin-layout { display: flex; min-height: 100vh; }
.admin-main { margin-left: 220px; flex: 1; padding: 32px; min-height: 100vh; transition: margin-left .2s ease; }
.admin-main.collapsed { margin-left: 64px; }
.public-layout { min-height: 100vh; display: flex; flex-direction: column; }

/* Topbar mobile: tersembunyi di desktop */
.mobile-topbar { display: none; }
@media (max-width: 768px) {
  .admin-main, .admin-main.collapsed { margin-left: 0; padding: 16px; padding-top: 68px; }
  .mobile-topbar {
    display: flex; align-items: center; gap: 12px; position: fixed; top: 0; left: 0; right: 0;
    height: 52px; background: #1a365d; z-index: 90; padding: 0 14px; box-shadow: 0 2px 6px rgba(0,0,0,.2);
  }
  .hamburger { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; line-height: 1; }
  .mobile-brand { color: #fff; font-weight: 700; font-size: 15px; }
}
@media print {
  .mobile-topbar { display: none !important; }
}
</style>
