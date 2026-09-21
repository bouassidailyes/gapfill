import { useState } from 'react'
import type { ChangeEvent } from 'react'
import { parseCalendar } from '../api'
import type { Event } from '../types'

type Props = {
  events: Event[]
  onEvents: (events: Event[]) => void
}

export function ScheduleUpload({ events, onEvents }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      onEvents(await parseCalendar(file))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not read this schedule.')
      onEvents([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <h2>Schedule</h2>
      <input
        type="file"
        accept=".csv,.ics,text/csv,text/calendar"
        onChange={handleChange}
        disabled={loading}
      />
      {loading && <p className="hint">Reading schedule…</p>}
      {error && <p className="field-error">{error}</p>}
      {!loading && !error && (
        <p className="hint">
          {events.length > 0
            ? `${events.length} events loaded`
            : 'Upload your timetable export (.csv or .ics).'}
        </p>
      )}
    </section>
  )
}
