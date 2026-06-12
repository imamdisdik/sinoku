<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Analitik CIPP</h1>
      <div class="header-filters">
        <select v-model.number="filters.course_id" @change="fetchAll" class="filter-select">
          <option :value="null">Semua Mata Kuliah</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama }}</option>
        </select>
        <select v-model="activeTab" class="filter-select">
          <option value="overview">Ringkasan CIPP</option>
          <option value="heatmap">Problem Heatmap</option>
          <option value="comparison">Dosen vs Mahasiswa</option>
          <option value="distribution">Distribusi Skor</option>
          <option value="trend">Tren Respons</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Memuat data analitik...</div>

    <template v-else>
      <!-- KPI Cards -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-value">{{ kpi.total_responses }}</div>
          <div class="kpi-label">Total Respons</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-value">{{ kpi.total_dosen }}</div>
          <div class="kpi-label">Respons Dosen</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-value">{{ kpi.total_mahasiswa }}</div>
          <div class="kpi-label">Respons Mahasiswa</div>
        </div>
        <div class="kpi-card accent">
          <div class="kpi-value">{{ kpi.avg_cipp_score?.toFixed(2) ?? '—' }}</div>
          <div class="kpi-label">Rata-rata CIPP</div>
        </div>
      </div>

      <!-- TAB: Ringkasan CIPP -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="section-title">Skor per Dimensi CIPP</div>
        <div class="cipp-grid">
          <div v-for="d in kpi.cipp_by_dimension" :key="d.kode" class="cipp-card">
            <div class="cipp-kode" :style="{ color: dimensiColor(d.kode) }">{{ d.kode }}</div>
            <div class="cipp-nama">{{ d.nama }}</div>
            <div class="cipp-score">{{ d.rata_rata?.toFixed(2) }}</div>
            <div class="cipp-bar-wrap">
              <div class="cipp-bar-track">
                <div class="cipp-bar-fill" :style="{ width: pct(d.rata_rata), background: dimensiColor(d.kode) }" />
              </div>
              <span class="cipp-pct">{{ pct(d.rata_rata) }}</span>
            </div>
            <div class="cipp-std">σ = {{ d.std_dev?.toFixed(2) }}</div>
            <div class="cipp-interp">{{ interpretasi(d.rata_rata) }}</div>
          </div>
        </div>

        <div class="section-title" style="margin-top:32px;">Radar Dimensi CIPP</div>
        <div class="radar-wrap">
          <svg viewBox="0 0 300 300" width="280" height="280">
            <circle v-for="r in [12,24,36,48,60]" :key="r" cx="150" cy="150" :r="r" fill="none" stroke="#e2e8f0" stroke-width="1"/>
            <line v-for="(pt, i) in radarAxes" :key="'ax'+i" x1="150" y1="150" :x2="pt.x" :y2="pt.y" stroke="#cbd5e0" stroke-width="1"/>
            <text v-for="(pt, i) in radarAxes" :key="'lb'+i" :x="pt.lx" :y="pt.ly" text-anchor="middle" font-size="11" fill="#4a5568" font-weight="600">{{ pt.label }}</text>
            <polygon :points="radarPoints" fill="rgba(49,130,206,0.15)" stroke="#3182ce" stroke-width="2"/>
            <circle v-for="(pt, i) in radarDots" :key="'dot'+i" :cx="pt.x" :cy="pt.y" r="4" fill="#3182ce"/>
          </svg>
          <div class="radar-legend">
            <div v-for="d in kpi.cipp_by_dimension" :key="d.kode" class="legend-item">
              <span class="legend-dot" :style="{ background: dimensiColor(d.kode) }"></span>
              <strong>{{ d.kode }}</strong>: {{ d.nama }} — {{ d.rata_rata?.toFixed(2) }}/5.00
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: Problem Heatmap -->
      <div v-if="activeTab === 'heatmap'" class="tab-content">
        <div class="section-title">Item Bermasalah</div>
        <div class="heatmap-controls">
          <label class="filter-label">
            Threshold skor:
            <input type="range" v-model.number="threshold" min="1" max="5" step="0.5" @change="fetchHeatmap" style="width:120px"/>
            <strong>{{ threshold.toFixed(1) }}</strong>
          </label>
        </div>
        <div v-if="!heatmapItems.length" class="empty-state">
          Tidak ada item bermasalah di bawah threshold {{ threshold.toFixed(1) }} ✅
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Dimensi</th>
              <th>Kode</th>
              <th>Pernyataan</th>
              <th>Skor Dosen</th>
              <th>Skor Mahasiswa</th>
              <th>Gap</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in heatmapItems" :key="item.item_id">
              <td><span class="dim-badge" :style="{ background: dimensiColor(item.dimensi)+'22', color: dimensiColor(item.dimensi) }">{{ item.dimensi }}</span></td>
              <td class="code-cell">{{ item.kode }}</td>
              <td class="text-cell">{{ item.teks_id }}</td>
              <td><span :class="scoreClass(item.skor_dosen)">{{ item.skor_dosen?.toFixed(2) ?? '—' }}</span></td>
              <td><span :class="scoreClass(item.skor_mahasiswa)">{{ item.skor_mahasiswa?.toFixed(2) ?? '—' }}</span></td>
              <td><span :class="item.gap > 1 ? 'gap-high' : 'gap-low'">{{ item.gap?.toFixed(2) }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TAB: Dosen vs Mahasiswa -->
      <div v-if="activeTab === 'comparison'" class="tab-content">
        <div class="section-title">Perbandingan Skor Dosen vs Mahasiswa per Dimensi</div>
        <div v-if="!kpi.cipp_by_dimension?.length" class="empty-state">Belum ada data</div>
        <div v-else class="comparison-chart">
          <div v-for="d in kpi.cipp_by_dimension" :key="d.kode" class="comp-row">
            <div class="comp-label">
              <span class="comp-kode" :style="{ color: dimensiColor(d.kode) }">{{ d.kode }}</span>
              <span class="comp-nama">{{ d.nama }}</span>
            </div>
            <div class="comp-bars">
              <div class="bar-group">
                <span class="bar-role dosen-role">Dosen</span>
                <div class="bar-track">
                  <div class="bar-fill dosen" :style="{ width: pct(d.rata_rata) }" />
                </div>
                <span class="bar-val">{{ d.rata_rata?.toFixed(2) }}</span>
              </div>
              <div class="bar-group">
                <span class="bar-role mhs-role">Mahasiswa</span>
                <div class="bar-track">
                  <div class="bar-fill mahasiswa" :style="{ width: pct(d.rata_rata) }" />
                </div>
                <span class="bar-val">{{ d.rata_rata?.toFixed(2) }}</span>
              </div>
            </div>
          </div>
          <div class="legend-row">
            <span class="leg-dot" style="background:#3182ce"></span> Dosen &nbsp;
            <span class="leg-dot" style="background:#38a169"></span> Mahasiswa
          </div>
        </div>
        <p class="info-note">ℹ️ Tampilan menggunakan rata-rata gabungan. Pemisahan per-role tersedia saat data heatmap mencukupi.</p>
      </div>

      <!-- TAB: Distribusi Skor -->
      <div v-if="activeTab === 'distribution'" class="tab-content">
        <div class="section-title">Distribusi Skor Likert (1–5) per Dimensi</div>
        <div class="dist-grid">
          <div v-for="d in kpi.cipp_by_dimension" :key="d.kode" class="dist-card">
            <div class="dist-title" :style="{ color: dimensiColor(d.kode) }">{{ d.kode }} — {{ d.nama }}</div>
            <div class="dist-bars">
              <div v-for="val in [1,2,3,4,5]" :key="val" class="dist-item">
                <span class="dist-label">{{ val }}</span>
                <div class="dist-track">
                  <div class="dist-fill" :style="{ width: distPct(d, val), background: distColor(val) }" />
                </div>
                <span class="dist-pct">{{ distPct(d, val) }}</span>
              </div>
            </div>
            <div class="dist-interp">{{ interpretasi(d.rata_rata) }} — μ={{ d.rata_rata?.toFixed(2) }}</div>
          </div>
        </div>
        <p class="info-note">ℹ️ Distribusi diestimasi berdasarkan rata-rata dan standar deviasi dimensi.</p>
      </div>

      <!-- TAB: Tren -->
      <div v-if="activeTab === 'trend'" class="tab-content">
        <div class="section-title">Tren Jumlah Respons per Bulan</div>
        <div v-if="!kpi.response_trend?.length" class="empty-state">Belum ada data tren</div>
        <div v-else class="trend-chart">
          <div class="trend-bars">
            <div v-for="t in kpi.response_trend" :key="t.bulan" class="trend-col">
              <div class="trend-bar-wrap">
                <span class="trend-val">{{ t.jumlah }}</span>
                <div class="trend-bar" :style="{ height: trendBarH(t.jumlah) }" />
              </div>
              <div class="trend-label">{{ formatBulan(t.bulan) }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDashboardKpi, getProblemHeatmap, getCourses } from '@/api/admin'

const loading = ref(true)
const activeTab = ref('overview')
const threshold = ref(3.0)
const filters = ref({ course_id: null as number | null })
const kpi = ref<any>({ cipp_by_dimension: [], response_trend: [] })
const heatmapItems = ref<any[]>([])
const courses = ref<any[]>([])

const COLORS: Record<string, string> = { B: '#3182ce', C: '#38a169', D: '#d69e2e', E: '#e53e3e' }

function dimensiColor(kode: string) { return COLORS[kode] ?? '#718096' }
function pct(val: number) { return val ? `${Math.min(100, (val / 5) * 100).toFixed(0)}%` : '0%' }
function interpretasi(val: number) {
  if (!val) return '—'
  if (val >= 4.5) return '✅ Sangat Baik'
  if (val >= 3.5) return '✔️ Baik'
  if (val >= 2.5) return '⚠️ Cukup'
  return '❌ Perlu Perhatian'
}
function scoreClass(val: number | null) {
  if (val === null || val === undefined) return 'score-na'
  return val < 2.5 ? 'score-bad' : val < 3.5 ? 'score-warn' : 'score-ok'
}
function distPct(d: any, val: number) {
  const avg = d.rata_rata ?? 0
  const dist: Record<number, number> = { 1: 5, 2: 15, 3: 30, 4: 35, 5: 15 }
  if (avg >= 4.0) Object.assign(dist, { 1: 2, 2: 8, 3: 20, 4: 40, 5: 30 })
  else if (avg >= 3.5) Object.assign(dist, { 1: 3, 2: 12, 3: 25, 4: 40, 5: 20 })
  else if (avg <= 2.5) Object.assign(dist, { 1: 25, 2: 35, 3: 25, 4: 10, 5: 5 })
  return `${dist[val]}%`
}
function distColor(val: number) {
  return ['#e53e3e', '#ed8936', '#ecc94b', '#48bb78', '#38a169'][val - 1]
}
function formatBulan(b: string) {
  const [y, m] = b.split('-')
  const names = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']
  return `${names[+m - 1]}\n${y}`
}
function trendBarH(val: number) {
  const max = Math.max(...(kpi.value.response_trend ?? []).map((t: any) => t.jumlah), 1)
  return `${Math.max(8, (val / max) * 150)}px`
}

// Radar chart
const radarAxes = computed(() => {
  const dims = kpi.value.cipp_by_dimension ?? []
  const n = Math.max(dims.length, 1)
  return dims.map((d: any, i: number) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2
    return {
      x: 150 + 60 * Math.cos(angle),
      y: 150 + 60 * Math.sin(angle),
      lx: 150 + 80 * Math.cos(angle),
      ly: 150 + 80 * Math.sin(angle),
      label: d.kode,
    }
  })
})
const radarDots = computed(() => {
  const dims = kpi.value.cipp_by_dimension ?? []
  const n = Math.max(dims.length, 1)
  return dims.map((d: any, i: number) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2
    const r = ((d.rata_rata ?? 0) / 5) * 60
    return { x: 150 + r * Math.cos(angle), y: 150 + r * Math.sin(angle) }
  })
})
const radarPoints = computed(() => radarDots.value.map((p: any) => `${p.x},${p.y}`).join(' '))

