import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => ['superadmin', 'admin', 'dosen'].includes(user.value?.role ?? ''))

  async function login(email: string, password: string) {
    const { data } = await authApi.login(email, password)
    accessToken.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    // Simpan refresh token jika ada di response (tambahkan di backend jika perlu)
  }

  async function logout() {
    if (refreshToken.value) {
      await authApi.logout(refreshToken.value).catch(() => {})
    }
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isLoggedIn, isAdmin, login, logout }
})
