import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

function loadUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem('auth_user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(loadUser())
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => ['superadmin', 'admin', 'dosen'].includes(user.value?.role ?? ''))
  const isSuperadmin = computed(() => user.value?.role === 'superadmin')
  const isDosen = computed(() => user.value?.role === 'dosen')

  async function login(email: string, password: string) {
    const { data } = await authApi.login(email, password)
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('auth_user', JSON.stringify(data.user))
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
    localStorage.removeItem('auth_user')
  }

  async function refreshAccessToken(): Promise<string> {
    const rt = refreshToken.value ?? localStorage.getItem('refresh_token')
    if (!rt) throw new Error('No refresh token')
    const { data } = await authApi.refresh(rt)
    accessToken.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    return data.access_token
  }

  return {
    user, accessToken, refreshToken,
    isLoggedIn, isAdmin, isSuperadmin, isDosen,
    login, logout, refreshAccessToken,
  }
})
