<template>
  <!-- Backdrop saat drawer terbuka di mobile -->
  <div v-if="ui.sidebarMobileOpen" class="sidebar-backdrop" @click="ui.closeSidebarMobile()" />

  <aside class="sidebar" :class="{ collapsed: ui.sidebarCollapsed, 'mobile-open': ui.sidebarMobileOpen }">
    <!-- Logo + tombol collapse -->
    <div class="sidebar-logo">
      <span class="logo-icon">汉</span>
      <span class="logo-text" v-show="!ui.sidebarCollapsed">SINOKU</span>
      <button class="collapse-btn" @click="ui.toggleSidebarCollapsed()" :title="ui.sidebarCollapsed ? 'Perluas' : 'Ciutkan'">
        {{ ui.sidebarCollapsed ? '»' : '«' }}
      </button>
    </div>

    <!-- Info user -->
    <div class="sidebar-user" v-if="user">
      <div class="user-avatar" :title="user.full_name">{{ initials }}</div>
      <div class="user-info" v-show="!ui.sidebarCollapsed">
        <div class="user-name">{{ user.full_name }}</div>
        <div class="user-role">{{ roleLabel }}</div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-group" v-for="grp in groups" :key="grp.label">
        <span class="nav-group-label" v-show="!ui.sidebarCollapsed">{{ grp.label }}</span>
        <router-link
          v-for="it in grp.items" :key="it.to"
          :to="it.to" class="nav-item" :class="{ active: isActive(it.to, it.exact) }"
          :title="ui.sidebarCollapsed ? it.text : ''"
          @click="ui.closeSidebarMobile()"
        >
          <span class="ni-icon">{{ it.icon }}</span>
          <span class="ni-label" v-show="!ui.sidebarCollapsed">{{ it.text }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <button @click="doLogout" class="logout-btn" :title="ui.sidebarCollapsed ? 'Keluar' : ''">
        <span>&#128275;</span><span v-show="!ui.sidebarCollapsed">Keluar</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const ui = useUiStore()
const { user, role } = storeToRefs(auth)
const router = useRouter()
const route = useRoute()

// Active: Dashboard (exact) hanya di /admin; lainnya termasuk sub-rute (mis. /admin/reports/123)
function isActive(to: string, exact?: boolean) {
  return exact ? route.path === to : route.path === to || route.path.startsWith(to + '/')
}

// Konstanta kelompok peran
const STAFF = ['superadmin', 'admin_universitas', 'admin_fakultas', 'admin_prodi', 'dosen']
const MANAGERS = ['superadmin', 'admin_universitas', 'admin_fakultas', 'admin_prodi']
const ATAS = ['superadmin', 'admin_universitas', 'admin_fakultas', 'admin_prodi']

// Definisi menu lengkap + peran yang boleh melihatnya
type NavItem = { to: string; icon: string; text: string; exact?: boolean; roles: string[] }
const ALL_GROUPS: { label: string; items: NavItem[] }[] = [
  { label: 'Utama', items: [
    { to: '/admin', icon: '▦', text: 'Dashboard', exact: true, roles: STAFF },
  ]},
  { label: 'Akademik', items: [
    { to: '/admin/universities', icon: '🏫', text: 'Universitas', roles: ['superadmin'] },
    { to: '/admin/faculties', icon: '🏛️', text: 'Fakultas', roles: ['superadmin', 'admin_universitas'] },
    { to: '/admin/programs', icon: '📚', text: 'Program Studi', roles: ['superadmin', 'admin_universitas', 'admin_fakultas'] },
    { to: '/admin/courses', icon: '📖', text: 'Mata Kuliah', roles: ATAS },
    { to: '/admin/cpls', icon: '🎯', text: 'CPL', roles: ['superadmin', 'admin_prodi'] },
    { to: '/admin/cpmks', icon: '🎓', text: 'CPMK', roles: ['superadmin', 'admin_prodi'] },
  ]},
  { label: 'Evaluasi', items: [
    { to: '/admin/instruments', icon: '📋', text: 'Instrumen', roles: ['superadmin', 'admin_prodi'] },
    { to: '/admin/anonymous-codes', icon: '🔑', text: 'Kode Anonim', roles: ATAS },
    { to: '/admin/analytics', icon: '📊', text: 'Analitik', roles: STAFF },
  ]},
  { label: 'Penilaian', items: [
    { to: '/admin/assessment/schemes', icon: '⚖️', text: 'Skema Penilaian', roles: ['superadmin', 'admin_prodi'] },
    { to: '/admin/assessment/rubrics', icon: '📝', text: 'Rubrik', roles: ['superadmin', 'admin_prodi'] },
    { to: '/admin/assessment/mbkm', icon: '🌐', text: 'MBKM', roles: ['superadmin', 'admin_prodi'] },
  ]},
  { label: 'RPS & Laporan', items: [
    { to: '/admin/rps', icon: '📄', text: 'RPS', roles: ['superadmin', 'admin_prodi', 'dosen'] },
    { to: '/admin/reports', icon: '📑', text: 'Laporan Diagnostik', roles: STAFF },
    { to: '/admin/laporan-template', icon: '📃', text: 'Laporan Template', roles: STAFF },
    { to: '/admin/export', icon: '⭳', text: 'Export Data', roles: ATAS },
  ]},
  { label: 'Manajemen', items: [
    { to: '/admin/users', icon: '👤', text: 'Kelola Akun', roles: MANAGERS },
  ]},
  { label: 'Evaluasi Saya', items: [
    { to: '/survey/dosen', icon: '✍️', text: 'Isi Evaluasi', roles: ['dosen'] },
  ]},
]

const groups = computed(() => {
  const r = role.value
  return ALL_GROUPS
    .map(g => ({ label: g.label, items: g.items.filter(it => it.roles.includes(r)) }))
    .filter(g => g.items.length > 0)
})

const initials = computed(() => {
  const name = user.value?.full_name ?? ''
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
})
const roleLabel = computed(() => {
  const map: Record<string, string> = {
    superadmin: 'Super Admin',
    admin_universitas: 'Admin Universitas',
    admin_fakultas: 'Admin Fakultas',
    admin_prodi: 'Admin Prodi',
    dosen: 'Dosen',
  }
  return map[role.value] ?? role.value
})

async function doLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 220px; height: 100vh; background: #1a365d;
  display: flex; flex-direction: column; position: fixed; top: 0; left: 0; z-index: 100;
  transition: width .2s ease, transform .25s ease;
}
.sidebar-logo, .sidebar-user, .sidebar-footer { flex-shrink: 0; }
.sidebar.collapsed { width: 64px; }

