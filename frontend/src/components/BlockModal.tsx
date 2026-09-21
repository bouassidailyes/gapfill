import type { Block } from '../types'
import { PALETTE } from './Legend'

type Props = {
  block: Block
  onClose: () => void
  onRemove: (id: string) => void
  onToggleLock: (id: string) => void
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

export function BlockModal({ block, onClose, onRemove, onToggleLock }: Props) {
  const palette = PALETTE[block.type]
  const minutes = Math.round((new Date(block.end).getTime() - new Date(block.start).getTime()) / 60_000)

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="block-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button type="button" className="modal-close" aria-label="Close" onClick={onClose}>
          ×
        </button>
        <div className="modal-kicker">
          <span className="swatch" style={{ background: palette.dot }} />
          {palette.label}
          {block.locked && <span style={{ marginLeft: 6, color: PALETTE.task.dot }}>· locked</span>}
        </div>
        <p id="block-modal-title" className="modal-title">
          {block.title}
        </p>
        <p className="modal-meta">
          {formatTime(block.start)} – {formatTime(block.end)} · {minutes} min
        </p>
        {block.location && <p className="modal-location">📍 {block.location}</p>}
        {block.type !== 'event' && (
          <div className="modal-actions">
            <button type="button" className="btn-danger" onClick={() => onRemove(block.id)}>
              Remove
            </button>
            <button
              type="button"
              className={block.locked ? 'btn-lock on' : 'btn-lock'}
              onClick={() => onToggleLock(block.id)}
            >
              {block.locked ? 'Unlock' : 'Lock slot'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
