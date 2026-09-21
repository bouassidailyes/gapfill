import type { Event } from './types'

/** A weekly commitment at a fixed time, e.g. "Gym, Tue + Thu, 19:00, 45min". */
export type RecurringRule = {
  id: string
  title: string
  weekdays: number[] // 0 = Sunday … 6 = Saturday, matching Date.getDay()
  start: string // "19:00"
  minutes: number
  location?: string
}

export const WEEKDAYS = [
  { value: 1, label: 'Mon' },
  { value: 2, label: 'Tue' },
  { value: 3, label: 'Wed' },
  { value: 4, label: 'Thu' },
  { value: 5, label: 'Fri' },
  { value: 6, label: 'Sat' },
  { value: 0, label: 'Sun' },
]

const pad = (n: number) => String(n).padStart(2, '0')

/** ISO 8601 with the local UTC offset, e.g. "2026-09-22T19:00:00+02:00". */
function toIsoWithOffset(d: Date): string {
  const offset = -d.getTimezoneOffset()
  const sign = offset >= 0 ? '+' : '-'
  const abs = Math.abs(offset)
  const date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  const time = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  return `${date}T${time}${sign}${pad(Math.floor(abs / 60))}:${pad(abs % 60)}`
}

export function describeRule(rule: RecurringRule): string {
  const days = WEEKDAYS.filter((d) => rule.weekdays.includes(d.value))
    .map((d) => d.label)
    .join(', ')
  return `${days} · ${rule.start} · ${rule.minutes}min`
}

/**
 * Expand weekly rules into one Event per occurrence across the horizon, so the
 * backend sees them as ordinary busy time and never plans work over them.
 */
export function expandRecurring(
  rules: RecurringRule[],
  horizonStart: string,
  horizonDays: number,
): Event[] {
  const [year, month, day] = horizonStart.split('-').map(Number)
  if (!year || !month || !day) return []

  const events: Event[] = []
  for (let offset = 0; offset < horizonDays; offset++) {
    const current = new Date(year, month - 1, day + offset)
    for (const rule of rules) {
      if (!rule.weekdays.includes(current.getDay())) continue
      const [hours, minutes] = rule.start.split(':').map(Number)
      const start = new Date(
        current.getFullYear(),
        current.getMonth(),
        current.getDate(),
        hours,
        minutes,
      )
      const end = new Date(start.getTime() + rule.minutes * 60_000)
      events.push({
        id: `${rule.id}-${offset}`,
        title: rule.title,
        start: toIsoWithOffset(start),
        end: toIsoWithOffset(end),
        ...(rule.location ? { location: rule.location } : {}),
      })
    }
  }
  return events
}
