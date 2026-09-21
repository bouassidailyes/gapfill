import type { Commute } from '../commute'
import { TRANSPORT_MODES } from '../commute'

type Props = {
  commute: Commute
  onPatch: (patch: Partial<Commute>) => void
}

export function CommuteForm({ commute, onPatch }: Props) {
  return (
    <section className="panel">
      <h2>Commute</h2>
      <label className="stacked">
        Home address
        <input
          type="text"
          value={commute.home}
          placeholder="Sint Servaasklooster 35, Maastricht"
          onChange={(e) => onPatch({ home: e.target.value })}
        />
      </label>
      <div className="mode-grid">
        {TRANSPORT_MODES.map((mode) => (
          <button
            key={mode.value}
            type="button"
            className={commute.mode === mode.value ? 'day on' : 'day'}
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
    </section>
  )
}
