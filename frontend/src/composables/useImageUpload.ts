/**
 * Konversi File gambar → data URI (base64) yang sudah diperkecil, agar aman
 * disimpan di DB & ringan dikirim. Maksimal sisi terpanjang = maxDim px.
 */
export async function fileToLogoDataUri(file: File, maxDim = 256): Promise<string> {
  if (!file.type.startsWith('image/')) throw new Error('File harus berupa gambar (PNG/JPG/SVG).')

  const dataUrl: string = await new Promise((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(r.result as string)
    r.onerror = () => reject(new Error('Gagal membaca file'))
    r.readAsDataURL(file)
  })

  // SVG tidak perlu di-resize via canvas (vektor) — simpan apa adanya
  if (file.type === 'image/svg+xml') return dataUrl

  const img: HTMLImageElement = await new Promise((resolve, reject) => {
    const im = new Image()
    im.onload = () => resolve(im)
    im.onerror = () => reject(new Error('Gambar tidak valid'))
    im.src = dataUrl
  })

  let { width, height } = img
  if (width > maxDim || height > maxDim) {
    const scale = maxDim / Math.max(width, height)
    width = Math.round(width * scale)
    height = Math.round(height * scale)
  }
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(img, 0, 0, width, height)
  return canvas.toDataURL('image/png')
}
