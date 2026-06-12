<template>
  <div>
    <div class="page-header">
      <div>
        <button class="btn-back" @click="router.back()">← Kembali ke RPS</button>
        <h1 class="page-title">Checklist RPS</h1>
        <div v-if="rpsInfo" class="rps-meta">
          {{ rpsInfo.tahun_akademik }} — Semester {{ rpsInfo.semester }}
          <span :class="statusBadge(rpsInfo.status)">{{ rpsInfo.status }}</span>
        </div>
      </div>
      <div class="progress-wrap" v-if="items.length">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPct + '%' }" />
        </div>
        <span class="progress-text">{{ fulfilled }} / {{ items.length }} terpenuhi ({{ progressPct }}%)</span>
      </div>
    </div>

    <div v-if="loading" class="card center">Memuat checklist...</div>
    <div v-else-if="!items.length" class="card center">
      Tidak ada item checklist. Tambahkan data checklist terlebih dahulu melalui database.
    </div>
    <div v-else class="checklist-wrap">
      <div v-for="item in items" :key="item.id" class="checklist-item" :class="{ fulfilled: item.is_fulfilled }">
        <div class="item-left">
          <label class="checkbox-wrap">
            <input type="checkbox" :checked="item.is_fulfilled" @change="toggle(item)" />
            <span class="checkmark"></span>
          </label>
        </div>
        <div class="item-body">
          <div class="item-header">
            <span class="item-kode">{{ item.checklist_item.kode }}</span>
            <span v-if="item.checklist_item.is_mandatory" class="mandatory-tag">Wajib</span>
          </div>
          <div class="item-nama">{{ item.checklist_item.nama_komponen }}</div>
          <div v-if="item.checklist_item.deskripsi" class="item-desc">{{ item.checklist_item.deskripsi }}</div>
          <div class="item-catatan-row" v-if="editingNote === item.id">
            <input v-model="noteText" class="note-input" placeholder="Catatan (opsional)..." />
            <button class="btn-save-note" @click="saveNote(item)">Simpan</button>
            <button class="btn-cancel-note" @click="editingNote=null">Batal</button>
          </div>
          <div v-else-if="item.catatan" class="item-catatan" @click="startNote(item)">
            &#128221; {{ item.catatan }}
          </div>
          <button v-else class="btn-add-note" @click="startNote(item)">+ Catatan</button>
        </div>
        <div class="item-right">
          <span v-if="item.is_fulfilled" class="status-ok">&#10003;</span>
          <span v-else class="status-pending">—</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { getRpsChecklist, updateRpsChecklist, getRpsList } from '@/api/admin'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()
const rpsId = Number(route.params.id)

const items = ref<any[]>([])
const rpsInfo = ref<any>(null)
const loading = ref(true)
const editingNote = ref<number | null>(null)
const noteText = ref('')

const fulfilled = computed(() => items.value.filter(i => i.is_fulfilled).length)
const progressPct = computed(() =>
  items.value.length ? Math.round((fulfilled.value / items.value.length) * 100) : 0
)

function statusBadge(s: string) {
  return { draft: 'badge-draft', aktif: 'badge-aktif', arsip: 'badge-arsip' }[s] ?? 'badge-draft'
}

async function fetchChecklist() {
  loading.value = true
  try {
    const res = await getRpsChecklist(rpsId)
    items.value = res.data
  } finally { loading.value = false }
}

async function toggle(item: any) {
  try {
    const res = await updateRpsChecklist(rpsId, item.checklist_item_id, {
      is_fulfilled: !item.is_fulfilled,
      catatan: item.catatan,
    })
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx] = res.data
    ui.showToast(res.data.is_fulfilled ? 'Ditandai terpenuhi' : 'Ditandai belum terpenuhi', 'success')
  } catch {
    ui.showToast('Gagal memperbarui checklist', 'error')
  }
}

function startNote(item: any) {
  editingNote.value = item.id
  noteText.value = item.catatan ?? ''
}

async function saveNote(item: any) {
  try {
    const res = await updateRpsChecklist(rpsId, item.checklist_item_id, {
      is_fulfilled: item.is_fulfilled,
      catatan: noteText.value,
    })
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx] = res.data
    editingNote.value = null
    ui.showToast('Catatan disimpan', 'success')
  } catch {
    ui.showToast('Gagal menyimpan catatan', 'error')
  }
}

onMounted(async () => {
  const rpsRes = await getRpsList({ limit: 1 }).catch(() => null)
  // Cari RPS yang sesuai — ambil dari list
  await fetchChecklist()
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.page-title{font-size:22px;font-weight:700;color:#1a365d;margin:4px 0}
.btn-back{background:none;border:none;color:#3182ce;font-size:13px;cursor:pointer;padding:0;margin-bottom:4px}
.rps-meta{display:flex;align-items:center;gap:8px;font-size:13px;color:#718096;margin-top:4px}
.progress-wrap{text-align:right}
.progress-bar{width:200px;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;margin-bottom:4px}
.progress-fill{height:100%;background:#38a169;border-radius:4px;transition:width .3s}
.progress-text{font-size:12px;color:#4a5568;font-weight:600}
.card{background:#fff;border-radius:10px;padding:40px;box-shadow:0 1px 3px rgba(0,0,0,0.08)}
.center{text-align:center;color:#718096}
.checklist-wrap{display:flex;flex-direction:column;gap:10px}
.checklist-item{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.07);display:flex;gap:14px;align-items:flex-start;border-left:4px solid #e2e8f0;transition:border-color .2s}
.checklist-item.fulfilled{border-left-color:#38a169;background:#f0fff4}
.checkbox-wrap{display:flex;align-items:center;cursor:pointer;margin-top:2px}
.checkbox-wrap input{width:18px;height:18px;cursor:pointer;accent-color:#38a169}
.item-body{flex:1}
.item-header{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.item-kode{font-size:11px;font-weight:700;background:#ebf8ff;color:#2b6cb0;padding:2px 6px;border-radius:4px}
.mandatory-tag{font-size:10px;background:#fff5f5;color:#e53e3e;padding:2px 6px;border-radius:4px;font-weight:700}
.item-nama{font-size:14px;font-weight:600;color:#2d3748}
.item-desc{font-size:12px;color:#718096;margin-top:4px;line-height:1.4}
.item-catatan{font-size:12px;color:#4a5568;margin-top:8px;background:#f7fafc;padding:6px 10px;border-radius:6px;cursor:pointer;border:1px solid #e2e8f0}
.item-catatan-row{display:flex;gap:8px;margin-top:8px;align-items:center}
.note-input{flex:1;padding:6px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:12px}
.btn-save-note{background:#1a365d;color:#fff;border:none;padding:5px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-cancel-note{background:#f7fafc;color:#718096;border:1px solid #e2e8f0;padding:5px 10px;border-radius:4px;font-size:12px;cursor:pointer}
.btn-add-note{background:none;border:none;color:#a0aec0;font-size:12px;cursor:pointer;margin-top:4px;padding:0}
.item-right{flex-shrink:0}
.status-ok{color:#38a169;font-size:20px;font-weight:700}
.status-pending{color:#cbd5e0;font-size:20px}
.badge-draft{background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-aktif{background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.badge-arsip{background:#e5e7eb;color:#374151;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
</style>
