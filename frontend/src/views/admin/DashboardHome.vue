<template>
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
