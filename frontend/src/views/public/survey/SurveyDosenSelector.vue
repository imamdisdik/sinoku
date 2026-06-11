<template>
  <div class="selector-wrap">
    <div class="selector-card">
      <div class="card-header">
        <h1 class="card-title">Mulai Evaluasi</h1>
        <p class="card-subtitle">Pilih mata kuliah yang akan dievaluasi</p>
      </div>

      <div v-if="loadingCourses" class="loading-text">Memuat mata kuliah...</div>

      <form v-else @submit.prevent="start" class="selector-form">
        <div class="form-group">
          <label class="form-label">Mata Kuliah *</label>
          <select v-model.number="selectedCourse" required class="form-select">
            <option :value="null" disabled>— Pilih Mata Kuliah —</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama }}</option>
          </select>
          <p v-if="!courses.length && !loadingCourses" class="form-hint warning">
            Tidak ada mata kuliah untuk program studi Anda. Hubungi admin.
          </p>
        </div>

        <div class="form-group">
          <label class="form-label">Bahasa Kuisioner *</label>
          <div class="radio-group">
            <label class="radio-item" :class="{ active: bahasa === 'id' }">
              <input type="radio" v-model="bahasa" value="id" />
              <span>Indonesia</span>
            </label>
            <label class="radio-item" :class="{ active: bahasa === 'zh' }">
              <input type="radio" v-model="bahasa" value="zh" />
              <span>中文 (Mandarin)</span>
            </label>
          </div>
        </div>

        <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

        <button type="submit" class="btn-start" :disabled="!selectedCourse || starting">
          {{ starting ? 'Memulai...' : 'Mulai Evaluasi' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCourses } from '@/api/admin'
import { publicApi } from '@/api/public'
import { useSurveyStore } from '@/stores/survey'

const router = useRouter()
const survey = useSurveyStore()

const courses = ref<any[]>([])
const selectedCourse = ref<number | null>(null)
const bahasa = ref('id')
const loadingCourses = ref(true)
const starting = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    const res = await getCourses({ limit: 200 })
    courses.value = res.data.data ?? res.data
  } catch {
    errorMsg.value = 'Gagal memuat mata kuliah'
  } finally {
    loadingCourses.value = false
  }
})

async function start() {
  if (!selectedCourse.value) return
  starting.value = true
  errorMsg.value = ''
  try {
    const res = await publicApi.startSurveyDosen(selectedCourse.value, bahasa.value)
    const { response_id, role, bahasa: lang } = res.data
    survey.initFromServer({ response_id, respondent_id: null, role, bahasa: lang, isDosen: true })
    router.push({ name: 'SurveyStep', params: { responseId: response_id, step: 'context' } })
  } catch (e: any) {
    errorMsg.value = e.response?.data?.detail || 'Gagal memulai evaluasi'
  } finally {
    starting.value = false
  }
}
</script>

<style scoped>
.selector-wrap { min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f7fafc; padding:24px }
.selector-card { background:#fff; border-radius:16px; box-shadow:0 4px 24px rgba(0,0,0,0.08); padding:40px; width:480px; max-width:100% }
.card-header { margin-bottom:32px }
.card-title { font-size:24px; font-weight:700; color:#1a365d; margin-bottom:6px }
.card-subtitle { color:#718096; font-size:14px }
.loading-text { color:#718096; text-align:center; padding:20px }
.selector-form { display:flex; flex-direction:column; gap:24px }
.form-group { display:flex; flex-direction:column; gap:8px }
.form-label { font-size:13px; font-weight:600; color:#4a5568 }
.form-select { padding:10px 12px; border:1px solid #e2e8f0; border-radius:8px; font-size:14px; color:#2d3748; background:#fff }
.form-hint { font-size:12px; color:#718096 }
.form-hint.warning { color:#e53e3e }
.radio-group { display:flex; gap:12px }
.radio-item { display:flex; align-items:center; gap:8px; padding:10px 16px; border:2px solid #e2e8f0; border-radius:8px; cursor:pointer; transition:all 0.15s; flex:1; justify-content:center; font-size:14px }
.radio-item.active { border-color:#1a365d; background:#ebf8ff; color:#1a365d; font-weight:600 }
.radio-item input { display:none }
.error-banner { background:#fff5f5; color:#e53e3e; border:1px solid #fed7d7; border-radius:8px; padding:10px 14px; font-size:13px }
.btn-start { background:#1a365d; color:#fff; border:none; padding:14px; border-radius:8px; font-size:15px; font-weight:600; cursor:pointer; transition:background 0.15s }
.btn-start:disabled { background:#a0aec0; cursor:not-allowed }
</style>
