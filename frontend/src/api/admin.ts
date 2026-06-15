import api from './client'

// Dashboard
export const getDashboardKpi = (params?: object) => api.get('/admin/dashboard/kpi', { params })
export const getProblemHeatmap = (params?: object) => api.get('/admin/dashboard/problem-heatmap', { params })

// Universities
export const getUniversities = (params?: object) => api.get('/admin/universities', { params })
export const createUniversity = (data: object) => api.post('/admin/universities', data)
export const updateUniversity = (id: number, data: object) => api.put(`/admin/universities/${id}`, data)
export const deleteUniversity = (id: number) => api.delete(`/admin/universities/${id}`)

// Programs
export const getPrograms = (params?: object) => api.get('/admin/programs', { params })
export const createProgram = (data: object) => api.post('/admin/programs', data)
export const updateProgram = (id: number, data: object) => api.put(`/admin/programs/${id}`, data)
export const deleteProgram = (id: number) => api.delete(`/admin/programs/${id}`)

// Courses
export const getCourses = (params?: object) => api.get('/admin/courses', { params })
export const createCourse = (data: object) => api.post('/admin/courses', data)
export const updateCourse = (id: number, data: object) => api.put(`/admin/courses/${id}`, data)
export const deleteCourse = (id: number) => api.delete(`/admin/courses/${id}`)

// Course ↔ CPL mapping (UC-14e)
export const getCourseCpls = (courseId: number) => api.get(`/admin/courses/${courseId}/cpls`)
export const mapCourseCpls = (courseId: number, cpl_ids: number[]) =>
  api.post(`/admin/courses/${courseId}/cpls`, { cpl_ids })
export const unmapCourseCpl = (courseId: number, cplId: number) =>
  api.delete(`/admin/courses/${courseId}/cpls/${cplId}`)

// CPL
export const getCpls = (params?: object) => api.get('/admin/cpls', { params })
export const createCpl = (data: object) => api.post('/admin/cpls', data)
export const updateCpl = (id: number, data: object) => api.put(`/admin/cpls/${id}`, data)
export const deleteCpl = (id: number) => api.delete(`/admin/cpls/${id}`)

// CPMK
export const getCpmks = (params?: object) => api.get('/admin/cpmks', { params })
export const createCpmk = (data: object) => api.post('/admin/cpmks', data)
export const updateCpmk = (id: number, data: object) => api.put(`/admin/cpmks/${id}`, data)
export const deleteCpmk = (id: number) => api.delete(`/admin/cpmks/${id}`)

// CPMK ↔ CPL mapping (UC-14g)
export const getCpmkCpls = (cpmkId: number) => api.get(`/admin/cpmks/${cpmkId}/cpls`)
export const mapCpmkCpls = (cpmkId: number, cpl_ids: number[]) =>
  api.post(`/admin/cpmks/${cpmkId}/cpls`, { cpl_ids })
export const unmapCpmkCpl = (cpmkId: number, cplId: number) =>
  api.delete(`/admin/cpmks/${cpmkId}/cpls/${cplId}`)

// User Management
export const getUsers = (params?: object) => api.get('/admin/users', { params })
export const createUser = (data: object) => api.post('/admin/users', data)
export const updateUser = (id: string, data: object) => api.put(`/admin/users/${id}`, data)
export const toggleUserActive = (id: string) => api.patch(`/admin/users/${id}/toggle`)

// Analytics
export const getAnalyticsComparison = (params?: object) => api.get('/admin/analytics/comparison', { params })
export const getAnalyticsDistribution = (params?: object) => api.get('/admin/analytics/distribution', { params })
export const getAnalyticsCippScores = (params?: object) => api.get('/admin/analytics/cipp-scores', { params })
export const getAnalyticsComparisonGroups = (groupBy: string) => api.get('/admin/analytics/comparison-groups', { params: { group_by: groupBy } })
export const getAnalyticsCplCpmkMatrix = (courseId: number) => api.get('/admin/analytics/cpl-cpmk-matrix', { params: { course_id: courseId } })

