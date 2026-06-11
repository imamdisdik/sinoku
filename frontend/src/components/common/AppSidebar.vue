<template>
  <aside class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-icon">汉</span>
      <span class="logo-text">SINOKU</span>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-group">
        <span class="nav-group-label">Utama</span>
        <router-link to="/admin" exact class="nav-item">
          <span class="nav-icon">&#9632;</span> Dashboard
        </router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">Akademik</span>
        <router-link to="/admin/universities" class="nav-item">&#127979; Universitas</router-link>
        <router-link to="/admin/programs" class="nav-item">&#128218; Program Studi</router-link>
        <router-link to="/admin/courses" class="nav-item">&#128214; Mata Kuliah</router-link>
        <router-link to="/admin/cpls" class="nav-item">&#127919; CPL</router-link>
        <router-link to="/admin/cpmks" class="nav-item">&#127891; CPMK</router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">Evaluasi</span>
        <router-link to="/admin/instruments" class="nav-item">&#128203; Instrumen</router-link>
        <router-link to="/admin/anonymous-codes" class="nav-item">&#128273; Kode Anonim</router-link>
        <router-link to="/admin/analytics" class="nav-item">&#128200; Analitik</router-link>
      </div>

      <div class="nav-group">
        <span class="nav-group-label">RPS & Laporan</span>
        <router-link to="/admin/rps" class="nav-item">&#128196; RPS</router-link>
        <router-link to="/admin/reports" class="nav-item">&#128221; Laporan Diagnostik</router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <button @click="logout" class="logout-btn">&#128275; Keluar</button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-height: 100vh;
  background: #1a365d;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  z-index: 100;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo-icon { font-size: 22px; color: #63b3ed; }
.logo-text { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.nav-group { margin-bottom: 8px; }
.nav-group-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 8px 16px 4px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  font-size: 13px;
  transition: background 0.15s;
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.router-link-active { background: rgba(99,179,237,0.2); color: #63b3ed; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.1); }
.logout-btn {
  width: 100%;
  padding: 8px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.6);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}
.logout-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }
</style>
