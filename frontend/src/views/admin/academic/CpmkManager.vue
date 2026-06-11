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
        <thead><tr><th>Kode CPMK</th><th>Deskripsi (ID)</th><th>Deskripsi (中文)</th><th>Bobot (%)</th><th>Status</th><th>Aksi</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada data. Pilih mata kuliah terlebih dahulu.</td></tr>
          <tr v-for="c in rows" :key="c.id">
            <td><span class="badge">{{ c.kode_cpmk }}</span></td>
            <td>{{ c.deskripsi_id }}</td>
            <td style="color:#718096;font-size:12px">{{ c.deskripsi_zh }}</td>
            <td class="center-cell">{{ c.bobot_persen }}%</td>
            <td><span :class="c.is_active?'status-active':'status-inactive'">{{ c.is_active?'Aktif':'Nonaktif' }}</span></td>
            <td>
              <button class="btn-edit" @click="openEdit(c)">Edit</button>
              <button class="btn-delete" @click="confirmDelete(c)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} CPMK</h2>
        <form @submit.prevent="save">
          <div class="form-group mb-16">
            <label>Mata Kuliah *</label>
            <select v-model.number="form.course_id" required class="form-input">
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
              <input v-model.number="form.bobot_persen" type="number" min="0" max="100" required class="form-input" />
            </div>
            <div class="form-group" style="grid-column:1/-1">
              <label>Deskripsi Indonesia *</label>
              <textarea v-model="form.deskripsi_id" required class="form-input" rows="3"></textarea>
            </div>
            <div class="form-group" style="grid-column:1/-1">
              <label>Deskripsi 中文 *</label>
              <textarea v-model="form.deskripsi_zh" required class="form-input" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving?'Menyimpan...':'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm=false">
      <div class="modal modal-sm">
        <h2 class="modal-title">Hapus CPMK?</h2>
        <p class="confirm-text">Yakin hapus CPMK <strong>{{ deleteTarget?.kode_cpmk }}</strong>?</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm=false">Batal</button>
          <button class="btn-delete" @click="doDelete" :disabled="saving">Hapus</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCpmks, createCpmk, updateCpmk, deleteCpmk, getCourses } from '@/api/admin'

const rows = ref<any[]>([])
const courseList = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const filterCourse = ref<number|''>('')
const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)
const defaultForm = () => ({ course_id: 0, kode_cpmk: '', deskripsi_id: '', deskripsi_zh: '', bobot_persen: 0 })
const form = ref(defaultForm())

async function fetchData() {
  if (!filterCourse.value) { rows.value = []; return }
  loading.value = true
  try {
    const res = await getCpmks({ course_id: filterCourse.value })
    rows.value = res.data
  } finally { loading.value = false }
}

onMounted(async () => {
  const res = await getCourses({ limit: 200 })
  courseList.value = res.data.data
})

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
function openEdit(c: any) { editing.value = c; form.value = { ...c }; showModal.value = true }
function confirmDelete(c: any) { deleteTarget.value = c; showConfirm.value = true }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateCpmk(editing.value.id, form.value)
    else await createCpmk(form.value)
    showModal.value = false; await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try { await deleteCpmk(deleteTarget.value.id); showConfirm.value = false; await fetchData() }
  finally { saving.value = false }
}
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{margin-bottom:16px}
.search-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:14px;min-width:280px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748}
.data-table tr:last-child td{border-bottom:none}
.center{text-align:center;color:#718096}
.center-cell{text-align:center}
.badge{background:#ebf8ff;color:#2b6cb0;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.status-active{color:#38a169;font-size:12px;font-weight:600}
.status-inactive{color:#e53e3e;font-size:12px;font-weight:600}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-edit{background:#ebf8ff;color:#2b6cb0;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.mb-16{margin-bottom:16px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:580px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-sm{width:380px}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group{display:flex;flex-direction:column;gap:6px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.confirm-text{font-size:14px;color:#4a5568;margin-bottom:20px;line-height:1.6}
</style>
