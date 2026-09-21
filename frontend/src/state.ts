import type { Block, Event, Settings, TaskInput } from './types'
import { DEFAULT_SETTINGS } from './types'

export type Status = 'idle' | 'loading-allocate' | 'loading-place' | 'error' | 'ready'

export type AppState = {
  events: Event[]
  tasks: TaskInput[]
  settings: Settings
  blocks: Block[]
  warnings: string[]
  status: Status
  error: string | null
}

export const initialState: AppState = {
  events: [],
  tasks: [],
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
  | { type: 'set-settings'; settings: Settings }
  | { type: 'patch-settings'; patch: Partial<Settings> }
  | { type: 'set-status'; status: Status; error?: string | null }
  | { type: 'set-plan'; blocks: Block[]; warnings: string[] }

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
    default:
      return state
  }
}
