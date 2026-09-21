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

  return (
    <>
      <button
        type="button"
        className="secondary"
        onClick={handleClick}
        disabled={busy || blocks.length === 0}
      >
        {busy ? 'Preparing…' : 'Download .ics'}
      </button>
      {error && <p className="field-error">{error}</p>}
    </>
  )
}
