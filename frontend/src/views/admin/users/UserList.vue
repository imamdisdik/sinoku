<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Kelola Akun</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah Akun</button>
    </div>

    <div class="toolbar">
      <select v-model="filterRole" @change="fetchData" class="search-input">
        <option value="">Semua Role</option>
        <option value="admin">Admin Universitas</option>
        <option value="dosen">Dosen</option>
      </select>
      <select v-model="filterActive" @change="fetchData" class="search-input">
        <option value="">Semua Status</option>
        <option value="true">Aktif</option>
        <option value="false">Nonaktif</option>
      </select>
      <input v-model="search" @input="onSearch" class="search-input" placeholder="Cari nama / email..." style="min-width:220px;" />
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nama</th>
            <th>Email</th>
            <th>Role</th>
            <th>Universitas</th>
            <th>Program Studi</th>
            <th>Status</th>
            <th>Login Terakhir</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="8" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="8" class="center">Belum ada akun</td></tr>
          <tr v-for="u in rows" :key="u.id">
            <td>
              <div class="user-name">{{ u.full_name }}</div>
            </td>
            <td class="email-cell">{{ u.email }}</td>
            <td><span :class="roleBadge(u.role)">{{ roleLabel(u.role) }}</span></td>
            <td>{{ univName(u.university_id) || '—' }}</td>
            <td>{{ programName(u.program_id) || '—' }}</td>
            <td><span :class="u.is_active ? 'status-active' : 'status-inactive'">{{ u.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
            <td class="meta-cell">{{ u.last_login ? formatDate(u.last_login) : 'Belum pernah' }}</td>
            <td>
              <button class="btn-edit" @click="openEdit(u)">Edit</button>
              <button :class="u.is_active ? 'btn-delete' : 'btn-activate'" @click="doToggle(u)">
                {{ u.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Create/Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit Akun' : 'Tambah Akun' }}</h2>
        <form @submit.prevent="save">
          <div class="form-grid">
            <div class="form-group" style="grid-column:1/-1">
              <label>Nama Lengkap *</label>
              <input v-model="form.full_name" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Email *</label>
              <input v-model="form.email" type="email" required class="form-input" />
            </div>
            <div class="form-group">
              <label>{{ editing ? 'Password Baru (kosongkan jika tidak diubah)' : 'Password *' }}</label>
              <input v-model="form.password" type="password" :required="!editing" class="form-input" autocomplete="new-password" />
            </div>
            <div class="form-group" v-if="!editing && auth.isSuperadmin">
              <label>Role *</label>
              <select v-model="form.role" required class="form-input">
                <option value="admin">Admin Universitas</option>
                <option value="dosen">Dosen</option>
              </select>
            </div>
            <div class="form-group" v-if="auth.isSuperadmin">
              <label>Universitas</label>
              <select v-model.number="form.university_id" class="form-input">
                <option :value="null">— Pilih Universitas —</option>
                <option v-for="u in univList" :key="u.id" :value="u.id">{{ u.nama_singkat }} — {{ u.nama }}</option>
              </select>
            </div>
            <div class="form-group" v-if="form.role === 'dosen'">
              <label>Program Studi</label>
              <select v-model.number="form.program_id" class="form-input">
                <option :value="null">— Pilih Prodi —</option>
                <option v-for="p in filteredPrograms" :key="p.id" :value="p.id">{{ p.nama_singkat }} — {{ p.nama }}</option>
              </select>
            </div>
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { getUsers, createUser, updateUser, toggleUserActive, getUniversities, getPrograms } from '@/api/admin'

const auth = useAuthStore()
const ui = useUiStore()

const rows = ref<any[]>([])
const univList = ref<any[]>([])
const programList = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editing = ref<any>(null)
const filterRole = ref('')
const filterActive = ref('')
const search = ref('')
let searchTimer: ReturnType<typeof setTimeout>

const defaultForm = () => ({
  full_name: '',
  email: '',
  password: '',
  role: auth.isSuperadmin ? 'dosen' : 'dosen',
  university_id: auth.isSuperadmin ? null : (auth.user?.university_id ?? null),
  program_id: null as number | null,
})
const form = ref(defaultForm())

const filteredPrograms = computed(() =>
  form.value.university_id
    ? programList.value.filter((p: any) => p.university_id === form.value.university_id)
    : programList.value
)

async function fetchData() {
  loading.value = true
  try {
    const params: any = {}
    if (filterRole.value) params.role = filterRole.value
    if (filterActive.value !== '') params.is_active = filterActive.value
    if (search.value) params.search = search.value
    const res = await getUsers(params)
    rows.value = res.data
  } finally { loading.value = false }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchData, 400)
}

function univName(id: number | null) {
  return univList.value.find((u: any) => u.id === id)?.nama_singkat ?? ''
}
function programName(id: number | null) {
  return programList.value.find((p: any) => p.id === id)?.nama_singkat ?? ''
}
function roleLabel(role: string) {
  return { superadmin: 'Super Admin', admin: 'Admin Univ', dosen: 'Dosen' }[role] ?? role
}
function roleBadge(role: string) {
  return { superadmin: 'badge-sa', admin: 'badge-admin', dosen: 'badge-dosen' }[role] ?? 'badge-dosen'
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function openCreate() {
  editing.value = null
  form.value = defaultForm()
  showModal.value = true
}
function openEdit(u: any) {
  editing.value = u
  form.value = { full_name: u.full_name, email: u.email, password: '', role: u.role, university_id: u.university_id, program_id: u.program_id }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    const payload: any = { ...form.value }
    if (!payload.password) delete payload.password
    if (editing.value) await updateUser(editing.value.id, payload)
    else await createUser(payload)
    showModal.value = false
    ui.showToast('Akun berhasil disimpan', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menyimpan', 'error')
  } finally { saving.value = false }
}

async function doToggle(u: any) {
  try {
    await toggleUserActive(u.id)
    ui.showToast(`Akun ${u.is_active ? 'dinonaktifkan' : 'diaktifkan'}`, 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal', 'error')
  }
}

onMounted(async () => {
  await Promise.all([
    getUniversities({ limit: 500 }).then(r => { univList.value = r.data.data }),
    getPrograms({ limit: 500 }).then(r => { programList.value = r.data.data }),
  ]).catch(() => {})
  await fetchData()
})
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px }
.page-title { font-size:22px; font-weight:700; color:#1a365d }
.toolbar { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px }
.search-input { padding:8px 12px; border:1px solid #e2e8f0; border-radius:6px; font-size:13px }
.table-wrap { background:#fff; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,0.08); overflow:hidden }
.data-table { width:100%; border-collapse:collapse; font-size:13px }
.data-table th { background:#f7fafc; padding:10px 14px; text-align:left; font-weight:600; color:#4a5568; border-bottom:1px solid #e2e8f0 }
.data-table td { padding:10px 14px; border-bottom:1px solid #f0f4f8; color:#2d3748 }
.data-table tr:last-child td { border-bottom:none }
.center { text-align:center; color:#718096 }
.user-name { font-weight:600 }
.email-cell { color:#718096; font-size:12px }
.meta-cell { color:#718096; font-size:12px }
.badge-sa { background:#faf5ff; color:#553c9a; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700 }
.badge-admin { background:#ebf8ff; color:#2b6cb0; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700 }
.badge-dosen { background:#f0fff4; color:#276749; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700 }
.status-active { color:#38a169; font-size:12px; font-weight:600 }
.status-inactive { color:#e53e3e; font-size:12px; font-weight:600 }
.btn-primary { background:#1a365d; color:#fff; border:none; padding:8px 16px; border-radius:6px; font-size:13px; cursor:pointer }
.btn-edit { background:#ebf8ff; color:#2b6cb0; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer; margin-right:4px }
.btn-delete { background:#fff5f5; color:#e53e3e; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer }
.btn-activate { background:#f0fff4; color:#276749; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer }
.btn-cancel { background:#f7fafc; color:#4a5568; border:1px solid #e2e8f0; padding:8px 16px; border-radius:6px; font-size:13px; cursor:pointer }
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:200 }
.modal { background:#fff; border-radius:12px; padding:28px; width:540px; max-width:95vw; max-height:90vh; overflow-y:auto }
.modal-title { font-size:18px; font-weight:700; color:#1a365d; margin-bottom:20px }
.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px }
.form-group { display:flex; flex-direction:column; gap:6px }
.form-group label { font-size:12px; font-weight:600; color:#4a5568 }
.form-input { padding:8px 10px; border:1px solid #e2e8f0; border-radius:6px; font-size:13px; width:100% }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px }
</style>
