import axios from 'axios'
import { getActivePinia } from 'pinia'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: tambah Bearer token dari localStorage
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor: auto-refresh saat 401
client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
          const newToken = data.access_token
          localStorage.setItem('access_token', newToken)
          // Sync ke Pinia store tanpa circular import (hindari useAuthStore langsung)
          const pinia = getActivePinia()
          if (pinia?.state.value['auth']) {
            pinia.state.value['auth'].accessToken = newToken
          }
          original.headers.Authorization = `Bearer ${newToken}`
          return client(original)
        } catch {
          // Refresh token expired/revoked — bersihkan semua state dan redirect login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('auth_user')
          window.location.href = '/login'
        }
      } else {
        // Tidak ada refresh token sama sekali
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
