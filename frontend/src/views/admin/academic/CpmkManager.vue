<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">CPMK (Capaian Pembelajaran Mata Kuliah)</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah CPMK</button>
    </div>

    <div class="toolbar">
      <select v-model="filterCourse" @change="fetchData" class="search-input">
        <option value="">Semua Mata Kuliah</option>
        <option v-for="c in courseList" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>Kode CPMK</th><th>Deskripsi (ID)</th><th>Deskripsi (中文)</th><th>Bobot (%)</th><th>Status</th><th>Aksi</th></tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada data CPMK.</td></tr>
          <template v-for="c in rows" :key="c.id">
            <tr :class="{ 'row-active': expandedId === c.id }">
              <td><span class="badge">{{ c.kode_cpmk }}</span></td>
              <td>{{ c.deskripsi_id }}</td>
              <td class="text-muted">{{ c.deskripsi_zh }}</td>
              <td class="tc">{{ c.bobot_persen }}%</td>
              <td><span :class="c.is_active ? 'status-active' : 'status-inactive'">{{ c.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
              <td class="action-cell">
                <button class="btn-edit" @click="openEdit(c)">Edit</button>
                <button class="btn-map" :class="{ active: expandedId === c.id }" @click="toggleMapping(c)" title="Kelola Mapping CPMK→CPL (UC-14g)">CPL</button>
                <button class="btn-delete" @click="confirmDelete(c)">Hapus</button>
              </td>
            </tr>
            <!-- ── Inline CPMK→CPL Mapping Panel (UC-14g) ── -->
            <tr v-if="expandedId === c.id" class="mapping-row">
              <td colspan="6">
                <div class="mapping-panel">
                  <div class="mapping-header">
                    <div>
                      <div class="mapping-title">Mapping CPMK &#8594; CPL: <strong>{{ c.kode_cpmk }}</strong></div>
                      <div class="mapping-subtitle">Pilih CPL yang didukung oleh CPMK ini (UC-14g) &mdash; CPL diambil dari prodi MK terkait</div>
                    </div>
                    <button class="btn-save-map" @click="saveMapping(c.id)" :disabled="mappingSaving">
                      {{ mappingSaving ? 'Menyimpan...' : 'Simpan Mapping' }}
                    </button>
                  </div>
                  <div v-if="mappingLoading" class="mapping-empty">Memuat daftar CPL...</div>
                  <div v-else-if="!availableCpls.length" class="mapping-empty">
                    Belum ada CPL untuk program studi terkait.
                    <router-link to="/admin/cpls" class="link">Tambah CPL terlebih dahulu.</router-link>
                  </div>
                  <div v-else class="cpl-checklist">
                    <label
                      v-for="cpl in availableCpls"
                      :key="cpl.id"
                      class="cpl-item"
                      :class="{ checked: selectedCplIds.has(cpl.id) }"
                    >
                      <input type="checkbox" :checked="selectedCplIds.has(cpl.id)" @change="toggleCpl(cpl.id)" class="cpl-checkbox" />
                      <div class="cpl-info">
                        <div class="cpl-kode">
                          <span class="badge-sm">{{ cpl.kode_cpl }}</span>
                          <span class="kat-tag" :class="'kat-' + cpl.kategori">{{ cpl.kategori }}</span>
                        </div>
                        <div class="cpl-desc">{{ cpl.deskripsi_id }}</div>
                        <div class="cpl-desc-zh">{{ cpl.deskripsi_zh }}</div>
                      </div>
                    </label>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Modal Create / Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} CPMK</h2>
        <form @submit.prevent="save">
          <div class="form-group mb-16">
            <label>Mata Kuliah *</label>
            <select v-model.number="form.course_id" required class="form-input">
              <option :value="0" disabled>— Pilih Mata Kuliah —</option>
              <option v-for="c in courseList" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
            </select>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label>Kode CPMK *</label>
              <input v-model="form.kode_cpmk" required class="form-input" placeholder="CPMK-01" />
            </div>
            <div class="form-group">
              <label>Bobot (%) *</label>
              <input v-model.number="form.bobot_persen" type="number" min="0" max="100" step="0.5" required class="form-input" />
            </div>
            <div class="form-group full">
              <label>Deskripsi Indonesia *</label>
              <textarea v-model="form.deskripsi_id" required class="form-input" rows="3"></textarea>
            </div>
            <div class="form-group full">
              <label>Deskripsi 中文 *</label>
              <textarea v-model="form.deskripsi_zh" required class="form-input" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal = false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Delete -->
    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
      <div class="modal modal-sm">
        <h2 class="modal-title">Hapus CPMK?</h2>
        <p class="confirm-text">Yakin hapus <strong>{{ deleteTarget?.kode_cpmk }}</strong>? Mapping ke CPL akan ikut terhapus.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm = false">Batal</button>
          <button class="btn-delete" @click="doDelete" :disabled="saving">Hapus</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  getCpmks, createCpmk, updateCpmk, deleteCpmk,
  getCourses, getCpls,
  getCpmkCpls, mapCpmkCpls, unmapCpmkCpl,
} from '@/api/admin'