.sidebar-logo {
  display: flex; align-items: center; gap: 10px; position: relative;
  padding: 18px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); min-height: 60px;
}
.sidebar.collapsed .sidebar-logo { justify-content: center; padding: 18px 8px; }
.logo-icon { font-size: 22px; color: #63b3ed; flex-shrink: 0; }
.logo-text { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.collapse-btn {
  margin-left: auto; background: rgba(255,255,255,0.08); border: none; color: #cbd5e0;
  width: 24px; height: 24px; border-radius: 5px; cursor: pointer; font-size: 14px; line-height: 1;
}
.sidebar.collapsed .collapse-btn { position: absolute; right: -12px; top: 20px; background: #2c5282; color: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.3); }
.collapse-btn:hover { background: #3182ce; color: #fff; }

.sidebar-user {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.1);
}
.sidebar.collapsed .sidebar-user { justify-content: center; padding: 12px 8px; }
.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(99,179,237,0.3); color: #63b3ed;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
}
.user-info { min-width: 0; }
.user-name { font-size: 12px; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 1px; }

.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; overflow-x: hidden; }
.sidebar-nav::-webkit-scrollbar { width: 6px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
.nav-group { margin-bottom: 8px; }
.nav-group-label {
  display: block; font-size: 10px; font-weight: 600;
  color: rgba(255,255,255,0.4); text-transform: uppercase;
  letter-spacing: 0.08em; padding: 8px 16px 4px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 16px;
  color: rgba(255,255,255,0.75); text-decoration: none; font-size: 13px;
  transition: background 0.15s; border-left: 3px solid transparent; white-space: nowrap;
}
.sidebar.collapsed .nav-item { justify-content: center; padding: 11px 0; gap: 0; }
.ni-icon { width: 20px; text-align: center; flex-shrink: 0; font-size: 14px; }
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: rgba(99,179,237,0.18); color: #fff; border-left-color: #63b3ed; }

.sidebar-footer { padding: 14px; border-top: 1px solid rgba(255,255,255,0.1); }
.logout-btn {
  width: 100%; padding: 8px; background: transparent; display: flex; align-items: center; justify-content: center; gap: 8px;
  border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.6);
  border-radius: 6px; font-size: 13px; cursor: pointer;
}
.logout-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }

.sidebar-backdrop { display: none; }

/* Mobile: sidebar jadi drawer off-canvas */
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); width: 230px !important; box-shadow: 4px 0 16px rgba(0,0,0,.3); }
  .sidebar.collapsed { width: 230px !important; }   /* abaikan collapse di mobile */
  .sidebar.collapsed .logo-text, .sidebar.collapsed .ni-label,
  .sidebar.collapsed .nav-group-label, .sidebar.collapsed .user-info { display: revert !important; }
  .sidebar.collapsed .nav-item { justify-content: flex-start; padding: 9px 16px; gap: 10px; }
  .sidebar.collapsed .collapse-btn { position: static; }
  .sidebar.mobile-open { transform: translateX(0); }
  .sidebar-backdrop { display: block; position: fixed; inset: 0; background: rgba(0,0,0,.45); z-index: 99; }
  .collapse-btn { display: none; }
}
</style>
