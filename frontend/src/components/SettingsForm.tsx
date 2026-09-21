import type { Settings } from '../types'

type Props = {
  settings: Settings
  onPatch: (patch: Partial<Settings>) => void
}

export function SettingsForm({ settings, onPatch }: Props) {
  const { meals, cooking } = settings

  return (
    <details className="panel" open>
      <summary>
        <h2>Settings</h2>
      </summary>

      <div className="field-row">
        <label>
          Day starts
          <input
            type="time"
            value={settings.day_start}
            onChange={(e) => onPatch({ day_start: e.target.value })}
          />
        </label>
        <label>
          Day ends
          <input
            type="time"
            value={settings.day_end}
            onChange={(e) => onPatch({ day_end: e.target.value })}
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          Lunch (min)
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
          Dinner (min)
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
          Cooking
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
        {cooking.mode === 'batch' && (
          <label>
            Batches / week
            <input
              type="number"
              min={1}
              max={7}
              value={cooking.batch_per_week}
              onChange={(e) =>
                onPatch({ cooking: { ...cooking, batch_per_week: Number(e.target.value) } })
              }
            />
          </label>
        )}
      </div>

      <div className="field-row">
        <label>
          Travel between locations (min)
          <input
            type="number"
            min={0}
            max={120}
            value={settings.transition_minutes}
            onChange={(e) => onPatch({ transition_minutes: Number(e.target.value) })}
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          Lost time (%)
          <input
            type="number"
            min={0}
            max={40}
            value={settings.lost_time_pct}
            onChange={(e) => onPatch({ lost_time_pct: Number(e.target.value) })}
          />
        </label>
        <label>
          Free time / day (min)
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
    </details>
  )
}
