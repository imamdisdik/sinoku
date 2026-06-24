<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Mata Kuliah</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah</button>
    </div>

    <div class="toolbar">
      <select v-model="filterProgram" @change="page=1; fetchData()" class="search-input">
        <option value="">Semua Program Studi</option>
        <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama_singkat }} — {{ p.nama }}</option>
      </select>
      <input v-model="search" placeholder="Cari nama / kode MK..." class="search-input ml-8" @input="fetchData" />
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Kode MK</th><th>Nama (ID)</th><th>Nama (中文)</th><th>SKS</th>
            <th>Sem.</th><th>Jenis</th><th>Status</th><th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="8" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="8" class="center">Belum ada data</td></tr>
          <template v-for="c in rows" :key="c.id">
            <tr :class="{ 'row-active': expandedId === c.id }">
              <td><span class="badge">{{ c.kode_mk }}</span></td>
              <td>{{ c.nama_id }}</td>
              <td class="text-muted">{{ c.nama_zh }}</td>
              <td class="tc">{{ c.sks }}</td>
              <td class="tc">{{ c.semester }}</td>
              <td><span class="tag">{{ c.status_mk }}</span></td>
              <td><span :class="c.is_active ? 'status-active' : 'status-inactive'">{{ c.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
              <td class="action-cell">
                <button class="btn-edit" @click="openEdit(c)">Edit</button>
                <button class="btn-map" :class="{ active: expandedId === c.id }" @click="toggleMapping(c)" title="Kelola Mapping CPL (UC-14e)">CPL</button>
                <button class="btn-dosen" :class="{ active: expandedDosenId === c.id }" @click="toggleDosen(c)" title="Kelola Dosen Pengampu">Dosen</button>
                <button class="btn-delete" @click="confirmDelete(c)">Hapus</button>
              </td>
            </tr>
            <!-- ── Inline CPL Mapping Panel (UC-14e) ── -->
            <tr v-if="expandedId === c.id" class="mapping-row">
              <td colspan="8">
                <div class="mapping-panel">
                  <div class="mapping-header">
                    <div>
                      <div class="mapping-title">Mapping CPL &#8594; <strong>{{ c.kode_mk }}</strong> — {{ c.nama_id }}</div>
                      <div class="mapping-subtitle">Pilih CPL yang dicakup oleh mata kuliah ini (UC-14e)</div>
                    </div>
                    <button class="btn-save-map" @click="saveMapping(c.id)" :disabled="mappingSaving">
                      {{ mappingSaving ? 'Menyimpan...' : 'Simpan Mapping' }}
                    </button>
                  </div>
                  <div v-if="mappingLoading" class="mapping-empty">Memuat daftar CPL...</div>
                  <div v-else-if="!availableCpls.length" class="mapping-empty">
                    Belum ada CPL untuk program studi ini.
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
            <!-- ── Inline Dosen Pengampu Panel ── -->
            <tr v-if="expandedDosenId === c.id" class="mapping-row dosen-row">
              <td colspan="8">
                <div class="mapping-panel">
                  <div class="mapping-header">
                    <div>
                      <div class="mapping-title dosen-title">Dosen Pengampu &#8594; <strong>{{ c.kode_mk }}</strong> — {{ c.nama_id }}</div>
                      <div class="mapping-subtitle dosen-subtitle">Pilih dosen program studi yang mengampu mata kuliah ini</div>
                    </div>
                    <button class="btn-save-dosen" @click="saveDosen(c.id)" :disabled="dosenSaving">
                      {{ dosenSaving ? 'Menyimpan...' : 'Simpan Pengampu' }}
                    </button>
                  </div>
                  <div v-if="dosenLoading" class="mapping-empty">Memuat daftar dosen...</div>
                  <div v-else-if="!availableLecturers.length" class="mapping-empty">
                    Belum ada akun dosen di program studi ini.
                    <router-link to="/admin/users" class="link">Tambah akun dosen terlebih dahulu.</router-link>
                  </div>
                  <div v-else class="cpl-checklist">
                    <label
                      v-for="d in availableLecturers"
                      :key="d.id"
                      class="cpl-item dosen-item"
                      :class="{ checked: selectedLecturerIds.has(d.id) }"
                    >
                      <input type="checkbox" :checked="selectedLecturerIds.has(d.id)" @change="toggleLecturer(d.id)" class="cpl-checkbox dosen-checkbox" />
                      <div class="cpl-info">
                        <div class="cpl-desc"><strong>{{ d.full_name }}</strong></div>
                        <div class="cpl-desc-zh">{{ d.email }}</div>
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

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--; fetchData()">&#8592;</button>
      <span>Halaman {{ page }} dari {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++; fetchData()">&#8594;</button>
    </div>

    <!-- Modal Create / Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} Mata Kuliah</h2>
        <form @submit.prevent="save">
          <div class="form-grid">
            <div class="form-group full">
              <label>Program Studi *</label>
              <select v-model.number="form.program_id" required class="form-input">
                <option :value="0" disabled>— Pilih Program Studi —</option>
                <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama }}</option>
              </select>
            </div>
            <div class="form-group"><label>Kode MK *</label><input v-model="form.kode_mk" required class="form-input" /></div>
            <div class="form-group"><label>SKS *</label><input v-model.number="form.sks" type="number" min="1" max="6" required class="form-input" /></div>
            <div class="form-group full"><label>Nama Indonesia *</label><input v-model="form.nama_id" required class="form-input" /></div>
            <div class="form-group full"><label>Nama 中文 *</label><input v-model="form.nama_zh" required class="form-input" /></div>
            <div class="form-group"><label>Semester *</label><input v-model.number="form.semester" type="number" min="1" max="8" required class="form-input" /></div>
            <div class="form-group">
              <label>Jenis MK</label>
              <select v-model="form.status_mk" class="form-input">
                <option value="wajib">Wajib</option>
                <option value="pilihan">Pilihan</option>
                <option value="mbkm">MBKM</option>
              </select>
            </div>
            <div class="form-group full"><label>Deskripsi</label><textarea v-model="form.deskripsi" class="form-input" rows="3"></textarea></div>
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
        <h2 class="modal-title">Hapus Mata Kuliah?</h2>
        <p class="confirm-text">Yakin hapus <strong>{{ deleteTarget?.nama_id }}</strong>?<br>⚠️ Seluruh data terkait akan <strong>ikut terhapus permanen</strong>: CPMK &amp; mapping CPL, RPS &amp; checklist, skema/rubrik, MBKM, serta <strong>respons evaluasi, kode anonim, dan laporan diagnostik</strong> mata kuliah ini.</p>
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
  getCourses, createCourse, updateCourse, deleteCourse,
  getPrograms, getCpls,
  getCourseCpls, mapCourseCpls, unmapCourseCpl,
  getCourseLecturers, getAvailableLecturers, assignCourseLecturers, unassignCourseLecturer,
} from '@/api/admin'

