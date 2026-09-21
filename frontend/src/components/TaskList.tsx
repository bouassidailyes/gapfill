import { useState } from 'react'
import type { FormEvent } from 'react'
import type { TaskInput } from '../types'

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
    <section className="panel">
      <h2>Tasks</h2>
      <form className="task-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          placeholder="Finish DB assignment, due Fri"
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
        <button type="submit" className="ghost">
          Add
        </button>
      </form>
      {tasks.length === 0 ? (
        <p className="hint">Homework and other work that can move around classes.</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <span>
                {task.text}
                {task.estimated_minutes ? (
                  <>
                    <br />
                    <small>~{task.estimated_minutes} min</small>
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
    </section>
  )
}
