class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.messageQueue = []
    this.isConnecting = false
    this.heartbeatInterval = null
    this.lastHeartbeat = null
  }

  connect(clientId) {
    if (this.isConnecting) {
      return Promise.resolve()
    }

    this.isConnecting = true
    
    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`
        
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.startHeartbeat()
          this.processMessageQueue()
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            // Handle heartbeat
            if (data.type === 'heartbeat') {
              this.lastHeartbeat = Date.now()
              return
            }
            
            // Handle different message types
            this.handleMessage(data)
            
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }
        
        this.ws.onclose = (event) => {
          this.isConnecting = false
          this.stopHeartbeat()
          this.notifyListeners('close', event)
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect(clientId)
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          this.notifyListeners('error', error)
          reject(error)
        }
        
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  attemptReconnect(clientId) {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    
    setTimeout(() => {
      this.connect(clientId).catch(() => {
        // Reconnection failed, will retry if attempts remain
      })
    }, delay)
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
    this.listeners.clear()
    this.messageQueue = []
    this.isConnecting = false
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(data)
      console.warn('WebSocket is not connected, message queued')
    }
  }

  // Enhanced message handling
  handleMessage(data) {
    // Route messages based on type
    switch (data.type) {
      case 'progress_update':
        this.notifyListeners('progress', data)
        break
      case 'agent_update':
        this.notifyListeners('agent_update', data)
        break
      case 'tool_call':
        this.notifyListeners('tool_call', data)
        break
      case 'conversation':
        this.notifyListeners('conversation', data)
        break
      case 'artifact_update':
        this.notifyListeners('artifact_update', data)
        break
      case 'streaming_content':
        this.notifyListeners('streaming_content', data)
        break
      case 'system_metrics':
        this.notifyListeners('system_metrics', data)
        break
      case 'error':
        this.notifyListeners('error', data)
        break
      default:
        this.notifyListeners('message', data)
    }
  }

  // Process queued messages when connection is restored
  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      this.send(message)
    }
  }

  // Heartbeat mechanism
  startHeartbeat() {
    this.lastHeartbeat = Date.now()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
        
        // Check if we've missed heartbeats
        if (Date.now() - this.lastHeartbeat > 30000) {
          console.warn('Heartbeat timeout, reconnecting...')
          this.ws.close()
        }
      }
    }, 10000) // Send ping every 10 seconds
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket listener:', error)
        }
      })
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

export default WebSocketService