<template>
  <div class="scope-filter">
    <select v-if="showUniv" v-model.number="uid" @change="onUniv" class="sf-select" title="Universitas">
      <option :value="null">Semua Universitas</option>
      <option v-for="u in univs" :key="u.id" :value="u.id">{{ u.nama_singkat }}</option>
    </select>
    <select v-if="showFaculty" v-model.number="fid" @change="onFaculty" class="sf-select" title="Fakultas">
      <option :value="null">Semua Fakultas</option>
      <option v-for="f in faculties" :key="f.id" :value="f.id">{{ f.nama_singkat }}</option>
    </select>
    <select v-if="showProgram" v-model.number="pid" @change="onProgram" class="sf-select" title="Program Studi">
      <option :value="null">Semua Prodi</option>
      <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.nama_singkat }}</option>
    </select>
    <select v-if="showCourseSel" v-model.number="cid" @change="emitChange" class="sf-select" title="Mata Kuliah">
      <option :value="null">Semua Mata Kuliah</option>
      <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.kode_mk }} — {{ c.nama_id }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { getUniversities, getFaculties, getPrograms, getCourses } from '@/api/admin'

export interface Scope {
  university_id: number | null
  faculty_id: number | null
  program_id: number | null
  course_id: number | null
}

const props = defineProps<{ showCourse?: boolean }>()
const emit = defineEmits<{ change: [Scope] }>()

const { user, isSuperadmin, isAdminUniversitas, isAdminFakultas } = storeToRefs(useAuthStore())

// Level yang bisa dipilih sesuai peran (level atas terkunci/tersembunyi)
const showUniv = computed(() => isSuperadmin.value)
const showFaculty = computed(() => isSuperadmin.value || isAdminUniversitas.value)
const showProgram = computed(() => isSuperadmin.value || isAdminUniversitas.value || isAdminFakultas.value)
const showCourseSel = computed(() => !!props.showCourse)

const uid = ref<number | null>(null)
const fid = ref<number | null>(null)
const pid = ref<number | null>(null)
const cid = ref<number | null>(null)

const univs = ref<any[]>([])
const faculties = ref<any[]>([])
const programs = ref<any[]>([])
const courses = ref<any[]>([])

// Universitas efektif untuk memuat fakultas/prodi (superadmin: pilihan; lainnya: milik akun)
const effUniv = computed(() => (isSuperadmin.value ? uid.value : user.value?.university_id ?? null))

function scope(): Scope {
  return {
    university_id: isSuperadmin.value ? uid.value : user.value?.university_id ?? null,
    faculty_id: showFaculty.value ? fid.value : user.value?.faculty_id ?? null,
    program_id: showProgram.value ? pid.value : user.value?.program_id ?? null,
    course_id: showCourseSel.value ? cid.value : null,
  }
}
function emitChange() { emit('change', scope()) }

async function loadFaculties() {
  faculties.value = []
  const params: any = { limit: 500 }
  if (effUniv.value) params.university_id = effUniv.value
  try { faculties.value = (await getFaculties(params)).data.data ?? [] } catch { /* abaikan */ }
}
async function loadPrograms() {
  programs.value = []
  const params: any = { limit: 500 }
  if (effUniv.value) params.university_id = effUniv.value
  if (fid.value) params.faculty_id = fid.value
  try { programs.value = (await getPrograms(params)).data.data ?? [] } catch { /* abaikan */ }
}
async function loadCourses() {
  courses.value = []
  if (!pid.value) return
  try { courses.value = (await getCourses({ program_id: pid.value, limit: 500 })).data.data ?? [] } catch { /* abaikan */ }
}

async function onUniv() { fid.value = null; pid.value = null; cid.value = null; await loadFaculties(); programs.value = []; emitChange() }
async function onFaculty() { pid.value = null; cid.value = null; courses.value = []; await loadPrograms(); emitChange() }
async function onProgram() { cid.value = null; if (showCourseSel.value) await loadCourses(); emitChange() }

onMounted(async () => {
  if (isSuperadmin.value) {
    univs.value = (await getUniversities({ limit: 500 }).catch(() => ({ data: { data: [] } }))).data.data ?? []
    // superadmin memuat fakultas/prodi setelah memilih universitas
  } else {
    // admin tingkat: daftar sudah dibatasi backend sesuai cakupan
    if (showFaculty.value) await loadFaculties()
    if (showProgram.value) await loadPrograms()
  }
})
</script>

<style scoped>
.scope-filter { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.sf-select { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; background: #fff; }
</style>
