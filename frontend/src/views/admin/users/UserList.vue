<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Kelola Akun</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah Akun</button>
    </div>

    <div class="toolbar">
      <select v-model="filterRole" @change="() => { page = 1; fetchData() }" class="search-input">
        <option value="">Semua Role</option>
        <option value="admin_universitas">Admin Universitas</option>
        <option value="admin_fakultas">Admin Fakultas</option>
        <option value="admin_prodi">Admin Prodi</option>
        <option value="dosen">Dosen</option>
      </select>
      <select v-model="filterActive" @change="() => { page = 1; fetchData() }" class="search-input">
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
            <th>Fakultas</th>
            <th>Program Studi</th>
            <th>Status</th>
            <th>Login Terakhir</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="9" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="9" class="center">Belum ada akun</td></tr>
          <tr v-for="u in rows" :key="u.id">
            <td>
              <div class="user-name">{{ u.full_name }}</div>
            </td>
            <td class="email-cell">{{ u.email }}</td>
            <td><span :class="roleBadge(u.role)">{{ roleLabel(u.role) }}</span></td>
            <td>{{ univName(u.university_id) || '—' }}</td>
            <td>{{ facultyName(u.faculty_id) || '—' }}</td>
            <td>{{ programName(u.program_id) || '—' }}</td>
            <td><span :class="u.is_active ? 'status-active' : 'status-inactive'">{{ u.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
            <td class="meta-cell">{{ u.last_login ? formatDate(u.last_login) : 'Belum pernah' }}</td>
            <td>
              <button class="btn-edit" @click="openEdit(u)">Edit</button>
              <button :class="u.is_active ? 'btn-toggle-off' : 'btn-activate'" @click="doToggle(u)">
                {{ u.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
              </button>
              <button class="btn-delete" @click="confirmDelete(u)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
      <!-- Paginasi -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="page === 1" @click="changePage(page - 1)">‹ Prev</button>
        <span class="page-info">Hal {{ page }} / {{ totalPages }} ({{ total }} akun)</span>
        <button class="page-btn" :disabled="page === totalPages" @click="changePage(page + 1)">Next ›</button>
      </div>
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
            <div class="form-group" v-if="!editing">
              <label>Role *</label>
              <select v-model="form.role" required class="form-input">
                <option v-for="r in creatableRoles" :key="r" :value="r">{{ roleLabel(r) }}</option>
              </select>
            </div>
            <div class="form-group" v-if="isSuperadmin">
              <label>Universitas</label>
              <select v-model.number="form.university_id" class="form-input">
                <option :value="null">— Pilih Universitas —</option>
                <option v-for="u in univList" :key="u.id" :value="u.id">{{ u.nama_singkat }} — {{ u.nama }}</option>
              </select>
            </div>
            <div class="form-group" v-if="showFacultyField">
              <label>Fakultas</label>
              <select v-model.number="form.faculty_id" class="form-input">
                <option :value="null">— Pilih Fakultas —</option>
                <option v-for="f in filteredFaculties" :key="f.id" :value="f.id">{{ f.nama_singkat }} — {{ f.nama }}</option>
              </select>
            </div>
            <div class="form-group" v-if="showProgramField">
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

    <!-- Confirm Hapus -->
    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm=false">
      <div class="modal modal-sm">
        <h2 class="modal-title">Hapus Akun?</h2>
        <p class="confirm-text">
          Yakin hapus akun <strong>{{ deleteTarget?.full_name }}</strong> ({{ deleteTarget?.email }})?<br>
          ⚠️ Tindakan ini <strong>permanen</strong>. Penugasan dosen pengampu & sesi login akun ini akan ikut terhapus.
        </p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirm=false">Batal</button>
          <button class="btn-delete" @click="doDelete" :disabled="saving">Hapus</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { getUsers, createUser, updateUser, toggleUserActive, deleteUser, getUniversities, getFaculties, getPrograms } from '@/api/admin'

const auth = useAuthStore()
const { user, role: myRole, isSuperadmin, isAdminUniversitas, isAdminFakultas } = storeToRefs(auth)
const ui = useUiStore()

// Peran yang boleh dibuat oleh pengelola saat ini (hierarki turun)
const CREATABLE: Record<string, string[]> = {
  superadmin: ['admin_universitas', 'admin_fakultas', 'admin_prodi', 'dosen'],
  admin_universitas: ['admin_fakultas', 'admin_prodi', 'dosen'],
  admin_fakultas: ['admin_prodi', 'dosen'],
  admin_prodi: ['dosen'],
}
const creatableRoles = computed(() => CREATABLE[myRole.value] ?? [])

const rows = ref<any[]>([])
const univList = ref<any[]>([])
const facultyListData = ref<any[]>([])
const programList = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const showConfirm = ref(false)
const deleteTarget = ref<any>(null)
const editing = ref<any>(null)
const filterRole = ref('')
const filterActive = ref('')
const search = ref('')
const page = ref(1)
const total = ref(0)
const limit = 20
let searchTimer: ReturnType<typeof setTimeout>

const defaultForm = () => ({
  full_name: '',
  email: '',
  password: '',
  role: creatableRoles.value[creatableRoles.value.length - 1] ?? 'dosen',  // default: peran terendah (dosen)
  university_id: isSuperadmin.value ? null : (user.value?.university_id ?? null),
  faculty_id: null as number | null,
  program_id: null as number | null,
})
const form = ref(defaultForm())

// Tampilkan field cakupan sesuai peran yang dibuat + kewenangan pengelola
const showFacultyField = computed(() =>
  (isSuperadmin.value || isAdminUniversitas.value) &&
  ['admin_fakultas', 'admin_prodi', 'dosen'].includes(form.value.role)
)
const showProgramField = computed(() =>
  (isSuperadmin.value || isAdminUniversitas.value || isAdminFakultas.value) &&
  ['admin_prodi', 'dosen'].includes(form.value.role)
)

const filteredFaculties = computed(() =>
  form.value.university_id
    ? facultyListData.value.filter((f: any) => f.university_id === form.value.university_id)
    : facultyListData.value
)
const filteredPrograms = computed(() => {
  let list = programList.value
  if (form.value.faculty_id) list = list.filter((p: any) => p.faculty_id === form.value.faculty_id)
  else if (form.value.university_id) list = list.filter((p: any) => p.university_id === form.value.university_id)
  return list
})

const totalPages = computed(() => Math.ceil(total.value / limit))

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: page.value, limit }
    if (filterRole.value) params.role = filterRole.value
    if (filterActive.value !== '') params.is_active = filterActive.value
    if (search.value) params.search = search.value
    const res = await getUsers(params)
    rows.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

function onSearch() {
  clearTimeout(searchTimer)
  page.value = 1
  searchTimer = setTimeout(fetchData, 400)
}

function changePage(p: number) { page.value = p; fetchData() }

function univName(id: number | null) {
  return univList.value.find((u: any) => u.id === id)?.nama_singkat ?? ''
}
function programName(id: number | null) {
  return programList.value.find((p: any) => p.id === id)?.nama_singkat ?? ''
}
function facultyName(id: number | null) {
  return facultyListData.value.find((f: any) => f.id === id)?.nama_singkat ?? ''
}
function roleLabel(role: string) {
  return ({
    superadmin: 'Super Admin', admin_universitas: 'Admin Universitas',
    admin_fakultas: 'Admin Fakultas', admin_prodi: 'Admin Prodi', dosen: 'Dosen',
  } as Record<string, string>)[role] ?? role
}
function roleBadge(role: string) {
  return ({
    superadmin: 'badge-sa', admin_universitas: 'badge-admin',
    admin_fakultas: 'badge-admin', admin_prodi: 'badge-prodi', dosen: 'badge-dosen',
  } as Record<string, string>)[role] ?? 'badge-dosen'
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
  form.value = { full_name: u.full_name, email: u.email, password: '', role: u.role, university_id: u.university_id, faculty_id: u.faculty_id ?? null, program_id: u.program_id }
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

function confirmDelete(u: any) { deleteTarget.value = u; showConfirm.value = true }

async function doDelete() {
  saving.value = true
  try {
    await deleteUser(deleteTarget.value.id)
    showConfirm.value = false
    ui.showToast('Akun dihapus', 'success')
    await fetchData()
  } catch (e: any) {
    ui.showToast(e.response?.data?.detail || 'Gagal menghapus', 'error')
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
    getFaculties({ limit: 500 }).then(r => { facultyListData.value = r.data.data }),
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
.badge-prodi { background:#fffaf0; color:#b7791f; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700 }
.badge-dosen { background:#f0fff4; color:#276749; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700 }
.status-active { color:#38a169; font-size:12px; font-weight:600 }
.status-inactive { color:#e53e3e; font-size:12px; font-weight:600 }
.btn-primary { background:#1a365d; color:#fff; border:none; padding:8px 16px; border-radius:6px; font-size:13px; cursor:pointer }
.btn-edit { background:#ebf8ff; color:#2b6cb0; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer; margin-right:4px }
.btn-delete { background:#fff5f5; color:#e53e3e; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer }
.btn-activate { background:#f0fff4; color:#276749; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer }
.btn-toggle-off { background:#fffaf0; color:#b7791f; border:none; padding:4px 10px; border-radius:4px; font-size:12px; cursor:pointer; margin-right:4px }
.btn-cancel { background:#f7fafc; color:#4a5568; border:1px solid #e2e8f0; padding:8px 16px; border-radius:6px; font-size:13px; cursor:pointer }
.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:200 }
.modal { background:#fff; border-radius:12px; padding:28px; width:540px; max-width:95vw; max-height:90vh; overflow-y:auto }
.modal-sm { width:400px }
.confirm-text { font-size:14px; color:#4a5568; margin-bottom:20px; line-height:1.6 }
.modal-title { font-size:18px; font-weight:700; color:#1a365d; margin-bottom:20px }
.form-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px }
.form-group { display:flex; flex-direction:column; gap:6px }
.form-group label { font-size:12px; font-weight:600; color:#4a5568 }
.form-input { padding:8px 10px; border:1px solid #e2e8f0; border-radius:6px; font-size:13px; width:100% }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px }
.pagination { display:flex; align-items:center; justify-content:center; gap:12px; padding:14px }
.page-btn { padding:6px 14px; border:1px solid #e2e8f0; border-radius:6px; cursor:pointer; background:#fff; font-size:13px }
.page-btn:disabled { opacity:.4; cursor:not-allowed }
.page-info { font-size:13px; color:#718096 }
</style>
