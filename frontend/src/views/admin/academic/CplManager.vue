<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">CPL (Capaian Pembelajaran Lulusan)</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah CPL</button>
    </div>

    <div class="toolbar">
      <ScopeFilter @change="onScope" />
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Kode CPL</th><th>Deskripsi (ID)</th><th>Deskripsi (中文)</th><th>Kategori</th><th>Status</th><th>Aksi</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada data CPL.</td></tr>
          <tr v-for="c in paged" :key="c.id">
            <td><span class="badge">{{ c.kode_cpl }}</span></td>
            <td>{{ c.deskripsi_id }}</td>
            <td style="color:#718096;font-size:12px">{{ c.deskripsi_zh }}</td>
            <td><span class="tag">{{ c.kategori }}</span></td>
            <td><span :class="c.is_active?'status-active':'status-inactive'">{{ c.is_active?'Aktif':'Nonaktif' }}</span></td>
            <td>
              <button class="btn-edit" @click="openEdit(c)">Edit</button>
              <button class="btn-delete" @click="confirmDelete(c)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pagination v-model:page="page" :total-pages="totalPages" />

    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} CPL</h2>
        <form @submit.prevent="save">
          <div class="form-group mb-16" style="grid-column:1/-1">
            <label>Program Studi *</label>
            <select v-model.number="form.program_id" required class="form-input">
              <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama }}</option>
            </select>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label>Kode CPL *</label>
              <input v-model="form.kode_cpl" required class="form-input" placeholder="CPL-01" />
            </div>
            <div class="form-group">
              <label>Kategori *</label>
              <select v-model="form.kategori" required class="form-input">
                <option value="sikap">Sikap</option>
                <option value="pengetahuan">Pengetahuan</option>
                <option value="keterampilan">Keterampilan</option>
              </select>
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
        <h2 class="modal-title">Hapus CPL?</h2>
        <p class="confirm-text">Yakin hapus CPL <strong>{{ deleteTarget?.kode_cpl }}</strong>?</p>
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
import { getCpls, createCpl, updateCpl, deleteCpl, getPrograms } from '@/api/admin'
import Pagination from '@/components/common/Pagination.vue'
import ScopeFilter from '@/components/common/ScopeFilter.vue'
import { usePagination } from '@/composables/usePagination'

type Scope = { university_id: number|null; faculty_id: number|null; program_id: number|null; course_id: number|null }
const rows = ref<any[]>([])
const { page, totalPages, paged } = usePagination(rows, 15)
const programList = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const scope = ref<Scope>({ university_id: null, faculty_id: null, program_id: null, course_id: null })
function onScope(s: Scope) { scope.value = s; fetchData() }
const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)
// Auto-fill program_id dari filter yang aktif
const defaultForm = () => ({
  program_id: scope.value.program_id || 0,
  kode_cpl: '', deskripsi_id: '', deskripsi_zh: '', kategori: 'pengetahuan',
})
const form = ref(defaultForm())

async function fetchData() {
  loading.value = true
  try {
    // Filter drill-down: Prodi → per prodi; Fakultas → seluruh prodi fakultas; Univ → seluruh univ
    const params: any = {}
    if (scope.value.program_id) params.program_id = scope.value.program_id
    else if (scope.value.faculty_id) params.faculty_id = scope.value.faculty_id
    else if (scope.value.university_id) params.university_id = scope.value.university_id
    const res = await getCpls(params)
    rows.value = res.data
    page.value = 1
  } finally { loading.value = false }
}

onMounted(async () => {
  try {
    const res = await getPrograms({ limit: 500 })
    programList.value = res.data.data
  } catch { /* tetap lanjut meski dropdown gagal */ }
  await fetchData()  // tampilkan semua CPL saat halaman dibuka
})

function openCreate() {
  editing.value = null
  // Auto-set program_id dari filter aktif agar user tidak perlu pilih ulang
  form.value = defaultForm()
  showModal.value = true
}
function openEdit(c: any) { editing.value = c; form.value = { ...c }; showModal.value = true }
function confirmDelete(c: any) { deleteTarget.value = c; showConfirm.value = true }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateCpl(editing.value.id, form.value)
    else await createCpl(form.value)
    showModal.value = false; await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try { await deleteCpl(deleteTarget.value.id); showConfirm.value = false; await fetchData() }
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
.badge{background:#ebf8ff;color:#2b6cb0;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.tag{background:#faf5ff;color:#6b46c1;padding:2px 8px;border-radius:4px;font-size:12px}
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
