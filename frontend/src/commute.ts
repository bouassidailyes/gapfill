/**
 * Kept in frontend state for now: the API contract (architecture.md §6) has no
 * home/transport fields yet. These move into Settings when the travel matrix
 * endpoint lands.
 */
export type TransportMode = 'bike' | 'walk' | 'transit' | 'car'

export type Commute = {
  home: string
  mode: TransportMode
}

/** Labels are ours; the comment is the Google Distance Matrix `mode` equivalent. */
export const TRANSPORT_MODES: { value: TransportMode; label: string }[] = [
  { value: 'bike', label: 'Bike' }, // bicycling
  { value: 'walk', label: 'Walking' }, // walking
  { value: 'transit', label: 'Public transport' }, // transit
  { value: 'car', label: 'Car' }, // driving
]

export const DEFAULT_COMMUTE: Commute = { home: '', mode: 'bike' }
