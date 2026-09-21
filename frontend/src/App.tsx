import { useMemo, useReducer, useState } from 'react'
import { schedule } from './api'
import { BlockModal } from './components/BlockModal'
import { CalendarView } from './components/CalendarView'
import { CommuteForm } from './components/CommuteForm'
import { DownloadIcs } from './components/DownloadIcs'
import { Legend } from './components/Legend'
import { RecurringForm } from './components/RecurringForm'
import { ScheduleUpload } from './components/ScheduleUpload'
import { SettingsForm } from './components/SettingsForm'
import { TaskList } from './components/TaskList'
import { expandRecurring } from './recurring'
import { initialState, reducer } from './state'
import type { Block } from './types'

function Spinner() {
  return (
    <svg className="spinner" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden>
      <circle cx="6.5" cy="6.5" r="5" stroke="rgba(255,255,255,0.25)" strokeWidth="2" />
      <path d="M6.5 1.5a5 5 0 0 1 5 5" stroke="white" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [selected, setSelected] = useState<Block | null>(null)

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

  const selectedBlock =
    selected === null ? null : (state.blocks.find((b) => b.id === selected.id) ?? selected)

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-mark" aria-hidden>
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <rect x="2" y="2" width="4.5" height="4.5" rx="1" fill="white" />
                <rect x="8.5" y="2" width="4.5" height="4.5" rx="1" fill="white" opacity="0.5" />
                <rect x="2" y="8.5" width="4.5" height="4.5" rx="1" fill="white" opacity="0.5" />
                <rect x="8.5" y="8.5" width="4.5" height="4.5" rx="1" fill="white" opacity="0.8" />
              </svg>
            </div>
            <div>
              <div className="brand-name">Gapfill</div>
              <div className="brand-tag">WEEK PLANNER</div>
            </div>
          </div>
        </div>

        <div className="sidebar-scroll">
          <ScheduleUpload
            events={state.events}
            onEvents={(events) => dispatch({ type: 'set-events', events })}
          />
          <CommuteForm
            commute={state.commute}
            onPatch={(patch) => dispatch({ type: 'patch-commute', patch })}
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
            onAdd={(rule) =>
              dispatch({ type: 'add-recurring', rule: { ...rule, id: crypto.randomUUID() } })
            }
            onRemove={(id) => dispatch({ type: 'remove-recurring', id })}
          />
          <SettingsForm
            settings={state.settings}
            onPatch={(patch) => dispatch({ type: 'patch-settings', patch })}
          />
        </div>

        <div className="sidebar-footer">
          <button
            type="button"
            className="btn-primary"
            onClick={handlePlan}
            disabled={progress !== null || (state.tasks.length === 0 && allEvents.length === 0)}
          >
            {progress ? (
              <>
                <Spinner />
                {progress}
              </>
            ) : (
              '↗ Plan my week'
            )}
          </button>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <Legend />
          <DownloadIcs blocks={state.blocks} />
        </div>

        {state.warnings.length > 0 && (
          <div className="banner warn">
            {state.warnings.map((w) => (
              <p key={w}>{w}</p>
            ))}
          </div>
        )}
        {state.error && <div className="banner error">{state.error}</div>}
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
            onSelect={setSelected}
          />
        </div>
      </main>

      {selectedBlock && (
        <BlockModal
          block={selectedBlock}
          onClose={() => setSelected(null)}
          onRemove={(id) => {
            dispatch({ type: 'remove-block', id })
            setSelected(null)
          }}
          onToggleLock={(id) => {
            dispatch({ type: 'toggle-lock', id })
            setSelected(null)
          }}
        />
      )}
    </div>
  )
}
