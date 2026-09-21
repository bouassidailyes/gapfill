import type { EventContentArg, EventInput } from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import type { Block, Event, Settings } from '../types'
import { PALETTE } from './Legend'

type Props = {
  blocks: Block[]
  previewEvents: Event[]
  settings: Settings
  onSelect: (block: Block) => void
}

/** "08:00" -> "08:00:00"; anything malformed falls back so the grid still renders. */
function toSlotTime(value: string, fallback: string): string {
  return /^\d{2}:\d{2}$/.test(value) ? `${value}:00` : fallback
}

function toBlock(event: Event): Block {
  return {
    id: event.id,
    type: 'event',
    title: event.title,
    start: event.start,
    end: event.end,
    location: event.location,
  }
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function CalendarEvent({ info }: { info: EventContentArg }) {
  const block = info.event.extendedProps.block as Block
  const palette = PALETTE[block.type] ?? PALETTE.event
  const durationMin =
    (new Date(block.end).getTime() - new Date(block.start).getTime()) / 60_000
  const compact = durationMin <= 35

  return (
    <div
      className={compact ? 'fc-event-inner compact' : 'fc-event-inner'}
      style={{ background: palette.bg, borderLeft: `2px solid ${palette.dot}` }}
    >
      <span className="fc-event-title" style={{ color: palette.text }}>
        {block.locked ? '🔒 ' : ''}
        {block.title}
      </span>
      {!compact && (
        <span className="fc-event-time" style={{ color: palette.dot }}>
          {formatTime(block.start)}
        </span>
      )}
    </div>
  )
}

export function CalendarView({ blocks, previewEvents, settings, onSelect }: Props) {
  // Always keep the uploaded timetable and weekly commitments visible.
  // Generated blocks (meals, tasks, free time) layer on top and never replace them.
  const fromInput: EventInput[] = previewEvents.map((event) => {
    const block = toBlock(event)
    return {
      id: event.id,
      title: event.title,
      start: event.start,
      end: event.end,
      backgroundColor: 'transparent',
      borderColor: 'transparent',
      allDay: event.start.includes('T00:00:00'),
      extendedProps: { block },
    }
  })
  const generated: EventInput[] = blocks
    .filter((block) => block.type !== 'event')
    .map((block) => ({
      id: block.id,
      title: block.title,
      start: block.start,
      end: block.end,
      backgroundColor: 'transparent',
      borderColor: 'transparent',
      extendedProps: { block },
    }))

  return (
    <FullCalendar
      plugins={[timeGridPlugin, dayGridPlugin, interactionPlugin]}
      initialView="timeGridWeek"
      initialDate={settings.horizon_start}
      firstDay={1}
      slotMinTime={toSlotTime(settings.day_start, '07:00:00')}
      slotMaxTime={toSlotTime(settings.day_end, '23:00:00')}
      allDaySlot={true}
      nowIndicator={true}
      expandRows={true}
      eventDisplay="block"
      slotLabelInterval="01:00"
      slotLabelFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      eventTimeFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      headerToolbar={{
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridDay,timeGridWeek,dayGridMonth',
      }}
      height="100%"
      events={[...fromInput, ...generated]}
      eventContent={(info) => <CalendarEvent info={info} />}
      eventClick={(info) => {
        const block = info.event.extendedProps.block as Block | undefined
        if (block) onSelect(block)
      }}
    />
  )
}
