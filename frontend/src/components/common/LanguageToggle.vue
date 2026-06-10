<template>
  <div class="lang-toggle">
    <button :class="['lang-btn', { active: ui.locale === 'id' }]" @click="ui.setLocale('id')">ID</button>
    <button :class="['lang-btn', { active: ui.locale === 'zh' }]" @click="ui.setLocale('zh')">中文</button>
  </div>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.lang-toggle { display: flex; gap: 2px; background: rgba(255,255,255,.1); border-radius: 6px; padding: 2px; }
.lang-btn { padding: 4px 10px; border-radius: 4px; border: none; background: transparent; color: rgba(255,255,255,.7); font-size: 12px; font-weight: 600; cursor: pointer; transition: all .15s; }
.lang-btn.active { background: #fff; color: #1a365d; }
</style>
