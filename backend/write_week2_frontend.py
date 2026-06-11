"""Week 2 frontend: Admin Layout + Dashboard + Academic CRUD pages"""
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "src")

files = {}

# ── api/admin.ts ─────────────────────────────────────────────────────────────
files["api/admin.ts"] = """import api from './client'

// Dashboard
export const getDashboardKpi = (params?: object) => api.get('/admin/dashboard/kpi', { params })
export const getProblemHeatmap = (params?: object) => api.get('/admin/dashboard/problem-heatmap', { params })

// Universities
export const getUniversities = (params?: object) => api.get('/admin/universities', { params })
export const createUniversity = (data: object) => api.post('/admin/universities', data)
export const updateUniversity = (id: number, data: object) => api.put(`/admin/universities/${id}`, data)
export const deleteUniversity = (id: number) => api.delete(`/admin/universities/${id}`)

// Programs
export const getPrograms = (params?: object) => api.get('/admin/programs', { params })
export const createProgram = (data: object) => api.post('/admin/programs', data)
export const updateProgram = (id: number, data: object) => api.put(`/admin/programs/${id}`, data)
export const deleteProgram = (id: number) => api.delete(`/admin/programs/${id}`)

// Courses
export const getCourses = (params?: object) => api.get('/admin/courses', { params })
export const createCourse = (data: object) => api.post('/admin/courses', data)
export const updateCourse = (id: number, data: object) => api.put(`/admin/courses/${id}`, data)
export const deleteCourse = (id: number) => api.delete(`/admin/courses/${id}`)

// CPL
export const getCpls = (params?: object) => api.get('/admin/cpls', { params })
export const createCpl = (data: object) => api.post('/admin/cpls', data)
export const updateCpl = (id: number, data: object) => api.put(`/admin/cpls/${id}`, data)
export const deleteCpl = (id: number) => api.delete(`/admin/cpls/${id}`)

// CPMK
export const getCpmks = (params?: object) => api.get('/admin/cpmks', { params })
export const createCpmk = (data: object) => api.post('/admin/cpmks', data)
export const updateCpmk = (id: number, data: object) => api.put(`/admin/cpmks/${id}`, data)
export const deleteCpmk = (id: number) => api.delete(`/admin/cpmks/${id}`)
"""

# ── components/common/AppSidebar.vue ─────────────────────────────────────────
files["components/common/AppSidebar.vue"] = """<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-icon">汉</span>
      <span class="logo-text">SINOKU</span>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-group">
        <span class="nav-group-label">Utama</span>
        <router-link to="/admin" exact class="nav-item">
          <span class="nav-icon">&#9632;</span> Dashboard
        </router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">Akademik</span>
        <router-link to="/admin/universities" class="nav-item">&#127979; Universitas</router-link>
        <router-link to="/admin/programs" class="nav-item">&#128218; Program Studi</router-link>
        <router-link to="/admin/courses" class="nav-item">&#128214; Mata Kuliah</router-link>
        <router-link to="/admin/cpls" class="nav-item">&#127919; CPL</router-link>
        <router-link to="/admin/cpmks" class="nav-item">&#127891; CPMK</router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">Evaluasi</span>
        <router-link to="/admin/instruments" class="nav-item">&#128203; Instrumen</router-link>
        <router-link to="/admin/anonymous-codes" class="nav-item">&#128273; Kode Anonim</router-link>
        <router-link to="/admin/analytics" class="nav-item">&#128200; Analitik</router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">RPS & Laporan</span>
        <router-link to="/admin/rps" class="nav-item">&#128196; RPS</router-link>
        <router-link to="/admin/reports" class="nav-item">&#128221; Laporan Diagnostik</router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <button @click="logout" class="logout-btn">&#128275; Keluar</button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1a365d;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  z-index: 100;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo-icon { font-size: 22px; color: #63b3ed; }
.logo-text { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.nav-group { margin-bottom: 8px; }
.nav-group-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 8px 16px 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  font-size: 13px;
  transition: background 0.15s;
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.router-link-active { background: rgba(99,179,237,0.2); color: #63b3ed; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.1); }
.logout-btn {
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.6);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}
.logout-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }
</style>
"""

