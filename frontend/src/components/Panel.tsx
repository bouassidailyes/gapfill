import { useState } from 'react'
import type { ReactNode } from 'react'

type Props = {
  label: string
  count?: number
  defaultOpen?: boolean
  children: ReactNode
}

export function Panel({ label, count, defaultOpen = true, children }: Props) {
  const [expanded, setExpanded] = useState(defaultOpen)

  return (
    <section className="panel">
      <button
        type="button"
        className="panel-toggle"
        aria-expanded={expanded}
        onClick={() => setExpanded((open) => !open)}
      >
        <span className="panel-label-row">
          <span className="panel-label">{label}</span>
          {count !== undefined && <span className="panel-count">{count}</span>}
        </span>
        <svg
          className={expanded ? 'panel-chevron open' : 'panel-chevron'}
          width="10"
          height="10"
          viewBox="0 0 10 10"
          fill="none"
          aria-hidden
        >
          <path
            d="M2 3.5l3 3 3-3"
            stroke="var(--fg3)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      {expanded && <div className="panel-body">{children}</div>}
    </section>
  )
}
