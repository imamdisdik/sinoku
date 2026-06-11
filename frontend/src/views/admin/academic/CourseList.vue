<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Mata Kuliah</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah</button>
    </div>

    <div class="toolbar">
      <select v-model="filterProgram" @change="page=1;fetchData()" class="search-input">
        <option value="">Semua Program Studi</option>
        <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama_singkat }} — {{ p.nama }}</option>
      </select>
      <input v-model="search" placeholder="Cari nama / kode MK..." class="search-input" @input="fetchData" style="margin-left:8px" />
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Kode MK</th><th>Nama (ID)</th><th>Nama (中文)</th><th>SKS</th><th>Sem.</th><th>Jenis</th><th>Status</th><th>Aksi</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="8" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="8" class="center">Belum ada data</td></tr>
          <tr v-for="c in rows" :key="c.id">
            <td><span class="badge">{{ c.kode_mk }}</span></td>
            <td>{{ c.nama_id }}</td>
            <td style="color:#718096">{{ c.nama_zh }}</td>
            <td class="center-cell">{{ c.sks }}</td>
            <td class="center-cell">{{ c.semester }}</td>
            <td><span class="tag">{{ c.status_mk }}</span></td>
            <td><span :class="c.is_active ? 'status-active':'status-inactive'">{{ c.is_active?'Aktif':'Nonaktif' }}</span></td>
            <td>
              <button class="btn-edit" @click="openEdit(c)">Edit</button>
              <button class="btn-delete" @click="confirmDelete(c)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button :disabled="page<=1" @click="page--;fetchData()">&#8592;</button>
      <span>Halaman {{ page }} dari {{ totalPages }}</span>
      <button :disabled="page>=totalPages" @click="page++;fetchData()">&#8594;</button>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} Mata Kuliah</h2>
        <form @submit.prevent="save">
          <div class="form-grid">
            <div class="form-group" style="grid-column:1/-1">
              <label>Program Studi *</label>
              <select v-model.number="form.program_id" required class="form-input">
                <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama }}</option>
              </select>
            </div>
            <div class="form-group"><label>Kode MK *</label><input v-model="form.kode_mk" required class="form-input" /></div>
            <div class="form-group"><label>SKS *</label><input v-model.number="form.sks" type="number" min="1" max="6" required class="form-input" /></div>
            <div class="form-group" style="grid-column:1/-1"><label>Nama Indonesia *</label><input v-model="form.nama_id" required class="form-input" /></div>
            <div class="form-group" style="grid-column:1/-1"><label>Nama 中文 *</label><input v-model="form.nama_zh" required class="form-input" /></div>
            <div class="form-group"><label>Semester *</label><input v-model.number="form.semester" type="number" min="1" max="8" required class="form-input" /></div>
            <div class="form-group">
              <label>Jenis MK</label>
              <select v-model="form.status_mk" class="form-input">
                <option value="wajib">Wajib</option><option value="pilihan">Pilihan</option><option value="mbkm">MBKM</option>
              </select>
            </div>
            <div class="form-group" style="grid-column:1/-1"><label>Deskripsi</label><textarea v-model="form.deskripsi" class="form-input" rows="3"></textarea></div>
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
        <h2 class="modal-title">Hapus Mata Kuliah?</h2>
        <p class="confirm-text">Yakin hapus <strong>{{ deleteTarget?.nama_id }}</strong>?</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm=false">Batal</button>
          <button class="btn-delete" @click="doDelete" :disabled="saving">Hapus</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getCourses, createCourse, updateCourse, deleteCourse, getPrograms } from '@/api/admin'

const rows = ref<any[]>([])
const programList = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const filterProgram = ref<number|''>('')
const page = ref(1)
const total = ref(0)
const limit = 20
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit)))
const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)
const defaultForm = () => ({ program_id: 0, kode_mk: '', nama_id: '', nama_zh: '', sks: 3, semester: 1, status_mk: 'wajib', deskripsi: '' })
const form = ref(defaultForm())

async function fetchData() {
  loading.value = true
  try {
    const res = await getCourses({ page: page.value, limit, program_id: filterProgram.value || undefined, search: search.value || undefined })
    rows.value = res.data.data; total.value = res.data.total
  } finally { loading.value = false }
}

onMounted(async () => {
  const res = await getPrograms({ limit: 200 })
  programList.value = res.data.data
  await fetchData()
})

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
function openEdit(c: any) { editing.value = c; form.value = { ...c }; showModal.value = true }
function confirmDelete(c: any) { deleteTarget.value = c; showConfirm.value = true }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateCourse(editing.value.id, form.value)
    else await createCourse(form.value)
    showModal.value = false; await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try { await deleteCourse(deleteTarget.value.id); showConfirm.value = false; await fetchData() }
  finally { saving.value = false }
}
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.toolbar{margin-bottom:16px;display:flex;align-items:center}
.search-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:14px;min-width:240px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748}
.data-table tr:last-child td{border-bottom:none}
.center{text-align:center;color:#718096}
.center-cell{text-align:center}
.badge{background:#ebf8ff;color:#2b6cb0;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.tag{background:#f0fff4;color:#276749;padding:2px 8px;border-radius:4px;font-size:12px}
.status-active{color:#38a169;font-size:12px;font-weight:600}
.status-inactive{color:#e53e3e;font-size:12px;font-weight:600}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-edit{background:#ebf8ff;color:#2b6cb0;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer;margin-right:4px}
.btn-delete{background:#fff5f5;color:#e53e3e;border:none;padding:4px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.pagination{display:flex;align-items:center;gap:12px;padding:16px 0;font-size:13px;color:#718096}
.pagination button{padding:6px 12px;border:1px solid #e2e8f0;background:#fff;border-radius:6px;cursor:pointer}
.pagination button:disabled{opacity:.4;cursor:not-allowed}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:200}
.modal{background:#fff;border-radius:12px;padding:28px;width:600px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-sm{width:380px}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group{display:flex;flex-direction:column;gap:6px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:100%}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.confirm-text{font-size:14px;color:#4a5568;margin-bottom:20px;line-height:1.6}
</style>
