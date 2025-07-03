import { createRouter, createWebHistory } from 'vue-router'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Index',
      component: () => import('@/views')
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login')
    }
  ],
})

export default router
