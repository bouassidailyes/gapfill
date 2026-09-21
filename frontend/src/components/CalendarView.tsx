import type { EventInput } from '@fullcalendar/core'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'
import type { Block } from '../types'
import { BLOCK_COLORS } from './Legend'

export function CalendarView({ blocks }: { blocks: Block[] }) {
  const events: EventInput[] = blocks.map((block) => ({
    id: block.id,
    title: block.title,
    start: block.start,
    end: block.end,
    backgroundColor: BLOCK_COLORS[block.type],
    borderColor: BLOCK_COLORS[block.type],
    allDay: block.start.endsWith('T00:00:00+02:00') && block.end.endsWith('T00:00:00+02:00'),
  }))

  return (
    <FullCalendar
      plugins={[timeGridPlugin, dayGridPlugin, interactionPlugin]}
      initialView="timeGridWeek"
      initialDate="2026-09-21"
      firstDay={1}
      slotMinTime="07:00:00"
      slotMaxTime="23:00:00"
      allDaySlot={true}
      nowIndicator={true}
      headerToolbar={{ left: 'prev,next today', center: 'title', right: 'timeGridWeek,dayGridMonth' }}
      height="100%"
      events={events}
    />
  )
}
