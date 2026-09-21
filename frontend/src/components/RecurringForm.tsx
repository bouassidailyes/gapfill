import { useState } from 'react'
import type { FormEvent } from 'react'
import type { RecurringRule } from '../recurring'
import { WEEKDAYS } from '../recurring'
import { Panel } from './Panel'

type Props = {
  rules: RecurringRule[]
  onAdd: (rule: Omit<RecurringRule, 'id'>) => void
  onRemove: (id: string) => void
}

export function RecurringForm({ rules, onAdd, onRemove }: Props) {
  const [title, setTitle] = useState('')
  const [weekdays, setWeekdays] = useState<number[]>([])
  const [start, setStart] = useState('19:00')
  const [minutes, setMinutes] = useState(45)

  function toggleDay(day: number) {
    setWeekdays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed || weekdays.length === 0) return
    onAdd({ title: trimmed, weekdays, start, minutes })
    setTitle('')
    setWeekdays([])
  }

  return (
    <Panel label="Weekly Commitments" count={rules.length}>
      {rules.length > 0 && (
        <ul className="task-list" style={{ marginBottom: 10 }}>
          {rules.map((rule) => (
            <li key={rule.id} className="list-card">
              <div className="list-card-top">
                <strong>{rule.title}</strong>
                <button
                  type="button"
                  className="icon"
                  aria-label={`Remove ${rule.title}`}
                  onClick={() => onRemove(rule.id)}
                >
                  ×
                </button>
              </div>
              <div className="chip-row">
                {WEEKDAYS.filter((day) => rule.weekdays.includes(day.value)).map((day) => (
                  <span key={day.value} className="chip-tag">
                    {day.label}
                  </span>
                ))}
                <span className="chip-meta">
                  {rule.start} · {rule.minutes} min
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          placeholder="Activity name (e.g. Gym)"
          onChange={(e) => setTitle(e.target.value)}
          style={{ marginBottom: 7 }}
        />
        <div className="weekday-row">
          {WEEKDAYS.map((day) => (
            <button
              key={day.value}
              type="button"
              className={weekdays.includes(day.value) ? 'chip on' : 'chip'}
              aria-pressed={weekdays.includes(day.value)}
              onClick={() => toggleDay(day.value)}
            >
              {day.label}
            </button>
          ))}
        </div>
        <div className="field-row">
          <label>
            <div className="field-label">Time</div>
            <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
          </label>
          <label>
            <div className="field-label">Minutes</div>
            <input
              type="number"
              min={15}
              max={300}
              step={15}
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
            />
          </label>
        </div>
        <button type="submit" className="btn-ghost" disabled={!title.trim() || weekdays.length === 0}>
          Add commitment
        </button>
      </form>
      {rules.length === 0 && (
        <p className="hint">
          Nothing weekly yet.{' '}
          <span style={{ color: 'var(--fg2)' }}>Sport, work shifts, a standing meeting.</span>
        </p>
      )}
    </Panel>
  )
}
