import { createRouter, createWebHistory } from 'vue-router'
import { usePlanStore } from '@/composables/usePlanStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'planning',
      component: () => import('@/views/PlanningView.vue'),
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('@/views/ResultView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  if (to.name === 'result') {
    const { currentPlan } = usePlanStore()
    if (!currentPlan.value) return { name: 'planning' }
  }
})

export default router
