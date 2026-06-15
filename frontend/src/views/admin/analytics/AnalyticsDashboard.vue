<template>
  <div>
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:12px">
        <h1 class="page-title">Analitik CIPP</h1>
        <button class="btn-pdf" @click="exportAnalyticsPdf" title="Unduh laporan analisis PDF">&#128196; PDF Analisis</button>
      </div>
      <div class="header-filters">
        <template v-if="isSuperadmin">
          <select v-model.number="filters.university_id" @change="onUnivChange" class="filter-select" title="Filter universitas">
            <option :value="null">Semua Universitas</option>
            <option v-for="u in universities" :key="u.id" :value="u.id">{{ u.nama_singkat }}</option>
          </select>
          <select v-model.number="filters.program_id" @change="fetchAll" class="filter-select" title="Filter program studi">
            <option :value="null">Semua Prodi</option>
            <option v-for="p in filteredPrograms" :key="p.id" :value="p.id">{{ p.nama_singkat }}</option>
          </select>
        </template>
        <select v-model.number="filters.course_id" @change="fetchAll" class="filter-select">
          <option :value="null">Semua Mata Kuliah</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama }}</option>
        </select>
        <select v-model="filters.role" @change="fetchAll" class="filter-select" title="Filter peran responden">
          <option value="">Semua Peran</option>
          <option value="dosen">Dosen</option>
          <option value="mahasiswa">Mahasiswa</option>
        </select>
        <input type="date" v-model="filters.periode_start" @change="fetchAll" class="filter-select" title="Periode mulai" />
        <input type="date" v-model="filters.periode_end" @change="fetchAll" class="filter-select" title="Periode akhir" />
        <button v-if="filters.course_id || filters.university_id || filters.program_id || filters.role || filters.periode_start || filters.periode_end" @click="resetFilters" class="filter-reset" title="Reset filter">✕ Reset</button>
        <select v-model="activeTab" class="filter-select">
          <option value="overview">Ringkasan CIPP</option>
          <option value="cipp-scores">Skor Sub-Dimensi</option>
          <option value="heatmap">Problem Heatmap</option>
          <option value="comparison">Dosen vs Mahasiswa</option>
          <option value="comparison-groups">Perbandingan Univ/Prodi/MK</option>
          <option value="distribution">Distribusi Skor</option>
          <option value="cpl-matrix">Matriks CPL-CPMK</option>
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

        <div class="section-title" style="margin-top:32px;display:flex;justify-content:space-between;align-items:center">
          <span>Radar Dimensi CIPP</span>
          <span class="chart-dl">
            <button class="chart-dl-btn" @click="downloadChart('png')" title="Unduh PNG">&#128247; PNG</button>
            <button class="chart-dl-btn" @click="downloadChart('svg')" title="Unduh SVG">&#128190; SVG</button>
          </span>
        </div>
        <div class="radar-wrap">
          <svg ref="radarSvg" viewBox="0 0 300 300" width="280" height="280" xmlns="http://www.w3.org/2000/svg">
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

      <!-- TAB: Skor Sub-Dimensi (UC-17a) -->
      <div v-if="activeTab === 'cipp-scores'" class="tab-content">
        <div class="page-header" style="margin-bottom:16px">
          <div class="section-title" style="margin:0">Skor CIPP per Sub-Dimensi</div>
          <span class="filter-hint">Gunakan filter peran &amp; periode di atas</span>
        </div>
        <div v-if="loadingCippScores" class="empty-state">Memuat data...</div>
        <div v-else-if="!cippScoresData.dimensions?.length" class="empty-state">Belum ada data</div>
        <div v-else>
          <div class="kpi-row" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px">
            <div class="kpi-card"><div class="kpi-value">{{ cippScoresData.total_responses }}</div><div class="kpi-label">Total Respons</div></div>
            <div class="kpi-card"><div class="kpi-value">{{ cippScoresData.total_dosen }}</div><div class="kpi-label">Dosen</div></div>
            <div class="kpi-card"><div class="kpi-value">{{ cippScoresData.total_mahasiswa }}</div><div class="kpi-label">Mahasiswa</div></div>
          </div>
          <div v-for="dim in cippScoresData.dimensions" :key="dim.kode" class="cipp-scores-dim">
            <div class="cipp-scores-header" :style="{ borderLeftColor: dimensiColor(dim.kode) }">
              <span class="cipp-kode-sm" :style="{ color: dimensiColor(dim.kode) }">{{ dim.kode }}</span>
              <span class="cipp-nama-sm">{{ dim.nama }}</span>
              <span class="cipp-avg-sm">Rata-rata: <strong>{{ dim.rata_rata?.toFixed(2) ?? '—' }}</strong> / 5.00</span>
              <span class="cipp-std-sm">σ = {{ dim.std_dev?.toFixed(2) ?? '—' }}</span>
              <span class="cipp-n-sm">n = {{ dim.n }}</span>
            </div>
            <table class="data-table" style="margin-top:8px">
              <thead><tr><th>Sub-Dimensi</th><th>Rata-rata</th><th>Std Dev</th><th>N</th><th>Interpretasi</th><th>Bar</th></tr></thead>
              <tbody>
                <tr v-for="sd in dim.sub_dimensions" :key="sd.kode">
                  <td><strong>{{ sd.kode }}</strong> — {{ sd.nama }}</td>
                  <td><span :class="scoreClass(sd.rata_rata)">{{ sd.rata_rata?.toFixed(2) ?? '—' }}</span></td>
                  <td>{{ sd.std_dev?.toFixed(2) ?? '—' }}</td>
                  <td>{{ sd.n }}</td>
                  <td>{{ interpretasi(sd.rata_rata) }}</td>
                  <td style="min-width:120px">
                    <div class="cipp-bar-track" style="height:8px">
                      <div class="cipp-bar-fill" :style="{ width: pct(sd.rata_rata), background: dimensiColor(dim.kode) }" />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
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
        <div v-if="loadingComparison" class="empty-state">Memuat data perbandingan...</div>
        <div v-else-if="!comparisonData.dimensions?.length" class="empty-state">Belum ada data perbandingan</div>
        <div v-else class="comparison-chart">
          <div class="comp-meta">
            <span class="comp-meta-item dosen-role">{{ comparisonData.total_dosen }} respons dosen</span>
            <span class="comp-meta-item mhs-role">{{ comparisonData.total_mahasiswa }} respons mahasiswa</span>
          </div>
          <div v-for="d in comparisonData.dimensions" :key="d.kode" class="comp-row">
            <div class="comp-label">
              <span class="comp-kode" :style="{ color: dimensiColor(d.kode) }">{{ d.kode }}</span>
              <span class="comp-nama">{{ d.nama }}</span>
            </div>
            <div class="comp-bars">
              <div class="bar-group">
                <span class="bar-role dosen-role">Dosen</span>
                <div class="bar-track">
                  <div class="bar-fill dosen" :style="{ width: pct(d.skor_dosen) }" />
                </div>
                <span class="bar-val">{{ d.skor_dosen != null ? d.skor_dosen.toFixed(2) : '—' }}</span>
                <span class="bar-n">(n={{ d.n_dosen }})</span>
              </div>
              <div class="bar-group">
                <span class="bar-role mhs-role">Mahasiswa</span>
                <div class="bar-track">
                  <div class="bar-fill mahasiswa" :style="{ width: pct(d.skor_mahasiswa) }" />
                </div>
                <span class="bar-val">{{ d.skor_mahasiswa != null ? d.skor_mahasiswa.toFixed(2) : '—' }}</span>
                <span class="bar-n">(n={{ d.n_mahasiswa }})</span>
              </div>
            </div>
          </div>
          <div class="legend-row">
            <span class="leg-dot" style="background:#3182ce"></span> Dosen &nbsp;
            <span class="leg-dot" style="background:#38a169"></span> Mahasiswa
          </div>
        </div>
      </div>

      <!-- TAB: Perbandingan Univ/Prodi/MK (UC-17b) -->
      <div v-if="activeTab === 'comparison-groups'" class="tab-content">
        <div class="page-header" style="margin-bottom:16px">
          <div class="section-title" style="margin:0">Perbandingan Skor CIPP antar {{ groupByLabel }}</div>
          <select v-model="groupBy" @change="fetchComparisonGroups" class="filter-select" style="font-size:12px">
            <option value="university">Per Universitas</option>
            <option value="program">Per Program Studi</option>
            <option value="course">Per Mata Kuliah</option>
          </select>
        </div>
        <div v-if="loadingGroups" class="empty-state">Memuat data perbandingan...</div>
        <div v-else-if="!groupsData.data?.length" class="empty-state">Belum ada data respons untuk dibandingkan</div>
        <div v-else class="matrix-scroll">
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ groupByLabel }}</th>
                <th>N Respons</th>
                <th v-for="d in groupsData.dimensions" :key="d.kode" :title="d.nama">
                  <span :style="{ color: d.warna_hex }">{{ d.kode }}</span>
                </th>
                <th>Rata-rata</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in groupsData.data" :key="row.group_id">
                <td><strong>{{ row.group_nama }}</strong></td>
                <td>{{ row.n_responses }}</td>
                <td v-for="d in groupsData.dimensions" :key="d.kode">
                  <span :class="scoreClass(row.cipp[d.kode])">{{ row.cipp[d.kode] != null ? row.cipp[d.kode].toFixed(2) : '—' }}</span>
                </td>
                <td><strong>{{ rowAvg(row) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- TAB: Distribusi Skor -->
      <div v-if="activeTab === 'distribution'" class="tab-content">
        <div class="section-title">Distribusi Skor Likert (1–5) per Dimensi</div>
        <div v-if="loadingDistribution" class="empty-state">Memuat data distribusi...</div>
        <div v-else-if="!distributionData.dimensions?.length" class="empty-state">Belum ada data distribusi</div>
        <div v-else class="dist-outer">
          <div v-for="d in distributionData.dimensions" :key="d.kode" class="dist-card-wide">
            <div class="dist-title" :style="{ color: dimensiColor(d.kode) }">{{ d.kode }} — {{ d.nama }}</div>
            <div class="dist-split">
              <div class="dist-half">
                <div class="dist-role-title dosen-role">Dosen (n={{ d.dosen.n }}, μ={{ d.dosen.mean }})</div>
                <div class="dist-bars">
                  <div v-for="val in [1,2,3,4,5]" :key="val" class="dist-item">
                    <span class="dist-label">{{ val }}</span>
                    <div class="dist-track">
                      <div class="dist-fill" :style="{ width: realDistPct(d.dosen, val), background: distColor(val) }" />
                    </div>
                    <span class="dist-pct">{{ d.dosen.distribution[val] ?? 0 }}</span>
                  </div>
                </div>
              </div>
              <div class="dist-half">
                <div class="dist-role-title mhs-role">Mahasiswa (n={{ d.mahasiswa.n }}, μ={{ d.mahasiswa.mean }})</div>
                <div class="dist-bars">
                  <div v-for="val in [1,2,3,4,5]" :key="val" class="dist-item">
                    <span class="dist-label">{{ val }}</span>
                    <div class="dist-track">
                      <div class="dist-fill" :style="{ width: realDistPct(d.mahasiswa, val), background: distColor(val) }" />
                    </div>
                    <span class="dist-pct">{{ d.mahasiswa.distribution[val] ?? 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: Matriks CPL-CPMK (UC-17c) -->
      <div v-if="activeTab === 'cpl-matrix'" class="tab-content">
        <div class="page-header" style="margin-bottom:16px">
          <div class="section-title" style="margin:0">Matriks CPL ↔ CPMK</div>
          <select v-model.number="matrixCourseId" @change="fetchMatrix" class="filter-select">
            <option :value="null">— Pilih Mata Kuliah —</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode }} — {{ c.nama }}</option>
          </select>
        </div>
        <div v-if="!matrixCourseId" class="empty-state">Pilih mata kuliah untuk melihat matriks CPL-CPMK</div>
        <div v-else-if="loadingMatrix" class="empty-state">Memuat matriks...</div>
        <div v-else-if="!matrixData.cpls?.length || !matrixData.cpmks?.length" class="empty-state">
          Belum ada data CPL / CPMK untuk mata kuliah ini
        </div>
        <div v-else class="matrix-wrap">
          <div class="matrix-info">
            <strong>{{ matrixData.course?.kode_mk }}</strong> — {{ matrixData.course?.nama }}
          </div>
          <div class="matrix-scroll">
            <table class="matrix-table">
              <thead>
                <tr>
                  <th class="matrix-th-cpmk">CPMK \ CPL</th>
                  <th v-for="cpl in matrixData.cpls" :key="cpl.id" class="matrix-th-cpl" :title="cpl.deskripsi">
                    {{ cpl.kode }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="cpmk in matrixData.cpmks" :key="cpmk.id">
                  <td class="matrix-td-label" :title="cpmk.deskripsi">
                    <strong>{{ cpmk.kode }}</strong>
                    <span class="bobot-badge">{{ cpmk.bobot }}%</span>
                  </td>
                  <td v-for="cpl in matrixData.cpls" :key="cpl.id"
                      class="matrix-cell"
                      :class="getCell(cpmk.id, cpl.id)?.has_mapping ? 'cell-mapped' : 'cell-empty'">
                    <span v-if="getCell(cpmk.id, cpl.id)?.has_mapping">✓</span>
                    <span v-else class="cell-dash">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="matrix-legend">
            <span class="cell-mapped" style="padding:2px 8px;border-radius:4px">✓ = Ada pemetaan</span>
            &nbsp;&nbsp;
            <span class="cell-empty" style="padding:2px 8px;border-radius:4px">— = Tidak dipetakan</span>
          </div>
        </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { useAuthStore } from '@/stores/auth'
import { getDashboardKpi, getProblemHeatmap, getCourses, getUniversities, getPrograms, getAnalyticsComparison, getAnalyticsDistribution, getAnalyticsCippScores, getAnalyticsCplCpmkMatrix, getAnalyticsComparisonGroups } from '@/api/admin'

const { isSuperadmin } = storeToRefs(useAuthStore())

const loading = ref(true)
const loadingComparison = ref(false)
const loadingDistribution = ref(false)
const loadingCippScores = ref(false)
const loadingMatrix = ref(false)
const activeTab = ref('overview')
const threshold = ref(3.0)
const filters = ref({
  course_id: null as number | null,
  university_id: null as number | null,
  program_id: null as number | null,
  role: '' as '' | 'dosen' | 'mahasiswa',
  periode_start: '' as string,
  periode_end: '' as string,
})
const universities = ref<any[]>([])
const programs = ref<any[]>([])
const filteredPrograms = computed(() =>
  filters.value.university_id
    ? programs.value.filter((p: any) => p.university_id === filters.value.university_id)
    : programs.value,
)
// Bangun query param global (UC-17f + F-07.3): hanya sertakan yang terisi
function globalParams(extra: Record<string, any> = {}) {
  const p: Record<string, any> = { ...extra }
  if (filters.value.course_id) p.course_id = filters.value.course_id
  if (filters.value.university_id) p.university_id = filters.value.university_id
  if (filters.value.program_id) p.program_id = filters.value.program_id
  if (filters.value.role) p.role = filters.value.role
  if (filters.value.periode_start) p.periode_start = filters.value.periode_start
  if (filters.value.periode_end) p.periode_end = filters.value.periode_end
  return p
}
function onUnivChange() {
  filters.value.program_id = null  // reset prodi saat universitas berubah
  fetchAll()
}
function resetFilters() {
  filters.value = { course_id: null, university_id: null, program_id: null, role: '', periode_start: '', periode_end: '' }
  fetchAll()
}
const matrixCourseId = ref<number | null>(null)
const kpi = ref<any>({ cipp_by_dimension: [], response_trend: [] })
const heatmapItems = ref<any[]>([])
const courses = ref<any[]>([])
const comparisonData = ref<any>({ total_dosen: 0, total_mahasiswa: 0, dimensions: [] })
const distributionData = ref<any>({ dimensions: [] })
const cippScoresData = ref<any>({ total_responses: 0, total_dosen: 0, total_mahasiswa: 0, dimensions: [] })
const matrixData = ref<any>({ cpls: [], cpmks: [], matrix: [] })
const loadingGroups = ref(false)
const groupBy = ref('university')
const groupsData = ref<any>({ group_by: 'university', dimensions: [], data: [] })
const radarSvg = ref<SVGSVGElement | null>(null)

// UC-02.15: unduh laporan analisis sebagai PDF (client-side jsPDF)
function exportAnalyticsPdf() {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const mx = 14
  let y = 18
  doc.setFontSize(16); doc.setTextColor(26, 54, 93); doc.setFont('helvetica', 'bold')
  doc.text('SINOKU — Laporan Analisis CIPP', mx, y); y += 8
  doc.setFontSize(10); doc.setTextColor(113, 128, 150); doc.setFont('helvetica', 'normal')
  const filterTxt: string[] = []
  if (filters.value.course_id) { const c = courses.value.find((x: any) => x.id === filters.value.course_id); filterTxt.push('MK: ' + (c?.kode ?? filters.value.course_id)) }
  if (filters.value.role) filterTxt.push('Peran: ' + filters.value.role)
  if (filters.value.periode_start || filters.value.periode_end) filterTxt.push(`Periode: ${filters.value.periode_start || '…'} s/d ${filters.value.periode_end || '…'}`)
  doc.text(filterTxt.length ? filterTxt.join('  |  ') : 'Semua data', mx, y); y += 6
  doc.text('Dibuat: ' + new Date().toLocaleString('id-ID'), mx, y); y += 8

  // KPI ringkas
  autoTable(doc, {
    startY: y,
    head: [['Total Respons', 'Dosen', 'Mahasiswa', 'Rata-rata CIPP']],
    body: [[String(kpi.value.total_responses ?? 0), String(kpi.value.total_dosen ?? 0), String(kpi.value.total_mahasiswa ?? 0), (kpi.value.avg_cipp_score ?? 0).toFixed?.(2) ?? '—']],
    headStyles: { fillColor: [26, 54, 93], textColor: 255, fontStyle: 'bold' },
    styles: { fontSize: 10, halign: 'center' }, margin: { left: mx, right: mx },
  })

  // Skor per dimensi
  autoTable(doc, {
    startY: (doc as any).lastAutoTable.finalY + 8,
    head: [['Kode', 'Dimensi', 'Rata-rata', 'Std Dev', 'Interpretasi']],
    body: (kpi.value.cipp_by_dimension ?? []).map((d: any) => [
      d.kode, d.nama, d.rata_rata?.toFixed(2) ?? '—', d.std_dev?.toFixed(2) ?? '—', interpretasi(d.rata_rata).replace(/[^\x20-\x7E]/g, '').trim(),
    ]),
    headStyles: { fillColor: [26, 54, 93], textColor: 255, fontStyle: 'bold' },
    styles: { fontSize: 10 }, margin: { left: mx, right: mx },
  })
  doc.save('SINOKU-Analisis-CIPP.pdf')
}

// F-11.5: unduh grafik radar sebagai SVG (native) atau PNG (via canvas)
function downloadChart(format: 'png' | 'svg') {
  const el = radarSvg.value
  if (!el) return
  const clone = el.cloneNode(true) as SVGSVGElement
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  clone.style.background = '#ffffff'
  const svgStr = new XMLSerializer().serializeToString(clone)
  const trigger = (url: string, ext: string) => {
    const a = document.createElement('a')
    a.href = url; a.download = `radar-cipp.${ext}`; a.click()
  }
  if (format === 'svg') {
    const blob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    trigger(url, 'svg'); URL.revokeObjectURL(url)
    return
  }
  // PNG: render SVG ke canvas resolusi 2x lalu ekspor
  const img = new Image()
  const svgUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgStr)))
  img.onload = () => {
    const scale = 2, size = 300
    const canvas = document.createElement('canvas')
    canvas.width = size * scale; canvas.height = size * scale
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.scale(scale, scale)
    ctx.drawImage(img, 0, 0, size, size)
    canvas.toBlob((blob) => {
      if (!blob) return
      const url = URL.createObjectURL(blob)
      trigger(url, 'png'); URL.revokeObjectURL(url)
    }, 'image/png')
  }
  img.src = svgUrl
}

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
function realDistPct(roleData: any, val: number) {
  const total = roleData?.n ?? 0
  if (!total) return '0%'
  const count = roleData?.distribution?.[val] ?? 0
  return `${Math.round((count / total) * 100)}%`
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
  const res = await getDashboardKpi(globalParams())
  kpi.value = res.data
}
async function fetchHeatmap() {
  const res = await getProblemHeatmap(globalParams({ threshold: threshold.value }))
  heatmapItems.value = res.data.items
}
async function fetchComparison() {
  loadingComparison.value = true
  try {
    const res = await getAnalyticsComparison(globalParams())
    comparisonData.value = res.data
  } catch { comparisonData.value = { total_dosen: 0, total_mahasiswa: 0, dimensions: [] } }
  finally { loadingComparison.value = false }
}
async function fetchDistribution() {
  loadingDistribution.value = true
  try {
    const res = await getAnalyticsDistribution(globalParams())
    distributionData.value = res.data
  } catch { distributionData.value = { dimensions: [] } }
  finally { loadingDistribution.value = false }
}
function getCell(cpmkId: number, cplId: number) {
  return matrixData.value.matrix?.find((m: any) => m.cpmk_id === cpmkId && m.cpl_id === cplId)
}
const groupByLabel = computed(() => ({ university: 'Universitas', program: 'Program Studi', course: 'Mata Kuliah' }[groupBy.value] ?? 'Grup'))
function rowAvg(row: any) {
  const vals = Object.values(row.cipp).filter((v: any) => v != null) as number[]
  if (!vals.length) return '—'
  return (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2)
}
async function fetchComparisonGroups() {
  loadingGroups.value = true
  try {
    const res = await getAnalyticsComparisonGroups(groupBy.value)
    groupsData.value = res.data
  } catch { groupsData.value = { group_by: groupBy.value, dimensions: [], data: [] } }
  finally { loadingGroups.value = false }
}
async function fetchCippScores() {
  loadingCippScores.value = true
  try {
    const res = await getAnalyticsCippScores(globalParams())
    cippScoresData.value = res.data
  } catch { cippScoresData.value = { total_responses: 0, total_dosen: 0, total_mahasiswa: 0, dimensions: [] } }
  finally { loadingCippScores.value = false }
}
async function fetchMatrix() {
  if (!matrixCourseId.value) { matrixData.value = { cpls: [], cpmks: [], matrix: [] }; return }
  loadingMatrix.value = true
  try {
    const res = await getAnalyticsCplCpmkMatrix(matrixCourseId.value)
    matrixData.value = res.data
  } catch { matrixData.value = { cpls: [], cpmks: [], matrix: [] } }
  finally { loadingMatrix.value = false }
}
async function fetchAll() {
  loading.value = true
  try { await Promise.all([fetchKpi(), fetchHeatmap(), fetchComparison(), fetchDistribution(), fetchCippScores()]) }
  finally { loading.value = false }
}

