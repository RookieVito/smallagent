import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import ResultView from '@/views/ResultView.vue'
import { usePlanStore } from '@/composables/usePlanStore'
import { editTripPlan } from '@/services/api'
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

const mockPlanMultiAttractions: TripPlan = {
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
        {
          name: '天坛',
          address: '北京市东城区天坛路',
          latitude: 39.8822,
          longitude: 116.4066,
          suggested_duration_minutes: 120,
          ticket_price: 15,
        },
        {
          name: '颐和园',
          address: '北京市海淀区',
          latitude: 39.9998,
          longitude: 116.2755,
          suggested_duration_minutes: 150,
          ticket_price: 30,
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
  map_points: [
    { name: '故宫', latitude: 39.9163, longitude: 116.3972, category: 'attraction' },
    { name: '天坛', latitude: 39.8822, longitude: 116.4066, category: 'attraction' },
    { name: '颐和园', latitude: 39.9998, longitude: 116.2755, category: 'attraction' },
  ],
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

  it('renders map error state when AMap key is not configured', async () => {
    const wrapper = mountResult()
    // initMap is async (onMounted), wait for it to complete
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('地图不可用')
    })
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

  describe('editing', () => {
    async function mountAndExpand(plan: TripPlan) {
      const wrapper = mountResult(plan)
      // Expand the first collapse panel so buttons are in the DOM
      const headers = wrapper.findAll('.ant-collapse-header')
      if (headers.length > 0) {
        await headers[0].trigger('click')
        await wrapper.vm.$nextTick()
      }
      return wrapper
    }

    it('renders delete button for each attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const deleteButtons = wrapper.findAll('button[title="删除"]')
      expect(deleteButtons.length).toBe(3)
    })

    it('renders up and down buttons for each attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const upButtons = wrapper.findAll('button[title="上移"]')
      const downButtons = wrapper.findAll('button[title="下移"]')
      expect(upButtons.length).toBe(3)
      expect(downButtons.length).toBe(3)
    })

    it('disables up button for first attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const upButtons = wrapper.findAll('button[title="上移"]')
      expect(upButtons[0].element.getAttribute('disabled')).not.toBeNull()
    })

    it('disables down button for last attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const downButtons = wrapper.findAll('button[title="下移"]')
      expect(downButtons[2].element.getAttribute('disabled')).not.toBeNull()
    })

    it('enables up button for non-first attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const upButtons = wrapper.findAll('button[title="上移"]')
      expect(upButtons[1].element.getAttribute('disabled')).toBeNull()
    })

    it('enables down button for non-last attraction', async () => {
      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const downButtons = wrapper.findAll('button[title="下移"]')
      expect(downButtons[0].element.getAttribute('disabled')).toBeNull()
    })

    it('calls editTripPlan with delete operation when delete button clicked', async () => {
      const editedPlan: TripPlan = {
        ...mockPlanMultiAttractions,
        days: [{
          ...mockPlanMultiAttractions.days[0],
          attractions: mockPlanMultiAttractions.days[0].attractions.filter((_, i) => i !== 1),
        }],
      }
      vi.mocked(editTripPlan).mockResolvedValueOnce(editedPlan)

      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const deleteButtons = wrapper.findAll('button[title="删除"]')

      // Click delete on the second attraction (天坛)
      await deleteButtons[1].trigger('click')

      expect(editTripPlan).toHaveBeenCalledWith({
        plan: mockPlanMultiAttractions,
        operation: 'delete_attraction',
        day_index: 0,
        attraction_index: 1,
      })
    })

    it('calls editTripPlan with move up operation when up button clicked', async () => {
      const movedPlan: TripPlan = {
        ...mockPlanMultiAttractions,
        days: [{
          ...mockPlanMultiAttractions.days[0],
          attractions: [
            mockPlanMultiAttractions.days[0].attractions[1],
            mockPlanMultiAttractions.days[0].attractions[0],
            mockPlanMultiAttractions.days[0].attractions[2],
          ],
        }],
      }
      vi.mocked(editTripPlan).mockResolvedValueOnce(movedPlan)

      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const upButtons = wrapper.findAll('button[title="上移"]')

      // Click up on the second attraction (天坛)
      await upButtons[1].trigger('click')

      expect(editTripPlan).toHaveBeenCalledWith({
        plan: mockPlanMultiAttractions,
        operation: 'move_attraction',
        day_index: 0,
        attraction_index: 1,
        direction: 'up',
      })
    })

    it('calls editTripPlan with move down operation when down button clicked', async () => {
      const movedPlan: TripPlan = {
        ...mockPlanMultiAttractions,
        days: [{
          ...mockPlanMultiAttractions.days[0],
          attractions: [
            mockPlanMultiAttractions.days[0].attractions[0],
            mockPlanMultiAttractions.days[0].attractions[2],
            mockPlanMultiAttractions.days[0].attractions[1],
          ],
        }],
      }
      vi.mocked(editTripPlan).mockResolvedValueOnce(movedPlan)

      const wrapper = await mountAndExpand(mockPlanMultiAttractions)
      const downButtons = wrapper.findAll('button[title="下移"]')

      // Click down on the first attraction (故宫)
      await downButtons[0].trigger('click')

      expect(editTripPlan).toHaveBeenCalledWith({
        plan: mockPlanMultiAttractions,
        operation: 'move_attraction',
        day_index: 0,
        attraction_index: 0,
        direction: 'down',
      })
    })
  })
})
