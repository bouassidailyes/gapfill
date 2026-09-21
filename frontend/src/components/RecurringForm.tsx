import { useState } from 'react'
import type { FormEvent } from 'react'
import type { RecurringRule } from '../recurring'
import { WEEKDAYS, describeRule } from '../recurring'

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
    <section className="panel">
      <h2>Weekly commitments</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={title}
          placeholder="Gym"
          onChange={(e) => setTitle(e.target.value)}
        />
        <div className="weekday-row">
          {WEEKDAYS.map((day) => (
            <button
              key={day.value}
              type="button"
              className={weekdays.includes(day.value) ? 'day on' : 'day'}
              aria-pressed={weekdays.includes(day.value)}
              onClick={() => toggleDay(day.value)}
            >
              {day.label}
            </button>
          ))}
        </div>
        <div className="field-row">
          <label>
            Time
            <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
          </label>
          <label>
            Minutes
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
        <button type="submit" className="ghost" disabled={!title.trim() || weekdays.length === 0}>
          Add commitment
        </button>
      </form>
      {rules.length === 0 ? (
        <p className="hint">Nothing weekly yet. Sport, work shifts, a standing meeting.</p>
      ) : (
        <ul className="task-list">
          {rules.map((rule) => (
            <li key={rule.id}>
              <span>
                <strong>{rule.title}</strong>
                <br />
                <small>{describeRule(rule)}</small>
              </span>
              <button
                type="button"
                className="icon"
                aria-label={`Remove ${rule.title}`}
                onClick={() => onRemove(rule.id)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
