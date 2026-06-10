"""Tulis semua file implementasi Minggu 1 SINOKU frontend."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"D:\Tesis SINOKA\sinoku\frontend"

FILES = {}

# ── package.json ──────────────────────────────────────────────────────────────
FILES["package.json"] = """{
  "name": "sinoku-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7",
    "vue-i18n": "^9.13.0",
    "axios": "^1.7.0",
    "vue3-apexcharts": "^1.5.0",
    "apexcharts": "^3.49.0",
    "jspdf": "^2.5.1",
    "jspdf-autotable": "^3.8.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vue-tsc": "^2.0.0"
  }
}
"""

# ── vite.config.ts ────────────────────────────────────────────────────────────
FILES["vite.config.ts"] = """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
"""

# ── tsconfig.json ─────────────────────────────────────────────────────────────
FILES["tsconfig.json"] = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*.ts", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

# ── index.html ────────────────────────────────────────────────────────────────
FILES["index.html"] = """<!DOCTYPE html>
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SINOKU — Evaluasi Mata Kuliah Budaya Tiongkok</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
"""

# ── src/types/index.ts ────────────────────────────────────────────────────────
FILES["src/types/index.ts"] = """export interface University {
  id: number
  nama: string
  nama_singkat: string
  kota: string
  provinsi: string
}

export interface Program {
  id: number
  nama: string
  nama_singkat: string
  jenjang: string
}

export interface Course {
  id: number
  kode_mk: string
  nama_id: string
  nama_zh: string
  sks: number
  semester: number
}

export interface SurveyItem {
  id: number
  kode: string
  nomor_urut: number
  teks: string
  answer_type: string
  scale_min: number
  scale_max: number
  is_required: boolean
}

export interface SubDimension {
  id: number
  kode: string
  nama: string
  items: SurveyItem[]
}

export interface OpenQuestion {
  id: number
  kode: string
  pertanyaan: string
  is_required: boolean
}

export interface SurveyStepData {
  dimensi: string
  nama_dimensi: string
  sub_dimensions: SubDimension[]
  open_questions: OpenQuestion[]
}

export interface CippScore {
  dimensi: string
  kode: string
  skor_rata: number
  std_dev: number
  jumlah_item: number
}

export interface UserInfo {
  id: string
  email: string
  full_name: string
  role: string
  university_id: number | null
}
"""

# ── src/i18n/index.ts ─────────────────────────────────────────────────────────
FILES["src/i18n/index.ts"] = """import { createI18n } from 'vue-i18n'
import id from './locales/id.json'
import zh from './locales/zh.json'

