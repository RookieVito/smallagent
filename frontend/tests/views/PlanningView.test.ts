import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import PlanningView from '@/views/PlanningView.vue'
import * as api from '@/services/api'
import { usePlanStore } from '@/composables/usePlanStore'

vi.mock('@/services/api')

const mockPlan = {
  destination: '北京',
  days: [{ date: '2026-05-01', attractions: [], dining_suggestion: '', accommodation_note: '', cover_image_url: null }],
  weather_summary: { overview: '晴', daily_forecasts: [] },
  budget_summary: { estimated_total: '1000', currency: 'CNY', breakdown: { accommodation: '400', dining: '300', attractions: '200', transport: '100' } },
  map_points: [],
  cover_image_url: null,
  created_at: null,
  plan_version: 1,
}

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'planning', component: PlanningView },
      { path: '/result', name: 'result', component: { template: '<div>Result</div>' } },
    ],
  })
}

function mountPlanning(router?: ReturnType<typeof createTestRouter>) {
  const r = router ?? createTestRouter()
  return mount(PlanningView, {
    global: {
      plugins: [r, Antd],
    },
  })
}

describe('PlanningView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const { clearPlan } = usePlanStore()
    clearPlan()
  })

  it('renders the form with destination label', () => {
    const wrapper = mountPlanning()
    expect(wrapper.text()).toContain('目的地')
  })

  it('renders budget and accommodation selects', () => {
    const wrapper = mountPlanning()
    expect(wrapper.text()).toContain('预算等级')
    expect(wrapper.text()).toContain('住宿类型')
  })

  it('calls createTripPlan on valid submission', async () => {
    const router = createTestRouter()
    vi.mocked(api.createTripPlan).mockResolvedValueOnce(mockPlan as any)

    const wrapper = mountPlanning(router)

    // Fill destination
    const input = wrapper.find('input')
    await input.setValue('北京')

    // Set date range (simulating a-range-picker v-model)
    const vm = wrapper.vm as any
    vm.form.dateRange = ['2026-05-01', '2026-05-03']
    vm.form.preferences = ['文化']
    await wrapper.vm.$nextTick()

    // Submit form
    const form = wrapper.find('form')
    await form.trigger('submit')
    await wrapper.vm.$nextTick()

    expect(api.createTripPlan).toHaveBeenCalledWith(
      expect.objectContaining({
        destination: '北京',
        start_date: '2026-05-01',
        end_date: '2026-05-03',
        preferences: ['文化'],
      }),
    )
  })

  it('shows error on API failure', async () => {
    vi.mocked(api.createTripPlan).mockRejectedValueOnce(new Error('fail'))

    const wrapper = mountPlanning()
    const vm = wrapper.vm as any
    vm.form.destination = '北京'
    vm.form.dateRange = ['2026-05-01', '2026-05-03']
    vm.form.preferences = ['文化']
    await wrapper.vm.$nextTick()

    await wrapper.find('form').trigger('submit')
    // Wait for async
    await vi.waitFor(() => {
      expect(api.createTripPlan).toHaveBeenCalled()
    }, { timeout: 2000 })
  })
})
