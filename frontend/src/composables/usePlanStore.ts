import { ref } from 'vue'
import type { TripPlan } from '@/types'

const currentPlan = ref<TripPlan | null>(null)

export function usePlanStore() {
  function setPlan(plan: TripPlan) {
    currentPlan.value = plan
  }

  function clearPlan() {
    currentPlan.value = null
  }

  return {
    currentPlan,
    setPlan,
    clearPlan,
  }
}
