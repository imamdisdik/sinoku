import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export async function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  if (!to.meta.requiresAuth) return next()

  const auth = useAuthStore()

  // Token ada di localStorage tapi store sudah load dari localStorage (via loadUser()),
  // jadi isLoggedIn sudah true jika user dan token sama-sama ada.
  if (auth.isLoggedIn) return next()

  // Token ada tapi user hilang (edge case localStorage corrupt) — coba refresh
  const rt = localStorage.getItem('refresh_token')
  if (rt) {
    try {
      await auth.refreshAccessToken()
      // Setelah refresh token berhasil, user masih dari localStorage — cukup untuk lanjut
      if (auth.isLoggedIn) return next()
    } catch {
      // Refresh gagal — paksa login ulang
    }
  }

  return next({ name: 'login', query: { redirect: to.fullPath } })
}