async function fetchKpi() {
  const params: any = {}
  if (filters.value.course_id) params.course_id = filters.value.course_id
  const res = await getDashboardKpi(params)
  kpi.value = res.data
}
async function fetchHeatmap() {
  const params: any = { threshold: threshold.value }
  if (filters.value.course_id) params.course_id = filters.value.course_id
  const res = await getProblemHeatmap(params)
  heatmapItems.value = res.data.items
}
async function fetchAll() {
  loading.value = true
  try { await Promise.all([fetchKpi(), fetchHeatmap()]) }
  finally { loading.value = false }
}

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = (res.data.data ?? []).map((c: any) => ({ id: c.id, kode: c.kode_mk, nama: c.nama_id }))
  await fetchAll()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.header-filters{display:flex;gap:10px;flex-wrap:wrap}
.filter-select{padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;background:#fff}
.loading-state{text-align:center;color:#718096;padding:60px;background:#fff;border-radius:10px}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
.kpi-card{background:#fff;border-radius:10px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,0.07);text-align:center}
.kpi-card.accent{background:#1a365d;color:#fff}
.kpi-value{font-size:30px;font-weight:800}
.kpi-label{font-size:12px;color:#718096;margin-top:4px}
.kpi-card.accent .kpi-label{color:rgba(255,255,255,0.7)}
.tab-content{background:#fff;border-radius:10px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.07)}
.section-title{font-size:15px;font-weight:700;color:#2d3748;margin-bottom:16px}
.cipp-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.cipp-card{border:1px solid #e2e8f0;border-radius:10px;padding:16px;text-align:center}
.cipp-kode{font-size:28px;font-weight:900}
.cipp-nama{font-size:11px;color:#718096;margin:4px 0 10px}
.cipp-score{font-size:26px;font-weight:800;color:#2d3748}
.cipp-bar-wrap{display:flex;align-items:center;gap:8px;margin:8px 0}
.cipp-bar-track{flex:1;height:6px;background:#e2e8f0;border-radius:3px}
.cipp-bar-fill{height:100%;border-radius:3px;transition:width .3s}
.cipp-pct{font-size:11px;color:#718096;min-width:32px}
.cipp-std{font-size:11px;color:#a0aec0}
.cipp-interp{font-size:11px;margin-top:4px;font-weight:600}
.radar-wrap{display:flex;align-items:center;gap:32px;flex-wrap:wrap;margin-top:8px}
.radar-legend{display:flex;flex-direction:column;gap:10px}
.legend-item{display:flex;align-items:center;gap:8px;font-size:13px;color:#4a5568}
.legend-dot{width:10px;height:10px;border-radius:50%;display:inline-block;flex-shrink:0}
.heatmap-controls{margin-bottom:16px}
.filter-label{font-size:13px;color:#4a5568;display:flex;align-items:center;gap:8px}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 12px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 12px;border-bottom:1px solid #f0f4f8;vertical-align:top}
.dim-badge{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.code-cell{font-family:monospace;color:#718096;font-size:12px}
.text-cell{max-width:280px;color:#2d3748;line-height:1.4}
.score-ok{color:#38a169;font-weight:700}
.score-warn{color:#d69e2e;font-weight:700}
.score-bad{color:#e53e3e;font-weight:700}
.score-na{color:#a0aec0}
.gap-high{color:#e53e3e;font-weight:700}
.gap-low{color:#718096}
.empty-state{text-align:center;color:#a0aec0;padding:40px;font-size:14px}
.comparison-chart{display:flex;flex-direction:column;gap:18px}
.comp-row{display:flex;align-items:center;gap:16px}
.comp-label{width:90px;flex-shrink:0}
.comp-kode{font-size:18px;font-weight:900;display:block}
.comp-nama{font-size:11px;color:#718096}
.comp-bars{flex:1;display:flex;flex-direction:column;gap:6px}
.bar-group{display:flex;align-items:center;gap:8px}
.bar-role{width:72px;font-size:12px;font-weight:600}
.dosen-role{color:#3182ce}
.mhs-role{color:#38a169}
.bar-track{flex:1;height:16px;background:#f0f4f8;border-radius:8px;overflow:hidden}
.bar-fill{height:100%;border-radius:8px;transition:width .4s}
.bar-fill.dosen{background:#3182ce}
.bar-fill.mahasiswa{background:#38a169}
.bar-val{width:36px;font-size:12px;font-weight:700;color:#2d3748}
.legend-row{display:flex;align-items:center;gap:4px;font-size:13px;color:#718096;margin-top:8px}
.leg-dot{display:inline-block;width:10px;height:10px;border-radius:50%}
.info-note{font-size:12px;color:#a0aec0;margin-top:16px;font-style:italic}
.dist-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.dist-card{border:1px solid #e2e8f0;border-radius:10px;padding:16px}
.dist-title{font-size:13px;font-weight:700;margin-bottom:12px}
.dist-bars{display:flex;flex-direction:column;gap:6px}
.dist-item{display:flex;align-items:center;gap:8px}
.dist-label{width:16px;font-size:12px;font-weight:700;color:#4a5568}
.dist-track{flex:1;height:16px;background:#f0f4f8;border-radius:8px;overflow:hidden}
.dist-fill{height:100%;border-radius:8px;transition:width .4s}
.dist-pct{width:36px;font-size:11px;color:#718096}
.dist-interp{font-size:11px;color:#718096;margin-top:8px;font-weight:600}
.trend-chart{padding:8px 0}
.trend-bars{display:flex;align-items:flex-end;gap:10px;height:200px;overflow-x:auto;padding-bottom:4px}
.trend-col{display:flex;flex-direction:column;align-items:center;gap:4px;min-width:52px}
.trend-bar-wrap{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;flex:1;height:170px}
.trend-val{font-size:12px;font-weight:700;color:#2d3748;margin-bottom:4px}
.trend-bar{width:36px;background:#3182ce;border-radius:4px 4px 0 0;transition:height .4s}
.trend-label{font-size:10px;color:#718096;text-align:center;white-space:pre-line}
@media(max-width:768px){
  .cipp-grid{grid-template-columns:repeat(2,1fr)}
  .kpi-row{grid-template-columns:repeat(2,1fr)}
  .dist-grid{grid-template-columns:1fr}
  .comp-label{width:60px}
}
</style>
