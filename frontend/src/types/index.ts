export interface University {
  id: number
  nama: string
  nama_singkat: string
  kota: string
  provinsi: string
}

export interface Program {
  id: number
  nama: string
  nama_singkat: string
  jenjang: string
}

export interface Course {
  id: number
  kode_mk: string
  nama_id: string
  nama_zh: string
  sks: number
  semester: number
}

export interface SurveyItem {
  id: number
  kode: string
  nomor_urut: number
  teks: string
  answer_type: string
  scale_min: number
  scale_max: number
  is_required: boolean
}

export interface SubDimension {
  id: number
  kode: string
  nama: string
  items: SurveyItem[]
}

export interface OpenQuestion {
  id: number
  kode: string
  pertanyaan: string
  is_required: boolean
}

export interface SurveyStepData {
  dimensi: string
  nama_dimensi: string
  sub_dimensions: SubDimension[]
  open_questions: OpenQuestion[]
}

export interface CippScore {
  dimensi: string
  kode: string
  skor_rata: number
  std_dev: number
  jumlah_item: number
}

export interface UserInfo {
  id: string
  email: string
  full_name: string
  role: string
  university_id: number | null
  program_id: number | null
}
