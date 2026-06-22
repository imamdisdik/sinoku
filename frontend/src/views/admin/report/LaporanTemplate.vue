<template>
  <div>
    <!-- Toolbar -->
    <div class="page-header no-print">
      <h1 class="page-title">Laporan Template CIPP</h1>
      <div class="filter-bar">
        <select v-model.number="courseId" class="inp">
          <option :value="null">— Pilih Mata Kuliah —</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
        </select>
        <select v-model="role" class="inp">
          <option value="semua">Mahasiswa &amp; Dosen</option>
          <option value="mahasiswa">Mahasiswa</option>
          <option value="dosen">Dosen</option>
        </select>
        <input type="date" v-model="periodeStart" class="inp" title="Periode mulai" />
        <input type="date" v-model="periodeEnd" class="inp" title="Periode akhir" />
        <button class="btn-primary" @click="generate" :disabled="!courseId || loading">{{ loading ? 'Memuat...' : 'Tampilkan' }}</button>
        <button v-if="data" class="btn-print" @click="printReport">🖨 Cetak / PDF</button>
      </div>
    </div>

    <div v-if="loading" class="center-msg">Memuat laporan...</div>
    <div v-else-if="!data" class="center-msg">Pilih mata kuliah, peran, dan periode lalu klik <strong>Tampilkan</strong>.</div>

    <!-- Dokumen Laporan -->
    <div v-else class="doc" id="laporan-doc">
      <div class="doc-head">
        <h2>LAPORAN MONITORING DAN EVALUASI<br />PEMBELAJARAN KEBUDAYAAN TIONGKOK</h2>
        <p class="doc-sub">Berbasis model CIPP — Sistem Evaluasi SINOKU</p>
      </div>

      <!-- A. Identitas -->
      <h3 class="sec">A. Identitas Program</h3>
      <table class="id-table">
        <tr><td class="lbl">Universitas</td><td>{{ data.identitas.universitas }}</td></tr>
        <tr><td class="lbl">Program Studi</td><td>{{ data.identitas.program_studi }}</td></tr>
        <tr><td class="lbl">Mata Kuliah</td><td>{{ data.identitas.mata_kuliah }}</td></tr>
        <tr><td class="lbl">Semester</td><td>{{ data.identitas.semester }}</td></tr>
        <tr><td class="lbl">Jumlah SKS</td><td>{{ data.identitas.jumlah_sks }}</td></tr>
        <tr><td class="lbl">Peran Responden</td><td>{{ data.identitas.peran_responden }}</td></tr>
        <tr><td class="lbl">Waktu Pelaksanaan</td><td>{{ data.identitas.periode }}</td></tr>
        <tr><td class="lbl">Jumlah Responden</td><td>{{ data.identitas.jumlah_responden }}</td></tr>
      </table>

      <!-- B. Ringkasan 15 Indikator -->
      <h3 class="sec">B. Ringkasan 15 Indikator Utama</h3>
      <table class="data-table">
        <thead><tr><th>No.</th><th>Dimensi</th><th>Subdimensi</th><th class="num">Rata-rata (%)</th></tr></thead>
        <tbody>
          <tr v-for="(s, i) in data.subdimensi" :key="s.kode">
            <td>{{ i + 1 }}</td><td>{{ s.dimensi }}</td><td>{{ s.nama }}</td>
            <td class="num"><span :class="pctClass(s.persen)">{{ s.persen != null ? s.persen + '%' : '—' }}</span></td>
          </tr>
        </tbody>
      </table>

      <!-- C. Indikator Detail -->
      <h3 class="sec">C. Indikator Detail SINOKU ({{ data.indikator.length }} Indikator)</h3>
      <template v-for="grp in groupedIndikator" :key="grp.kode">
        <div class="subgrp">{{ grp.kode }} — {{ grp.nama }}</div>
        <table class="data-table">
          <thead><tr><th>Kode</th><th>Indikator</th><th class="num">Persentase (%)</th></tr></thead>
          <tbody>
            <tr v-for="it in grp.items" :key="it.kode">
              <td>{{ it.kode }}</td><td>{{ it.indikator }}</td>
              <td class="num"><span :class="pctClass(it.persen)">{{ it.persen != null ? it.persen + '%' : '—' }}</span></td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- D. Interpretasi -->
      <h3 class="sec">D. Interpretasi Hasil dan Rekomendasi</h3>
      <div class="interp">
        <p class="interp-q">1. Kekuatan utama program:</p>
        <ul><li v-for="(k, i) in data.interpretasi.kekuatan" :key="'k'+i">{{ k }}</li></ul>
        <p class="interp-q">2. Area yang perlu ditingkatkan:</p>
        <ul><li v-for="(k, i) in data.interpretasi.kelemahan" :key="'w'+i">{{ k }}</li></ul>
        <p class="interp-q">3. Rekomendasi tindak lanjut:</p>
        <ul><li v-for="(k, i) in data.interpretasi.rekomendasi" :key="'r'+i">{{ k }}</li></ul>
      </div>

      <div class="doc-foot">Digenerate otomatis oleh SINOKU — {{ new Date().toLocaleDateString('id-ID') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import { getCourses, getTemplateReportData } from '@/api/admin'

const ui = useUiStore()
const courses = ref<any[]>([])
const courseId = ref<number | null>(null)
const role = ref('semua')
const periodeStart = ref('2025-01-01')
const periodeEnd = ref('2026-12-31')
const data = ref<any>(null)
const loading = ref(false)

const groupedIndikator = computed(() => {
  if (!data.value) return []
  const map: Record<string, any> = {}
  for (const it of data.value.indikator) {
    if (!map[it.subdim_kode]) {
      const sd = data.value.subdimensi.find((s: any) => s.kode === it.subdim_kode)
      map[it.subdim_kode] = { kode: it.subdim_kode, nama: sd?.nama ?? it.subdim_kode, items: [] }
    }
    map[it.subdim_kode].items.push(it)
  }
  return Object.values(map)
})

function pctClass(p: number | null) {
  if (p == null) return 'pna'
  return p >= 75 ? 'pok' : p >= 60 ? 'pwarn' : 'pbad'
}

async function generate() {
  if (!courseId.value) return
  loading.value = true
  data.value = null
  try {
    const res = await getTemplateReportData({
      course_id: courseId.value, role: role.value,
      periode_start: periodeStart.value, periode_end: periodeEnd.value,
    })
    data.value = res.data
    if (!res.data.identitas.jumlah_responden) ui.showToast('Tidak ada respons pada filter ini', 'warning')
  } catch {
    ui.showToast('Gagal memuat laporan', 'error')
  } finally { loading.value = false }
}

function printReport() { window.print() }

onMounted(async () => {
  const res = await getCourses({ limit: 200 }).catch(() => ({ data: { data: [] } }))
  courses.value = res.data.data ?? []
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.filter-bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.inp{padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.btn-primary{background:#1a365d;color:#fff;border:none;padding:8px 16px;border-radius:6px;font-size:13px;cursor:pointer}
.btn-print{background:#fff;border:1px solid #cbd5e0;color:#2d3748;padding:8px 14px;border-radius:6px;font-size:13px;cursor:pointer}
.center-msg{background:#fff;border-radius:10px;padding:48px;text-align:center;color:#718096;box-shadow:0 1px 3px rgba(0,0,0,.07)}
.doc{background:#fff;border-radius:10px;padding:40px;box-shadow:0 1px 3px rgba(0,0,0,.08);max-width:900px;margin:0 auto;color:#1a202c}
.doc-head{text-align:center;border-bottom:3px solid #1a365d;padding-bottom:16px;margin-bottom:24px}
.doc-head h2{font-size:18px;color:#1a365d;margin:0;line-height:1.4}
.doc-sub{font-size:12px;color:#718096;margin:8px 0 0}
.sec{font-size:15px;color:#1a365d;margin:28px 0 10px;border-left:4px solid #3182ce;padding-left:10px}
.id-table{width:100%;border-collapse:collapse;font-size:13px}
.id-table td{padding:6px 8px;border-bottom:1px solid #edf2f7}
.id-table .lbl{font-weight:600;width:200px;color:#4a5568}
.data-table{width:100%;border-collapse:collapse;font-size:12.5px;margin-bottom:12px}
.data-table th{background:#1a365d;color:#fff;padding:7px 9px;text-align:left;font-weight:600}
.data-table th.num,.data-table td.num{text-align:center}
.data-table td{padding:6px 9px;border-bottom:1px solid #edf2f7}
.subgrp{font-weight:700;color:#2c5282;font-size:13px;margin:14px 0 6px}
.pok{color:#2f855a;font-weight:700}
.pwarn{color:#b7791f;font-weight:700}
.pbad{color:#c53030;font-weight:700}
.pna{color:#a0aec0}
.interp{font-size:13px}
.interp-q{font-weight:600;color:#2d3748;margin:12px 0 4px}
.interp ul{margin:0 0 8px;padding-left:22px}
.interp li{margin:3px 0;line-height:1.5}
.doc-foot{text-align:center;font-size:11px;color:#a0aec0;margin-top:28px;border-top:1px solid #edf2f7;padding-top:12px}
@media print {
  .no-print{display:none !important}
  .doc{box-shadow:none;max-width:100%;padding:0}
  .sec,.subgrp{break-after:avoid}
  .data-table{break-inside:auto}
  tr{break-inside:avoid}
}
</style>
