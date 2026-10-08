import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/features/auth/authStore'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
  }
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/sandbox', name: 'sandbox', component: () => import('@/views/SandboxView.vue') },
    { path: '/entrar', name: 'login', component: () => import('@/features/auth/LoginView.vue') },
    {
      path: '/salas',
      name: 'rooms',
      component: () => import('@/features/lobby/LobbyView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/sala/:id',
      name: 'room',
      component: () => import('@/features/lobby/RoomView.vue'),
      props: true,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.restore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return { name: 'login', query: { next: to.fullPath } }
  if (to.name === 'login' && auth.isLoggedIn) return { name: 'rooms' }
  return true
})