# ── App.vue (dengan admin layout) ────────────────────────────────────────────
files["App.vue"] = """<template>
  <div v-if="isAdmin" class="admin-layout">
    <AppSidebar />
    <main class="admin-main">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/common/AppSidebar.vue'

const route = useRoute()
const isAdmin = computed(() => route.path.startsWith('/admin'))
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f7fafc; }
.admin-layout { display: flex; min-height: 100vh; }
.admin-main { margin-left: 220px; flex: 1; padding: 32px; min-height: 100vh; }
</style>
"""

# ── views/admin/DashboardHome.vue ─────────────────────────────────────────────
files["views/admin/DashboardHome.vue"] = """<template>
  <div>
    <h1 class="page-title">Dashboard</h1>

    <div v-if="loading" class="loading">Memuat data...</div>

    <template v-else>
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-num">{{ kpi.total_responses }}</div>
          <div class="kpi-label">Total Respons</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-num">{{ kpi.total_dosen }}</div>
          <div class="kpi-label">Responden Dosen</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-num">{{ kpi.total_mahasiswa }}</div>
          <div class="kpi-label">Responden Mahasiswa</div>
        </div>
        <div class="kpi-card kpi-highlight">
          <div class="kpi-num">{{ kpi.avg_cipp_score?.toFixed(2) || '-' }}</div>
          <div class="kpi-label">Rata-rata CIPP</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-num">{{ kpi.total_universities }}</div>
          <div class="kpi-label">Universitas</div>
        </div>
      </div>

      <!-- CIPP Per Dimensi -->
      <div class="card mt-24">
        <h2 class="card-title">Skor per Dimensi CIPP</h2>
        <div class="dim-grid">
          <div v-for="d in kpi.cipp_by_dimension" :key="d.kode" class="dim-item">
            <div class="dim-label">{{ d.kode }} — {{ d.nama }}</div>
            <div class="dim-bar-wrap">
              <div class="dim-bar" :style="{ width: (d.rata_rata / 5 * 100) + '%', background: dimColor(d.kode) }"></div>
            </div>
            <div class="dim-score">{{ d.rata_rata.toFixed(2) }} / 5.00</div>
          </div>
        </div>
      </div>

      <!-- Tren Respons -->
      <div class="card mt-24" v-if="kpi.response_trend?.length">
        <h2 class="card-title">Tren Respons Bulanan</h2>
        <div class="trend-grid">
          <div v-for="t in kpi.response_trend" :key="t.bulan" class="trend-item">
            <div class="trend-bar-wrap">
              <div class="trend-bar" :style="{ height: trendHeight(t.jumlah) + 'px' }"></div>
            </div>
            <div class="trend-label">{{ t.bulan }}</div>
            <div class="trend-val">{{ t.jumlah }}</div>
          </div>
        </div>
      </div>

      <div class="card mt-24 empty-state" v-else>
        <p>Belum ada data respons. Mulai dengan menambahkan universitas dan mata kuliah, lalu bagikan kuesioner.</p>
        <router-link to="/admin/universities" class="btn-primary mt-12">Kelola Universitas</router-link>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDashboardKpi } from '@/api/admin'

const loading = ref(true)
const kpi = ref<any>({})

const DIM_COLORS: Record<string, string> = {
  B: '#3182ce', C: '#38a169', D: '#d69e2e', E: '#e53e3e'
}
function dimColor(kode: string) { return DIM_COLORS[kode] || '#718096' }

function trendHeight(val: number) {
  const max = Math.max(...(kpi.value.response_trend || []).map((t: any) => t.jumlah), 1)
  return Math.max(8, (val / max) * 100)
}

onMounted(async () => {
  try {
    const res = await getDashboardKpi()
    kpi.value = res.data
  } catch { /* no data yet */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-title { font-size: 22px; font-weight: 700; color: #1a365d; margin-bottom: 24px; }
.loading { color: #718096; padding: 40px 0; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }
.kpi-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center; }
.kpi-highlight { background: #1a365d; }
.kpi-highlight .kpi-num, .kpi-highlight .kpi-label { color: #fff; }
.kpi-num { font-size: 32px; font-weight: 700; color: #1a365d; }
.kpi-label { font-size: 12px; color: #718096; margin-top: 4px; }
.card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.card-title { font-size: 15px; font-weight: 600; color: #2d3748; margin-bottom: 16px; }
.mt-24 { margin-top: 24px; }
.mt-12 { margin-top: 12px; }
.dim-grid { display: flex; flex-direction: column; gap: 12px; }
.dim-item { display: grid; grid-template-columns: 200px 1fr 80px; align-items: center; gap: 12px; }
.dim-label { font-size: 13px; color: #4a5568; }
.dim-bar-wrap { background: #edf2f7; border-radius: 4px; height: 8px; }
.dim-bar { height: 8px; border-radius: 4px; transition: width 0.5s; }
.dim-score { font-size: 13px; font-weight: 600; color: #2d3748; text-align: right; }
.trend-grid { display: flex; gap: 8px; align-items: flex-end; height: 140px; }
.trend-item { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.trend-bar-wrap { display: flex; align-items: flex-end; height: 100px; }
.trend-bar { width: 24px; background: #3182ce; border-radius: 3px 3px 0 0; }
.trend-label { font-size: 10px; color: #718096; }
.trend-val { font-size: 11px; font-weight: 600; color: #2d3748; }
.empty-state { color: #718096; font-size: 14px; }
.btn-primary { display: inline-block; background: #1a365d; color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; }
</style>
"""

