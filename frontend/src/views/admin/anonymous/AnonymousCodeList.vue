<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Kode Anonim Responden</h1>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <input class="filter-input" v-model="search" placeholder="Cari kode..." @input="onSearch" />
      <select class="filter-select" v-model="filterRole" @change="fetchData">
        <option value="">Semua Role</option>
        <option value="mahasiswa">Mahasiswa</option>
        <option value="dosen">Dosen</option>
      </select>
      <select class="filter-select" v-model.number="filterCourse" @change="fetchData">
        <option :value="null">Semua MK</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama }}</option>
      </select>
      <select class="filter-select" v-model="filterAccessible" @change="fetchData">
        <option value="">Semua Status</option>
        <option value="true">Bisa Diakses</option>
        <option value="false">Diblokir</option>
      </select>
    </div>

    <!-- KPI -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-val">{{ total }}</div>
        <div class="kpi-label">Total Kode</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-val">{{ codes.filter(c => c.is_accessible).length }}</div>
        <div class="kpi-label">Aktif (halaman ini)</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-val">{{ codes.filter(c => !c.is_accessible).length }}</div>
        <div class="kpi-label">Diblokir (halaman ini)</div>
      </div>
    </div>

    <div class="content-card">
      <div v-if="loading" class="loading-state">Memuat data...</div>
      <div v-else-if="!codes.length" class="empty-state">Tidak ada kode anonim yang ditemukan</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Kode Anonim</th>
            <th>Role</th>
            <th>MK ID</th>
            <th>Nama Responden</th>
            <th>Digenerate</th>
            <th>Terakhir Diakses</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in codes" :key="c.kode">
            <td><code class="kode-cell">{{ c.kode }}</code></td>
            <td>
              <span :class="c.role === 'dosen' ? 'badge-dosen' : 'badge-mhs'">{{ c.role }}</span>
            </td>
            <td class="center-cell">{{ c.course_id }}</td>
            <td class="name-cell">{{ c.respondent_name ?? '—' }}</td>
            <td class="date-cell">{{ formatDate(c.generated_at) }}</td>
            <td class="date-cell">{{ c.last_accessed ? formatDate(c.last_accessed) : '—' }}</td>
            <td>
              <span :class="c.is_accessible ? 'badge-active' : 'badge-blocked'">
                {{ c.is_accessible ? 'Aktif' : 'Diblokir' }}
              </span>
            </td>
            <td>
              <button
                class="btn-sm"
                :class="c.is_accessible ? 'btn-block' : 'btn-unblock'"
                @click="toggle(c)"
              >
                {{ c.is_accessible ? 'Blokir' : 'Aktifkan' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Paginasi -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="page === 1" @click="changePage(page - 1)">‹ Prev</button>
        <span class="page-info">Hal {{ page }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="page === totalPages" @click="changePage(page + 1)">Next ›</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getAnonymousCodes, toggleAnonymousCode, getCourses } from '@/api/admin'

const loading = ref(true)
const codes = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const limit = 20
const search = ref('')
const filterRole = ref('')
const filterCourse = ref<number | null>(null)
const filterAccessible = ref('')
const courses = ref<any[]>([])

const totalPages = computed(() => Math.ceil(total.value / limit))

let searchTimer: ReturnType<typeof setTimeout>
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchData() }, 400)
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: page.value, limit }
    if (search.value) params.search = search.value
    if (filterRole.value) params.role = filterRole.value
    if (filterCourse.value) params.course_id = filterCourse.value
    if (filterAccessible.value !== '') params.is_accessible = filterAccessible.value === 'true'
    const res = await getAnonymousCodes(params)
    codes.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

function changePage(p: number) { page.value = p; fetchData() }

async function toggle(c: any) {
  await toggleAnonymousCode(c.kode)
  await fetchData()
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = (res.data.data ?? []).map((c: any) => ({ id: c.id, kode: c.kode_mk, nama: c.nama_id }))
  await fetchData()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.filter-bar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.filter-input{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;min-width:180px}
.filter-select{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.kpi-row{display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.kpi-card{background:#fff;border-radius:10px;padding:14px 20px;box-shadow:0 1px 3px rgba(0,0,0,.07);text-align:center;min-width:120px}
.kpi-card.green{background:#f0fff4}
.kpi-card.red{background:#fff5f5}
.kpi-val{font-size:26px;font-weight:800;color:#1a365d}
.kpi-card.green .kpi-val{color:#276749}
.kpi-card.red .kpi-val{color:#c53030}
.kpi-label{font-size:11px;color:#718096;margin-top:2px}
.content-card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.07)}
.loading-state,.empty-state{text-align:center;padding:40px;color:#a0aec0;font-size:14px}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:9px 12px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:9px 12px;border-bottom:1px solid #f0f4f8;vertical-align:middle}
.kode-cell{font-size:13px;font-weight:700;letter-spacing:.5px;color:#1a365d}
.center-cell{text-align:center;color:#718096}
.name-cell{color:#2d3748}
.date-cell{font-size:12px;color:#718096;white-space:nowrap}
.badge-dosen{background:#ebf4ff;color:#2b6cb0;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.badge-mhs{background:#f0fff4;color:#276749;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.badge-active{background:#c6f6d5;color:#276749;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.badge-blocked{background:#fed7d7;color:#c53030;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.btn-sm{padding:4px 12px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600}
.btn-block{background:#fed7d7;color:#c53030}
.btn-unblock{background:#c6f6d5;color:#276749}
.pagination{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:16px}
.page-btn{padding:6px 14px;border:1px solid #e2e8f0;border-radius:6px;cursor:pointer;background:#fff;font-size:13px}
.page-btn:disabled{opacity:.4;cursor:not-allowed}
.page-info{font-size:13px;color:#718096}
</style>