const rows = ref<any[]>([])
const courseList = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const filterCourse = ref<number | ''>('')

const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)

const defaultForm = () => ({
  course_id: (filterCourse.value as number) || 0,
  kode_cpmk: '', deskripsi_id: '', deskripsi_zh: '', bobot_persen: 0,
})
const form = ref(defaultForm())

// ── Mapping state (UC-14g) ──────────────────────────────────────────────────
const expandedId = ref<number | null>(null)
const availableCpls = ref<any[]>([])
const selectedCplIds = ref<Set<number>>(new Set())
const originalCplIds = ref<Set<number>>(new Set())
const mappingLoading = ref(false)
const mappingSaving = ref(false)

// Resolve program_id dari course yang sedang dipilih di filter
const activeProgramId = computed<number | null>(() => {
  if (!filterCourse.value) return null
  const found = courseList.value.find((c: any) => c.id === filterCourse.value)
  return found?.program_id ?? null
})

async function fetchData() {
  loading.value = true
  try {
    // "Semua Mata Kuliah" (filter kosong) → ambil semua CPMK; jika dipilih → filter per MK
    const params = filterCourse.value ? { course_id: filterCourse.value } : {}
    const res = await getCpmks(params)
    rows.value = res.data
    if (expandedId.value && !rows.value.find((r: any) => r.id === expandedId.value)) {
      expandedId.value = null
    }
  } finally { loading.value = false }
}

onMounted(async () => {
  try {
    const res = await getCourses({ limit: 500 })
    courseList.value = res.data.data
  } catch { /* tetap lanjut meski dropdown gagal */ }
  await fetchData()  // tampilkan semua CPMK saat halaman dibuka
})

function openCreate() {
  editing.value = null
  form.value = defaultForm()
  showModal.value = true
}
function openEdit(c: any) {
  editing.value = c
  form.value = { ...c }
  showModal.value = true
}
function confirmDelete(c: any) {
  deleteTarget.value = c
  showConfirm.value = true
}

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateCpmk(editing.value.id, form.value)
    else await createCpmk(form.value)
    showModal.value = false
    await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try {
    await deleteCpmk(deleteTarget.value.id)
    showConfirm.value = false
    if (expandedId.value === deleteTarget.value.id) expandedId.value = null
    await fetchData()
  } finally { saving.value = false }
}

// ── Mapping CPMK→CPL (UC-14g) handlers ────────────────────────────────────
async function toggleMapping(cpmk: any) {
  if (expandedId.value === cpmk.id) { expandedId.value = null; return }
  expandedId.value = cpmk.id
  mappingLoading.value = true
  selectedCplIds.value = new Set()
  originalCplIds.value = new Set()
  availableCpls.value = []
  try {
    // Ambil program_id dari courseList berdasarkan course_id CPMK ini
    const course = courseList.value.find((c: any) => c.id === cpmk.course_id)
    const programId = course?.program_id ?? activeProgramId.value

    const [cplsRes, mappedRes] = await Promise.all([
      programId ? getCpls({ program_id: programId }) : Promise.resolve({ data: [] }),
      getCpmkCpls(cpmk.id),
    ])
    availableCpls.value = cplsRes.data
    const mapped: number[] = mappedRes.data
    selectedCplIds.value = new Set(mapped)
    originalCplIds.value = new Set(mapped)
  } finally { mappingLoading.value = false }
}

function toggleCpl(cplId: number) {
  const s = new Set(selectedCplIds.value)
  s.has(cplId) ? s.delete(cplId) : s.add(cplId)
  selectedCplIds.value = s
}