// Instruments
export const getInstrumentDimensions = () => api.get('/admin/instruments/dimensions')
export const getInstrumentItems = (dimId: number, params?: object) => api.get(`/admin/instruments/dimensions/${dimId}/items`, { params })
export const createInstrumentItem = (data: object) => api.post('/admin/instruments/items', data)
export const updateInstrumentItem = (id: number, data: object) => api.put(`/admin/instruments/items/${id}`, data)
export const toggleInstrumentItem = (id: number) => api.patch(`/admin/instruments/items/${id}/toggle`)
export const deleteInstrumentItem = (id: number) => api.delete(`/admin/instruments/items/${id}`)
export const importInstrumentItems = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/admin/instruments/items/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const exportInstrumentItems = (template = false) =>
  api.get('/admin/instruments/items/export', { params: { template }, responseType: 'blob' })
export const getOpenQuestions = () => api.get('/admin/instruments/open-questions')
export const createOpenQuestion = (data: object) => api.post('/admin/instruments/open-questions', data)
export const updateOpenQuestion = (id: number, data: object) => api.put(`/admin/instruments/open-questions/${id}`, data)
export const toggleOpenQuestion = (id: number) => api.patch(`/admin/instruments/open-questions/${id}/toggle`)

// Anonymous Codes
export const getAnonymousCodes = (params?: object) => api.get('/admin/anonymous-codes', { params })
export const toggleAnonymousCode = (kode: string) => api.patch(`/admin/anonymous-codes/${kode}/toggle`)

// RPS
export const getRpsList = (params?: object) => api.get('/admin/rps', { params })
export const createRps = (data: object) => api.post('/admin/rps', data)
export const updateRps = (id: number, data: object) => api.put(`/admin/rps/${id}`, data)
export const deleteRps = (id: number) => api.delete(`/admin/rps/${id}`)
export const getRpsChecklist = (rpsId: number) => api.get(`/admin/rps/${rpsId}/checklist`)
export const updateRpsChecklist = (rpsId: number, itemId: number, data: object) =>
  api.patch(`/admin/rps/${rpsId}/checklist/${itemId}`, data)

// Assessment Scheme (UC-14j)
export const getSchemes = (params?: object) => api.get('/admin/assessment/schemes', { params })
export const createScheme = (data: object) => api.post('/admin/assessment/schemes', data)
export const updateScheme = (id: number, data: object) => api.put(`/admin/assessment/schemes/${id}`, data)
export const deleteScheme = (id: number) => api.delete(`/admin/assessment/schemes/${id}`)

// Rubrik (UC-14k)
export const getRubrics = (schemeId: number) => api.get(`/admin/assessment/schemes/${schemeId}/rubrics`)
export const createRubric = (schemeId: number, data: object) => api.post(`/admin/assessment/schemes/${schemeId}/rubrics`, data)
export const updateRubric = (id: number, data: object) => api.put(`/admin/assessment/rubrics/${id}`, data)
export const deleteRubric = (id: number) => api.delete(`/admin/assessment/rubrics/${id}`)

// MBKM Integration (UC-14l)
export const getMbkmList = (params?: object) => api.get('/admin/assessment/mbkm', { params })
export const createMbkm = (data: object) => api.post('/admin/assessment/mbkm', data)
export const updateMbkm = (id: number, data: object) => api.put(`/admin/assessment/mbkm/${id}`, data)
export const deleteMbkm = (id: number) => api.delete(`/admin/assessment/mbkm/${id}`)
export const toggleMbkm = (id: number) => api.patch(`/admin/assessment/mbkm/${id}/toggle`)

// Export (UC-18) — gunakan window.open atau link download langsung
export const exportUrl = (path: string, params?: Record<string, any>) => {
  const token = localStorage.getItem('access_token')
  const qs = params ? '&' + new URLSearchParams(params).toString() : ''
  return `/api/v1/admin/export/${path}?format=xlsx${qs}`
}
export const exportWithAuth = (path: string, params?: Record<string, any>) =>
  api.get(`/admin/export/${path}`, { params: { format: 'xlsx', ...params }, responseType: 'blob' })
export const exportCsvWithAuth = (path: string, params?: Record<string, any>) =>
  api.get(`/admin/export/${path}`, { params: { format: 'csv', ...params }, responseType: 'blob' })

// Diagnostic Report (UC-19)
export const getReports = (params?: object) => api.get('/admin/reports', { params })
export const generateReport = (data: object) => api.post('/admin/reports', data)
export const getReport = (id: string) => api.get(`/admin/reports/${id}`)
export const deleteReport = (id: string) => api.delete(`/admin/reports/${id}`)
