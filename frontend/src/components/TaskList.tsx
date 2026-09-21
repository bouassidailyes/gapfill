import { useState } from 'react'
import type { FormEvent } from 'react'
import type { TaskInput } from '../types'

type Props = {
  tasks: TaskInput[]
  onAdd: (text: string) => void
  onRemove: (id: string) => void
}

export function TaskList({ tasks, onAdd, onRemove }: Props) {
  const [text, setText] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    onAdd(trimmed)
    setText('')
  }

  return (
    <section className="panel">
      <h2>Tasks</h2>
      <form className="task-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={text}
          placeholder="Finish DB assignment, due Fri, ~3h"
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" className="ghost">
          Add
        </button>
      </form>
      {tasks.length === 0 ? (
        <p className="hint">No tasks yet. Add one per line of your to-do list.</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id}>
              <span>{task.text}</span>
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