async function saveMapping(cpmkId: number) {
  mappingSaving.value = true
  try {
    const toAdd = [...selectedCplIds.value].filter(id => !originalCplIds.value.has(id))
    const toRemove = [...originalCplIds.value].filter(id => !selectedCplIds.value.has(id))
    const ops: Promise<any>[] = []
    if (toAdd.length) ops.push(mapCpmkCpls(cpmkId, toAdd))
    toRemove.forEach(id => ops.push(unmapCpmkCpl(cpmkId, id)))
    await Promise.all(ops)
    originalCplIds.value = new Set(selectedCplIds.value)
  } finally { mappingSaving.value = false }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a365d; }
.toolbar { margin-bottom: 16px; }
.search-input { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; min-width: 280px; }
.table-wrap { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #f7fafc; padding: 10px 14px; text-align: left; font-weight: 600; color: #4a5568; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 10px 14px; border-bottom: 1px solid #f0f4f8; color: #2d3748; vertical-align: middle; }
.row-active td { background: #f3ebff; }
.data-table tr:last-child td { border-bottom: none; }
.center { text-align: center; color: #718096; }
.tc { text-align: center; }
.text-muted { color: #718096; font-size: 12px; }
.action-cell { white-space: nowrap; }
.badge { background: #ebf8ff; color: #2b6cb0; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge-sm { background: #ebf8ff; color: #2b6cb0; padding: 1px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.status-active { color: #38a169; font-size: 12px; font-weight: 600; }
.status-inactive { color: #e53e3e; font-size: 12px; font-weight: 600; }
.btn-primary { background: #1a365d; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-edit { background: #ebf8ff; color: #2b6cb0; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; }
.btn-map { background: #faf5ff; color: #6b46c1; border: 1px solid #d6bcfa; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; font-weight: 600; }
.btn-map.active { background: #6b46c1; color: #fff; border-color: #6b46c1; }
.btn-delete { background: #fff5f5; color: #e53e3e; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; }
.btn-cancel { background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
/* ── Mapping Panel ── */
.mapping-row td { padding: 0 !important; background: #faf5ff; border-bottom: 2px solid #d6bcfa !important; }
.mapping-panel { padding: 20px 24px; }
.mapping-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 16px; }
.mapping-title { font-size: 14px; font-weight: 600; color: #44337a; }
.mapping-subtitle { font-size: 11px; color: #805ad5; margin-top: 2px; }
.btn-save-map { background: #6b46c1; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-size: 13px; cursor: pointer; white-space: nowrap; flex-shrink: 0; }
.btn-save-map:disabled { opacity: 0.5; cursor: not-allowed; }
.mapping-empty { color: #718096; font-size: 13px; padding: 8px 0; }
.link { color: #3182ce; text-decoration: underline; }
.cpl-checklist { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 10px; }
.cpl-item { display: flex; align-items: flex-start; gap: 10px; padding: 12px; border: 2px solid #e9d8fd; border-radius: 8px; cursor: pointer; background: #fff; transition: border-color 0.15s, background 0.15s; }
.cpl-item.checked { border-color: #6b46c1; background: #faf5ff; }
.cpl-item:hover { border-color: #9f7aea; }
.cpl-checkbox { margin-top: 2px; width: 16px; height: 16px; accent-color: #6b46c1; flex-shrink: 0; cursor: pointer; }
.cpl-info { flex: 1; min-width: 0; }
.cpl-kode { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.kat-tag { font-size: 10px; padding: 1px 6px; border-radius: 10px; font-weight: 600; }
.kat-sikap { background: #fed7d7; color: #c53030; }
.kat-pengetahuan { background: #bee3f8; color: #2a69ac; }
.kat-keterampilan { background: #c6f6d5; color: #276749; }
.cpl-desc { font-size: 12px; color: #2d3748; line-height: 1.4; }
.cpl-desc-zh { font-size: 11px; color: #718096; margin-top: 2px; }
/* ── Modal ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: 12px; padding: 28px; width: 580px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
.modal-sm { width: 400px; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a365d; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 12px; font-weight: 600; color: #4a5568; }
.form-input { padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; width: 100%; }
.mb-16 { margin-bottom: 16px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.confirm-text { font-size: 14px; color: #4a5568; margin-bottom: 20px; line-height: 1.6; }
</style>
