export type BudgetLevel = 'budget' | 'moderate' | 'luxury'

export type AccommodationType = 'hotel' | 'hostel' | 'apartment' | 'resort' | 'any'

export interface TripPlanRequest {
  destination: string
  start_date: string
  end_date: string
  preferences: string[]
  budget_level: BudgetLevel
  accommodation_type: AccommodationType
}

export interface Attraction {
  name: string
  address: string
  latitude: number
  longitude: number
  suggested_duration_minutes: number
  ticket_price: number | null
}

export interface DayPlan {
  date: string
  attractions: Attraction[]
  dining_suggestion: string
  accommodation_note: string
}

export interface MapPoint {
  name: string
  latitude: number
  longitude: number
  category: string
}

export interface BudgetSummary {
  estimated_total: number
  currency: string
  breakdown: Record<string, number>
  notes: string
}

export interface WeatherSummary {
  overview: string
  daily_forecasts: Record<string, unknown>[]
}

export interface TripPlan {
  destination: string
  days: DayPlan[]
  weather_summary: WeatherSummary
  budget_summary: BudgetSummary
  map_points: MapPoint[]
}

export interface EditRequest {
  plan: TripPlan
  operation: 'delete_attraction' | 'move_attraction'
  day_index: number
  attraction_index: number
  direction?: 'up' | 'down'
}