const rows = ref<any[]>([])
const programList = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const filterProgram = ref<number | ''>('')
const page = ref(1)
const total = ref(0)
const limit = 20
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit)))

const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)

const defaultForm = () => ({
  program_id: (filterProgram.value as number) || 0,
  kode_mk: '', nama_id: '', nama_zh: '',
  sks: 3, semester: 1, status_mk: 'wajib', deskripsi: '',
})
const form = ref(defaultForm())

// ── Mapping state (UC-14e) ──────────────────────────────────────────────────
const expandedId = ref<number | null>(null)
const availableCpls = ref<any[]>([])
const selectedCplIds = ref<Set<number>>(new Set())
const originalCplIds = ref<Set<number>>(new Set())
const mappingLoading = ref(false)
const mappingSaving = ref(false)

// ── Dosen Pengampu state ────────────────────────────────────────────────────
const expandedDosenId = ref<number | null>(null)
const availableLecturers = ref<any[]>([])
const selectedLecturerIds = ref<Set<string>>(new Set())
const originalLecturerIds = ref<Set<string>>(new Set())
const dosenLoading = ref(false)
const dosenSaving = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const res = await getCourses({
      page: page.value, limit,
      program_id: filterProgram.value || undefined,
      search: search.value || undefined,
    })
    rows.value = res.data.data
    total.value = res.data.total
    if (expandedId.value && !rows.value.find((r: any) => r.id === expandedId.value)) {
      expandedId.value = null
    }
    if (expandedDosenId.value && !rows.value.find((r: any) => r.id === expandedDosenId.value)) {
      expandedDosenId.value = null
    }
  } finally { loading.value = false }
}

