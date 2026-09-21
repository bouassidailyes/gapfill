import { useState } from 'react'
import { exportIcs } from '../api'
import type { Block } from '../types'

export function DownloadIcs({ blocks }: { blocks: Block[] }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleClick() {
    setBusy(true)
    setError(null)
    try {
      const blob = await exportIcs({ blocks, include_fixed: false })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'gapfill-plan.ics'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed.')
    } finally {
      setBusy(false)
    }
  }

  if (blocks.length === 0) return null

  return (
    <div>
      <button type="button" className="btn-toolbar" onClick={handleClick} disabled={busy}>
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden>
          <path
            d="M5.5 1v6.5M3 5l2.5 2.5L8 5M1 9.5h9"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        {busy ? 'Preparing…' : 'Download .ics'}
      </button>
      {error && <p className="field-error">{error}</p>}
    </div>
  )
}