export const i18n = createI18n({
  legacy: false,
  locale: 'id',
  fallbackLocale: 'id',
  messages: { id, zh },
})
"""

# ── src/i18n/locales/id.json ──────────────────────────────────────────────────
FILES["src/i18n/locales/id.json"] = """{
  "nav": {
    "home": "Beranda",
    "survey": "Isi Kuesioner",
    "result": "Lihat Hasil",
    "login": "Masuk Admin"
  },
  "landing": {
    "hero_title": "Sistem Evaluasi Mata Kuliah Budaya Tiongkok",
    "hero_subtitle": "Evaluasi berbasis CIPP untuk meningkatkan kualitas pembelajaran budaya Tiongkok di perguruan tinggi Indonesia",
    "start_survey": "Mulai Kuesioner",
    "view_result": "Lihat Hasil Saya",
    "stats_universities": "Universitas",
    "stats_respondents": "Responden",
    "stats_courses": "Mata Kuliah Dievaluasi"
  },
  "survey": {
    "select_title": "Pilih Mata Kuliah",
    "select_university": "Universitas",
    "select_program": "Program Studi",
    "select_course": "Mata Kuliah",
    "select_role": "Peran Anda",
    "select_language": "Bahasa Kuesioner",
    "role_dosen": "Dosen Pengajar",
    "role_mahasiswa": "Mahasiswa",
    "lang_id": "Bahasa Indonesia",
    "lang_zh": "中文",
    "next": "Lanjut",
    "prev": "Kembali",
    "submit": "Kirim Kuesioner",
    "consent_title": "Persetujuan Partisipasi",
    "consent_text": "Data yang Anda berikan bersifat anonim dan hanya digunakan untuk keperluan penelitian evaluasi pendidikan. Tidak ada data identitas yang akan dipublikasikan.",
    "consent_agree": "Saya setuju dan ingin melanjutkan",
    "progress_step": "Langkah {current} dari {total}",
    "step_context": "Konteks",
    "step_input": "Masukan",
    "step_process": "Proses",
    "step_product": "Produk",
    "step_profile": "Profil",
    "likert_1": "Sangat Tidak Setuju",
    "likert_2": "Tidak Setuju",
    "likert_3": "Netral",
    "likert_4": "Setuju",
    "likert_5": "Sangat Setuju",
    "thankyou_title": "Terima Kasih!",
    "thankyou_desc": "Kuesioner Anda telah berhasil disimpan. Simpan kode anonim berikut untuk melihat hasil Anda:",
    "copy_code": "Salin Kode",
    "copied": "Tersalin!"
  },
  "result": {
    "title": "Hasil Kuesioner",
    "enter_code": "Masukkan Kode Anonim",
    "code_placeholder": "SIN-2025-XXXX",
    "search": "Lihat Hasil",
    "cipp_score": "Skor CIPP",
    "open_answers": "Jawaban Terbuka",
    "download_pdf": "Unduh PDF"
  },
  "auth": {
    "login_title": "Masuk Admin",
    "email": "Email",
    "password": "Kata Sandi",
    "login_btn": "Masuk",
    "logout": "Keluar"
  },
  "common": {
    "loading": "Memuat...",
    "error": "Terjadi kesalahan",
    "save": "Simpan",
    "cancel": "Batal",
    "delete": "Hapus",
    "edit": "Edit",
    "add": "Tambah",
    "search": "Cari",
    "required_field": "Wajib diisi",
    "placeholder_select": "-- Pilih --"
  }
}
"""

# ── src/i18n/locales/zh.json ──────────────────────────────────────────────────
FILES["src/i18n/locales/zh.json"] = """{
  "nav": {
    "home": "首页",
    "survey": "填写问卷",
    "result": "查看结果",
    "login": "管理员登录"
  },
  "landing": {
    "hero_title": "中国文化课程评估系统",
    "hero_subtitle": "基于CIPP方法，提升印度尼西亚高校中国文化课程的教学质量",
    "start_survey": "开始问卷",
    "view_result": "查看我的结果",
    "stats_universities": "所大学",
    "stats_respondents": "位受访者",
    "stats_courses": "门课程已评估"
  },
  "survey": {
    "select_title": "选择课程",
    "select_university": "大学",
    "select_program": "专业",
    "select_course": "课程",
    "select_role": "您的身份",
    "select_language": "问卷语言",
    "role_dosen": "授课教师",
    "role_mahasiswa": "学生",
    "lang_id": "印尼语",
    "lang_zh": "中文",
    "next": "下一步",
    "prev": "上一步",
    "submit": "提交问卷",
    "consent_title": "参与同意书",
    "consent_text": "您提供的数据是匿名的，仅用于教育评估研究。不会公开任何个人身份信息。",
    "consent_agree": "我同意并继续",
    "progress_step": "第 {current} 步，共 {total} 步",
    "step_context": "背景",
    "step_input": "投入",
    "step_process": "过程",
    "step_product": "成果",
    "step_profile": "个人信息",
    "likert_1": "非常不同意",
    "likert_2": "不同意",
    "likert_3": "中立",
    "likert_4": "同意",
    "likert_5": "非常同意",
    "thankyou_title": "感谢您！",
    "thankyou_desc": "您的问卷已成功提交。请保存以下匿名代码以查看您的结果：",
    "copy_code": "复制代码",
    "copied": "已复制！"
  },
  "result": {
    "title": "问卷结果",
    "enter_code": "输入匿名代码",
    "code_placeholder": "SIN-2025-XXXX",
    "search": "查看结果",
    "cipp_score": "CIPP评分",
    "open_answers": "开放性回答",
    "download_pdf": "下载PDF"
  },
  "auth": {
    "login_title": "管理员登录",
    "email": "邮箱",
    "password": "密码",
    "login_btn": "登录",
    "logout": "退出"
  },
  "common": {
    "loading": "加载中...",
    "error": "发生错误",
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "add": "添加",
    "search": "搜索",
    "required_field": "必填项",
    "placeholder_select": "-- 请选择 --"
  }
}
"""

# ── src/api/client.ts ─────────────────────────────────────────────────────────
FILES["src/api/client.ts"] = """import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: tambah Bearer token jika ada
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor: handle 401 dengan refresh token
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
          localStorage.setItem('access_token', data.access_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return client(original)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default client
"""

# ── src/api/public.ts ─────────────────────────────────────────────────────────
FILES["src/api/public.ts"] = """import client from './client'
import type { SurveyStartRequest } from '@/types'

export const publicApi = {
  getLandingData: () => client.get('/public/landing'),

  getUniversities: () => client.get('/public/universities'),

  getPrograms: (universityId: number) =>
    client.get(`/public/universities/${universityId}/programs`),

  getCourses: (programId: number) =>
    client.get(`/public/programs/${programId}/courses`),

  startSurvey: (body: Record<string, unknown>) =>
    client.post('/public/survey/start', body),

  getSurveyItems: (responseId: string, dimensi?: string) =>
    client.get(`/public/survey/${responseId}/items`, { params: { dimensi } }),

  saveAnswers: (responseId: string, body: { items: Array<{item_id: number; skor: number}>; open_answers: Array<{open_question_id: number; jawaban_teks: string}> }) =>
    client.post(`/public/survey/${responseId}/answers`, body),

  submitSurvey: (responseId: string) =>
    client.post(`/public/survey/${responseId}/submit`, {}),

  getResult: (kode: string) =>
    client.get(`/public/result/${kode}`),
}
"""

# ── src/api/auth.ts ───────────────────────────────────────────────────────────
FILES["src/api/auth.ts"] = """import client from './client'

export const authApi = {
  login: (email: string, password: string) =>
    client.post('/auth/login', { email, password }),

  logout: (refreshToken: string) =>
    client.post('/auth/logout', { refresh_token: refreshToken }),

  refresh: (refreshToken: string) =>
    client.post('/auth/refresh', { refresh_token: refreshToken }),
}
"""

# ── src/stores/auth.ts ────────────────────────────────────────────────────────
FILES["src/stores/auth.ts"] = """import { defineStore } from 'pinia'
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
"""

# ── src/stores/survey.ts ──────────────────────────────────────────────────────
FILES["src/stores/survey.ts"] = """import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { University, Program, Course, SurveyStepData } from '@/types'

// Step urutan: selector -> consent -> profile -> B -> C -> D -> E -> thankyou
export const SURVEY_STEPS = ['selector', 'consent', 'profile', 'B', 'C', 'D', 'E', 'thankyou'] as const
export type SurveyStep = typeof SURVEY_STEPS[number]

export const useSurveyStore = defineStore('survey', () => {
  const currentStep = ref<SurveyStep>('selector')
  const responseId = ref<string | null>(null)
  const respondentId = ref<string | null>(null)
  const anonymousCode = ref<string | null>(null)

  // Konteks yang dipilih
  const selectedUniversity = ref<University | null>(null)
  const selectedProgram = ref<Program | null>(null)
  const selectedCourse = ref<Course | null>(null)
  const selectedRole = ref<'dosen' | 'mahasiswa'>('mahasiswa')
  const selectedBahasa = ref<'id' | 'zh'>('id')

  // Jawaban: item_id -> skor
  const answers = reactive<Record<number, number>>({})
  // Jawaban terbuka: question_id -> teks
  const openAnswers = reactive<Record<number, string>>({})

  // Data step saat ini
  const stepData = ref<SurveyStepData | null>(null)

  function setAnswer(itemId: number, skor: number) {
    answers[itemId] = skor
  }

  function setOpenAnswer(questionId: number, teks: string) {
    openAnswers[questionId] = teks
  }

  function getAnswersForStep(dimensi: string) {
    if (!stepData.value) return []
    const result: Array<{ item_id: number; skor: number }> = []
    for (const sd of stepData.value.sub_dimensions) {
      for (const item of sd.items) {
        if (answers[item.id] !== undefined) {
          result.push({ item_id: item.id, skor: answers[item.id] })
        }
      }
    }
    return result
  }

  function getOpenAnswersForSubmit() {
    return Object.entries(openAnswers).map(([id, teks]) => ({
      open_question_id: Number(id),
      jawaban_teks: teks,
    }))
  }

  function goToStep(step: SurveyStep) {
    currentStep.value = step
  }

  function nextStep() {
    const idx = SURVEY_STEPS.indexOf(currentStep.value)
    if (idx < SURVEY_STEPS.length - 1) {
      currentStep.value = SURVEY_STEPS[idx + 1]
    }
  }

  function prevStep() {
    const idx = SURVEY_STEPS.indexOf(currentStep.value)
    if (idx > 0) {
      currentStep.value = SURVEY_STEPS[idx - 1]
    }
  }

  function reset() {
    currentStep.value = 'selector'
    responseId.value = null
    respondentId.value = null
    anonymousCode.value = null
    selectedUniversity.value = null
    selectedProgram.value = null
    selectedCourse.value = null
    selectedRole.value = 'mahasiswa'
    selectedBahasa.value = 'id'
    Object.keys(answers).forEach(k => delete answers[Number(k)])
    Object.keys(openAnswers).forEach(k => delete openAnswers[Number(k)])
    stepData.value = null
  }

  return {
    currentStep, responseId, respondentId, anonymousCode,
    selectedUniversity, selectedProgram, selectedCourse, selectedRole, selectedBahasa,
    answers, openAnswers, stepData,
    setAnswer, setOpenAnswer, getAnswersForStep, getOpenAnswersForSubmit,
    goToStep, nextStep, prevStep, reset,
  }
})
"""

# ── src/stores/ui.ts ──────────────────────────────────────────────────────────
FILES["src/stores/ui.ts"] = """import { defineStore } from 'pinia'
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
"""

# ── src/router/index.ts ───────────────────────────────────────────────────────
FILES["src/router/index.ts"] = """import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ZONA PUBLIK
    { path: '/', name: 'landing', component: () => import('@/views/public/LandingPage.vue') },
    { path: '/survey', name: 'survey', component: () => import('@/views/public/survey/SurveySelector.vue') },
    { path: '/survey/consent', name: 'survey-consent', component: () => import('@/views/public/survey/SurveyConsent.vue') },
    { path: '/survey/step/B', name: 'survey-B', component: () => import('@/views/public/survey/SurveyStepContext.vue') },
    { path: '/survey/step/C', name: 'survey-C', component: () => import('@/views/public/survey/SurveyStepInput.vue') },
    { path: '/survey/step/D', name: 'survey-D', component: () => import('@/views/public/survey/SurveyStepProcess.vue') },
    { path: '/survey/step/E', name: 'survey-E', component: () => import('@/views/public/survey/SurveyStepProduct.vue') },
    { path: '/survey/thankyou', name: 'survey-thankyou', component: () => import('@/views/public/survey/SurveyThankYou.vue') },
    { path: '/result', name: 'result', component: () => import('@/views/public/result/ResultByCode.vue') },

    // AUTH
    { path: '/login', name: 'login', component: () => import('@/views/auth/LoginPage.vue') },

    // ADMIN (guard: harus login)
    {
      path: '/admin',
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/admin/DashboardHome.vue') },
        { path: 'universities', name: 'admin-universities', component: () => import('@/views/admin/academic/UniversityList.vue') },
        { path: 'programs', name: 'admin-programs', component: () => import('@/views/admin/academic/ProgramList.vue') },
        { path: 'courses', name: 'admin-courses', component: () => import('@/views/admin/academic/CourseList.vue') },
        { path: 'cpls', name: 'admin-cpls', component: () => import('@/views/admin/academic/CplManager.vue') },
        { path: 'cpmks', name: 'admin-cpmks', component: () => import('@/views/admin/academic/CpmkManager.vue') },
        { path: 'rps', name: 'admin-rps', component: () => import('@/views/admin/rps/RpsList.vue') },
        { path: 'rps/:id/checklist', name: 'admin-rps-checklist', component: () => import('@/views/admin/rps/RpsChecklist.vue') },
        { path: 'instruments', name: 'admin-instruments', component: () => import('@/views/admin/instrument/InstrumentList.vue') },
        { path: 'instruments/items', name: 'admin-items', component: () => import('@/views/admin/instrument/ItemManager.vue') },
        { path: 'anonymous-codes', name: 'admin-anon', component: () => import('@/views/admin/anonymous/AnonymousCodeList.vue') },
        { path: 'analytics', name: 'admin-analytics', component: () => import('@/views/admin/analytics/AnalyticsDashboard.vue') },
        { path: 'reports', name: 'admin-reports', component: () => import('@/views/admin/report/DiagnosticHistory.vue') },
      ],
    },

    // 404
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(authGuard)

