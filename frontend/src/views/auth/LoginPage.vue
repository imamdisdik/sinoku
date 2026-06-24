<template>
  <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f0f4f8;">
    <div class="card" style="width:100%; max-width:400px;">
      <div style="text-align:center; margin-bottom:28px;">
        <div style="font-size:32px; font-weight:900; color:#1a365d;">汉 SINOKU</div>
        <div style="color:#718096; font-size:13px; margin-top:4px;">{{ t('auth.login_title') }}</div>
      </div>
      <form @submit.prevent="doLogin">
        <div class="form-group">
          <label class="form-label">{{ t('auth.email') }}</label>
          <input class="form-input" type="email" v-model="email" required autocomplete="email" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ t('auth.password') }}</label>
          <input class="form-input" type="password" v-model="password" required autocomplete="current-password" />
        </div>
        <p v-if="error" style="color:#e53e3e; font-size:13px; margin-bottom:12px;">{{ error }}</p>
        <button class="btn btn-primary" type="submit" style="width:100%;" :disabled="loading">
          {{ loading ? t('common.loading') : t('auth.login_btn') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function doLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    // Dosen hanya untuk evaluasi → langsung ke halaman dosen (abaikan redirect ke /admin)
    const redirect = auth.isDosen
      ? '/survey/dosen'
      : ((route.query.redirect as string) || '/admin')
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>
