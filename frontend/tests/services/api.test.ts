import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTripPlan, editTripPlan } from '@/services/api'
import type { TripPlanRequest, TripPlan, EditRequest } from '@/types'

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(),
}))
vi.mock('axios', () => ({
  default: {
    create: () => ({ post: mockPost }),
  },
}))

const mockTripPlanRequest: TripPlanRequest = {
  destination: '北京',
  start_date: '2026-05-01',
  end_date: '2026-05-03',
  preferences: ['文化'],
  budget_level: 'moderate',
  accommodation_type: 'hotel',
}

const mockTripPlan: TripPlan = {
  destination: '北京',
  days: [
    {
      date: '2026-05-01',
      attractions: [
        {
          name: '故宫',
          address: '北京市东城区景山前街4号',
          latitude: 39.9163,
          longitude: 116.3972,
          suggested_duration_minutes: 180,
          ticket_price: 60,
        },
      ],
      dining_suggestion: '王府井小吃街',
      accommodation_note: '推荐住在王府井附近',
    },
  ],
  weather_summary: { overview: '晴朗', daily_forecasts: [] },
  budget_summary: { estimated_total: 3000, currency: 'CNY', breakdown: {}, notes: '' },
  map_points: [{ name: '故宫', latitude: 39.9163, longitude: 116.3972, category: 'attraction' }],
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('createTripPlan', () => {
  it('should call POST /api/trip/plan and return TripPlan', async () => {
    mockPost.mockResolvedValueOnce({ data: mockTripPlan })
    const result = await createTripPlan(mockTripPlanRequest)
    expect(mockPost).toHaveBeenCalledWith('/api/trip/plan', mockTripPlanRequest)
    expect(result).toEqual(mockTripPlan)
  })

  it('should throw on API error', async () => {
    mockPost.mockRejectedValueOnce(new Error('Service Unavailable'))
    await expect(createTripPlan(mockTripPlanRequest)).rejects.toThrow('Service Unavailable')
  })
})

describe('editTripPlan', () => {
  it('should call POST /api/trip/edit with delete operation', async () => {
    const editReq: EditRequest = {
      plan: mockTripPlan,
      operation: 'delete_attraction',
      day_index: 0,
      attraction_index: 0,
    }
    const editedPlan: TripPlan = { ...mockTripPlan, days: [{ ...mockTripPlan.days[0], attractions: [] }] }
    mockPost.mockResolvedValueOnce({ data: editedPlan })
    const result = await editTripPlan(editReq)
    expect(mockPost).toHaveBeenCalledWith('/api/trip/edit', editReq)
    expect(result).toEqual(editedPlan)
  })

  it('should call POST /api/trip/edit with move operation', async () => {
    const editReq: EditRequest = {
      plan: mockTripPlan,
      operation: 'move_attraction',
      day_index: 0,
      attraction_index: 0,
      direction: 'down',
    }
    mockPost.mockResolvedValueOnce({ data: mockTripPlan })
    const result = await editTripPlan(editReq)
    expect(mockPost).toHaveBeenCalledWith('/api/trip/edit', editReq)
    expect(result).toEqual(mockTripPlan)
  })
})
