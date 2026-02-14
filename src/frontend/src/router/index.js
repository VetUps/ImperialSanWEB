import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/catalog'
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/catalog',
    name: 'catalog',
    component: () => import('@/views/CatalogView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, roles: ['Manager', 'Admin'] }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const { isAuthenticated, userRole } = authStore

  console.log('Navigation guard triggered:')
  console.log('  To:', to.path)
  console.log('  From:', from.path)
  console.log('  isAuthenticated:', isAuthenticated)
  console.log('  userRole:', userRole)

  // Проверка на аутентификацию
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  // Проверка на доступ только для гостей
  if (to.meta.guestOnly && isAuthenticated) {
    return next('/catalog')
  }

  // Проверка ролей
  if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    return next('/catalog')
  }

  next()
})

export default router