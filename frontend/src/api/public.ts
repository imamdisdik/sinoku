import client from './client'
import type { SurveyStartRequest } from '@/types'

export const publicApi = {
  getLandingData: () => client.get('/public/landing'),

  getUniversities: () => client.get('/public/universities'),

  getPrograms: (universityId: number) =>
    client.get(`/public/universities/${universityId}/programs`),

  getCourses: (programId: number) =>
    client.get(`/public/programs/${programId}/courses`),

  getCourseLecturers: (courseId: number) =>
    client.get(`/public/courses/${courseId}/lecturers`),

  startSurvey: (body: Record<string, unknown>) =>
    client.post('/public/survey/start', body),

  startSurveyDosen: (courseId: number, bahasa: string) =>
    client.post('/public/survey/start-dosen', { course_id: courseId, bahasa }),

  getSurveyItems: (responseId: string, dimensi?: string) =>
    client.get(`/public/survey/${responseId}/items`, { params: { dimensi } }),

  saveAnswers: (responseId: string, body: { items: Array<{item_id: number; skor: number}>; open_answers: Array<{open_question_id: number; jawaban_teks: string}> }) =>
    client.post(`/public/survey/${responseId}/answers`, body),

  submitSurvey: (responseId: string) =>
    client.post(`/public/survey/${responseId}/submit`, {}),

  getResult: (kode: string) =>
    client.get(`/public/result/${kode}`),
}
