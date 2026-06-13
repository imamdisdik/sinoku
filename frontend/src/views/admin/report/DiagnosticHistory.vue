<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Laporan Diagnostik</h1>
      <button class="btn-primary" @click="showWizard = true">+ Generate Laporan</button>
    </div>

    <div class="toolbar">
      <select v-model.number="filterCourse" @change="fetchData" class="filter-input">
        <option :value="null">Semua Mata Kuliah</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Judul Laporan</th>
            <th>Mata Kuliah</th>
            <th>Periode</th>
            <th>Dibuat</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="5" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="5" class="center">Belum ada laporan diagnostik</td></tr>
          <tr v-for="r in rows" :key="r.id">
            <td><strong>{{ r.title }}</strong></td>
            <td class="meta">{{ courseName(r.course_id) }}</td>
            <td class="meta">{{ r.periode_start }} s/d {{ r.periode_end }}</td>
            <td class="meta">{{ formatDate(r.generated_at) }}</td>
            <td>
              <button class="btn-view" @click="viewReport(r.id)">&#128065; Lihat</button>
              <button class="btn-delete" @click="doDelete(r)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Wizard Modal -->
    <div v-if="showWizard" class="modal-overlay" @click.self="showWizard = false">
      <div class="modal">
        <h2 class="modal-title">Generate Laporan Diagnostik</h2>
        <form @submit.prevent="doGenerate">
          <div class="form-group">
            <label>Judul Laporan *</label>
            <input v-model="wForm.title" required class="form-input"
              placeholder="cth: Laporan CIPP Budaya Tiongkok 2024/2025" />
          </div>
          <div class="form-group">
            <label>Mata Kuliah *</label>
            <select v-model.number="wForm.course_id" required class="form-input">
              <option :value="null">— Pilih MK —</option>
              <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Periode Mulai *</label>
              <input v-model="wForm.periode_start" type="date" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Periode Akhir *</label>
              <input v-model="wForm.periode_end" type="date" required class="form-input" />
            </div>
          </div>
          <p class="hint-text">
            Sistem akan mengambil semua respons selesai dalam periode tersebut dan menyimpan snapshot data CIPP.
          </p>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showWizard = false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="generating">
              {{ generating ? 'Memproses...' : 'Generate Laporan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { getReports, generateReport, deleteReport, getCourses } from '@/api/admin'

const router = useRouter()
const ui = useUiStore()

const rows = ref<any[]>([])
const courses = ref<any[]>([])
const loading = ref(true)
const generating = ref(false)
const showWizard = ref(false)
const filterCourse = ref<number | null>(null)

const wForm = ref({
  title: '',
  course_id: null as number | null,
  periode_start: '',
  periode_end: '',
})

function courseName(id: number) {
  const c = courses.value.find(c => c.id === id)
  return c ? `${c.kode_mk} — ${c.nama_id}` : `MK #${id}`
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (filterCourse.value) params.course_id = filterCourse.value
    const res = await getReports(params)
    rows.value = res.data
  } finally { loading.value = false }
}

async function doGenerate() {
  if (!wForm.value.course_id) return
  if (wForm.value.periode_start > wForm.value.periode_end) {
    ui.showToast('Periode mulai tidak boleh setelah periode akhir', 'error')
    return
  }
  generating.value = true
  try {
    const res = await generateReport(wForm.value)
    showWizard.value = false
    ui.showToast('Laporan berhasil digenerate', 'success')
    await fetchData()
    router.push({ name: 'admin-report-preview', params: { id: res.data.id } })
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal generate laporan', 'error')
  } finally { generating.value = false }
}

function viewReport(id: string) {
  router.push({ name: 'admin-report-preview', params: { id } })
}

async function doDelete(r: any) {
  if (!confirm(`Hapus laporan "${r.title}"?`)) return
  try {
    await deleteReport(r.id)
    ui.showToast('Laporan dihapus', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menghapus', 'error')
  }
}

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = res.data.data ?? []
  await fetchData()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{display:flex;gap:10px;margin-bottom:16px}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748}
.center{text-align:center;color:#718096}
.meta{color:#718096;font-size:12px}
.hint-text{font-size:12px;color:#718096;background:#f7fafc;border-radius:6px;padding:10px 12px;margin-bottom:16px}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-primary:disabled{background:#a0aec0;cursor:not-allowed}
.btn-view{background:#ebf8ff;color:#2b6cb0;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:520px;max-width:95vw}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-group{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%;box-sizing:border-box}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
</style>
