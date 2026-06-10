import { defineStore } from 'pinia'
import { ref } from 'vue'
import { i18n } from '@/i18n'

export const useUiStore = defineStore('ui', () => {
  const isLoading = ref(false)
  const locale = ref<'id' | 'zh'>('id')
  const toast = ref<{ message: string; type: 'success' | 'error' | 'info' } | null>(null)

  function setLocale(lang: 'id' | 'zh') {
    locale.value = lang
    i18n.global.locale.value = lang
  }

  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    toast.value = { message, type }
    setTimeout(() => { toast.value = null }, 3000)
  }

  return { isLoading, locale, toast, setLocale, showToast }
})
