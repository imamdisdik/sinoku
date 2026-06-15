<template>
  <div class="container" style="max-width:700px; padding-top:40px;">
    <!-- Form cari kode -->
    <div class="card no-print" style="margin-bottom:24px;">
      <h1 style="font-size:20px; font-weight:800; color:#1a365d; margin:0 0 16px;">{{ t('result.title') }}</h1>
      <div style="display:flex; gap:12px;">
        <input class="form-input" v-model="kode" :placeholder="t('result.code_placeholder')" style="flex:1;" @keyup.enter="search" />
        <button class="btn btn-primary" @click="search" :disabled="!kode || loading">
          {{ loading ? t('common.loading') : t('result.search') }}
        </button>
      </div>
      <p v-if="error" style="color:#e53e3e; font-size:13px; margin-top:8px;">{{ error }}</p>
    </div>

    <!-- Hasil -->
    <div v-if="result" class="card" id="result-card">
      <div class="result-header" style="margin-bottom:20px; display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
        <div>
          <div style="font-size:12px; color:#718096;">{{ result.course.kode_mk }}</div>
          <div style="font-size:18px; font-weight:700;">{{ result.course.nama_id }}</div>
          <div style="font-size:12px; color:#718096; margin-top:4px;">
            Peran: {{ result.role }} | Bahasa: {{ result.bahasa }} |
            Submit: {{ new Date(result.submitted_at).toLocaleDateString('id-ID') }}
          </div>
        </div>
        <div class="no-print" style="display:flex; gap:8px; flex-shrink:0;">
          <button class="btn-action" @click="downloadPdf" :disabled="generating">
            {{ generating ? '...' : '⬇ PDF' }}
          </button>
          <button class="btn-action" @click="doPrint">🖨 Cetak</button>
        </div>
      </div>

      <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.cipp_score') }}</h3>
      <div class="score-grid">
        <div v-for="s in result.cipp_scores" :key="s.kode" class="score-card">
          <div class="score-card__kode">{{ s.kode }}</div>
          <div class="score-card__name">{{ s.dimensi }}</div>
          <div class="score-card__score">{{ s.skor_rata.toFixed(2) }}</div>
          <div class="score-card__bar">
            <div class="score-fill" :style="{ width: `${(s.skor_rata / 5) * 100}%` }" />
          </div>
          <div class="score-card__n">n={{ s.jumlah_item }}</div>
        </div>
      </div>

      <!-- F-05.3: Ringkasan Capaian Pembelajaran (dimensi Produk) -->
      <div v-if="result.capaian_pembelajaran && result.capaian_pembelajaran.length" style="margin-top:24px;">
        <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 4px;">Ringkasan Capaian Pembelajaran</h3>
        <p style="font-size:11px; color:#a0aec0; margin:0 0 12px;">Berdasarkan dimensi Produk (capaian kompetensi & hasil belajar). Target tercapai bila skor ≥ 3.5.</p>
        <table class="capaian-table">
          <thead><tr><th>Aspek Capaian</th><th>Skor</th><th>Target</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="c in result.capaian_pembelajaran" :key="c.kode">
              <td><strong>{{ c.kode }}</strong> — {{ c.nama }}</td>
              <td>{{ c.skor_rata.toFixed(2) }}</td>
              <td>{{ c.target.toFixed(1) }}</td>
              <td><span :class="c.tercapai ? 'cap-ok' : 'cap-no'">{{ c.tercapai ? '✓ Tercapai' : '✗ Belum' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="result.open_answers.length" style="margin-top:24px;">
        <h3 style="font-size:14px; font-weight:700; color:#4a5568; margin:0 0 12px;">{{ t('result.open_answers') }}</h3>
        <div v-for="(oa, i) in result.open_answers" :key="i" style="margin-bottom:14px; padding:12px; background:#f7fafc; border-radius:8px;">
          <div style="font-size:13px; font-weight:600; color:#2d3748; margin-bottom:6px;">{{ oa.pertanyaan }}</div>
          <div style="font-size:13px; color:#4a5568;">{{ oa.jawaban }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { publicApi } from '@/api/public'

const { t } = useI18n()
const kode = ref('')
const loading = ref(false)
const generating = ref(false)
const error = ref('')
const result = ref<any>(null)

async function search() {
  if (!kode.value.trim()) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await publicApi.getResult(kode.value.trim().toUpperCase())
    result.value = data
  } catch (e: any) {
    error.value = e.response?.data?.detail || t('common.error')
  } finally {
    loading.value = false
  }
}

// UC-10: Cetak hasil (print-friendly via @media print)
function doPrint() {
  window.print()
}

// UC-09: Download hasil sebagai PDF (jsPDF, client-side)
function downloadPdf() {
  if (!result.value) return
  generating.value = true
  try {
    const r = result.value
    const doc = new jsPDF({ unit: 'mm', format: 'a4' })
    const marginX = 14
    let y = 18

    doc.setFontSize(16); doc.setTextColor(26, 54, 93); doc.setFont('helvetica', 'bold')
    doc.text('SINOKU — Hasil Evaluasi CIPP', marginX, y)
    y += 8
    doc.setFontSize(11); doc.setTextColor(45, 55, 72); doc.setFont('helvetica', 'normal')
    doc.text(`${r.course.kode_mk} — ${r.course.nama_id}`, marginX, y)
    y += 6
    doc.setFontSize(9); doc.setTextColor(113, 128, 150)
    const submit = r.submitted_at ? new Date(r.submitted_at).toLocaleDateString('id-ID') : '-'
    doc.text(`Kode: ${r.kode}   |   Peran: ${r.role}   |   Bahasa: ${r.bahasa}   |   Submit: ${submit}`, marginX, y)
    y += 8

    // Tabel skor CIPP per dimensi
    autoTable(doc, {
      startY: y,
      head: [['Kode', 'Dimensi', 'Skor Rata-rata', 'Std Dev', 'Jumlah Item']],
      body: (r.cipp_scores ?? []).map((s: any) => [
        s.kode, s.dimensi, s.skor_rata.toFixed(2), s.std_dev.toFixed(2), String(s.jumlah_item),
      ]),
      headStyles: { fillColor: [26, 54, 93], textColor: 255, fontStyle: 'bold' },
      styles: { fontSize: 10, cellPadding: 3 },
      margin: { left: marginX, right: marginX },
    })

    // F-05.3: Capaian Pembelajaran (Produk)
    const capaian = r.capaian_pembelajaran ?? []
    if (capaian.length) {
      autoTable(doc, {
        startY: (doc as any).lastAutoTable.finalY + 8,
        head: [['Aspek Capaian', 'Skor', 'Target', 'Status']],
        body: capaian.map((c: any) => [`${c.kode} — ${c.nama}`, c.skor_rata.toFixed(2), c.target.toFixed(1), c.tercapai ? 'Tercapai' : 'Belum']),
        headStyles: { fillColor: [56, 161, 105], textColor: 255, fontStyle: 'bold' },
        styles: { fontSize: 10, cellPadding: 3 },
        margin: { left: marginX, right: marginX },
      })
    }

    // Jawaban terbuka
    const openAnswers = r.open_answers ?? []
    if (openAnswers.length) {
      let yAfter = (doc as any).lastAutoTable.finalY + 10
      doc.setFontSize(12); doc.setTextColor(45, 55, 72); doc.setFont('helvetica', 'bold')
      doc.text('Jawaban Pertanyaan Terbuka', marginX, yAfter)
      yAfter += 6
      doc.setFont('helvetica', 'normal'); doc.setFontSize(10)
      for (const oa of openAnswers) {
        if (yAfter > 270) { doc.addPage(); yAfter = 18 }
        doc.setTextColor(45, 55, 72); doc.setFont('helvetica', 'bold')
        const qLines = doc.splitTextToSize(oa.pertanyaan, 180)
        doc.text(qLines, marginX, yAfter); yAfter += qLines.length * 5 + 1
        doc.setTextColor(74, 85, 104); doc.setFont('helvetica', 'normal')
        const aLines = doc.splitTextToSize(oa.jawaban, 180)
        doc.text(aLines, marginX, yAfter); yAfter += aLines.length * 5 + 5
      }
    }

    doc.save(`SINOKU-Hasil-${r.kode}.pdf`)
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.score-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.score-card { background: #f7fafc; border-radius: 10px; padding: 14px; text-align: center; border: 1px solid #e2e8f0; }
.score-card__kode { font-size: 20px; font-weight: 900; color: #3182ce; }
.score-card__name { font-size: 11px; color: #718096; margin: 2px 0 8px; }
.score-card__score { font-size: 26px; font-weight: 800; color: #2d3748; }
.score-card__bar { height: 4px; background: #e2e8f0; border-radius: 2px; margin: 8px 0; }
.score-fill { height: 100%; background: #3182ce; border-radius: 2px; }
.score-card__n { font-size: 11px; color: #a0aec0; }
.capaian-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.capaian-table th { background: #f7fafc; text-align: left; padding: 8px 10px; font-weight: 600; color: #4a5568; border-bottom: 1px solid #e2e8f0; }
.capaian-table td { padding: 8px 10px; border-bottom: 1px solid #f0f4f8; }
.cap-ok { color: #38a169; font-weight: 700; font-size: 12px; }
.cap-no { color: #e53e3e; font-weight: 700; font-size: 12px; }
.btn-action {
  background: #fff; border: 1px solid #cbd5e0; color: #2d3748;
  padding: 7px 12px; border-radius: 6px; font-size: 13px; cursor: pointer; white-space: nowrap;
}
.btn-action:hover { background: #f7fafc; border-color: #a0aec0; }
.btn-action:disabled { opacity: 0.6; cursor: default; }

/* UC-10: Print-friendly — sembunyikan elemen non-cetak & optimalkan layout */
@media print {
  .no-print { display: none !important; }
  .container { max-width: 100% !important; padding-top: 0 !important; }
  .card { box-shadow: none !important; border: none !important; }
  .score-grid { grid-template-columns: repeat(4, 1fr) !important; }
}
</style>
