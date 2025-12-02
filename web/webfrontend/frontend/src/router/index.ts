import { createRouter, createWebHistory} from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: () => import('@/pages/LoginPage.vue') },
  { path: '/home', component: () => import('@/pages/HomePage.vue') },
  { path: '/format', component: () => import('@/pages/FormatPage.vue') },
  { path: '/outline', name: 'OutlinePage', component: () => import('@/pages/OutlinePage.vue') },
  { path: '/content', component: () => import('@/pages/ContentPage.vue') },
  { path: '/knowledge', component: () => import('@/pages/KnowledgeConfigPage.vue') },
  { path: '/svgdraw', component: () => import('@/pages/SVGEditorPage.vue') },
    { path: '/userList', component: () => import('@/pages/UserListPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

