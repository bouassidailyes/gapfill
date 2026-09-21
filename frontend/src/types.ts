export type Event = {
  id: string
  title: string
  start: string
  end: string
  location?: string
}

export type MealSpec = {
  window: [string, string]
  minutes: number
}

export type Settings = {
  timezone: string
  horizon_start: string
  horizon_days: number
  day_start: string
  day_end: string
  meals: {
    breakfast?: MealSpec
    lunch: MealSpec
    dinner: MealSpec
  }
  cooking: { mode: 'daily' | 'batch' | 'none'; batch_per_week: number; cook_minutes: number }
  transition_minutes: number
  travel_overrides: { from: string; to: string; minutes: number }[]
  lost_time_pct: number
  free_time_min_per_day: number
}

export type TaskInput = { id: string; text: string }

export type Block = {
  id: string
  type: 'event' | 'task' | 'meal' | 'cook' | 'travel' | 'free' | 'slack'
  title: string
  start: string
  end: string
  task_id?: string
  location?: string
  locked?: boolean
}

export type Session = { id: string; minutes: number; kind: 'deep' | 'light' }

export type TaskPlan = {
  task_id: string
  title: string
  deadline: string | null
  priority: 1 | 2 | 3
  estimated_minutes: number
  sessions: Session[]
  preferred_time: 'morning' | 'afternoon' | 'evening' | 'any'
  notes?: string
}

export type ScheduleRequest = {
  events: Event[]
  tasks: TaskInput[]
  settings: Settings
  pinned?: Block[]
}

export type ScheduleResponse = {
  blocks: Block[]
  task_plans: TaskPlan[]
  warnings: string[]
}

export type ParseIcsResponse = { events: Event[] }

export type ExportIcsRequest = {
  blocks: Block[]
  include_fixed: boolean
}

export const DEFAULT_SETTINGS: Settings = {
  timezone: 'Europe/Amsterdam',
  horizon_start: '2026-09-21',
  horizon_days: 7,
  day_start: '08:00',
  day_end: '22:30',
  meals: {
    breakfast: { window: ['08:00', '09:00'], minutes: 20 },
    lunch: { window: ['12:00', '13:30'], minutes: 30 },
    dinner: { window: ['18:30', '20:00'], minutes: 30 },
  },
  cooking: { mode: 'batch', batch_per_week: 3, cook_minutes: 45 },
  transition_minutes: 15,
  travel_overrides: [{ from: 'UM Campus', to: 'University Library', minutes: 20 }],
  lost_time_pct: 15,
  free_time_min_per_day: 60,
}
