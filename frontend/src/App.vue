<template>
  <div v-if="isAdmin" class="admin-layout">
    <AppSidebar />
    <main class="admin-main">
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppNavbar from '@/components/common/AppNavbar.vue'
import AppFooter from '@/components/common/AppFooter.vue'

const route = useRoute()
const isAdmin = computed(() => route.path.startsWith('/admin'))
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f7fafc; }
.admin-layout { display: flex; min-height: 100vh; }
.admin-main { margin-left: 220px; flex: 1; padding: 32px; min-height: 100vh; }
.public-layout { min-height: 100vh; display: flex; flex-direction: column; }
</style>