# ── views/admin/academic/UniversityList.vue ───────────────────────────────────
files["views/admin/academic/UniversityList.vue"] = """<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Universitas</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah</button>
    </div>

    <!-- Search -->
    <div class="toolbar">
      <input v-model="search" placeholder="Cari nama universitas..." class="search-input" @input="fetchData" />
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nama</th><th>Singkat</th><th>Jenis</th><th>Kota</th><th>Provinsi</th><th>Status</th><th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="7" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="7" class="center">Belum ada data</td></tr>
          <tr v-for="u in rows" :key="u.id">
            <td>{{ u.nama }}</td>
            <td><span class="badge">{{ u.nama_singkat }}</span></td>
            <td>{{ u.jenis }}</td>
            <td>{{ u.kota }}</td>
            <td>{{ u.provinsi }}</td>
            <td><span :class="u.is_active ? 'status-active' : 'status-inactive'">{{ u.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
            <td>
              <button class="btn-edit" @click="openEdit(u)">Edit</button>
              <button class="btn-delete" @click="confirmDelete(u)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button :disabled="page <= 1" @click="page--; fetchData()">&#8592;</button>
      <span>Halaman {{ page }} dari {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++; fetchData()">&#8594;</button>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal=false">
      <div class="modal">
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} Universitas</h2>
        <form @submit.prevent="save">
          <div class="form-grid">
            <div class="form-group">
              <label>Nama Lengkap *</label>
              <input v-model="form.nama" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Singkatan *</label>
              <input v-model="form.nama_singkat" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Jenis *</label>
              <select v-model="form.jenis" required class="form-input">
                <option value="negeri">Negeri</option>
                <option value="swasta">Swasta</option>
              </select>
            </div>
            <div class="form-group">
              <label>Kota *</label>
              <input v-model="form.kota" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Provinsi *</label>
              <input v-model="form.provinsi" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Website</label>
              <input v-model="form.website" class="form-input" />
            </div>
            <div class="form-group">
              <label>Akreditasi</label>
              <input v-model="form.akreditasi" class="form-input" placeholder="A / B / C" />
            </div>
            <div class="form-group">
              <label>Tahun Berdiri</label>
              <input v-model.number="form.tahun_berdiri" type="number" class="form-input" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Delete -->
    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm=false">
      <div class="modal modal-sm">
        <h2 class="modal-title">Hapus Universitas?</h2>
        <p class="confirm-text">Yakin ingin menghapus <strong>{{ deleteTarget?.nama }}</strong>? Tindakan ini tidak dapat dibatalkan.</p>
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
import { getUniversities, createUniversity, updateUniversity, deleteUniversity } from '@/api/admin'

const rows = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const page = ref(1)
const total = ref(0)
const limit = 15
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit)))

const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)

const defaultForm = () => ({ nama: '', nama_singkat: '', jenis: 'negeri', kota: '', provinsi: '', website: '', akreditasi: '', tahun_berdiri: null as number | null })
const form = ref(defaultForm())

async function fetchData() {
  loading.value = true
  try {
    const res = await getUniversities({ page: page.value, limit, search: search.value || undefined })
    rows.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
function openEdit(u: any) { editing.value = u; form.value = { ...u }; showModal.value = true }
function confirmDelete(u: any) { deleteTarget.value = u; showConfirm.value = true }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateUniversity(editing.value.id, form.value)
    else await createUniversity(form.value)
    showModal.value = false
    await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try {
    await deleteUniversity(deleteTarget.value.id)
    showConfirm.value = false
    await fetchData()
  } finally { saving.value = false }
}

onMounted(fetchData)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a365d; }
.toolbar { margin-bottom: 16px; }
.search-input { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; width: 280px; }
.table-wrap { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #f7fafc; padding: 10px 14px; text-align: left; font-weight: 600; color: #4a5568; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 10px 14px; border-bottom: 1px solid #f0f4f8; color: #2d3748; }
.data-table tr:last-child td { border-bottom: none; }
.center { text-align: center; color: #718096; }
.badge { background: #ebf8ff; color: #2b6cb0; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.status-active { color: #38a169; font-size: 12px; font-weight: 600; }
.status-inactive { color: #e53e3e; font-size: 12px; font-weight: 600; }
.btn-primary { background: #1a365d; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-edit { background: #ebf8ff; color: #2b6cb0; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; margin-right: 4px; }
.btn-delete { background: #fff5f5; color: #e53e3e; border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; }
.btn-cancel { background: #f7fafc; color: #4a5568; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }
.pagination { display: flex; align-items: center; gap: 12px; padding: 16px 0; font-size: 13px; color: #718096; }
.pagination button { padding: 6px 12px; border: 1px solid #e2e8f0; background: #fff; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 200; }
.modal { background: #fff; border-radius: 12px; padding: 28px; width: 600px; max-width: 95vw; max-height: 90vh; overflow-y: auto; }
.modal-sm { width: 380px; }
.modal-title { font-size: 18px; font-weight: 700; color: #1a365d; margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 12px; font-weight: 600; color: #4a5568; }
.form-input { padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.confirm-text { font-size: 14px; color: #4a5568; margin-bottom: 20px; line-height: 1.6; }
</style>
"""

