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
  ticket_price: string | null
  image_url: string | null
}

export interface DayPlan {
  date: string
  attractions: Attraction[]
  dining_suggestion: string
  accommodation_note: string
  cover_image_url: string | null
}

export interface MapPoint {
  name: string
  latitude: number
  longitude: number
  category?: string
}

export interface BudgetBreakdown {
  accommodation: string
  dining: string
  attractions: string
  transport: string
}

export interface BudgetSummary {
  estimated_total: string
  currency: string
  breakdown: BudgetBreakdown
}

export interface DailyForecast {
  date: string
  condition: string
  high_celsius: number
  low_celsius: number
}

export interface WeatherSummary {
  overview: string
  daily_forecasts: DailyForecast[]
}

export interface TripPlan {
  destination: string
  days: DayPlan[]
  weather_summary: WeatherSummary
  budget_summary: BudgetSummary
  map_points: MapPoint[]
  cover_image_url: string | null
  created_at: string | null
  plan_version: number
}

export interface EditRequest {
  plan: TripPlan
  operation: 'delete_attraction' | 'move_attraction'
  day_index: number
  attraction_index: number
  direction?: 'up' | 'down' | null
}
