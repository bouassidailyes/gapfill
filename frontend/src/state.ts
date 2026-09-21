import type { Commute } from './commute'
import { DEFAULT_COMMUTE } from './commute'
import type { RecurringRule } from './recurring'
import type { Block, Event, Settings, TaskInput } from './types'
import { DEFAULT_SETTINGS } from './types'

export type Status = 'idle' | 'loading-allocate' | 'loading-place' | 'error' | 'ready'

export type AppState = {
  events: Event[]
  tasks: TaskInput[]
  recurring: RecurringRule[]
  commute: Commute
  settings: Settings
  blocks: Block[]
  warnings: string[]
  status: Status
  error: string | null
}

export const initialState: AppState = {
  events: [],
  tasks: [],
  recurring: [],
  commute: DEFAULT_COMMUTE,
  settings: DEFAULT_SETTINGS,
  blocks: [],
  warnings: [],
  status: 'idle',
  error: null,
}

export type Action =
  | { type: 'set-events'; events: Event[] }
  | { type: 'set-tasks'; tasks: TaskInput[] }
  | { type: 'add-task'; task: TaskInput }
  | { type: 'remove-task'; id: string }
  | { type: 'add-recurring'; rule: RecurringRule }
  | { type: 'remove-recurring'; id: string }
  | { type: 'patch-commute'; patch: Partial<Commute> }
  | { type: 'set-settings'; settings: Settings }
  | { type: 'patch-settings'; patch: Partial<Settings> }
  | { type: 'set-status'; status: Status; error?: string | null }
  | { type: 'set-plan'; blocks: Block[]; warnings: string[] }
  | { type: 'remove-block'; id: string }
  | { type: 'toggle-lock'; id: string }

export function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'set-events':
      return { ...state, events: action.events }
    case 'set-tasks':
      return { ...state, tasks: action.tasks }
    case 'add-task':
      return { ...state, tasks: [...state.tasks, action.task] }
    case 'remove-task':
      return {
        ...state,
        tasks: state.tasks.filter((t) => t.id !== action.id),
        blocks: state.blocks.filter((b) => b.task_id !== action.id),
      }
    case 'add-recurring':
      return { ...state, recurring: [...state.recurring, action.rule] }
    case 'remove-recurring':
      return { ...state, recurring: state.recurring.filter((r) => r.id !== action.id) }
    case 'patch-commute':
      return { ...state, commute: { ...state.commute, ...action.patch } }
    case 'set-settings':
      return { ...state, settings: action.settings }
    case 'patch-settings':
      return { ...state, settings: { ...state.settings, ...action.patch } }
    case 'set-status':
      return { ...state, status: action.status, error: action.error ?? null }
    case 'set-plan':
      return {
        ...state,
        blocks: action.blocks,
        warnings: action.warnings,
        status: 'ready',
        error: null,
      }
    case 'remove-block':
      return { ...state, blocks: state.blocks.filter((b) => b.id !== action.id) }
    case 'toggle-lock':
      return {
        ...state,
        blocks: state.blocks.map((b) =>
          b.id === action.id ? { ...b, locked: !b.locked } : b,
        ),
      }
    default:
      return state
  }
}
