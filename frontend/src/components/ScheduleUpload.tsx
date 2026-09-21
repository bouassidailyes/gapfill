import { useRef, useState } from 'react'
import type { ChangeEvent } from 'react'
import { parseCalendar } from '../api'
import type { Event } from '../types'
import { Panel } from './Panel'

type Props = {
  events: Event[]
  onEvents: (events: Event[]) => void
}

export function ScheduleUpload({ events, onEvents }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)

  async function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    setFileName(file.name)
    try {
      onEvents(await parseCalendar(file))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not read this schedule.')
      onEvents([])
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  return (
    <Panel label="Calendar">
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.ics,text/csv,text/calendar"
        onChange={handleChange}
        disabled={loading}
        hidden
      />
      <button
        type="button"
        className="upload-btn"
        onClick={() => inputRef.current?.click()}
        disabled={loading}
      >
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden>
          <path
            d="M6.5 1v7.5M4 4l2.5-3 2.5 3M1.5 10.5h10"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span>{fileName ?? 'Upload .csv or .ics calendar'}</span>
      </button>
      {loading && <p className="hint">Reading schedule…</p>}
      {error && <p className="field-error">{error}</p>}
      {!loading && !error && (
        <p className="hint">
          {events.length > 0
            ? `${events.length} events parsed`
            : 'No calendar yet (optional).'}
        </p>
      )}
    </Panel>
  )
}
