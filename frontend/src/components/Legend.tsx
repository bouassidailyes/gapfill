import type { Block } from '../types'

export type Palette = { bg: string; dot: string; text: string; label: string }

export const PALETTE: Record<Block['type'], Palette> = {
  event: { bg: 'rgba(148,163,184,0.12)', dot: '#94a3b8', text: '#cbd5e1', label: 'Event' },
  task: { bg: 'rgba(99,102,241,0.15)', dot: '#6366f1', text: '#a5b4fc', label: 'Task' },
  meal: { bg: 'rgba(251,191,36,0.12)', dot: '#f59e0b', text: '#fcd34d', label: 'Meal' },
  cook: { bg: 'rgba(249,115,22,0.12)', dot: '#f97316', text: '#fdba74', label: 'Cook' },
  travel: { bg: 'rgba(167,139,250,0.12)', dot: '#a78bfa', text: '#c4b5fd', label: 'Travel' },
  free: { bg: 'rgba(34,197,94,0.10)', dot: '#22c55e', text: '#86efac', label: 'Free' },
  slack: { bg: 'rgba(75,85,99,0.15)', dot: '#6b7280', text: '#9ca3af', label: 'Slack' },
}

export function Legend() {
  return (
    <ul className="legend">
      {(Object.keys(PALETTE) as Block['type'][]).map((type) => (
        <li key={type}>
          <span className="swatch" style={{ background: PALETTE[type].dot }} />
          {PALETTE[type].label}
        </li>
      ))}
    </ul>
  )
}
