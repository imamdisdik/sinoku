<template>
  <div>
    <!-- Toolbar -->
    <div class="page-header no-print">
      <button class="btn-back" @click="router.push({ name: 'admin-reports' })">← Kembali</button>
      <div class="action-group">
        <button class="btn-export" @click="doExportXlsx">&#128196; Excel</button>
        <button class="btn-export" @click="doExportCsv">&#128196; CSV</button>
        <button class="btn-print" @click="window.print()">&#128424; Cetak / PDF</button>
      </div>
    </div>

    <div v-if="loading" class="center-msg">Memuat laporan...</div>

    <div v-else-if="!report" class="center-msg err">Laporan tidak ditemukan.</div>

    <div v-else class="report-body" id="report-print">

      <!-- Header Laporan -->
      <div class="report-header">
        <div class="report-logo">SINOKU</div>
        <h1 class="report-title">{{ report.title }}</h1>
        <div class="report-meta">
          Mata Kuliah #{{ report.course_id }} &nbsp;|&nbsp;
          Periode: {{ report.periode_start }} s/d {{ report.periode_end }} &nbsp;|&nbsp;
          Dibuat: {{ formatDate(report.generated_at) }}
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-num">{{ snap.total_respons }}</div>
          <div class="kpi-label">Total Respons</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-num">{{ snap.total_dosen }}</div>
          <div class="kpi-label">Dosen</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-num">{{ snap.total_mahasiswa }}</div>
          <div class="kpi-label">Mahasiswa</div>
        </div>
        <div class="kpi-card kpi-highlight">
          <div class="kpi-num">{{ overallAvg }}</div>
          <div class="kpi-label">Rata-rata CIPP</div>
        </div>
      </div>

      <!-- Skor Per Dimensi -->
      <div class="section-card">
        <h2 class="section-title">Skor Per Dimensi CIPP</h2>
        <table class="dim-table">
          <thead>
            <tr>
              <th>Dimensi</th>
              <th>Rata-rata Dosen</th>
              <th>Rata-rata Mahasiswa</th>
              <th>Grafik</th>
              <th>Kategori</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in snap.dimensions" :key="d.kode">
              <td>
                <span class="dim-dot" :style="{ background: d.warna_hex }"></span>
                <strong>{{ d.kode }}</strong> — {{ d.nama }}
              </td>
              <td class="score-cell">{{ d.avg_dosen != null ? d.avg_dosen.toFixed(2) : '—' }}</td>
              <td class="score-cell">{{ d.avg_mahasiswa != null ? d.avg_mahasiswa.toFixed(2) : '—' }}</td>
              <td style="min-width:160px">
                <div class="bar-wrap">
                  <div class="bar dosen-bar" :style="{ width: barPct(d.avg_dosen) }" :title="`Dosen: ${d.avg_dosen}`"></div>
                </div>
                <div class="bar-wrap" style="margin-top:3px">
                  <div class="bar mhs-bar" :style="{ width: barPct(d.avg_mahasiswa) }" :title="`Mahasiswa: ${d.avg_mahasiswa}`"></div>
                </div>
              </td>
              <td><span :class="categoryBadge(avgOf(d))">{{ categoryLabel(avgOf(d)) }}</span></td>
            </tr>
          </tbody>
        </table>
        <div class="bar-legend">
          <span class="legend-dot dosen-dot"></span> Dosen &nbsp;&nbsp;
          <span class="legend-dot mhs-dot"></span> Mahasiswa
        </div>
      </div>

      <!-- Rekomendasi -->
      <div class="section-card">
        <h2 class="section-title">Rekomendasi Per Dimensi</h2>
        <div v-for="d in snap.dimensions" :key="d.kode + '-rec'" class="rec-item">
          <div class="rec-label">
            <span class="dim-dot" :style="{ background: d.warna_hex }"></span>
            <strong>{{ d.kode }} — {{ d.nama }}</strong>
          </div>
          <p class="rec-text">{{ d.recommendation }}</p>
        </div>
      </div>

      <!-- Profil Responden -->
      <div class="section-card" v-if="snap.total_mahasiswa > 0">
        <h2 class="section-title">Profil Responden Mahasiswa</h2>
        <div class="profile-grid">
          <div class="profile-group">
            <h3 class="profile-subtitle">Jenis Kelamin</h3>
            <div v-for="(val, key) in snap.profil_responden.gender" :key="key" class="dist-row">
              <span class="dist-label">{{ key }}</span>
              <div class="dist-bar-wrap">
                <div class="dist-bar" :style="{ width: distPct(val, snap.total_mahasiswa) }"></div>
              </div>
              <span class="dist-val">{{ val }} ({{ distPct(val, snap.total_mahasiswa) }})</span>
            </div>
          </div>
          <div class="profile-group">
            <h3 class="profile-subtitle">Level HSK</h3>
            <div v-for="(val, key) in snap.profil_responden.hsk" :key="key" class="dist-row">
              <span class="dist-label">{{ key }}</span>
              <div class="dist-bar-wrap">
                <div class="dist-bar" :style="{ width: distPct(val, snap.total_mahasiswa) }"></div>
              </div>
              <span class="dist-val">{{ val }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="report-footer">
        Laporan ini digenerate otomatis oleh sistem SINOKU &mdash; {{ formatDate(report.generated_at) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { getReport, exportWithAuth, exportCsvWithAuth } from '@/api/admin'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const report = ref<any>(null)
const loading = ref(true)

const snap = computed(() => report.value?.snapshot_json ?? {
  total_respons: 0, total_dosen: 0, total_mahasiswa: 0,
  overall_avg_dosen: null, overall_avg_mahasiswa: null,
  dimensions: [], profil_responden: { gender: {}, semester: {}, hsk: {} },
})

const overallAvg = computed(() => {
  const vals = [snap.value.overall_avg_dosen, snap.value.overall_avg_mahasiswa].filter(v => v != null)
  if (!vals.length) return '—'
  return (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2)
})

function avgOf(d: any) {
  const vals = [d.avg_dosen, d.avg_mahasiswa].filter(v => v != null)
  return vals.length ? vals.reduce((a: number, b: number) => a + b, 0) / vals.length : null
}

function barPct(val: number | null) {
  if (val == null) return '0%'
  return (val / 5 * 100).toFixed(0) + '%'
}

function distPct(val: number, total: number) {
  if (!total) return '0%'
  return (val / total * 100).toFixed(0) + '%'
}

function categoryLabel(avg: number | null) {
  if (avg == null) return 'N/A'
  if (avg >= 4.5) return 'Sangat Baik'
  if (avg >= 3.5) return 'Baik'
  if (avg >= 2.5) return 'Cukup'
  return 'Kurang'
}

function categoryBadge(avg: number | null) {
  if (avg == null) return 'cat-na'
  if (avg >= 4.5) return 'cat-a'
  if (avg >= 3.5) return 'cat-b'
  if (avg >= 2.5) return 'cat-c'
  return 'cat-d'
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

async function doExportXlsx() {
  try {
    const res = await exportWithAuth('scores', { course_id: report.value?.course_id })
    triggerDownload(res.data, 'sinoku_skor_cipp.xlsx')
  } catch {
    ui.showToast('Gagal export Excel', 'error')
  }
}

async function doExportCsv() {
  try {
    const res = await exportCsvWithAuth('scores', { course_id: report.value?.course_id })
    triggerDownload(res.data, 'sinoku_skor_cipp.csv')
  } catch {
    ui.showToast('Gagal export CSV', 'error')
  }
}

onMounted(async () => {
  try {
    const res = await getReport(route.params.id as string)
    report.value = res.data
  } catch {
    report.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.btn-back{background:#f7fafc;color:#4a5568;border:1px solid #e2e8f0;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer}
.action-group{display:flex;gap:8px}
.btn-export{background:#fff;color:#2b6cb0;border:1px solid #bee3f8;padding:7px 14px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-export:hover{background:#ebf8ff}
.btn-print{background:#1a365d;color:#fff;border:none;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer}
.center-msg{text-align:center;padding:60px;color:#718096;font-size:15px}
.center-msg.err{color:#e53e3e}

/* Report body */
.report-body{max-width:860px;margin:0 auto}
.report-header{text-align:center;background:#1a365d;color:#fff;border-radius:12px;padding:28px 20px;margin-bottom:24px}
.report-logo{font-size:12px;font-weight:700;letter-spacing:2px;color:#90cdf4;margin-bottom:8px}
.report-title{font-size:22px;font-weight:700;margin:0 0 8px}
.report-meta{font-size:12px;color:rgba(255,255,255,0.7)}

.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.kpi-card{background:#fff;border-radius:10px;padding:20px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.07)}
.kpi-highlight{background:#1a365d;color:#fff}
.kpi-num{font-size:28px;font-weight:800;color:#1a365d}
.kpi-highlight .kpi-num{color:#90cdf4}
.kpi-label{font-size:11px;color:#718096;margin-top:4px;font-weight:600}
.kpi-highlight .kpi-label{color:rgba(255,255,255,0.7)}

.section-card{background:#fff;border-radius:10px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.07)}
.section-title{font-size:16px;font-weight:700;color:#1a365d;margin:0 0 16px;padding-bottom:10px;border-bottom:2px solid #ebf8ff}

.dim-table{width:100%;border-collapse:collapse;font-size:13px}
.dim-table th{background:#f7fafc;padding:8px 12px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.dim-table td{padding:10px 12px;border-bottom:1px solid #f0f4f8;vertical-align:middle}
.dim-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:middle}
.score-cell{text-align:center;font-weight:700;font-size:15px}
.bar-wrap{height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden}
.bar{height:100%;border-radius:4px;transition:width .3s}
.dosen-bar{background:#3182ce}
.mhs-bar{background:#38a169}
.bar-legend{margin-top:10px;font-size:12px;color:#718096;display:flex;align-items:center;gap:4px}
.legend-dot{display:inline-block;width:10px;height:10px;border-radius:50%}
.dosen-dot{background:#3182ce}
.mhs-dot{background:#38a169}

.cat-a{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.cat-b{background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.cat-c{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.cat-d{background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.cat-na{background:#f3f4f6;color:#6b7280;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}

.rec-item{padding:12px 0;border-bottom:1px solid #f0f4f8}
.rec-item:last-child{border-bottom:none}
.rec-label{font-size:13px;font-weight:600;color:#2d3748;margin-bottom:4px;display:flex;align-items:center;gap:6px}
.rec-text{margin:0;font-size:13px;color:#4a5568;line-height:1.6}

.profile-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.profile-subtitle{font-size:13px;font-weight:700;color:#4a5568;margin:0 0 12px}
.dist-row{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:12px}
.dist-label{width:120px;color:#4a5568;flex-shrink:0}
.dist-bar-wrap{flex:1;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden}
.dist-bar{height:100%;background:#3182ce;border-radius:4px}
.dist-val{width:60px;text-align:right;color:#718096;flex-shrink:0}

.report-footer{text-align:center;font-size:11px;color:#a0aec0;padding:16px 0}

@media print {
  .no-print { display: none !important; }
  .report-body { max-width: 100%; }
  .section-card, .kpi-card { box-shadow: none; border: 1px solid #e2e8f0; }
  .report-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .dosen-bar, .mhs-bar, .dist-bar { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
