/**
 * SSE (Server-Sent Events) client — replaces WebSocket for Vercel serverless.
 * Provides the same event-listener interface the Results page expects.
 */
class SSEService {
  constructor() {
    this.es = null
    this.listeners = new Map()
  }

  /**
   * Open an SSE connection to /api/v1/generate/{id}/stream
   * Returns a promise that resolves once the connection is open.
   */
  connect(generationId) {
    return new Promise((resolve, reject) => {
      const url = `/api/v1/generate/${generationId}/stream`
      this.es = new EventSource(url)

      this.es.onopen = () => resolve()

      this.es.onerror = (err) => {
        // EventSource auto-reconnects on transient errors;
        // only reject on the very first connection failure.
        if (this.es.readyState === EventSource.CLOSED) {
          reject(new Error('SSE connection failed'))
        }
      }

      this.es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this._dispatch(data)
        } catch {
          // ignore malformed frames
        }
      }
    })
  }

  disconnect() {
    if (this.es) {
      this.es.close()
      this.es = null
    }
    this.listeners.clear()
  }

  on(event, callback) {
    if (!this.listeners.has(event)) this.listeners.set(event, [])
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    const cbs = this.listeners.get(event)
    if (!cbs) return
    const idx = cbs.indexOf(callback)
    if (idx > -1) cbs.splice(idx, 1)
  }

  isConnected() {
    return this.es?.readyState === EventSource.OPEN
  }

  // ── internal ──────────────────────────────────────────────────────────────

  _dispatch(data) {
    switch (data.type) {
      case 'progress_update':    this._notify('progress', data); break
      case 'agent_update':       this._notify('agent_update', data); break
      case 'artifact_update':    this._notify('artifact_update', data); break
      case 'streaming_content':  this._notify('streaming_content', data); break
      case 'error':              this._notify('error', data); break
      case 'stream_end':         this._notify('close', data); this.disconnect(); break
      default:                   this._notify('message', data)
    }
  }

  _notify(event, data) {
    this.listeners.get(event)?.forEach(cb => {
      try { cb(data) } catch (e) { console.error('SSE listener error:', e) }
    })
  }
}

export default SSEService
