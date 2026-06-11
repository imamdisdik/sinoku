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
