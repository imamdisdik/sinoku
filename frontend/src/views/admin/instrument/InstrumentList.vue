<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Instrumen CIPP</h1>
    </div>

    <div v-if="loading" class="loading-state">Memuat instrumen...</div>

    <template v-else>
      <!-- Tab: Kuesioner CIPP -->
      <div class="tab-bar">
        <button :class="['tab-btn', activeTab === 'items' && 'active']" @click="activeTab = 'items'">Item Kuesioner</button>
        <button :class="['tab-btn', activeTab === 'openq' && 'active']" @click="activeTab = 'openq'">Pertanyaan Terbuka</button>
      </div>

      <!-- TAB: Item Kuesioner -->
      <template v-if="activeTab === 'items'">
        <!-- Dimensi selector -->
        <div class="dim-row">
          <button
            v-for="dim in dimensions"
            :key="dim.id"
            :class="['dim-btn', selectedDimId === dim.id && 'active']"
            :style="selectedDimId === dim.id ? { background: dim.warna_hex, borderColor: dim.warna_hex } : { borderColor: dim.warna_hex, color: dim.warna_hex }"
            @click="selectDim(dim)"
          >
            <span class="dim-kode">{{ dim.kode }}</span>
            <span class="dim-nama">{{ dim.nama_id }}</span>
          </button>
        </div>

        <div v-if="selectedDim" class="content-card">
          <div class="card-header">
            <div>
              <div class="card-title" :style="{ color: selectedDim.warna_hex }">
                Dimensi {{ selectedDim.kode }} — {{ selectedDim.nama_id }}
              </div>
              <div class="sub-filter">
                <select v-model.number="selectedSubDimId" @change="fetchItems" class="filter-select">
                  <option :value="null">Semua Sub-Dimensi</option>
                  <option v-for="sd in selectedDim.sub_dimensions" :key="sd.id" :value="sd.id">
                    {{ sd.kode }} — {{ sd.nama_id }} ({{ sd.item_count }} item)
                  </option>
                </select>
                <label class="toggle-label">
                  <input type="checkbox" v-model="includeInactive" @change="fetchItems" />
                  Tampilkan nonaktif
                </label>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <button class="btn btn-secondary" @click="triggerImport">&#8645; Import CSV</button>
              <input ref="importInputRef" type="file" accept=".csv" style="display:none" @change="doImport" />
              <button class="btn btn-primary" @click="openCreate">+ Tambah Item</button>
            </div>
          </div>

          <div v-if="loadingItems" class="loading-state">Memuat item...</div>
          <div v-else-if="!items.length" class="empty-state">Belum ada item di dimensi ini</div>
          <table v-else class="data-table">
            <thead>
              <tr>
                <th>Kode</th>
                <th>#</th>
                <th>Teks (Indonesia — Dosen)</th>
                <th>Teks (Indonesia — Mahasiswa)</th>
                <th>Sub-Dim</th>
                <th>Status</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.id" :class="!item.is_active ? 'row-inactive' : ''">
                <td><code>{{ item.kode }}</code></td>
                <td>{{ item.nomor_urut }}</td>
                <td class="text-cell">{{ item.text_id_dosen }}</td>
                <td class="text-cell">{{ item.text_id_mahasiswa }}</td>
                <td>{{ subDimLabel(item.sub_dimension_id) }}</td>
                <td>
                  <span :class="item.is_active ? 'badge-active' : 'badge-inactive'">
                    {{ item.is_active ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>
                <td>
                  <div class="action-row">
                    <button class="btn-sm btn-edit" @click="openEdit(item)">Edit</button>
                    <button class="btn-sm" :class="item.is_active ? 'btn-warn' : 'btn-ok'" @click="toggleItem(item)">
                      {{ item.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- TAB: Pertanyaan Terbuka -->
      <template v-if="activeTab === 'openq'">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">Pertanyaan Terbuka (Isian Bebas)</div>
            <button class="btn btn-primary" @click="openCreateOQ">+ Tambah Pertanyaan</button>
          </div>
          <div v-if="!openQuestions.length" class="empty-state">Belum ada pertanyaan terbuka</div>
          <table v-else class="data-table">
            <thead>
              <tr>
                <th>Kode</th>
                <th>Urutan</th>
                <th>Pertanyaan (Indonesia)</th>
                <th>Target</th>
                <th>Status</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="oq in openQuestions" :key="oq.id" :class="!oq.is_active ? 'row-inactive' : ''">
                <td><code>{{ oq.kode }}</code></td>
                <td>{{ oq.urutan }}</td>
                <td class="text-cell">{{ oq.pertanyaan_id }}</td>
                <td><span class="role-badge">{{ oq.target_role }}</span></td>
                <td><span :class="oq.is_active ? 'badge-active' : 'badge-inactive'">{{ oq.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
                <td>
                  <div class="action-row">
                    <button class="btn-sm btn-edit" @click="openEditOQ(oq)">Edit</button>
                    <button class="btn-sm" :class="oq.is_active ? 'btn-warn' : 'btn-ok'" @click="toggleOQ(oq)">
                      {{ oq.is_active ? 'Nonaktifkan' : 'Aktifkan' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </template>

    <!-- Modal Item -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <div class="modal-title">{{ editItem ? 'Edit Item' : 'Tambah Item Baru' }}</div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Kode *</label>
              <input class="form-input" v-model="form.kode" :disabled="!!editItem" placeholder="B1" />
            </div>
            <div class="form-group">
              <label class="form-label">Nomor Urut *</label>
              <input class="form-input" type="number" v-model.number="form.nomor_urut" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Sub-Dimensi *</label>
            <select class="form-input" v-model.number="form.sub_dimension_id" :disabled="!!editItem">
              <option v-for="sd in allSubDims" :key="sd.id" :value="sd.id">{{ sd.kode }} — {{ sd.nama_id }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Teks Indonesia — Dosen *</label>
            <textarea class="form-input" rows="2" v-model="form.text_id_dosen" />
          </div>
          <div class="form-group">
            <label class="form-label">Teks Indonesia — Mahasiswa *</label>
            <textarea class="form-input" rows="2" v-model="form.text_id_mahasiswa" />
          </div>
          <div class="form-group">
            <label class="form-label">Teks Mandarin — Dosen</label>
            <textarea class="form-input" rows="2" v-model="form.text_zh_dosen" placeholder="(opsional)" />
          </div>
          <div class="form-group">
            <label class="form-label">Teks Mandarin — Mahasiswa</label>
            <textarea class="form-input" rows="2" v-model="form.text_zh_mahasiswa" placeholder="(opsional)" />
          </div>
          <div class="form-group">
            <label class="form-label">Indikator / Keterangan</label>
            <input class="form-input" v-model="form.indikator" placeholder="(opsional)" />
          </div>
          <p v-if="formError" class="form-error">{{ formError }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Batal</button>
          <button class="btn btn-primary" @click="saveItem" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Open Question -->
    <div v-if="showOQModal" class="modal-overlay" @click.self="closeOQModal">
      <div class="modal-box">
        <div class="modal-title">{{ editOQ ? 'Edit Pertanyaan' : 'Tambah Pertanyaan Terbuka' }}</div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Kode *</label>
              <input class="form-input" v-model="oqForm.kode" :disabled="!!editOQ" placeholder="OQ1" />
            </div>
            <div class="form-group">
              <label class="form-label">Urutan *</label>
              <input class="form-input" type="number" v-model.number="oqForm.urutan" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Pertanyaan (Indonesia) *</label>
            <textarea class="form-input" rows="2" v-model="oqForm.pertanyaan_id" />
          </div>
          <div class="form-group">
            <label class="form-label">Pertanyaan (Mandarin)</label>
            <textarea class="form-input" rows="2" v-model="oqForm.pertanyaan_zh" placeholder="(opsional)" />
          </div>
          <div class="form-group">
            <label class="form-label">Tujuan</label>
            <input class="form-input" v-model="oqForm.tujuan" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Target Role</label>
              <select class="form-input" v-model="oqForm.target_role">
                <option value="semua">Semua</option>
                <option value="dosen">Dosen</option>
                <option value="mahasiswa">Mahasiswa</option>
              </select>
            </div>
            <div class="form-group" style="display:flex;align-items:center;gap:8px;padding-top:24px">
              <input type="checkbox" v-model="oqForm.is_required" id="oq-required" />
              <label for="oq-required" class="form-label" style="margin:0">Wajib diisi</label>
            </div>
          </div>
          <p v-if="oqFormError" class="form-error">{{ oqFormError }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeOQModal">Batal</button>
          <button class="btn btn-primary" @click="saveOQ" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  getInstrumentDimensions, getInstrumentItems,
  createInstrumentItem, updateInstrumentItem, toggleInstrumentItem,
  getOpenQuestions, createOpenQuestion, updateOpenQuestion, toggleOpenQuestion,
  importInstrumentItems,
} from '@/api/admin'
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()

const loading = ref(true)
const loadingItems = ref(false)
const activeTab = ref<'items' | 'openq'>('items')
const dimensions = ref<any[]>([])
const selectedDimId = ref<number | null>(null)
const selectedSubDimId = ref<number | null>(null)
const includeInactive = ref(false)
const items = ref<any[]>([])
const openQuestions = ref<any[]>([])

const importInputRef = ref<HTMLInputElement | null>(null)
const selectedDim = computed(() => dimensions.value.find(d => d.id === selectedDimId.value) ?? null)
const allSubDims = computed(() => dimensions.value.flatMap((d: any) => d.sub_dimensions ?? []))

function subDimLabel(sdId: number) {
  const sd = allSubDims.value.find((s: any) => s.id === sdId)
  return sd ? sd.kode : sdId
}

function triggerImport() {
  importInputRef.value?.click()
}
async function doImport(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  try {
    const res = await importInstrumentItems(file)
    const { imported, skipped, errors } = res.data
    ui.showToast(`Import selesai: ${imported} item diimpor, ${skipped} dilewati`, imported > 0 ? 'success' : 'warning')
    if (errors?.length) console.warn('Import errors:', errors)
    await fetchDimensions()
    if (selectedDimId.value) await fetchItems()
  } catch {
    ui.showToast('Gagal mengimpor file CSV', 'error')
  } finally {
    if (importInputRef.value) importInputRef.value.value = ''
  }
}

async function fetchDimensions() {
  const res = await getInstrumentDimensions()
  dimensions.value = res.data.data
  if (dimensions.value.length && !selectedDimId.value) {
    selectedDimId.value = dimensions.value[0].id
    await fetchItems()
  }
}

async function selectDim(dim: any) {
  selectedDimId.value = dim.id
  selectedSubDimId.value = null
  await fetchItems()
}

async function fetchItems() {
  if (!selectedDimId.value) return
  loadingItems.value = true
  try {
    const params: any = { include_inactive: includeInactive.value }
    if (selectedSubDimId.value) params.sub_dimension_id = selectedSubDimId.value
    const res = await getInstrumentItems(selectedDimId.value, params)
    items.value = res.data.data
  } finally {
    loadingItems.value = false }
}

async function fetchOpenQuestions() {
  const res = await getOpenQuestions()
  openQuestions.value = res.data.data
}

// ── Item Modal ────────────────────────────────────────────────────────────────
const showModal = ref(false)
const editItem = ref<any>(null)
const saving = ref(false)
const formError = ref('')
const form = ref({
  kode: '', nomor_urut: 1, sub_dimension_id: 0,
  text_id_dosen: '', text_id_mahasiswa: '',
  text_zh_dosen: '', text_zh_mahasiswa: '',
  indikator: '', answer_type: 'likert', scale_min: 1, scale_max: 5, is_required: true,
})

function openCreate() {
  editItem.value = null
  formError.value = ''
  const firstSD = selectedDim.value?.sub_dimensions?.[0]
  form.value = {
    kode: '', nomor_urut: items.value.length + 1,
    sub_dimension_id: selectedSubDimId.value ?? firstSD?.id ?? 0,
    text_id_dosen: '', text_id_mahasiswa: '',
    text_zh_dosen: '', text_zh_mahasiswa: '',
    indikator: '', answer_type: 'likert', scale_min: 1, scale_max: 5, is_required: true,
  }
  showModal.value = true
}

function openEdit(item: any) {
  editItem.value = item
  formError.value = ''
  form.value = { ...item }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function saveItem() {
  if (!form.value.kode || !form.value.text_id_dosen || !form.value.text_id_mahasiswa) {
    formError.value = 'Kode, teks dosen, dan teks mahasiswa wajib diisi'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editItem.value) {
      await updateInstrumentItem(editItem.value.id, {
        nomor_urut: form.value.nomor_urut,
        text_id_dosen: form.value.text_id_dosen,
        text_id_mahasiswa: form.value.text_id_mahasiswa,
        text_zh_dosen: form.value.text_zh_dosen,
        text_zh_mahasiswa: form.value.text_zh_mahasiswa,
        indikator: form.value.indikator || null,
        is_required: form.value.is_required,
      })
    } else {
      await createInstrumentItem({ ...form.value, indikator: form.value.indikator || null })
    }
    closeModal()
    await fetchItems()
  } catch (e: any) {
    formError.value = e.response?.data?.detail ?? 'Gagal menyimpan'
  } finally { saving.value = false }
}

async function toggleItem(item: any) {
  await toggleInstrumentItem(item.id)
  await fetchItems()
}

// ── Open Question Modal ───────────────────────────────────────────────────────
const showOQModal = ref(false)
const editOQ = ref<any>(null)
const oqFormError = ref('')
const oqForm = ref({
  kode: '', pertanyaan_id: '', pertanyaan_zh: '',
  tujuan: '', target_role: 'semua', is_required: false, urutan: 1,
})

function openCreateOQ() {
  editOQ.value = null
  oqFormError.value = ''
  oqForm.value = { kode: '', pertanyaan_id: '', pertanyaan_zh: '', tujuan: '', target_role: 'semua', is_required: false, urutan: openQuestions.value.length + 1 }
  showOQModal.value = true
}
function openEditOQ(oq: any) {
  editOQ.value = oq
  oqFormError.value = ''
  oqForm.value = { ...oq }
  showOQModal.value = true
}
function closeOQModal() { showOQModal.value = false }

async function saveOQ() {
  if (!oqForm.value.kode || !oqForm.value.pertanyaan_id) {
    oqFormError.value = 'Kode dan pertanyaan wajib diisi'
    return
  }
  saving.value = true
  oqFormError.value = ''
  try {
    if (editOQ.value) {
      await updateOpenQuestion(editOQ.value.id, {
        pertanyaan_id: oqForm.value.pertanyaan_id,
        pertanyaan_zh: oqForm.value.pertanyaan_zh,
        tujuan: oqForm.value.tujuan,
        target_role: oqForm.value.target_role,
        is_required: oqForm.value.is_required,
        urutan: oqForm.value.urutan,
      })
    } else {
      await createOpenQuestion({ ...oqForm.value })
    }
    closeOQModal()
    await fetchOpenQuestions()
  } catch (e: any) {
    oqFormError.value = e.response?.data?.detail ?? 'Gagal menyimpan'
  } finally { saving.value = false }
}

async function toggleOQ(oq: any) {
  await toggleOpenQuestion(oq.id)
  await fetchOpenQuestions()
}

onMounted(async () => {
  try {
    await Promise.all([fetchDimensions(), fetchOpenQuestions()])
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.page-title{font-size:22px;font-weight:700;color:#1a365d}
.loading-state{text-align:center;padding:60px;color:#718096;background:#fff;border-radius:10px}
.empty-state{text-align:center;padding:40px;color:#a0aec0;font-size:14px}
.tab-bar{display:flex;gap:4px;margin-bottom:20px;background:#e2e8f0;border-radius:8px;padding:4px;width:fit-content}
.tab-btn{padding:8px 20px;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;background:transparent;color:#718096;transition:.2s}
.tab-btn.active{background:#fff;color:#1a365d;box-shadow:0 1px 3px rgba(0,0,0,.1)}
.dim-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.dim-btn{display:flex;flex-direction:column;align-items:center;padding:10px 18px;border:2px solid;border-radius:10px;cursor:pointer;background:#fff;transition:.2s;min-width:100px}
.dim-btn.active{color:#fff !important}
.dim-kode{font-size:22px;font-weight:900}
.dim-nama{font-size:10px;font-weight:600;margin-top:2px}
.content-card{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.07)}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;gap:12px}
.card-title{font-size:15px;font-weight:700;color:#2d3748;margin-bottom:8px}
.sub-filter{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.filter-select{padding:6px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px}
.toggle-label{font-size:12px;color:#718096;display:flex;align-items:center;gap:4px;cursor:pointer}
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{background:#f7fafc;padding:9px 12px;text-align:left;font-weight:600;color:#4a5568;border-bottom:1px solid #e2e8f0}
.data-table td{padding:9px 12px;border-bottom:1px solid #f0f4f8;vertical-align:top}
.text-cell{max-width:260px;line-height:1.4;color:#2d3748}
.row-inactive td{opacity:.5}
.badge-active{background:#c6f6d5;color:#276749;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.badge-inactive{background:#fed7d7;color:#c53030;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700}
.role-badge{background:#ebf4ff;color:#2b6cb0;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600}
.action-row{display:flex;gap:6px;flex-wrap:wrap}
.btn-sm{padding:4px 10px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600}
.btn-edit{background:#ebf4ff;color:#2b6cb0}
.btn-warn{background:#fefcbf;color:#975a16}
.btn-ok{background:#c6f6d5;color:#276749}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;z-index:1000;padding:16px}
.modal-box{background:#fff;border-radius:12px;width:100%;max-width:680px;max-height:90vh;overflow-y:auto}
.modal-title{padding:20px 24px 0;font-size:16px;font-weight:700;color:#1a365d}
.modal-body{padding:16px 24px}
.modal-footer{padding:16px 24px;display:flex;justify-content:flex-end;gap:10px;border-top:1px solid #e2e8f0}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.form-group{margin-bottom:12px}
.form-label{display:block;font-size:12px;font-weight:600;color:#4a5568;margin-bottom:4px}
.form-input{width:100%;padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;box-sizing:border-box}
.form-error{color:#e53e3e;font-size:12px;margin-top:4px}
.btn{padding:8px 18px;border:none;border-radius:7px;font-size:13px;font-weight:600;cursor:pointer}
.btn-primary{background:#1a365d;color:#fff}
.btn-secondary{background:#e2e8f0;color:#4a5568}
</style>