// Lazy-load tab Perbandingan Univ/Prodi/MK saat pertama dibuka
watch(activeTab, (tab) => {
  if (tab === 'comparison-groups' && !groupsData.value.data.length) fetchComparisonGroups()
})

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = (res.data.data ?? []).map((c: any) => ({ id: c.id, kode: c.kode_mk, nama: c.nama_id }))
  // F-07.3: muat universitas & prodi untuk filter global (superadmin)
  if (isSuperadmin.value) {
    const [u, p] = await Promise.all([
      getUniversities({ limit: 200 }).catch(() => ({ data: { data: [] } })),
      getPrograms({ limit: 500 }).catch(() => ({ data: { data: [] } })),
    ])
    universities.value = u.data.data ?? []
    programs.value = p.data.data ?? []
  }
  await fetchAll()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.header-filters{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.filter-reset{padding:8px 12px;border:1px solid #fc8181;background:#fff5f5;color:#c53030;border-radius:6px;font-size:12px;cursor:pointer}
.filter-reset:hover{background:#fed7d7}
.filter-hint{font-size:11px;color:#a0aec0;font-style:italic}
.chart-dl{display:flex;gap:6px}
.chart-dl-btn{background:#fff;border:1px solid #cbd5e0;color:#2d3748;padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer}
.chart-dl-btn:hover{background:#f7fafc;border-color:#a0aec0}
.btn-pdf{background:#fff;border:1px solid #cbd5e0;color:#1a365d;padding:6px 12px;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer}
.btn-pdf:hover{background:#f7fafc;border-color:#1a365d}
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
.comp-meta{display:flex;gap:16px;margin-bottom:16px;padding:10px 14px;background:#f7fafc;border-radius:8px}
.comp-meta-item{font-size:13px;font-weight:600}
.bar-n{font-size:11px;color:#a0aec0;margin-left:2px}
.dist-outer{display:flex;flex-direction:column;gap:16px}
.dist-card-wide{border:1px solid #e2e8f0;border-radius:10px;padding:16px}
.dist-split{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:10px}
.dist-half{display:flex;flex-direction:column;gap:6px}
.dist-role-title{font-size:12px;font-weight:700;margin-bottom:6px}
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
.cipp-scores-dim{margin-bottom:24px;border:1px solid #e2e8f0;border-radius:10px;padding:16px}
.cipp-scores-header{display:flex;align-items:center;gap:14px;border-left:4px solid;padding-left:12px;flex-wrap:wrap}
.cipp-kode-sm{font-size:20px;font-weight:900}
.cipp-nama-sm{font-size:13px;font-weight:600;color:#2d3748}
.cipp-avg-sm{font-size:13px;color:#4a5568;margin-left:auto}
.cipp-std-sm{font-size:12px;color:#a0aec0}
.cipp-n-sm{font-size:12px;color:#a0aec0}
.matrix-wrap{display:flex;flex-direction:column;gap:16px}
.matrix-info{font-size:14px;color:#2d3748;padding:10px 14px;background:#f7fafc;border-radius:8px}
.matrix-scroll{overflow-x:auto}
.matrix-table{border-collapse:collapse;min-width:400px}
.matrix-th-cpmk{padding:10px 14px;background:#1a365d;color:#fff;font-size:12px;text-align:left;white-space:nowrap;min-width:160px}
.matrix-th-cpl{padding:10px 14px;background:#1a365d;color:#fff;font-size:12px;text-align:center;min-width:80px}
.matrix-td-label{padding:8px 14px;background:#f7fafc;font-size:12px;white-space:nowrap;border-bottom:1px solid #e2e8f0}
.bobot-badge{margin-left:6px;background:#e2e8f0;color:#4a5568;border-radius:4px;padding:1px 5px;font-size:10px}
.matrix-cell{padding:8px;text-align:center;font-size:14px;border-bottom:1px solid #f0f4f8;border-left:1px solid #f0f4f8}
.cell-mapped{background:#c6f6d5;color:#276749;font-weight:700}
.cell-empty{background:#fff;color:#e2e8f0}
.cell-dash{color:#e2e8f0}
.matrix-legend{display:flex;align-items:center;gap:8px;font-size:12px;color:#718096}
@media(max-width:768px){
  .cipp-grid{grid-template-columns:repeat(2,1fr)}
  .kpi-row{grid-template-columns:repeat(2,1fr)}
  .dist-grid{grid-template-columns:1fr}
  .comp-label{width:60px}
}
</style>
