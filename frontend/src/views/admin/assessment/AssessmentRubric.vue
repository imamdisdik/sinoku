<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Rubrik Penilaian</h1>
      <button class="btn-primary" :disabled="!filterScheme" @click="openCreate">+ Tambah Rubrik</button>
    </div>

    <!-- Filter -->
    <div class="toolbar">
      <select v-model.number="filterCourse" @change="onCourseChange" class="filter-input">
        <option :value="null">— Pilih Mata Kuliah —</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
      </select>
      <select v-model.number="filterScheme" @change="fetchData" class="filter-input" :disabled="!filterCourse">
        <option :value="null">— Pilih Skema —</option>
        <option v-for="s in schemes" :key="s.id" :value="s.id">{{ s.nama_komponen }} ({{ s.tipe }})</option>
      </select>
    </div>

    <div v-if="!filterScheme" class="empty-hint">
      Pilih mata kuliah dan skema penilaian untuk melihat rubrik.
    </div>

    <div v-else class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>CPMK</th>
            <th>Level</th>
            <th>Rentang Skor</th>
            <th>Deskriptor</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="5" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="5" class="center">Belum ada rubrik untuk skema ini</td></tr>
          <tr v-for="r in rows" :key="r.id">
            <td><strong>{{ cpmkName(r.cpmk_id) }}</strong></td>
            <td><span :class="levelBadge(r.level)">{{ r.level }}</span></td>
            <td style="white-space:nowrap">
              <span class="skor-range">{{ Number(r.skor_min).toFixed(0) }} – {{ Number(r.skor_max).toFixed(0) }}</span>
            </td>
            <td style="max-width:320px;white-space:pre-wrap;font-size:12px;color:#4a5568">{{ r.deskriptor }}</td>
            <td>
              <button class="btn-edit" @click="openEdit(r)">Edit</button>
              <button class="btn-delete" @click="doDelete(r)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit Rubrik' : 'Tambah Rubrik' }}</h2>
        <form @submit.prevent="save">
          <div class="form-group">
            <label>CPMK *</label>
            <select v-model.number="form.cpmk_id" required class="form-input">
              <option :value="null">— Pilih CPMK —</option>
              <option v-for="c in cpmks" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama_id }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Level *</label>
            <select v-model="form.level" required class="form-input">
              <option value="">— Pilih Level —</option>
              <option v-for="l in levelOptions" :key="l" :value="l">{{ l }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Skor Minimum *</label>
              <input v-model.number="form.skor_min" type="number" min="0" max="100"
                required class="form-input" placeholder="0" />
            </div>
            <div class="form-group">
              <label>Skor Maksimum *</label>
              <input v-model.number="form.skor_max" type="number" min="0" max="100"
                required class="form-input" placeholder="100" />
            </div>
          </div>
          <div v-if="form.skor_min >= form.skor_max && form.skor_max > 0" class="err-msg">
            Skor min harus lebih kecil dari skor max
          </div>
          <div class="form-group">
            <label>Deskriptor *</label>
            <textarea v-model="form.deskriptor" required class="form-input" rows="4"
              placeholder="Jelaskan kriteria penilaian untuk level ini..." />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary"
              :disabled="saving || (form.skor_min >= form.skor_max && form.skor_max > 0)">
              {{ saving ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import {
  getRubrics, createRubric, updateRubric, deleteRubric,
  getSchemes, getCourses, getCpmks,
} from '@/api/admin'

const ui = useUiStore()

const rows = ref<any[]>([])
const courses = ref<any[]>([])
const schemes = ref<any[]>([])
const cpmks = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<any>(null)
const filterCourse = ref<number | null>(null)
const filterScheme = ref<number | null>(null)

const levelOptions = ['A (Sangat Baik)', 'B (Baik)', 'C (Cukup)', 'D (Kurang)', 'E (Sangat Kurang)']

const defaultForm = () => ({
  cpmk_id: null as number | null,
  level: '',
  skor_min: 0,
  skor_max: 100,
  deskriptor: '',
})
const form = ref(defaultForm())

function cpmkName(id: number) {
  const c = cpmks.value.find(c => c.id === id)
  return c ? `${c.kode} — ${c.nama_id}` : `CPMK #${id}`
}

function levelBadge(l: string) {
  if (l.startsWith('A')) return 'badge-a'
  if (l.startsWith('B')) return 'badge-b'
  if (l.startsWith('C')) return 'badge-c'
  if (l.startsWith('D')) return 'badge-d'
  return 'badge-e'
}

async function onCourseChange() {
  filterScheme.value = null
  rows.value = []
  if (!filterCourse.value) { schemes.value = []; return }
  const res = await getSchemes({ course_id: filterCourse.value }).catch(() => ({ data: [] }))
  schemes.value = res.data
}

async function fetchData() {
  if (!filterScheme.value) { rows.value = []; return }
  loading.value = true
  try {
    const res = await getRubrics(filterScheme.value)
    rows.value = res.data
  } finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  form.value = defaultForm()
  showModal.value = true
}
function openEdit(r: any) {
  editing.value = r
  form.value = {
    cpmk_id: r.cpmk_id,
    level: r.level,
    skor_min: Number(r.skor_min),
    skor_max: Number(r.skor_max),
    deskriptor: r.deskriptor,
  }
  showModal.value = true
}

async function save() {
  if (!filterScheme.value) return
  saving.value = true
  try {
    if (editing.value) await updateRubric(editing.value.id, form.value)
    else await createRubric(filterScheme.value, form.value)
    showModal.value = false
    ui.showToast('Rubrik berhasil disimpan', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { saving.value = false }
}

async function doDelete(r: any) {
  if (!confirm(`Hapus rubrik level "${r.level}"?`)) return
  try {
    await deleteRubric(r.id)
    ui.showToast('Rubrik dihapus', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menghapus', 'error')
  }
}

onMounted(async () => {
  const [cRes, cpRes] = await Promise.all([
    getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } })),
    getCpmks({ limit: 200 }).catch(() => ({ data: [] })),
  ])
  courses.value = cRes.data.data ?? []
  cpmks.value = Array.isArray(cpRes.data) ? cpRes.data : cpRes.data.data ?? []
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;min-width:240px}
.empty-hint{background:#fff;border-radius:10px;padding:48px 20px;text-align:center;color:#a0aec0;font-size:14px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748;vertical-align:top}
.center{text-align:center;color:#718096}
.skor-range{background:#f7fafc;border:1px solid #e2e8f0;border-radius:4px;padding:2px 8px;font-weight:700;font-size:12px}
.err-msg{color:#e53e3e;font-size:12px;margin:-10px 0 10px}
.badge-a{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-b{background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-c{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-d{background:#ffedd5;color:#9a3412;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-e{background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-primary:disabled{background:#a0aec0;cursor:not-allowed}
.btn-edit{background:#f0fff4;color:#276749;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:520px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-group{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%;box-sizing:border-box}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
</style>