export default router
"""

# ── src/router/guards.ts ──────────────────────────────────────────────────────
FILES["src/router/guards.ts"] = """import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

export async function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
  }
  next()
}
"""

# ── src/main.ts ───────────────────────────────────────────────────────────────
FILES["src/main.ts"] = """import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')
"""

# ── src/App.vue ───────────────────────────────────────────────────────────────
FILES["src/App.vue"] = """<template>
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
"""

# ── src/assets/styles/main.css ────────────────────────────────────────────────
FILES["src/assets/styles/main.css"] = """*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f7fafc;
  color: #1a202c;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
button { cursor: pointer; }

.container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600;
  border: none; transition: all .15s; gap: 6px;
}
.btn-primary { background: #2b6cb0; color: #fff; }
.btn-primary:hover { background: #2c5282; }
.btn-outline { background: transparent; color: #2b6cb0; border: 1.5px solid #2b6cb0; }
.btn-outline:hover { background: #ebf8ff; }
.btn-danger  { background: #e53e3e; color: #fff; }
.btn-danger:hover { background: #c53030; }
.btn:disabled { opacity: .5; cursor: not-allowed; }

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}

.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: #4a5568; margin-bottom: 6px; }
.form-input, .form-select {
  width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; background: #fff; color: #1a202c;
  transition: border-color .15s;
}
.form-input:focus, .form-select:focus {
  outline: none; border-color: #3182ce; box-shadow: 0 0 0 3px rgba(66,153,225,.15);
}
"""

# ── src/assets/styles/print.css ───────────────────────────────────────────────
FILES["src/assets/styles/print.css"] = """@media print {
  .no-print, nav, .sidebar, .btn, footer { display: none !important; }
  body { background: #fff; font-size: 11pt; }
  .card { box-shadow: none; border: 1px solid #e2e8f0; }
  @page { size: A4; margin: 20mm; }
}
"""

# ── src/components/common/AppNavbar.vue ───────────────────────────────────────
FILES["src/components/common/AppNavbar.vue"] = """<template>
  <nav class="navbar">
    <div class="container navbar__inner">
      <RouterLink to="/" class="navbar__brand">
        <span class="brand-icon">汉</span>
        <span>SINOKU</span>
      </RouterLink>
      <div class="navbar__links">
        <RouterLink to="/" class="navbar__link">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/survey" class="navbar__link">{{ t('nav.survey') }}</RouterLink>
        <RouterLink to="/result" class="navbar__link">{{ t('nav.result') }}</RouterLink>
        <RouterLink to="/login" class="navbar__link navbar__link--cta" v-if="!auth.isLoggedIn">
          {{ t('nav.login') }}
        </RouterLink>
        <RouterLink to="/admin" class="navbar__link navbar__link--cta" v-else>Dashboard</RouterLink>
        <LanguageToggle />
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import LanguageToggle from './LanguageToggle.vue'

const { t } = useI18n()
const auth = useAuthStore()
</script>

<style scoped>
.navbar {
  background: #1a365d;
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.15);
}
.navbar__inner { display: flex; align-items: center; justify-content: space-between; height: 60px; }
.navbar__brand { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 800; color: #fff; }
.brand-icon { background: #3182ce; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.navbar__links { display: flex; align-items: center; gap: 8px; }
.navbar__link { padding: 7px 14px; border-radius: 6px; font-size: 13px; color: rgba(255,255,255,.85); transition: all .15s; }
.navbar__link:hover, .navbar__link.router-link-active { background: rgba(255,255,255,.1); color: #fff; }
.navbar__link--cta { background: #3182ce; color: #fff !important; }
.navbar__link--cta:hover { background: #2c5282 !important; }
</style>
"""

# ── src/components/common/LanguageToggle.vue ──────────────────────────────────
FILES["src/components/common/LanguageToggle.vue"] = """<template>
  <div class="lang-toggle">
    <button :class="['lang-btn', { active: ui.locale === 'id' }]" @click="ui.setLocale('id')">ID</button>
    <button :class="['lang-btn', { active: ui.locale === 'zh' }]" @click="ui.setLocale('zh')">中文</button>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.lang-toggle { display: flex; gap: 2px; background: rgba(255,255,255,.1); border-radius: 6px; padding: 2px; }
.lang-btn { padding: 4px 10px; border-radius: 4px; border: none; background: transparent; color: rgba(255,255,255,.7); font-size: 12px; font-weight: 600; cursor: pointer; transition: all .15s; }
.lang-btn.active { background: #fff; color: #1a365d; }
</style>
"""

# ── src/components/survey/LikertScale.vue ────────────────────────────────────
FILES["src/components/survey/LikertScale.vue"] = """<template>
  <div class="likert">
    <div class="likert__labels">
      <span>{{ t('survey.likert_1') }}</span>
      <span>{{ t('survey.likert_5') }}</span>
    </div>
    <div class="likert__buttons">
      <button
        v-for="n in 5"
        :key="n"
        :class="['likert__btn', { selected: modelValue === n }]"
        @click="emit('update:modelValue', n)"
        :aria-label="`Pilih ${n}`"
      >
        {{ n }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
defineProps<{ modelValue?: number }>()
const emit = defineEmits<{ 'update:modelValue': [n: number] }>()
</script>

<style scoped>
.likert { margin: 4px 0; }
.likert__labels { display: flex; justify-content: space-between; font-size: 11px; color: #718096; margin-bottom: 6px; }
.likert__buttons { display: flex; gap: 8px; }
.likert__btn {
  width: 42px; height: 42px; border-radius: 50%; border: 2px solid #e2e8f0;
  font-size: 15px; font-weight: 700; background: #fff; color: #4a5568;
  transition: all .15s; flex-shrink: 0;
}
.likert__btn:hover { border-color: #3182ce; color: #3182ce; }
.likert__btn.selected { background: #3182ce; border-color: #3182ce; color: #fff; }
</style>
"""

# ── src/components/survey/SurveyProgressBar.vue ───────────────────────────────
FILES["src/components/survey/SurveyProgressBar.vue"] = """<template>
  <div class="progress">
    <div class="progress__steps">
      <div
        v-for="(step, i) in steps"
        :key="step.key"
        :class="['progress__step', {
          'progress__step--done': i < currentIndex,
          'progress__step--active': i === currentIndex,
        }]"
      >
        <div class="step-circle">{{ i + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>
    <div class="progress__bar">
      <div class="progress__fill" :style="{ width: `${(currentIndex / (steps.length - 1)) * 100}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ currentStep: string }>()

const steps = [
  { key: 'B', label: computed(() => t('survey.step_context')).value },
  { key: 'C', label: computed(() => t('survey.step_input')).value },
  { key: 'D', label: computed(() => t('survey.step_process')).value },
  { key: 'E', label: computed(() => t('survey.step_product')).value },
]
const currentIndex = computed(() => steps.findIndex(s => s.key === props.currentStep))
</script>

<style scoped>
.progress { margin-bottom: 28px; }
.progress__steps { display: flex; justify-content: space-between; position: relative; z-index: 1; }
.progress__step { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.step-circle {
  width: 32px; height: 32px; border-radius: 50%; background: #e2e8f0; color: #718096;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px;
  transition: all .2s;
}
.progress__step--done .step-circle  { background: #48bb78; color: #fff; }
.progress__step--active .step-circle { background: #3182ce; color: #fff; }
.step-label { font-size: 11px; color: #718096; font-weight: 600; }
.progress__step--active .step-label { color: #3182ce; }
.progress__bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin: -20px 16px 0; position: relative; }
.progress__fill { height: 100%; background: #3182ce; border-radius: 2px; transition: width .3s ease; }
</style>
"""

# ── src/components/survey/StepNavigation.vue ─────────────────────────────────
FILES["src/components/survey/StepNavigation.vue"] = """<template>
  <div class="step-nav">
    <button class="btn btn-outline" @click="emit('prev')" :disabled="isFirst">
      ← {{ t('survey.prev') }}
    </button>
    <slot />
    <button class="btn btn-primary" @click="emit('next')" :disabled="isLast || loading">
      <span v-if="loading">{{ t('common.loading') }}</span>
      <span v-else-if="isLast">{{ t('survey.submit') }}</span>
      <span v-else>{{ t('survey.next') }} →</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
defineProps<{ isFirst?: boolean; isLast?: boolean; loading?: boolean }>()
const emit = defineEmits<{ prev: []; next: [] }>()
</script>

<style scoped>
.step-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 32px; padding-top: 20px; border-top: 1px solid #e2e8f0; }
</style>
"""

# ── src/components/survey/AnonymousCodeCard.vue ───────────────────────────────
FILES["src/components/survey/AnonymousCodeCard.vue"] = """<template>
  <div class="code-card">
    <div class="code-display">{{ code }}</div>
    <button class="btn btn-outline" @click="copy">
      {{ copied ? t('survey.copied') : t('survey.copy_code') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
const props = defineProps<{ code: string }>()
const copied = ref(false)
async function copy() {
  await navigator.clipboard.writeText(props.code)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.code-card { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 24px; background: #ebf8ff; border-radius: 12px; border: 2px dashed #3182ce; }
.code-display { font-size: 28px; font-weight: 900; letter-spacing: 4px; color: #2b6cb0; font-family: 'Consolas', monospace; }
</style>
"""

# ── src/views/public/LandingPage.vue ─────────────────────────────────────────
FILES["src/views/public/LandingPage.vue"] = """<template>
  <div class="landing">
    <!-- Hero -->
    <section class="hero">
      <div class="container hero__content">
        <h1 class="hero__title">{{ t('landing.hero_title') }}</h1>
        <p class="hero__subtitle">{{ t('landing.hero_subtitle') }}</p>
        <div class="hero__actions">
          <RouterLink to="/survey" class="btn btn-primary">{{ t('landing.start_survey') }}</RouterLink>
          <RouterLink to="/result" class="btn btn-outline" style="color:#fff;border-color:#fff">{{ t('landing.view_result') }}</RouterLink>
        </div>
        <!-- Stats -->
        <div class="stats" v-if="stats">
          <div class="stat">
            <div class="stat__num">{{ stats.total_universities }}</div>
            <div class="stat__lbl">{{ t('landing.stats_universities') }}</div>
          </div>
          <div class="stat">
            <div class="stat__num">{{ stats.total_respondents }}</div>
            <div class="stat__lbl">{{ t('landing.stats_respondents') }}</div>
          </div>
          <div class="stat">
            <div class="stat__num">{{ stats.total_courses_evaluated }}</div>
            <div class="stat__lbl">{{ t('landing.stats_courses') }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CIPP Penjelasan -->
    <section class="cipp-section container">
      <h2 class="section-title">Metodologi Evaluasi CIPP</h2>
      <div class="cipp-grid">
        <div v-for="dim in cippDims" :key="dim.kode" class="cipp-card" :style="{ borderTopColor: dim.color }">
          <div class="cipp-card__kode" :style="{ background: dim.color }">{{ dim.kode }}</div>
          <div class="cipp-card__name">{{ dim.name }}</div>
          <div class="cipp-card__desc">{{ dim.desc }}</div>
        </div>
      </div>
    </section>

    <!-- Universitas -->
    <section class="univ-section container" v-if="universities.length">
      <h2 class="section-title">Universitas Mitra</h2>
      <div class="univ-grid">
        <div v-for="u in universities" :key="u.id" class="univ-card">
          <div class="univ-card__singkat">{{ u.nama_singkat }}</div>
          <div class="univ-card__nama">{{ u.nama }}</div>
          <div class="univ-card__kota">{{ u.kota }}, {{ u.provinsi }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { publicApi } from '@/api/public'
import type { University } from '@/types'

const { t } = useI18n()
const stats = ref<any>(null)
const universities = ref<University[]>([])

const cippDims = [
  { kode: 'C', name: 'Context / Konteks', color: '#3182CE', desc: 'Relevansi program terhadap kebutuhan masyarakat dan kebijakan pendidikan' },
  { kode: 'I', name: 'Input / Masukan',   color: '#38A169', desc: 'Kualitas sumber daya, kurikulum, kompetensi dosen, dan fasilitas' },
  { kode: 'P', name: 'Process / Proses',  color: '#D69E2E', desc: 'Pelaksanaan pembelajaran, interaksi, dan strategi pengajaran' },
  { kode: 'P', name: 'Product / Produk',  color: '#E53E3E', desc: 'Capaian kompetensi, sikap budaya, dan dampak program' },
]

onMounted(async () => {
  try {
    const { data } = await publicApi.getLandingData()
    stats.value = data
    universities.value = data.universities || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
  color: #fff; padding: 80px 0 60px;
}
.hero__content { text-align: center; }
.hero__title { font-size: 32px; font-weight: 800; margin: 0 0 16px; line-height: 1.2; }
.hero__subtitle { font-size: 16px; color: rgba(255,255,255,.85); max-width: 600px; margin: 0 auto 32px; }
.hero__actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 40px; }
.stats { display: flex; gap: 40px; justify-content: center; flex-wrap: wrap; }
.stat { text-align: center; }
.stat__num { font-size: 36px; font-weight: 800; }
.stat__lbl { font-size: 12px; opacity: .8; margin-top: 4px; }

.section-title { font-size: 22px; font-weight: 700; color: #1a365d; margin: 40px 0 20px; }
.cipp-section { padding-bottom: 40px; }
.cipp-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.cipp-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); border-top: 4px solid #e2e8f0; }
.cipp-card__kode { display: inline-block; color: #fff; width: 36px; height: 36px; border-radius: 8px; font-size: 18px; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
.cipp-card__name { font-size: 14px; font-weight: 700; color: #2d3748; margin-bottom: 8px; }
.cipp-card__desc { font-size: 12px; color: #718096; line-height: 1.5; }

.univ-section { padding-bottom: 60px; }
.univ-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.univ-card { background: #fff; border-radius: 8px; padding: 14px; border: 1px solid #e2e8f0; }
.univ-card__singkat { font-size: 18px; font-weight: 800; color: #2b6cb0; margin-bottom: 4px; }
.univ-card__nama { font-size: 12px; color: #2d3748; font-weight: 500; margin-bottom: 4px; }
.univ-card__kota { font-size: 11px; color: #718096; }
</style>
"""

# ── src/views/public/survey/SurveySelector.vue ────────────────────────────────
FILES["src/views/public/survey/SurveySelector.vue"] = """<template>
  <div class="container" style="max-width:600px; padding-top:40px;">
    <div class="card">
      <h1 style="font-size:20px; font-weight:800; margin:0 0 24px; color:#1a365d;">
        {{ t('survey.select_title') }}
      </h1>

      <div class="form-group">
        <label class="form-label">{{ t('survey.select_university') }} *</label>
        <select class="form-select" v-model="survey.selectedUniversity" @change="onUnivChange">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="u in universities" :key="u.id" :value="u">{{ u.nama }}</option>
        </select>
      </div>

      <div class="form-group" v-if="programs.length">
        <label class="form-label">{{ t('survey.select_program') }} *</label>
        <select class="form-select" v-model="survey.selectedProgram" @change="onProgramChange">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="p in programs" :key="p.id" :value="p">{{ p.nama }} ({{ p.jenjang }})</option>
        </select>
      </div>

      <div class="form-group" v-if="courses.length">
        <label class="form-label">{{ t('survey.select_course') }} *</label>
        <select class="form-select" v-model="survey.selectedCourse">
          <option :value="null">{{ t('common.placeholder_select') }}</option>
          <option v-for="c in courses" :key="c.id" :value="c">{{ c.kode_mk }} — {{ survey.selectedBahasa === 'zh' ? c.nama_zh : c.nama_id }}</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('survey.select_role') }} *</label>
        <div style="display:flex; gap:12px;">
          <label class="radio-option" :class="{ active: survey.selectedRole === 'mahasiswa' }">
            <input type="radio" v-model="survey.selectedRole" value="mahasiswa" />
            {{ t('survey.role_mahasiswa') }}
          </label>
          <label class="radio-option" :class="{ active: survey.selectedRole === 'dosen' }">
            <input type="radio" v-model="survey.selectedRole" value="dosen" />
            {{ t('survey.role_dosen') }}
          </label>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('survey.select_language') }}</label>
        <div style="display:flex; gap:12px;">
          <label class="radio-option" :class="{ active: survey.selectedBahasa === 'id' }">
            <input type="radio" v-model="survey.selectedBahasa" value="id" />
            {{ t('survey.lang_id') }}
          </label>
          <label class="radio-option" :class="{ active: survey.selectedBahasa === 'zh' }">
            <input type="radio" v-model="survey.selectedBahasa" value="zh" />
            {{ t('survey.lang_zh') }}
          </label>
        </div>
      </div>

      <button class="btn btn-primary" style="width:100%; margin-top:8px;" :disabled="!canProceed" @click="proceed">
        {{ t('survey.next') }} →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import { publicApi } from '@/api/public'
import type { University, Program, Course } from '@/types'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()

const universities = ref<University[]>([])
const programs = ref<Program[]>([])
const courses = ref<Course[]>([])

const canProceed = computed(() =>
  !!survey.selectedUniversity && !!survey.selectedProgram && !!survey.selectedCourse
)

onMounted(async () => {
  const { data } = await publicApi.getUniversities()
  universities.value = data.data
})

async function onUnivChange() {
  survey.selectedProgram = null
  survey.selectedCourse = null
  programs.value = []
  courses.value = []
  if (!survey.selectedUniversity) return
  const { data } = await publicApi.getPrograms(survey.selectedUniversity.id)
  programs.value = data.data
}

async function onProgramChange() {
  survey.selectedCourse = null
  courses.value = []
  if (!survey.selectedProgram) return
  const { data } = await publicApi.getCourses(survey.selectedProgram.id)
  courses.value = data.data
}

function proceed() {
  if (canProceed.value) router.push({ name: 'survey-consent' })
}
</script>

<style scoped>
.radio-option {
  flex: 1; display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500;
  transition: all .15s;
}
.radio-option.active { border-color: #3182ce; background: #ebf8ff; color: #2b6cb0; }
.radio-option input { display: none; }
</style>
"""

# ── src/views/public/survey/SurveyConsent.vue ────────────────────────────────
FILES["src/views/public/survey/SurveyConsent.vue"] = """<template>
  <div class="container" style="max-width:600px; padding-top:40px;">
    <div class="card">
      <h1 style="font-size:20px; font-weight:800; margin:0 0 16px; color:#1a365d;">
        {{ t('survey.consent_title') }}
      </h1>
      <p style="color:#4a5568; line-height:1.7; margin-bottom:24px;">{{ t('survey.consent_text') }}</p>
      <div style="background:#f7fafc; border-radius:8px; padding:16px; margin-bottom:24px; font-size:13px; color:#718096;">
        <strong style="color:#2d3748;">Universitas:</strong> {{ survey.selectedUniversity?.nama }}<br/>
        <strong style="color:#2d3748;">Program Studi:</strong> {{ survey.selectedProgram?.nama }}<br/>
        <strong style="color:#2d3748;">Mata Kuliah:</strong>
          {{ survey.selectedBahasa === 'zh' ? survey.selectedCourse?.nama_zh : survey.selectedCourse?.nama_id }}<br/>
        <strong style="color:#2d3748;">Peran:</strong>
          {{ survey.selectedRole === 'dosen' ? t('survey.role_dosen') : t('survey.role_mahasiswa') }}<br/>
        <strong style="color:#2d3748;">Bahasa:</strong>
          {{ survey.selectedBahasa === 'id' ? t('survey.lang_id') : t('survey.lang_zh') }}
      </div>
      <div style="display:flex; gap:12px;">
        <button class="btn btn-outline" @click="router.back()">{{ t('survey.prev') }}</button>
        <button class="btn btn-primary" style="flex:1;" @click="proceed" :disabled="loading">
          {{ loading ? t('common.loading') : t('survey.consent_agree') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import { useUiStore } from '@/stores/ui'
import { publicApi } from '@/api/public'

const { t } = useI18n()
const router = useRouter()
const survey = useSurveyStore()
const ui = useUiStore()
const loading = ref(false)

async function proceed() {
  if (!survey.selectedCourse || !survey.selectedUniversity) return
  loading.value = true
  try {
    const body = {
      course_id: survey.selectedCourse.id,
      role: survey.selectedRole,
      bahasa: survey.selectedBahasa,
      university_id: survey.selectedUniversity.id,
      program_id: survey.selectedProgram?.id ?? null,
    }
    const { data } = await publicApi.startSurvey(body)
    survey.responseId = data.response_id
    survey.respondentId = data.respondent_id
    router.push({ name: 'survey-B' })
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  } finally {
    loading.value = false
  }
}
</script>
"""

# Buat template generik untuk 4 SurveyStep (B,C,D,E)
def make_survey_step(kode: str, prev_route: str, next_route: str, is_last: bool = False) -> str:
    return f"""<template>
  <div class="container" style="max-width:720px; padding-top:32px;">
    <SurveyProgressBar current-step="{kode}" />
    <div class="card" v-if="stepData">
      <h2 style="font-size:18px; font-weight:800; color:#1a365d; margin:0 0 24px;">
        {{ stepData.nama_dimensi }}
      </h2>

      <div v-for="sd in stepData.sub_dimensions" :key="sd.id" class="sub-dim">
        <h3 class="sub-dim__title">{{ sd.kode }} — {{ sd.nama }}</h3>
        <div v-for="item in sd.items" :key="item.id" class="item-row">
          <div class="item-row__text">
            <span class="item-row__num">{{ item.nomor_urut }}.</span>
            {{ item.teks }}
            <span class="item-required" v-if="item.is_required">*</span>
          </div>
          <LikertScale v-model="survey.answers[item.id]" />
        </div>
      </div>

      <!-- Pertanyaan terbuka hanya di step E (Product / terakhir) -->
      <div v-if="stepData.open_questions.length" class="open-section">
        <h3 class="sub-dim__title">Pertanyaan Terbuka</h3>
        <div v-for="q in stepData.open_questions" :key="q.id" class="form-group">
          <label class="form-label">{{ q.pertanyaan }}<span class="item-required" v-if="q.is_required"> *</span></label>
          <textarea class="form-input" rows="3" v-model="survey.openAnswers[q.id]" />
        </div>
      </div>

      <StepNavigation
        :is-first="{'true' if prev_route == '' else 'false'}"
        :is-last="{str(is_last).lower()}"
        :loading="loading"
        @prev="goBack"
        @next="saveAndNext"
      />
    </div>
    <div v-else class="card" style="text-align:center; color:#718096;">
      {{ t('common.loading') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, onMounted }} from 'vue'
import {{ useRouter }} from 'vue-router'
import {{ useI18n }} from 'vue-i18n'
import {{ useSurveyStore }} from '@/stores/survey'
import {{ useUiStore }} from '@/stores/ui'
import {{ publicApi }} from '@/api/public'
import SurveyProgressBar from '@/components/survey/SurveyProgressBar.vue'
import LikertScale from '@/components/survey/LikertScale.vue'
import StepNavigation from '@/components/survey/StepNavigation.vue'

const {{ t }} = useI18n()
const router = useRouter()
const survey = useSurveyStore()
const ui = useUiStore()
const loading = ref(false)
const stepData = survey.stepData

onMounted(async () => {{
  if (!survey.responseId) return router.push({{ name: 'survey' }})
  try {{
    const {{ data }} = await publicApi.getSurveyItems(survey.responseId, '{kode}')
    survey.stepData = data
  }} catch (e: any) {{
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  }}
}})

function goBack() {{
  router.push({{ name: '{prev_route}' }})
}}

async function saveAndNext() {{
  if (!survey.responseId) return
  loading.value = true
  try {{
    const items = survey.getAnswersForStep('{kode}')
    const openAnswers = {'survey.getOpenAnswersForSubmit()' if is_last else '[]'}
    await publicApi.saveAnswers(survey.responseId, {{ items, open_answers: openAnswers }})
    {'const { data } = await publicApi.submitSurvey(survey.responseId); survey.anonymousCode = data.kode_anonim' if is_last else ''}
    router.push({{ name: '{'survey-thankyou' if is_last else next_route}' }})
  }} catch (e: any) {{
    ui.showToast(e.response?.data?.detail || t('common.error'), 'error')
  }} finally {{
    loading.value = false
  }}
}}
</script>

<style scoped>
.sub-dim {{ margin-bottom: 28px; }}
.sub-dim__title {{ font-size: 13px; font-weight: 700; color: #4a5568; text-transform: uppercase; letter-spacing: .05em; margin: 0 0 14px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }}
.item-row {{ display: flex; flex-direction: column; gap: 8px; padding: 14px 0; border-bottom: 1px solid #f4f7fb; }}
.item-row__text {{ font-size: 14px; color: #2d3748; line-height: 1.5; }}
.item-row__num {{ font-weight: 700; color: #3182ce; margin-right: 6px; }}
.item-required {{ color: #e53e3e; margin-left: 4px; }}
.open-section {{ margin-top: 28px; padding-top: 20px; border-top: 2px solid #e2e8f0; }}
</style>
"""

FILES["src/views/public/survey/SurveyStepContext.vue"] = make_survey_step("B", "survey-consent", "survey-C")
FILES["src/views/public/survey/SurveyStepInput.vue"]   = make_survey_step("C", "survey-B",       "survey-D")
FILES["src/views/public/survey/SurveyStepProcess.vue"] = make_survey_step("D", "survey-C",       "survey-E")
FILES["src/views/public/survey/SurveyStepProduct.vue"] = make_survey_step("E", "survey-D",       "survey-thankyou", is_last=True)

# ── src/views/public/survey/SurveyThankYou.vue ───────────────────────────────
FILES["src/views/public/survey/SurveyThankYou.vue"] = """<template>
  <div class="container" style="max-width:520px; padding-top:60px; text-align:center;">
    <div class="card">
      <div class="check-icon">&#10003;</div>
      <h1 style="font-size:24px; font-weight:800; color:#1a365d; margin:16px 0 8px;">
        {{ t('survey.thankyou_title') }}
      </h1>
      <p style="color:#718096; margin-bottom:28px;">{{ t('survey.thankyou_desc') }}</p>
      <AnonymousCodeCard v-if="survey.anonymousCode" :code="survey.anonymousCode" />
      <div style="margin-top:24px; display:flex; gap:12px; justify-content:center;">
        <RouterLink to="/result" class="btn btn-outline">{{ t('result.title') }}</RouterLink>
        <RouterLink to="/" class="btn btn-primary">{{ t('nav.home') }}</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useSurveyStore } from '@/stores/survey'
import AnonymousCodeCard from '@/components/survey/AnonymousCodeCard.vue'

const { t } = useI18n()
const survey = useSurveyStore()
</script>

<style scoped>
.check-icon {
  width: 64px; height: 64px; background: #48bb78; color: #fff;
  border-radius: 50%; font-size: 32px; display: flex; align-items: center;
  justify-content: center; margin: 0 auto;
}
</style>
"""

# ── src/views/public/result/ResultByCode.vue ─────────────────────────────────
FILES["src/views/public/result/ResultByCode.vue"] = """<template>
  <div class="container" style="max-width:700px; padding-top:40px;">
    <!-- Form cari kode -->
    <div class="card" style="margin-bottom:24px;">
      <h1 style="font-size:20px; font-weight:800; color:#1a365d; margin:0 0 16px;">{{ t('result.title') }}</h1>
      <div style="display:flex; gap:12px;">
        <input class="form-input" v-model="kode" :placeholder="t('result.code_placeholder')" style="flex:1;" @keyup.enter="search" />
        <button class="btn btn-primary" @click="search" :disabled="!kode || loading">
          {{ loading ? t('common.loading') : t('result.search') }}
        </button>
      </div>
      <p v-if="error" style="color:#e53e3e; font-size:13px; margin-top:8px;">{{ error }}</p>
    </div>

    <!-- Hasil -->
    <div v-if="result" class="card">
      <div style="margin-bottom:20px;">
        <div style="font-size:12px; color:#718096;">{{ result.course.kode_mk }}</div>
        <div style="font-size:18px; font-weight:700;">{{ result.course.nama_id }}</div>
        <div style="font-size:12px; color:#718096; margin-top:4px;">
          Peran: {{ result.role }} | Bahasa: {{ result.bahasa }} |
          Submit: {{ new Date(result.submitted_at).toLocaleDateString('id-ID') }}
        </div>
      </div>

      <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.cipp_score') }}</h3>
      <div class="score-grid">
        <div v-for="s in result.cipp_scores" :key="s.kode" class="score-card">
          <div class="score-card__kode">{{ s.kode }}</div>
          <div class="score-card__name">{{ s.dimensi }}</div>
          <div class="score-card__score">{{ s.skor_rata.toFixed(2) }}</div>
          <div class="score-card__bar">
            <div class="score-fill" :style="{ width: `${(s.skor_rata / 5) * 100}%` }" />
          </div>
          <div class="score-card__n">n={{ s.jumlah_item }}</div>
        </div>
      </div>

      <div v-if="result.open_answers.length" style="margin-top:24px;">
        <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.open_answers') }}</h3>
        <div v-for="(oa, i) in result.open_answers" :key="i" style="margin-bottom:14px; padding:12px; background:#f7fafc; border-radius:8px;">
          <div style="font-size:13px; font-weight:600; color:#2d3748; margin-bottom:6px;">{{ oa.pertanyaan }}</div>
          <div style="font-size:13px; color:#4a5568;">{{ oa.jawaban }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { publicApi } from '@/api/public'

const { t } = useI18n()
const kode = ref('')
const loading = ref(false)
const error = ref('')
const result = ref<any>(null)

async function search() {
  if (!kode.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await publicApi.getResult(kode.value.trim().toUpperCase())
    result.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.score-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.score-card { background: #f7fafc; border-radius: 10px; padding: 14px; text-align: center; border: 1px solid #e2e8f0; }
.score-card__kode { font-size: 20px; font-weight: 900; color: #3182ce; }
.score-card__name { font-size: 11px; color: #718096; margin: 2px 0 8px; }
.score-card__score { font-size: 26px; font-weight: 800; color: #2d3748; }
.score-card__bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin: 8px 0; }
.score-fill { height: 100%; background: #3182ce; border-radius: 2px; }
.score-card__n { font-size: 11px; color: #a0aec0; }
</style>
"""

# ── src/views/auth/LoginPage.vue ──────────────────────────────────────────────
FILES["src/views/auth/LoginPage.vue"] = """<template>
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
    const redirect = (route.query.redirect as string) || '/admin'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}
</script>
"""

# ── src/views/admin/DashboardHome.vue (placeholder) ──────────────────────────
FILES["src/views/admin/DashboardHome.vue"] = """<template>
  <div class="container" style="padding-top:32px;">
    <h1 style="font-size:22px; font-weight:800; color:#1a365d; margin-bottom:24px;">Dashboard SINOKU</h1>
    <p style="color:#718096;">Dashboard analitik akan diimplementasikan pada Minggu 4.</p>
  </div>
</template>
"""

# ─────────────────────────────────────────────────────────────────────────────
written = 0
for rel, content in FILES.items():
    full = os.path.join(BASE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    written += 1
    print(f"[OK] {rel}")

print(f"\n{written} file frontend berhasil ditulis.")
