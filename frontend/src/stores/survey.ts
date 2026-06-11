import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { University, Program, Course, SurveyStepData } from '@/types'

// Step urutan: selector -> consent -> profile -> B -> C -> D -> E -> thankyou
export const SURVEY_STEPS = ['selector', 'consent', 'profile', 'B', 'C', 'D', 'E', 'thankyou'] as const
export type SurveyStep = typeof SURVEY_STEPS[number]

export const useSurveyStore = defineStore('survey', () => {
  const currentStep = ref<SurveyStep>('selector')
  const responseId = ref<string | null>(null)
  const respondentId = ref<string | null>(null)
  const anonymousCode = ref<string | null>(null)
  const isDosen = ref(false)

  // Konteks yang dipilih
  const selectedUniversity = ref<University | null>(null)
  const selectedProgram = ref<Program | null>(null)
  const selectedCourse = ref<Course | null>(null)
  const selectedRole = ref<'dosen' | 'mahasiswa'>('mahasiswa')
  const selectedBahasa = ref<'id' | 'zh'>('id')

  // Jawaban: item_id -> skor
  const answers = reactive<Record<number, number>>({})
  // Jawaban terbuka: question_id -> teks
  const openAnswers = reactive<Record<number, string>>({})

  // Data step saat ini
  const stepData = ref<SurveyStepData | null>(null)

  function setAnswer(itemId: number, skor: number) {
    answers[itemId] = skor
  }

  function setOpenAnswer(questionId: number, teks: string) {
    openAnswers[questionId] = teks
  }

  function getAnswersForStep(dimensi: string) {
    if (!stepData.value) return []
    const result: Array<{ item_id: number; skor: number }> = []
    for (const sd of stepData.value.sub_dimensions) {
      for (const item of sd.items) {
        if (answers[item.id] !== undefined) {
          result.push({ item_id: item.id, skor: answers[item.id] })
        }
      }
    }
    return result
  }

  function getOpenAnswersForSubmit() {
    return Object.entries(openAnswers).map(([id, teks]) => ({
      open_question_id: Number(id),
      jawaban_teks: teks,
    }))
  }

  function goToStep(step: SurveyStep) {
    currentStep.value = step
  }

  function nextStep() {
    const idx = SURVEY_STEPS.indexOf(currentStep.value)
    if (idx < SURVEY_STEPS.length - 1) {
      currentStep.value = SURVEY_STEPS[idx + 1]
    }
  }

  function prevStep() {
    const idx = SURVEY_STEPS.indexOf(currentStep.value)
    if (idx > 0) {
      currentStep.value = SURVEY_STEPS[idx - 1]
    }
  }

  function initFromServer(data: { response_id: string; respondent_id: string | null; role: string; bahasa: string; isDosen?: boolean }) {
    responseId.value = data.response_id
    respondentId.value = data.respondent_id
    selectedRole.value = data.role as 'dosen' | 'mahasiswa'
    selectedBahasa.value = data.bahasa as 'id' | 'zh'
    isDosen.value = data.isDosen ?? false
  }

  function reset() {
    currentStep.value = 'selector'
    responseId.value = null
    respondentId.value = null
    anonymousCode.value = null
    isDosen.value = false
    selectedUniversity.value = null
    selectedProgram.value = null
    selectedCourse.value = null
    selectedRole.value = 'mahasiswa'
    selectedBahasa.value = 'id'
    Object.keys(answers).forEach(k => delete answers[Number(k)])
    Object.keys(openAnswers).forEach(k => delete openAnswers[Number(k)])
    stepData.value = null
  }

  return {
    currentStep, responseId, respondentId, anonymousCode, isDosen,
    selectedUniversity, selectedProgram, selectedCourse, selectedRole, selectedBahasa,
    answers, openAnswers, stepData,
    setAnswer, setOpenAnswer, getAnswersForStep, getOpenAnswersForSubmit,
    goToStep, nextStep, prevStep, reset, initFromServer,
  }
})
