import type { Event, ExportIcsRequest, ScheduleRequest, ScheduleResponse } from './types'

const useMock = import.meta.env.VITE_USE_MOCK === '1'

export async function parseIcs(file: File): Promise<Event[]> {
  if (useMock) {
    return []
  }
  const body = new FormData()
  body.append('file', file)
  const res = await fetch('/api/parse-ics', { method: 'POST', body })
  if (!res.ok) {
    throw new Error(await readError(res, 'Could not parse this calendar.'))
  }
  const data: { events: Event[] } = await res.json()
  return data.events
}

export async function schedule(req: ScheduleRequest): Promise<ScheduleResponse> {
  if (useMock) {
    const mod = await import('../../fixtures/schedule.mock.json')
    return mod.default as ScheduleResponse
  }
  const res = await fetch('/api/schedule', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(await readError(res, 'Scheduling failed.'))
  }
  return (await res.json()) as ScheduleResponse
}

export async function exportIcs(req: ExportIcsRequest): Promise<Blob> {
  if (useMock) {
    throw new Error('ICS export is not available in mock mode.')
  }
  const res = await fetch('/api/export-ics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(await readError(res, 'Export failed.'))
  }
  return await res.blob()
}

async function readError(res: Response, fallback: string): Promise<string> {
  try {
    const data: unknown = await res.json()
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
    }
  } catch {
    /* ignore */
  }
  return fallback
}
