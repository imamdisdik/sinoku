import { defineStore } from 'pinia'
import { ref } from 'vue'
import { i18n } from '@/i18n'

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const locale = ref<'id' | 'zh'>('id')
  const toast = ref<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)

  // Sidebar admin: collapse (desktop, ikon-saja) + drawer (mobile)
  const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === '1')
  const sidebarMobileOpen = ref(false)
  function toggleSidebarCollapsed() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value ? '1' : '0')
  }
  function toggleSidebarMobile() { sidebarMobileOpen.value = !sidebarMobileOpen.value }
  function closeSidebarMobile() { sidebarMobileOpen.value = false }

  function setLocale(lang: 'id' | 'zh') {
    locale.value = lang
    i18n.global.locale.value = lang
  }

  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    toast.value = { message, type }
    setTimeout(() => { toast.value = null }, 3000)
  }

  return {
    isLoading, locale, toast, setLocale, showToast,
    sidebarCollapsed, sidebarMobileOpen, toggleSidebarCollapsed, toggleSidebarMobile, closeSidebarMobile,
  }
})
