<template>
  <div>
    <h1 class="page-title">Export Data</h1>
    <p class="page-desc">Unduh data evaluasi dalam format Excel (.xlsx) atau CSV untuk analisis lebih lanjut.</p>

    <div class="export-grid">

      <!-- Export Respons -->
      <div class="export-card">
        <div class="card-icon">&#128203;</div>
        <h2 class="card-title">Data Respons</h2>
        <p class="card-desc">Semua respons beserta profil dasar responden, status pengisian, dan mata kuliah.</p>
        <div class="filter-row">
          <select v-model.number="courseFilter.responses" class="filter-input">
            <option :value="null">Semua MK</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
          </select>
          <select v-model="roleFilter" class="filter-input">
            <option value="">Semua Role</option>
            <option value="dosen">Dosen</option>
            <option value="mahasiswa">Mahasiswa</option>
          </select>
        </div>
        <div class="btn-group">
          <button class="btn-xlsx" @click="download('responses', 'xlsx', { course_id: courseFilter.responses, role: roleFilter || undefined })">
            &#128196; Excel
          </button>
          <button class="btn-csv" @click="download('responses', 'csv', { course_id: courseFilter.responses, role: roleFilter || undefined })">
            &#128196; CSV
          </button>
        </div>
      </div>

      <!-- Export Skor CIPP -->
      <div class="export-card">
        <div class="card-icon">&#128200;</div>
        <h2 class="card-title">Skor CIPP per Item</h2>
        <p class="card-desc">Rata-rata skor setiap item instrumen, dipisah antara dosen dan mahasiswa.</p>
        <div class="filter-row">
          <select v-model.number="courseFilter.scores" class="filter-input">
            <option :value="null">Semua MK</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
          </select>
        </div>
        <div class="btn-group">
          <button class="btn-xlsx" @click="download('scores', 'xlsx', { course_id: courseFilter.scores })">
            &#128196; Excel
          </button>
          <button class="btn-csv" @click="download('scores', 'csv', { course_id: courseFilter.scores })">
            &#128196; CSV
          </button>
        </div>
      </div>

      <!-- Export Profil Responden -->
      <div class="export-card">
        <div class="card-icon">&#128100;</div>
        <h2 class="card-title">Profil Responden Mahasiswa</h2>
        <p class="card-desc">Data demografis dan latar belakang mahasiswa yang telah mengisi evaluasi.</p>
        <div class="filter-row">
          <select v-model.number="courseFilter.respondents" class="filter-input">
            <option :value="null">Semua MK</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
          </select>
        </div>
        <div class="btn-group">
          <button class="btn-xlsx" @click="download('respondents', 'xlsx', { course_id: courseFilter.respondents })">
            &#128196; Excel
          </button>
          <button class="btn-csv" @click="download('respondents', 'csv', { course_id: courseFilter.respondents })">
            &#128196; CSV
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { exportWithAuth, exportCsvWithAuth, getCourses } from '@/api/admin'

const ui = useUiStore()
const courses = ref<any[]>([])
const roleFilter = ref('')
const courseFilter = ref({ responses: null as number | null, scores: null as number | null, respondents: null as number | null })

function cleanParams(params: Record<string, any>) {
  return Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
}

async function download(path: string, format: 'xlsx' | 'csv', params: Record<string, any> = {}) {
  const p = cleanParams(params)
  try {
    const res = format === 'xlsx'
      ? await exportWithAuth(path, p)
      : await exportCsvWithAuth(path, p)
    const ext = format === 'xlsx' ? 'xlsx' : 'csv'
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `sinoku_${path}.${ext}`
    a.click()
    URL.revokeObjectURL(url)
    ui.showToast('File berhasil diunduh', 'success')
  } catch {
    ui.showToast('Gagal mengunduh file', 'error')
  }
}

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = res.data.data ?? []
})
</script>

<style scoped>
.page-title{font-size:22px;font-weight:700;color:#1a365d;margin-bottom:6px}
.page-desc{font-size:13px;color:#718096;margin-bottom:24px}
.export-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.export-card{background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08);display:flex;flex-direction:column;gap:12px}
.card-icon{font-size:32px}
.card-title{font-size:16px;font-weight:700;color:#1a365d;margin:0}
.card-desc{font-size:13px;color:#718096;margin:0;line-height:1.5;flex:1}
.filter-row{display:flex;gap:8px;flex-wrap:wrap}
.filter-input{padding:7px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px;flex:1;min-width:120px}
.btn-group{display:flex;gap:8px}
.btn-xlsx{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer;flex:1}
.btn-xlsx:hover{background:#2a4a7f}
.btn-csv{background:#fff;color:#2b6cb0;border:1px solid #bee3f8;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer;flex:1}
.btn-csv:hover{background:#ebf8ff}
</style>
