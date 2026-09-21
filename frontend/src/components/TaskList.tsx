import { useState } from 'react'
import type { FormEvent } from 'react'
import type { TaskInput } from '../types'
import { Panel } from './Panel'

type Props = {
  tasks: TaskInput[]
  onAdd: (text: string, minutes: number) => void
  onRemove: (id: string) => void
}

export function TaskList({ tasks, onAdd, onRemove }: Props) {
  const [text, setText] = useState('')
  const [minutes, setMinutes] = useState(60)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    onAdd(trimmed, minutes)
    setText('')
    setMinutes(60)
  }

  return (
    <Panel label="Tasks" count={tasks.length}>
      <form className="task-form" onSubmit={handleSubmit}>
        <input
          className="grow"
          type="text"
          value={text}
          placeholder="e.g. Finish DB assignment, due Fri"
          onChange={(e) => setText(e.target.value)}
        />
        <label className="minutes">
          ~min
          <input
            type="number"
            min={25}
            max={480}
            step={5}
            value={minutes}
            onChange={(e) => setMinutes(Number(e.target.value) || 60)}
          />
        </label>
        <button type="submit" className="btn-add">
          Add
        </button>
      </form>
      {tasks.length === 0 ? (
        <p className="hint">
          No tasks yet. Add one <span style={{ color: 'var(--accent2)' }}>per line</span> of your
          to-do list.
        </p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <span className="task-dot" />
              <span>
                {task.text}
                {task.estimated_minutes ? (
                  <>
                    <br />
                    <small className="chip-meta">~{task.estimated_minutes} min</small>
                  </>
                ) : null}
              </span>
              <button
                type="button"
                className="icon"
                aria-label={`Remove ${task.text}`}
                onClick={() => onRemove(task.id)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  )
}