# ── views/admin/academic/ProgramList.vue ─────────────────────────────────────
files["views/admin/academic/ProgramList.vue"] = """<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Program Studi</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah</button>
    </div>

    <div class="toolbar">
      <select v-model="filterUniv" @change="page=1; fetchData()" class="search-input">
        <option value="">Semua Universitas</option>
        <option v-for="u in univList" :key="u.id" :value="u.id">{{ u.nama_singkat }} — {{ u.nama }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Nama Program</th><th>Singkat</th><th>Jenjang</th><th>Status</th><th>Aksi</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="5" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="5" class="center">Belum ada data</td></tr>
          <tr v-for="p in rows" :key="p.id">
            <td>{{ p.nama }}</td>
            <td><span class="badge">{{ p.nama_singkat }}</span></td>
            <td>{{ p.jenjang }}</td>
            <td><span :class="p.is_active ? 'status-active' : 'status-inactive'">{{ p.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
            <td>
              <button class="btn-edit" @click="openEdit(p)">Edit</button>
              <button class="btn-delete" @click="confirmDelete(p)">Hapus</button>
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
        <h2 class="modal-title">{{ editing ? 'Edit' : 'Tambah' }} Program Studi</h2>
        <form @submit.prevent="save">
          <div class="form-grid">
            <div class="form-group" style="grid-column:1/-1">
              <label>Universitas *</label>
              <select v-model.number="form.university_id" required class="form-input">
                <option v-for="u in univList" :key="u.id" :value="u.id">{{ u.nama }}</option>
              </select>
            </div>
            <div class="form-group" style="grid-column:1/-1">
              <label>Nama Program *</label>
              <input v-model="form.nama" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Singkatan *</label>
              <input v-model="form.nama_singkat" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Jenjang *</label>
              <select v-model="form.jenjang" required class="form-input">
                <option value="S1">S1</option><option value="S2">S2</option><option value="D3">D3</option><option value="D4">D4</option>
              </select>
            </div>
            <div class="form-group">
              <label>Tahun Berdiri</label>
              <input v-model.number="form.tahun_berdiri" type="number" class="form-input" />
            </div>
            <div class="form-group">
              <label>Akreditasi</label>
              <input v-model="form.akreditasi" class="form-input" placeholder="A / B / C" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showModal=false">Batal</button>
            <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm=false">
      <div class="modal modal-sm">
        <h2 class="modal-title">Hapus Program Studi?</h2>
        <p class="confirm-text">Yakin hapus <strong>{{ deleteTarget?.nama }}</strong>?</p>
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
import { getPrograms, createProgram, updateProgram, deleteProgram, getUniversities } from '@/api/admin'

const rows = ref<any[]>([])
const univList = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const filterUniv = ref<number | ''>('')
const page = ref(1)
const total = ref(0)
const limit = 20
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / limit)))
const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)
const defaultForm = () => ({ university_id: 0, nama: '', nama_singkat: '', jenjang: 'S1', tahun_berdiri: null as number|null, akreditasi: '' })
const form = ref(defaultForm())

async function fetchData() {
  loading.value = true
  try {
    const res = await getPrograms({ page: page.value, limit, university_id: filterUniv.value || undefined })
    rows.value = res.data.data; total.value = res.data.total
  } finally { loading.value = false }
}

async function fetchUnivs() {
  const res = await getUniversities({ limit: 100 })
  univList.value = res.data.data
}

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
function openEdit(p: any) { editing.value = p; form.value = { ...p }; showModal.value = true }
function confirmDelete(p: any) { deleteTarget.value = p; showConfirm.value = true }

async function save() {
  saving.value = true
  try {
    if (editing.value) await updateProgram(editing.value.id, form.value)
    else await createProgram(form.value)
    showModal.value = false; await fetchData()
  } finally { saving.value = false }
}

async function doDelete() {
  saving.value = true
  try { await deleteProgram(deleteTarget.value.id); showConfirm.value = false; await fetchData() }
  finally { saving.value = false }
}

onMounted(async () => { await fetchUnivs(); await fetchData() })
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
.modal{background:#fff;border-radius:12px;padding:28px;width:560px;max-width:95vw;max-height:90vh;overflow-y:auto}
.modal-sm{width:380px}
.modal-title{font-size:18px;font-weight:700;color:#1a365d;margin-bottom:20px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-group{display:flex;flex-direction:column;gap:6px}
.form-group label{font-size:12px;font-weight:600;color:#4a5568}
.form-input{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
.confirm-text{font-size:14px;color:#4a5568;margin-bottom:20px;line-height:1.6}
</style>
"""

