import { useState } from 'react'
import type { ChangeEvent } from 'react'
import { parseIcs } from '../api'
import type { Event } from '../types'

type Props = {
  events: Event[]
  onEvents: (events: Event[]) => void
}

export function IcsUpload({ events, onEvents }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      onEvents(await parseIcs(file))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not read this calendar.')
      onEvents([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <h2>Calendar</h2>
      <input type="file" accept=".ics,text/calendar" onChange={handleChange} disabled={loading} />
      {loading && <p className="hint">Reading calendar…</p>}
      {error && <p className="field-error">{error}</p>}
      {!loading && !error && (
        <p className="hint">
          {events.length > 0 ? `${events.length} events loaded` : 'No calendar yet (optional).'}
        </p>
      )}
    </section>
  )
}
