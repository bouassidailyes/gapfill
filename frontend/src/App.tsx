import { useEffect, useReducer } from 'react'
import { schedule } from './api'
import { CalendarView } from './components/CalendarView'
import { Legend } from './components/Legend'
import { initialState, reducer } from './state'
import { DEFAULT_SETTINGS } from './types'

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)

  useEffect(() => {
    let cancelled = false
    dispatch({ type: 'set-status', status: 'loading-place' })
    schedule({ events: [], tasks: [], settings: DEFAULT_SETTINGS })
      .then((res) => {
        if (!cancelled) {
          dispatch({ type: 'set-plan', blocks: res.blocks, warnings: res.warnings })
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Could not load the mock week.'
          dispatch({ type: 'set-status', status: 'error', error: message })
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  const progress =
    state.status === 'loading-allocate'
      ? 'Estimating time…'
      : state.status === 'loading-place'
        ? 'Placing tasks…'
        : null

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Gapfill</h1>
        <p className="lede">Plan a student week from a calendar and a to-do list.</p>
        <p className="hint">
          Upload, settings and tasks land in phase 2. This scaffold shows the mock week.
        </p>
        <button type="button" disabled>
          Plan my week
        </button>
        <Legend />
      </aside>
      <main className="main">
        {state.warnings.length > 0 && (
          <div className="banner warn">
            {state.warnings.map((w) => (
              <p key={w}>{w}</p>
            ))}
          </div>
        )}
        {state.error && <div className="banner error">{state.error}</div>}
        {progress && <div className="banner">{progress}</div>}
        {state.status === 'idle' && state.blocks.length === 0 && !progress && (
          <div className="banner">No plan yet.</div>
        )}
        <div className="calendar-wrap">
          <CalendarView blocks={state.blocks} />
        </div>
      </main>
    </div>
  )
}
