import type { Commute } from '../commute'
import { TRANSPORT_MODES } from '../commute'
import { Panel } from './Panel'

type Props = {
  commute: Commute
  onPatch: (patch: Partial<Commute>) => void
}

export function CommuteForm({ commute, onPatch }: Props) {
  return (
    <Panel label="Commute">
      <div className="field-label">Home address</div>
      <input
        type="text"
        value={commute.home}
        placeholder="Your home address"
        onChange={(e) => onPatch({ home: e.target.value })}
        style={{ marginBottom: 8 }}
      />
      <div className="mode-grid">
        {TRANSPORT_MODES.map((mode) => (
          <button
            key={mode.value}
            type="button"
            className={commute.mode === mode.value ? 'chip on' : 'chip'}
            aria-pressed={commute.mode === mode.value}
            onClick={() => onPatch({ mode: mode.value })}
          >
            {mode.label}
          </button>
        ))}
      </div>
      <p className="hint">
        Travel time to each lecture comes from your calendar’s locations once the schedule is
        connected.
      </p>
    </Panel>
  )
}
