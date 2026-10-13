// The obligations pane's $.state contract. Self-contained: no imports.

/** One obligation as parsed from memory/obligations.yaml, plus the line its item starts on. */
export type ObligationRow = {
  obligation: string
  actor: string
  since: string
  check: string
  expires: string
  ref: string
  /** 1-based line of the item's "- " in the file: file order for ties, and the row key. */
  line: number
}

/** One live subagent or teammate as the footer lists it. */
export type PaneAgent = {
  id: string
  name: string
  /** Model id or alias as the spawn resolved it; '' when unknown. */
  model: string
  status: string
}

/** Everything the pane draws, gathered by one refresh. Rendering does no I/O. */
export type PaneSnapshot = {
  /** Absolute path of the obligations file this snapshot read (or looked for). */
  path: string
  source: 'ok' | 'missing' | 'error'
  /** For source 'error': what went wrong, with the line when known. */
  error: string
  items: ObligationRow[]
  /** urls/<name> -> URL, for every name the items cite that resolved. */
  urls: Record<string, string>
  /** Milliseconds since the epoch when the snapshot was taken. */
  now: number
  /** Local UTC offset in minutes east, for the header clock and "today". */
  offsetMinutes: number
  self: { name: string; model: string; tokens: number | null; window: number | null }
  agents: PaneAgent[]
}

declare module 'claude-code' {
  interface PluginState {
    'obligations-pane': {
      snapshot: PaneSnapshot | null
      /** Index of the first obligation shown (scroll position). */
      index: number
      /** agentId -> model, captured at agent.spawn (agent.list carries no model). */
      models: Record<string, string>
    }
  }
}
