import type { Settings } from '../types'
import { Panel } from './Panel'

type Props = {
  settings: Settings
  onPatch: (patch: Partial<Settings>) => void
}

export function SettingsForm({ settings, onPatch }: Props) {
  const { meals, cooking } = settings

  return (
    <Panel label="Settings">
      <div className="field-row">
        <label>
          <div className="field-label">Day starts</div>
          <input
            type="time"
            value={settings.day_start}
            onChange={(e) => onPatch({ day_start: e.target.value })}
          />
        </label>
        <label>
          <div className="field-label">Day ends</div>
          <input
            type="time"
            value={settings.day_end}
            onChange={(e) => onPatch({ day_end: e.target.value })}
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          <div className="field-label">Lunch (min)</div>
          <input
            type="number"
            min={0}
            max={120}
            value={meals.lunch.minutes}
            onChange={(e) =>
              onPatch({
                meals: { ...meals, lunch: { ...meals.lunch, minutes: Number(e.target.value) } },
              })
            }
          />
        </label>
        <label>
          <div className="field-label">Dinner (min)</div>
          <input
            type="number"
            min={0}
            max={120}
            value={meals.dinner.minutes}
            onChange={(e) =>
              onPatch({
                meals: { ...meals, dinner: { ...meals.dinner, minutes: Number(e.target.value) } },
              })
            }
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          <div className="field-label">Cooking</div>
          <select
            value={cooking.mode}
            onChange={(e) =>
              onPatch({ cooking: { ...cooking, mode: e.target.value as Settings['cooking']['mode'] } })
            }
          >
            <option value="daily">Daily</option>
            <option value="batch">Batch</option>
            <option value="none">None</option>
          </select>
        </label>
        <label>
          <div className="field-label">Batches / week</div>
          <input
            type="number"
            min={1}
            max={7}
            value={cooking.batch_per_week}
            disabled={cooking.mode !== 'batch'}
            onChange={(e) =>
              onPatch({ cooking: { ...cooking, batch_per_week: Number(e.target.value) } })
            }
          />
        </label>
      </div>

      <div className="field-stack">
        <label>
          <div className="field-label">Travel between locations (min)</div>
          <input
            type="number"
            min={0}
            max={120}
            value={settings.transition_minutes}
            onChange={(e) => onPatch({ transition_minutes: Number(e.target.value) })}
          />
        </label>
      </div>

      <div className="field-row" style={{ marginBottom: 0 }}>
        <label>
          <div className="field-label">Lost time (%)</div>
          <input
            type="number"
            min={0}
            max={40}
            value={settings.lost_time_pct}
            onChange={(e) => onPatch({ lost_time_pct: Number(e.target.value) })}
          />
        </label>
        <label>
          <div className="field-label">Free time / day (min)</div>
          <input
            type="number"
            min={0}
            max={480}
            step={15}
            value={settings.free_time_min_per_day}
            onChange={(e) => onPatch({ free_time_min_per_day: Number(e.target.value) })}
          />
        </label>
      </div>
    </Panel>
  )
}
