import type { EventInput } from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import type { Block, Event, Settings } from '../types'
import { BLOCK_COLORS } from './Legend'

type Props = {
  blocks: Block[]
  previewEvents: Event[]
  settings: Settings
}

/** "08:00" -> "08:00:00"; anything malformed falls back so the grid still renders. */
function toSlotTime(value: string, fallback: string): string {
  return /^\d{2}:\d{2}$/.test(value) ? `${value}:00` : fallback
}

export function CalendarView({ blocks, previewEvents, settings }: Props) {
  // Always keep the uploaded timetable and weekly commitments visible.
  // Generated blocks (meals, tasks, free time) layer on top and never replace them.
  const fromInput: EventInput[] = previewEvents.map((event) => ({
    id: event.id,
    title: event.title,
    start: event.start,
    end: event.end,
    backgroundColor: BLOCK_COLORS.event,
    borderColor: BLOCK_COLORS.event,
    allDay: event.start.includes('T00:00:00'),
  }))
  const generated: EventInput[] = blocks
    .filter((block) => block.type !== 'event')
    .map((block) => ({
      id: block.id,
      title: block.title,
      start: block.start,
      end: block.end,
      backgroundColor: BLOCK_COLORS[block.type],
      borderColor: BLOCK_COLORS[block.type],
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
      slotLabelFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      eventTimeFormat={{ hour: '2-digit', minute: '2-digit', hour12: false }}
      headerToolbar={{
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridDay,timeGridWeek,dayGridMonth',
      }}
      height="100%"
      events={[...fromInput, ...generated]}
    />
  )
}
