<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Mata Kuliah Saya</h1>
    </div>
    <p class="subtitle">Daftar mata kuliah yang Anda ampu. Diatur oleh Admin Prodi.</p>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr><th>Kode MK</th><th>Nama (ID)</th><th>Nama (中文)</th><th>SKS</th><th>Semester</th><th>Aksi</th></tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">Memuat...</td></tr>
          <tr v-else-if="!rows.length"><td colspan="6" class="center">Anda belum ditugaskan mengampu mata kuliah. Hubungi admin prodi.</td></tr>
          <tr v-for="c in rows" :key="c.id">
            <td><span class="badge">{{ c.kode_mk }}</span></td>
            <td>{{ c.nama_id }}</td>
            <td class="text-muted">{{ c.nama_zh }}</td>
            <td class="tc">{{ c.sks }}</td>
            <td class="tc">{{ c.semester }}</td>
            <td>
              <router-link to="/admin/rps" class="btn-link">RPS</router-link>
              <router-link to="/admin/reports" class="btn-link">Laporan</router-link>
              <router-link to="/survey/dosen" class="btn-link green">Isi Evaluasi</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyCourses } from '@/api/admin'

const rows = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getMyCourses()
    rows.value = res.data ?? []
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.subtitle{color:#718096;font-size:13px;margin-bottom:20px}
.table-wrap{background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:10px 14px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:10px 14px;border-bottom:1px solid #f0f4f8;color:#2d3748}
.data-table tr:last-child td{border-bottom:none}
.center{text-align:center;color:#718096}
.tc{text-align:center}
.text-muted{color:#718096;font-size:12px}
.badge{background:#ebf8ff;color:#2b6cb0;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.btn-link{display:inline-block;background:#ebf8ff;color:#2b6cb0;border-radius:4px;padding:4px 10px;font-size:12px;text-decoration:none;margin-right:4px}
.btn-link.green{background:#f0fff4;color:#276749}
.btn-link:hover{filter:brightness(0.96)}
</style>
