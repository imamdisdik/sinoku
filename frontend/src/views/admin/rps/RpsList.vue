<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Rencana Pembelajaran Semester (RPS)</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah RPS</button>
    </div>

    <div class="toolbar">
      <ScopeFilter show-course @change="onScope" />
      <select v-model="filterStatus" @change="fetchData" class="filter-input">
        <option value="">Semua Status</option>
        <option value="draft">Draft</option>
        <option value="aktif">Aktif</option>
        <option value="arsip">Arsip</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Mata Kuliah</th>
            <th>Tahun Akademik</th>
            <th>Semester</th>
            <th>Status</th>
            <th>Dibuat</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada RPS</td></tr>
          <tr v-for="r in paged" :key="r.id">
            <td>{{ courseName(r.course_id) }}</td>
            <td>{{ r.tahun_akademik }}</td>
            <td>{{ r.semester }}</td>
            <td><span :class="statusBadge(r.status)">{{ r.status }}</span></td>
            <td class="meta">{{ formatDate(r.created_at) }}</td>
            <td>
              <button class="btn-checklist" @click="goChecklist(r.id)">&#9745; Checklist</button>
              <button class="btn-edit" @click="openEdit(r)">Edit</button>
              <button class="btn-delete" @click="doDelete(r)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination v-model:page="page" :total-pages="totalPages" />

    <!-- Modal Create/Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit RPS' : 'Tambah RPS' }}</h2>
        <form @submit.prevent="save">
          <div class="form-group">
            <label>Mata Kuliah *</label>
            <select v-model.number="form.course_id" required class="form-input" :disabled="!!editing">
              <option :value="null">— Pilih MK —</option>
              <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Tahun Akademik *</label>
              <input v-model="form.tahun_akademik" required class="form-input" placeholder="2024/2025" />
            </div>
            <div class="form-group">
              <label>Semester *</label>
              <select v-model="form.semester" required class="form-input">
                <option value="Ganjil">Ganjil</option>
                <option value="Genap">Genap</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status" class="form-input">
              <option value="draft">Draft</option>
              <option value="aktif">Aktif</option>
              <option value="arsip">Arsip</option>
            </select>
          </div>
          <div class="form-group">
            <label>URL File RPS (opsional)</label>
            <input v-model="form.file_url" class="form-input" placeholder="https://drive.google.com/..." />
          </div>
          <div class="form-group">
            <label>Catatan</label>
            <textarea v-model="form.catatan" class="form-input" rows="2" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
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
import { getRpsList, createRps, updateRps, deleteRps, getCourses, getMyCourses } from '@/api/admin'
import { useAuthStore } from '@/stores/auth'
import Pagination from '@/components/common/Pagination.vue'
import ScopeFilter from '@/components/common/ScopeFilter.vue'
import { usePagination } from '@/composables/usePagination'

const router = useRouter()
const ui = useUiStore()
const auth = useAuthStore()

type Scope = { university_id: number|null; faculty_id: number|null; program_id: number|null; course_id: number|null }
const rows = ref<any[]>([])
const { page, totalPages, paged } = usePagination(rows, 15)
const scope = ref<Scope>({ university_id: null, faculty_id: null, program_id: null, course_id: null })
function onScope(s: Scope) { scope.value = s; fetchData() }
const courses = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<any>(null)
const filterStatus = ref('')

const defaultForm = () => ({ course_id: null as number | null, tahun_akademik: '', semester: 'Ganjil', status: 'draft', file_url: '', catatan: '' })
const form = ref(defaultForm())

function courseName(id: number) {
  const c = courses.value.find(c => c.id === id)
  return c ? `${c.kode_mk} — ${c.nama_id}` : `MK #${id}`
}
function statusBadge(s: string) {
  return { draft: 'badge-draft', aktif: 'badge-aktif', arsip: 'badge-arsip' }[s] ?? 'badge-draft'
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (scope.value.course_id) params.course_id = scope.value.course_id
    else if (scope.value.program_id) params.program_id = scope.value.program_id
    else if (scope.value.faculty_id) params.faculty_id = scope.value.faculty_id
    else if (scope.value.university_id) params.university_id = scope.value.university_id
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getRpsList(params)
    rows.value = res.data
    page.value = 1
  } finally { loading.value = false }
}

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
function openEdit(r: any) {
  editing.value = r
  form.value = { course_id: r.course_id, tahun_akademik: r.tahun_akademik, semester: r.semester, status: r.status, file_url: r.file_url ?? '', catatan: r.catatan ?? '' }
  showModal.value = true
}
function goChecklist(id: number) { router.push({ name: 'admin-rps-checklist', params: { id } }) }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateRps(editing.value.id, form.value)
    else await createRps(form.value)
    showModal.value = false
    ui.showToast('RPS berhasil disimpan', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { saving.value = false }
}

async function doDelete(r: any) {
  if (!confirm(`Hapus RPS ${r.tahun_akademik} ${r.semester}?`)) return
  try {
    await deleteRps(r.id)
    ui.showToast('RPS dihapus', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menghapus', 'error')
  }
}

onMounted(async () => {
  // Dosen: hanya MK yang ia ampu; lainnya: MK dalam cakupannya
  try {
    if (auth.isDosen) {
      const res = await getMyCourses()
      courses.value = res.data ?? []
    } else {
      const res = await getCourses({ limit: 200 })
      courses.value = res.data.data ?? []
    }
  } catch { courses.value = [] }
  await fetchData()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748}
.center{text-align:center;color:#718096}
.meta{color:#718096;font-size:12px}
.badge-draft{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-aktif{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-arsip{background:#e5e7eb;color:#374151;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-checklist{background:#ebf8ff;color:#2b6cb0;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-edit{background:#f0fff4;color:#276749;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:500px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-group{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
</style>
