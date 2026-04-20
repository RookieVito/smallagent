import axios from 'axios'
import type { TripPlanRequest, TripPlan, EditRequest } from '@/types'

const apiClient = axios.create({
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

export async function createTripPlan(request: TripPlanRequest): Promise<TripPlan> {
  const { data } = await apiClient.post<TripPlan>('/api/trip/plan', request)
  return data
}

export async function editTripPlan(request: EditRequest): Promise<TripPlan> {
  const { data } = await apiClient.post<TripPlan>('/api/trip/edit', request)
  return data
}
