<template>
  <div id="app-root">
    <AppNavbar v-if="!isAdminRoute" />
    <RouterView />
    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="ui.toast" :class="['toast', `toast--${ui.toast.type}`]">
        {{ ui.toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import AppNavbar from '@/components/common/AppNavbar.vue'

const route = useRoute()
const ui = useUiStore()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
</script>

<style>
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
}
.toast--success { background: #48bb78; color: #fff; }
.toast--error   { background: #fc8181; color: #fff; }
.toast--info    { background: #4299e1; color: #fff; }
.toast-enter-active, .toast-leave-active { transition: all .3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(10px); }
</style>