# ── views/admin/academic/CourseList.vue ──────────────────────────────────────
files["views/admin/academic/CourseList.vue"] = """<template>
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
"""

# ── views/admin/academic/CplManager.vue ──────────────────────────────────────
files["views/admin/academic/CplManager.vue"] = """<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">CPL (Capaian Pembelajaran Lulusan)</h1>
      <button class="btn-primary" @click="openCreate">+ Tambah CPL</button>
    </div>

    <div class="toolbar">
      <select v-model="filterProgram" @change="fetchData" class="search-input">
        <option value="">Semua Program Studi</option>
        <option v-for="p in programList" :key="p.id" :value="p.id">{{ p.nama_singkat }} — {{ p.nama }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Kode CPL</th><th>Deskripsi (ID)</th><th>Deskripsi (中文)</th><th>Kategori</th><th>Status</th><th>Aksi</th></tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Belum ada data. Pilih program studi.</td></tr>
          <tr v-for="c in rows" :key="c.id">
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

const rows = ref<any[]>([])
const programList = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const filterProgram = ref<number|''>('')
const showModal = ref(false)
const showConfirm = ref(false)
const editing = ref<any>(null)
const deleteTarget = ref<any>(null)
const defaultForm = () => ({ program_id: 0, kode_cpl: '', deskripsi_id: '', deskripsi_zh: '', kategori: 'pengetahuan' })
const form = ref(defaultForm())

async function fetchData() {
  if (!filterProgram.value) { rows.value = []; return }
  loading.value = true
  try {
    const res = await getCpls({ program_id: filterProgram.value })
    rows.value = res.data
  } finally { loading.value = false }
}

onMounted(async () => {
  const res = await getPrograms({ limit: 200 })
  programList.value = res.data.data
})

function openCreate() { editing.value = null; form.value = defaultForm(); showModal.value = true }
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
"""

# ── views/admin/academic/CpmkManager.vue ─────────────────────────────────────
files["views/admin/academic/CpmkManager.vue"] = """<template>
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
"""

# ── Write all files ───────────────────────────────────────────────────────────
for rel, content in files.items():
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {rel}")

print(f"Done - {len(files)} files written.")
