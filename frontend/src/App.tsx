import { useMemo, useReducer } from 'react'
import { schedule } from './api'
import { CalendarView } from './components/CalendarView'
import { DownloadIcs } from './components/DownloadIcs'
import { Legend } from './components/Legend'
import { RecurringForm } from './components/RecurringForm'
import { ScheduleUpload } from './components/ScheduleUpload'
import { SettingsForm } from './components/SettingsForm'
import { TaskList } from './components/TaskList'
import { expandRecurring } from './recurring'
import { initialState, reducer } from './state'

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)

  const allEvents = useMemo(
    () => [
      ...state.events,
      ...expandRecurring(
        state.recurring,
        state.settings.horizon_start,
        state.settings.horizon_days,
      ),
    ],
    [state.events, state.recurring, state.settings.horizon_start, state.settings.horizon_days],
  )

  const progress =
    state.status === 'loading-allocate'
      ? 'Estimating time…'
      : state.status === 'loading-place'
        ? 'Placing tasks…'
        : null

  async function handlePlan() {
    dispatch({ type: 'set-status', status: 'loading-allocate' })
    const toPlacing = window.setTimeout(
      () => dispatch({ type: 'set-status', status: 'loading-place' }),
      400,
    )
    try {
      const res = await schedule({
        events: allEvents,
        tasks: state.tasks,
        settings: state.settings,
      })
      dispatch({ type: 'set-plan', blocks: res.blocks, warnings: res.warnings })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Scheduling failed.'
      dispatch({ type: 'set-status', status: 'error', error: message })
    } finally {
      window.clearTimeout(toPlacing)
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Gapfill</h1>
        <p className="lede">Plan a student week from a calendar and a to-do list.</p>

        <ScheduleUpload
          events={state.events}
          onEvents={(events) => dispatch({ type: 'set-events', events })}
        />

        <TaskList
          tasks={state.tasks}
          onAdd={(text, minutes) =>
            dispatch({
              type: 'add-task',
              task: { id: crypto.randomUUID(), text, estimated_minutes: minutes },
            })
          }
          onRemove={(id) => dispatch({ type: 'remove-task', id })}
        />

        <RecurringForm
          rules={state.recurring}
          onAdd={(rule) => dispatch({ type: 'add-recurring', rule: { ...rule, id: crypto.randomUUID() } })}
          onRemove={(id) => dispatch({ type: 'remove-recurring', id })}
        />

        <SettingsForm
          settings={state.settings}
          onPatch={(patch) => dispatch({ type: 'patch-settings', patch })}
        />

        <button
          type="button"
          className="primary"
          onClick={handlePlan}
          disabled={progress !== null || (state.tasks.length === 0 && allEvents.length === 0)}
        >
          {progress ?? 'Plan my week'}
        </button>

        <DownloadIcs blocks={state.blocks} />

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
        {state.blocks.length === 0 && !progress && !state.error && (
          <div className="banner">
            {allEvents.length > 0
              ? 'Showing your fixed commitments. Add tasks, then hit “Plan my week”.'
              : 'No plan yet. Add your tasks, check the settings, then hit “Plan my week”.'}
          </div>
        )}
        <div className="calendar-wrap">
          <CalendarView
            blocks={state.blocks}
            previewEvents={allEvents}
            settings={state.settings}
          />
        </div>
      </main>
    </div>
  )
}
