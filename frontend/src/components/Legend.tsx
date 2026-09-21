import type { Block } from '../types'

export const BLOCK_COLORS: Record<Block['type'], string> = {
  event: '#64748b',
  task: '#2563eb',
  meal: '#ea580c',
  cook: '#b45309',
  travel: '#7c3aed',
  free: '#16a34a',
  slack: '#94a3b8',
}

const LABELS: Record<Block['type'], string> = {
  event: 'Event',
  task: 'Task',
  meal: 'Meal',
  cook: 'Cook',
  travel: 'Travel',
  free: 'Free',
  slack: 'Slack',
}

export function Legend() {
  return (
    <ul className="legend">
      {(Object.keys(BLOCK_COLORS) as Block['type'][]).map((type) => (
        <li key={type}>
          <span className="swatch" style={{ background: BLOCK_COLORS[type] }} />
          {LABELS[type]}
        </li>
      ))}
    </ul>
  )
}
