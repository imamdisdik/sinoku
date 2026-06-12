<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Skema Penilaian</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah Skema</button>
    </div>

    <!-- Filter -->
    <div class="toolbar">
      <select v-model.number="filterCourse" @change="fetchData" class="filter-input">
        <option :value="null">Semua Mata Kuliah</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
      </select>
    </div>

    <!-- Bobot total indicator -->
    <div v-if="filterCourse && rows.length" class="bobot-bar">
      <span>Total bobot:</span>
      <span :class="['bobot-val', totalBobot > 100 ? 'bobot-over' : totalBobot === 100 ? 'bobot-ok' : 'bobot-warn']">
        {{ totalBobot.toFixed(1) }}%
      </span>
      <span v-if="totalBobot > 100" class="bobot-msg err">Melebihi 100%!</span>
      <span v-else-if="totalBobot < 100" class="bobot-msg warn">Belum mencapai 100%</span>
      <span v-else class="bobot-msg ok">Sempurna</span>
    </div>

    <!-- Tabel -->
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Mata Kuliah</th>
            <th>Komponen</th>
            <th>Tipe</th>
            <th style="text-align:right">Bobot (%)</th>
            <th>Deskripsi</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada skema penilaian</td></tr>
          <tr v-for="r in rows" :key="r.id">
            <td class="meta">{{ courseName(r.course_id) }}</td>
            <td><strong>{{ r.nama_komponen }}</strong></td>
            <td><span :class="tipeBadge(r.tipe)">{{ r.tipe }}</span></td>
            <td style="text-align:right;font-weight:700">{{ Number(r.bobot_persen).toFixed(1) }}%</td>
            <td class="meta">{{ r.deskripsi || '—' }}</td>
            <td>
              <button class="btn-rubric" @click="goRubric(r)">&#128203; Rubrik</button>
              <button class="btn-edit" @click="openEdit(r)">Edit</button>
              <button class="btn-delete" @click="doDelete(r)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Create/Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit Skema' : 'Tambah Skema Penilaian' }}</h2>
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
              <label>Nama Komponen *</label>
              <input v-model="form.nama_komponen" required class="form-input" placeholder="cth: Ujian Tengah Semester" />
            </div>
            <div class="form-group">
              <label>Tipe *</label>
              <select v-model="form.tipe" required class="form-input">
                <option value="">— Pilih —</option>
                <option v-for="t in tipeOptions" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Bobot (%) *</label>
            <input v-model.number="form.bobot_persen" type="number" min="0" max="100" step="0.5"
              required class="form-input" placeholder="0–100" />
            <span v-if="form.course_id && !editing" class="hint">
              Sisa bobot tersedia: {{ remainingBobot.toFixed(1) }}%
            </span>
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="form.deskripsi" class="form-input" rows="2" placeholder="Opsional" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Panel Rubrik (inline, di bawah) -->
    <div v-if="activeScheme" class="rubric-panel">
      <div class="rubric-header">
        <h2 class="rubric-title">Rubrik: {{ activeScheme.nama_komponen }}</h2>
        <div style="display:flex;gap:8px;align-items:center">
          <button class="btn-primary" @click="openCreateRubric">+ Tambah Rubrik</button>
          <button class="btn-cancel" @click="activeScheme=null">Tutup</button>
        </div>
      </div>

      <div class="table-wrap" style="margin-top:0">
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
            <tr v-if="rubricLoading"><td colspan="5" class="center">Memuat...</td></tr>
            <tr v-else-if="!rubrics.length"><td colspan="5" class="center">Belum ada rubrik</td></tr>
            <tr v-for="rb in rubrics" :key="rb.id">
              <td class="meta">{{ cpmkName(rb.cpmk_id) }}</td>
              <td><span :class="levelBadge(rb.level)">{{ rb.level }}</span></td>
              <td>{{ Number(rb.skor_min).toFixed(0) }} – {{ Number(rb.skor_max).toFixed(0) }}</td>
              <td style="max-width:260px;white-space:pre-wrap;font-size:12px">{{ rb.deskriptor }}</td>
              <td>
                <button class="btn-edit" @click="openEditRubric(rb)">Edit</button>
                <button class="btn-delete" @click="doDeleteRubric(rb)">Hapus</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Rubrik -->
    <div v-if="showRubricModal" class="modal-overlay" @click.self="showRubricModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editingRubric ? 'Edit Rubrik' : 'Tambah Rubrik' }}</h2>
        <form @submit.prevent="saveRubric">
          <div class="form-group">
            <label>CPMK *</label>
            <select v-model.number="rubricForm.cpmk_id" required class="form-input">
              <option :value="null">— Pilih CPMK —</option>
              <option v-for="c in cpmks" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama_id }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Level *</label>
            <select v-model="rubricForm.level" required class="form-input">
              <option value="">— Pilih —</option>
              <option v-for="l in levelOptions" :key="l" :value="l">{{ l }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Skor Min *</label>
              <input v-model.number="rubricForm.skor_min" type="number" min="0" max="100" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Skor Max *</label>
              <input v-model.number="rubricForm.skor_max" type="number" min="0" max="100" required class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>Deskriptor *</label>
            <textarea v-model="rubricForm.deskriptor" required class="form-input" rows="3"
              placeholder="Kriteria penilaian untuk level ini..." />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showRubricModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="savingRubric">{{ savingRubric ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import {
  getSchemes, createScheme, updateScheme, deleteScheme,
  getRubrics, createRubric, updateRubric, deleteRubric,
  getCourses, getCpmks,
} from '@/api/admin'

const ui = useUiStore()

// ── State Skema ────────────────────────────────────────────────────────────
const rows = ref<any[]>([])
const courses = ref<any[]>([])
const cpmks = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<any>(null)
const filterCourse = ref<number | null>(null)

const tipeOptions = ['UTS', 'UAS', 'Tugas', 'Praktikum', 'Proyek', 'Kuis', 'Presentasi', 'Lainnya']
const levelOptions = ['A (Sangat Baik)', 'B (Baik)', 'C (Cukup)', 'D (Kurang)', 'E (Sangat Kurang)']

const defaultForm = () => ({
  course_id: null as number | null,
  nama_komponen: '',
  tipe: '',
  bobot_persen: 0,
  deskripsi: '',
})
const form = ref(defaultForm())

const totalBobot = computed(() =>
  rows.value
    .filter(r => !filterCourse.value || r.course_id === filterCourse.value)
    .reduce((s, r) => s + Number(r.bobot_persen), 0)
)

const remainingBobot = computed(() => {
  const used = rows.value
    .filter(r => r.course_id === form.value.course_id)
    .reduce((s, r) => s + Number(r.bobot_persen), 0)
  return Math.max(0, 100 - used)
})

function courseName(id: number) {
  const c = courses.value.find(c => c.id === id)
  return c ? `${c.kode_mk} — ${c.nama_id}` : `MK #${id}`
}

function tipeBadge(t: string) {
  const map: Record<string, string> = {
    UTS: 'badge-uts', UAS: 'badge-uas', Tugas: 'badge-tugas',
    Praktikum: 'badge-prak', Proyek: 'badge-proyek',
  }
  return map[t] ?? 'badge-other'
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (filterCourse.value) params.course_id = filterCourse.value
    const res = await getSchemes(params)
    rows.value = res.data
  } finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  form.value = defaultForm()
  if (filterCourse.value) form.value.course_id = filterCourse.value
  showModal.value = true
}
function openEdit(r: any) {
  editing.value = r
  form.value = {
    course_id: r.course_id,
    nama_komponen: r.nama_komponen,
    tipe: r.tipe,
    bobot_persen: Number(r.bobot_persen),
    deskripsi: r.deskripsi ?? '',
  }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    const body = { ...form.value, deskripsi: form.value.deskripsi || null }
    if (editing.value) await updateScheme(editing.value.id, body)
    else await createScheme(body)
    showModal.value = false
    ui.showToast('Skema berhasil disimpan', 'success')
    await fetchData()
    if (activeScheme.value) await loadRubrics(activeScheme.value.id)
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { saving.value = false }
}

async function doDelete(r: any) {
  if (!confirm(`Hapus skema "${r.nama_komponen}"? Semua rubrik terkait juga dihapus.`)) return
  try {
    await deleteScheme(r.id)
    ui.showToast('Skema dihapus', 'success')
    if (activeScheme.value?.id === r.id) activeScheme.value = null
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menghapus', 'error')
  }
}

// ── State Rubrik ───────────────────────────────────────────────────────────
const activeScheme = ref<any>(null)
const rubrics = ref<any[]>([])
const rubricLoading = ref(false)
const savingRubric = ref(false)
const showRubricModal = ref(false)
const editingRubric = ref<any>(null)

const defaultRubricForm = () => ({
  cpmk_id: null as number | null,
  level: '',
  skor_min: 0,
  skor_max: 100,
  deskriptor: '',
})
const rubricForm = ref(defaultRubricForm())

function cpmkName(id: number) {
  const c = cpmks.value.find(c => c.id === id)
  return c ? `${c.kode}` : `CPMK #${id}`
}

function levelBadge(l: string) {
  if (l.startsWith('A')) return 'badge-a'
  if (l.startsWith('B')) return 'badge-b'
  if (l.startsWith('C')) return 'badge-c'
  if (l.startsWith('D')) return 'badge-d'
  return 'badge-e'
}

async function goRubric(scheme: any) {
  activeScheme.value = scheme
  await loadRubrics(scheme.id)
}

async function loadRubrics(schemeId: number) {
  rubricLoading.value = true
  try {
    const res = await getRubrics(schemeId)
    rubrics.value = res.data
  } finally { rubricLoading.value = false }
}

function openCreateRubric() {
  editingRubric.value = null
  rubricForm.value = defaultRubricForm()
  showRubricModal.value = true
}
function openEditRubric(rb: any) {
  editingRubric.value = rb
  rubricForm.value = {
    cpmk_id: rb.cpmk_id,
    level: rb.level,
    skor_min: Number(rb.skor_min),
    skor_max: Number(rb.skor_max),
    deskriptor: rb.deskriptor,
  }
  showRubricModal.value = true
}

async function saveRubric() {
  if (!activeScheme.value) return
  savingRubric.value = true
  try {
    const body = { ...rubricForm.value }
    if (editingRubric.value) await updateRubric(editingRubric.value.id, body)
    else await createRubric(activeScheme.value.id, body)
    showRubricModal.value = false
    ui.showToast('Rubrik berhasil disimpan', 'success')
    await loadRubrics(activeScheme.value.id)
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { savingRubric.value = false }
}

async function doDeleteRubric(rb: any) {
  if (!confirm(`Hapus rubrik level "${rb.level}"?`)) return
  try {
    await deleteRubric(rb.id)
    ui.showToast('Rubrik dihapus', 'success')
    await loadRubrics(activeScheme.value!.id)
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
  await fetchData()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}

.bobot-bar{display:flex;align-items:center;gap:8px;background:#fff;border-radius:8px;padding:10px 16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.06);font-size:13px;font-weight:600;color:#4a5568}
.bobot-val{font-size:18px;font-weight:800}
.bobot-val.bobot-over{color:#e53e3e}
.bobot-val.bobot-ok{color:#38a169}
.bobot-val.bobot-warn{color:#d69e2e}
.bobot-msg{font-size:12px;font-weight:500}
.bobot-msg.err{color:#e53e3e}
.bobot-msg.ok{color:#38a169}
.bobot-msg.warn{color:#d69e2e}

.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden;margin-bottom:20px}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748;vertical-align:top}
.center{text-align:center;color:#718096}
.meta{color:#718096;font-size:12px}
.hint{font-size:11px;color:#718096;margin-top:2px}

.badge-uts{background:#ebf8ff;color:#2b6cb0;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-uas{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-tugas{background:#f0fff4;color:#276749;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-prak{background:#faf5ff;color:#6b46c1;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-proyek{background:#fff5f5;color:#c53030;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-other{background:#f7fafc;color:#4a5568;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}

.badge-a{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-b{background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-c{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-d{background:#ffedd5;color:#9a3412;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-e{background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}

.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer;white-space:nowrap}
.btn-rubric{background:#faf5ff;color:#6b46c1;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-edit{background:#f0fff4;color:#276749;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}

.rubric-panel{background:#fff;border-radius:12px;box-shadow:0 1px 8px rgba(0,0,0,0.1);border:2px solid #e9d8fd;padding:20px;margin-top:8px}
.rubric-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.rubric-title{font-size:16px;font-weight:700;color:#553c9a}

.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:520px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-group{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%;box-sizing:border-box}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
</style>