onMounted(async () => {
  try {
    const res = await getPrograms({ limit: 500 })
    programList.value = res.data.data
  } catch { /* tetap lanjut meski dropdown gagal */ }
  await fetchData()
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
    if (editing.value) await updateCourse(editing.value.id, form.value)
    else await createCourse(form.value)
    showModal.value = false
    await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try {
    await deleteCourse(deleteTarget.value.id)
    showConfirm.value = false
    if (expandedId.value === deleteTarget.value.id) expandedId.value = null
    await fetchData()
  } finally { saving.value = false }
}

// ── Mapping CPL (UC-14e) handlers ──────────────────────────────────────────
async function toggleMapping(course: any) {
  if (expandedId.value === course.id) { expandedId.value = null; return }
  expandedDosenId.value = null
  expandedId.value = course.id
  mappingLoading.value = true
  selectedCplIds.value = new Set()
  originalCplIds.value = new Set()
  availableCpls.value = []
  try {
    const [cplsRes, mappedRes] = await Promise.all([
      getCpls({ program_id: course.program_id }),
      getCourseCpls(course.id),
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

async function saveMapping(courseId: number) {
  mappingSaving.value = true
  try {
    const toAdd = [...selectedCplIds.value].filter(id => !originalCplIds.value.has(id))
    const toRemove = [...originalCplIds.value].filter(id => !selectedCplIds.value.has(id))
    const ops: Promise<any>[] = []
    if (toAdd.length) ops.push(mapCourseCpls(courseId, toAdd))
    toRemove.forEach(id => ops.push(unmapCourseCpl(courseId, id)))
    await Promise.all(ops)
    originalCplIds.value = new Set(selectedCplIds.value)
  } finally { mappingSaving.value = false }
}

// ── Dosen Pengampu handlers ─────────────────────────────────────────────────
async function toggleDosen(course: any) {
  if (expandedDosenId.value === course.id) { expandedDosenId.value = null; return }
  expandedId.value = null
  expandedDosenId.value = course.id
  dosenLoading.value = true
  availableLecturers.value = []
  selectedLecturerIds.value = new Set()
  originalLecturerIds.value = new Set()
  try {
    const [availRes, assignedRes] = await Promise.all([
      getAvailableLecturers(course.id),
      getCourseLecturers(course.id),
    ])
    availableLecturers.value = availRes.data
    const assigned: string[] = assignedRes.data.map((d: any) => d.id)
    selectedLecturerIds.value = new Set(assigned)
    originalLecturerIds.value = new Set(assigned)
  } finally { dosenLoading.value = false }
}

function toggleLecturer(uid: string) {
  const s = new Set(selectedLecturerIds.value)
  s.has(uid) ? s.delete(uid) : s.add(uid)
  selectedLecturerIds.value = s
}

async function saveDosen(courseId: number) {
  dosenSaving.value = true
  try {
    const toAdd = [...selectedLecturerIds.value].filter(id => !originalLecturerIds.value.has(id))
    const toRemove = [...originalLecturerIds.value].filter(id => !selectedLecturerIds.value.has(id))
    const ops: Promise<any>[] = []
    if (toAdd.length) ops.push(assignCourseLecturers(courseId, toAdd))
    toRemove.forEach(id => ops.push(unassignCourseLecturer(courseId, id)))
    await Promise.all(ops)
    originalLecturerIds.value = new Set(selectedLecturerIds.value)
  } finally { dosenSaving.value = false }
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a365d; }
.toolbar { display: flex; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.search-input { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; min-width: 220px; }
.ml-8 { margin-left: 8px; }
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
.tag { background: #f0fff4; color: #276749; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.status-active { color: #38a169; font-size: 12px; font-weight: 600; }
.status-inactive { color: #e53e3e; font-size: 12px; font-weight: 600; }
.btn-primary { background: #1a365d; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-edit { background: #ebf8ff; color: #2b6cb0; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; }
.btn-map { background: #faf5ff; color: #6b46c1; border: 1px solid #d6bcfa; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; font-weight: 600; }
.btn-map.active { background: #6b46c1; color: #fff; border-color: #6b46c1; }
.btn-dosen { background: #f0fff4; color: #276749; border: 1px solid #9ae6b4; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; font-weight: 600; }
.btn-dosen.active { background: #276749; color: #fff; border-color: #276749; }
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
/* ── Dosen Pengampu panel (hijau) ── */
.dosen-row td { background: #f0fff4 !important; border-bottom: 2px solid #9ae6b4 !important; }
.dosen-title { color: #22543d; }
.dosen-subtitle { color: #38a169; }
.btn-save-dosen { background: #276749; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-size: 13px; cursor: pointer; white-space: nowrap; flex-shrink: 0; }
.btn-save-dosen:disabled { opacity: 0.5; cursor: not-allowed; }
.dosen-item { border-color: #c6f6d5; }
.dosen-item.checked { border-color: #276749; background: #f0fff4; }
.dosen-item:hover { border-color: #48bb78; }
.dosen-checkbox { accent-color: #276749; }
/* ── Pagination & Modal ── */
.pagination { display: flex; align-items: center; gap: 12px; padding: 16px 0; font-size: 13px; color: #718096; }
.pagination button { padding: 6px 12px; border: 1px solid #e2e8f0; background: #fff; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: 12px; padding: 28px; width: 620px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
.modal-sm { width: 400px; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a365d; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 12px; font-weight: 600; color: #4a5568; }
.form-input { padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; width: 100%; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.confirm-text { font-size: 14px; color: #4a5568; margin-bottom: 20px; line-height: 1.6; }
</style>
