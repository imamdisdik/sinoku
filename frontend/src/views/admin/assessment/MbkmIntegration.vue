<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Integrasi MBKM</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah Program MBKM</button>
    </div>

    <!-- Filter -->
    <div class="toolbar">
      <select v-model.number="filterCourse" @change="fetchData" class="filter-input">
        <option :value="null">Semua Mata Kuliah</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
      </select>
      <select v-model="filterActive" @change="fetchData" class="filter-input">
        <option value="">Semua Status</option>
        <option value="true">Aktif</option>
        <option value="false">Tidak Aktif</option>
      </select>
    </div>

    <!-- Tabel -->
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Mata Kuliah</th>
            <th>Jenis Program</th>
            <th>Nama Mitra</th>
            <th>SKS Diakui</th>
            <th>Tahun Akademik</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="7" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="7" class="center">Belum ada data MBKM</td></tr>
          <tr v-for="r in rows" :key="r.id">
            <td class="meta">{{ courseName(r.course_id) }}</td>
            <td><span class="badge-program">{{ r.jenis_program }}</span></td>
            <td><strong>{{ r.nama_mitra }}</strong></td>
            <td style="text-align:center;font-weight:700">{{ r.sks_diakui }} SKS</td>
            <td class="meta">{{ r.tahun_akademik }}</td>
            <td>
              <button :class="r.is_active ? 'badge-aktif' : 'badge-nonaktif'" @click="doToggle(r)" style="cursor:pointer;border:none">
                {{ r.is_active ? 'Aktif' : 'Nonaktif' }}
              </button>
            </td>
            <td>
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
        <h2 class="modal-title">{{ editing ? 'Edit Program MBKM' : 'Tambah Program MBKM' }}</h2>
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
              <label>Jenis Program *</label>
              <select v-model="form.jenis_program" required class="form-input">
                <option value="">— Pilih —</option>
                <option v-for="j in jenisList" :key="j" :value="j">{{ j }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Tahun Akademik *</label>
              <input v-model="form.tahun_akademik" required class="form-input" placeholder="2024/2025" />
            </div>
          </div>
          <div class="form-group">
            <label>Nama Mitra *</label>
            <input v-model="form.nama_mitra" required class="form-input" placeholder="Nama institusi/perusahaan mitra" />
          </div>
          <div class="form-group">
            <label>SKS yang Diakui *</label>
            <input v-model.number="form.sks_diakui" type="number" min="1" max="24"
              required class="form-input" placeholder="1–24 SKS" />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="form.deskripsi" class="form-input" rows="3"
              placeholder="Deskripsi singkat program dan kegiatan yang dilakukan..." />
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
import { useUiStore } from '@/stores/ui'
import { getMbkmList, createMbkm, updateMbkm, deleteMbkm, toggleMbkm, getCourses } from '@/api/admin'

const ui = useUiStore()

const rows = ref<any[]>([])
const courses = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<any>(null)
const filterCourse = ref<number | null>(null)
const filterActive = ref('')

const jenisList = [
  'Magang/Praktik Kerja',
  'Proyek Kemanusiaan',
  'Asistensi Mengajar',
  'Penelitian/Riset',
  'Wirausaha',
  'Studi/Proyek Independen',
  'Pertukaran Pelajar',
  'KKN Tematik',
]

const defaultForm = () => ({
  course_id: null as number | null,
  jenis_program: '',
  nama_mitra: '',
  deskripsi: '',
  sks_diakui: 4,
  tahun_akademik: '',
})
const form = ref(defaultForm())

function courseName(id: number) {
  const c = courses.value.find(c => c.id === id)
  return c ? `${c.kode_mk} — ${c.nama_id}` : `MK #${id}`
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (filterCourse.value) params.course_id = filterCourse.value
    if (filterActive.value !== '') params.is_active = filterActive.value === 'true'
    const res = await getMbkmList(params)
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
    jenis_program: r.jenis_program,
    nama_mitra: r.nama_mitra,
    deskripsi: r.deskripsi ?? '',
    sks_diakui: r.sks_diakui,
    tahun_akademik: r.tahun_akademik,
  }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    const body = { ...form.value, deskripsi: form.value.deskripsi || null }
    if (editing.value) await updateMbkm(editing.value.id, body)
    else await createMbkm(body)
    showModal.value = false
    ui.showToast('Data MBKM berhasil disimpan', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { saving.value = false }
}

async function doToggle(r: any) {
  try {
    const res = await toggleMbkm(r.id)
    r.is_active = res.data.is_active
    ui.showToast(`Status diubah menjadi ${res.data.is_active ? 'Aktif' : 'Nonaktif'}`, 'success')
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal mengubah status', 'error')
  }
}

async function doDelete(r: any) {
  if (!confirm(`Hapus program MBKM "${r.nama_mitra}"?`)) return
  try {
    await deleteMbkm(r.id)
    ui.showToast('Data MBKM dihapus', 'success')
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
.toolbar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748;vertical-align:middle}
.center{text-align:center;color:#718096}
.meta{color:#718096;font-size:12px}
.badge-program{background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;white-space:nowrap}
.badge-aktif{background:#d1fae5;color:#065f46;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700}
.badge-nonaktif{background:#f3f4f6;color:#6b7280;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
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
