import { ref, computed, watch, type Ref } from 'vue'

/**
 * Pagination sisi-klien untuk daftar yang sudah dimuat penuh (kecil & tersaring).
 * Kembalikan `paged` (baris halaman aktif) + `page`/`totalPages` untuk kontrol.
 */
export function usePagination<T>(source: Ref<T[]>, pageSize = 15) {
  const page = ref(1)
  const totalPages = computed(() => Math.max(1, Math.ceil(source.value.length / pageSize)))
  const paged = computed(() => {
    const start = (page.value - 1) * pageSize
    return source.value.slice(start, start + pageSize)
  })
  // Jika sumber berubah (mis. difilter) dan halaman aktif jadi di luar batas → kembali ke 1
  watch(() => source.value.length, () => {
    if (page.value > totalPages.value) page.value = 1
  })
  return { page, totalPages, paged, pageSize }
}
