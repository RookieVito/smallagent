import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import ResultView from '@/views/ResultView.vue'
import { usePlanStore } from '@/composables/usePlanStore'
import type { TripPlan } from '@/types'

vi.mock('@/services/api', () => ({
  createTripPlan: vi.fn(),
  editTripPlan: vi.fn(),
}))

const mockPlan: TripPlan = {
  destination: '北京',
  days: [
    {
      date: '2026-05-01',
      attractions: [
        {
          name: '故宫',
          address: '北京市东城区',
          latitude: 39.9163,
          longitude: 116.3972,
          suggested_duration_minutes: 180,
          ticket_price: 60,
        },
      ],
      dining_suggestion: '王府井小吃街',
      accommodation_note: '王府井附近酒店',
    },
  ],
  weather_summary: { overview: '晴朗宜人', daily_forecasts: [] },
  budget_summary: {
    estimated_total: 3000,
    currency: 'CNY',
    breakdown: { '住宿': 1200, '餐饮': 900 },
    notes: '预估费用',
  },
  map_points: [{ name: '故宫', latitude: 39.9163, longitude: 116.3972, category: 'attraction' }],
}

function mountResult(plan: TripPlan | null = mockPlan) {
  const { setPlan, clearPlan } = usePlanStore()
  clearPlan()
  if (plan) setPlan(plan)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'planning', component: { template: '<div>Planning</div>' } },
      { path: '/result', name: 'result', component: ResultView },
    ],
  })

  return mount(ResultView, {
    global: {
      plugins: [router, Antd],
    },
  })
}

describe('ResultView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const { clearPlan } = usePlanStore()
    clearPlan()
  })

  it('renders destination in overview', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('北京')
  })

  it('renders budget summary with total', () => {
    const wrapper = mountResult()
    // a-statistic formats with locale thousand separator
    expect(wrapper.text()).toContain('3,000')
  })

  it('renders daily itinerary day header in collapse panel', () => {
    const wrapper = mountResult()
    // Collapse panel header shows day number and date
    expect(wrapper.text()).toContain('第 1 天')
    expect(wrapper.text()).toContain('2026-05-01')
  })

  it('renders weather overview', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('晴朗宜人')
  })

  it('shows empty state when no plan data', () => {
    const wrapper = mountResult(null)
    expect(wrapper.text()).toContain('暂无行程数据')
  })

  it('renders budget breakdown labels', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('住宿')
    expect(wrapper.text()).toContain('餐饮')
  })

  it('renders budget breakdown values', () => {
    const wrapper = mountResult()
    // a-descriptions renders values without locale formatting
    expect(wrapper.text()).toContain('1200')
    expect(wrapper.text()).toContain('900')
  })

  it('renders budget notes', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('预估费用')
  })

  it('renders map placeholder', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('地图加载中')
  })

  it('renders date range and day count in subtitle', () => {
    const wrapper = mountResult()
    expect(wrapper.text()).toContain('2026-05-01 ~ 2026-05-01')
    expect(wrapper.text()).toContain('1天')
  })

  it('exposes day data through computed plan for collapsed content', () => {
    const wrapper = mountResult()
    const vm = wrapper.vm as any
    // Verify the plan data is accessible (content is inside collapse, rendered on expand)
    expect(vm.plan.days[0].attractions[0].name).toBe('故宫')
    expect(vm.plan.days[0].dining_suggestion).toBe('王府井小吃街')
    expect(vm.plan.days[0].accommodation_note).toBe('王府井附近酒店')
  })
})
