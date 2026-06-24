import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ZONA PUBLIK
    { path: '/', name: 'landing', component: () => import('@/views/public/LandingPage.vue') },
    { path: '/survey', name: 'survey', component: () => import('@/views/public/survey/SurveySelector.vue') },
    { path: '/survey/consent', name: 'survey-consent', component: () => import('@/views/public/survey/SurveyConsent.vue') },
    { path: '/survey/profile', name: 'survey-profile', component: () => import('@/views/public/survey/SurveyProfile.vue') },
    { path: '/survey/step/B', name: 'survey-B', component: () => import('@/views/public/survey/SurveyStepContext.vue') },
    { path: '/survey/step/C', name: 'survey-C', component: () => import('@/views/public/survey/SurveyStepInput.vue') },
    { path: '/survey/step/D', name: 'survey-D', component: () => import('@/views/public/survey/SurveyStepProcess.vue') },
    { path: '/survey/step/E', name: 'survey-E', component: () => import('@/views/public/survey/SurveyStepProduct.vue') },
    { path: '/survey/thankyou', name: 'survey-thankyou', component: () => import('@/views/public/survey/SurveyThankYou.vue') },
    { path: '/result', name: 'result', component: () => import('@/views/public/result/ResultByCode.vue') },

    // AUTH
    { path: '/login', name: 'login', component: () => import('@/views/auth/LoginPage.vue') },

    // ADMIN (guard: harus login)
    {
      path: '/admin',
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/admin/DashboardHome.vue') },
        { path: 'universities', name: 'admin-universities', component: () => import('@/views/admin/academic/UniversityList.vue') },
        { path: 'mata-kuliah-saya', name: 'admin-my-courses', component: () => import('@/views/admin/academic/MyCourses.vue') },
        { path: 'faculties', name: 'admin-faculties', component: () => import('@/views/admin/academic/FacultyList.vue') },
        { path: 'programs', name: 'admin-programs', component: () => import('@/views/admin/academic/ProgramList.vue') },
        { path: 'courses', name: 'admin-courses', component: () => import('@/views/admin/academic/CourseList.vue') },
        { path: 'cpls', name: 'admin-cpls', component: () => import('@/views/admin/academic/CplManager.vue') },
        { path: 'cpmks', name: 'admin-cpmks', component: () => import('@/views/admin/academic/CpmkManager.vue') },
        { path: 'assessment/schemes', name: 'admin-assessment-schemes', component: () => import('@/views/admin/assessment/AssessmentScheme.vue') },
        { path: 'assessment/rubrics', name: 'admin-assessment-rubrics', component: () => import('@/views/admin/assessment/AssessmentRubric.vue') },
        { path: 'assessment/mbkm', name: 'admin-assessment-mbkm', component: () => import('@/views/admin/assessment/MbkmIntegration.vue') },
        { path: 'rps', name: 'admin-rps', component: () => import('@/views/admin/rps/RpsList.vue') },
        { path: 'rps/:id/checklist', name: 'admin-rps-checklist', component: () => import('@/views/admin/rps/RpsChecklist.vue') },
        { path: 'instruments', name: 'admin-instruments', component: () => import('@/views/admin/instrument/InstrumentList.vue') },
        { path: 'anonymous-codes', name: 'admin-anon', component: () => import('@/views/admin/anonymous/AnonymousCodeList.vue') },
        { path: 'analytics', name: 'admin-analytics', component: () => import('@/views/admin/analytics/AnalyticsDashboard.vue') },
        { path: 'reports', name: 'admin-reports', component: () => import('@/views/admin/report/DiagnosticHistory.vue') },
        { path: 'reports/:id', name: 'admin-report-preview', component: () => import('@/views/admin/report/DiagnosticPreview.vue') },
        { path: 'laporan-template', name: 'admin-laporan-template', component: () => import('@/views/admin/report/LaporanTemplate.vue') },
        { path: 'export', name: 'admin-export', component: () => import('@/views/admin/report/ExportData.vue') },
        { path: 'users', name: 'admin-users', component: () => import('@/views/admin/users/UserList.vue') },
      ],
    },

    // DOSEN SURVEY (guard: harus login sebagai dosen)
    { path: '/survey/dosen', name: 'survey-dosen', meta: { requiresAuth: true, requiresRole: 'dosen' }, component: () => import('@/views/public/survey/SurveyDosenSelector.vue') },

    // 404
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(authGuard)

export default router
