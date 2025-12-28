import React, { useState, useEffect, useRef } from 'react'
import { Terminal, Download, RotateCcw } from 'lucide-react'

import { getSandboxLogs } from '../../services/sandbox'

const LogViewer = ({ generationId, isActive }) => {
  const [logs, setLogs] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const logContainerRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (isActive && generationId) {
      loadLogs()
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }

    return () => stopAutoRefresh()
  }, [isActive, generationId])

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const loadLogs = async () => {
    if (!generationId) return

    setIsLoading(true)
    try {
      const result = await getSandboxLogs(generationId)
      
      if (result.processes) {
        // Flatten logs from all processes
        const allLogs = []
        result.processes.forEach(process => {
          if (process.output) {
            // Add stdout logs
            process.output.stdout?.forEach(line => {
              allLogs.push({
                timestamp: new Date().toISOString(),
                level: 'info',
                source: process.command,
                message: line,
                type: 'stdout'
              })
            })
            
            // Add stderr logs
            process.output.stderr?.forEach(line => {
              allLogs.push({
                timestamp: new Date().toISOString(),
                level: 'error',
                source: process.command,
                message: line,
                type: 'stderr'
              })
            })
          }
        })
        
        // Sort by timestamp
        allLogs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        setLogs(allLogs)
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
      setLogs([{
        timestamp: new Date().toISOString(),
        level: 'error',
        source: 'system',
        message: `Failed to load logs: ${error.message}`,
        type: 'stderr'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const startAutoRefresh = () => {
    stopAutoRefresh()
    intervalRef.current = setInterval(loadLogs, 2000) // Refresh every 2 seconds
  }

  const stopAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const handleRefresh = () => {
    loadLogs()
  }

  const handleDownload = () => {
    const logText = logs.map(log => 
      `[${log.timestamp}] ${log.level.toUpperCase()} ${log.source}: ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sandbox-logs-${generationId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10
      setAutoScroll(isAtBottom)
    }
  }

  const getLogLineClass = (log) => {
    const baseClass = "font-mono text-sm py-1 px-3 border-l-2"
    
    switch (log.type) {
      case 'stderr':
        return `${baseClass} border-red-400 bg-red-50 text-red-800`
      case 'stdout':
        return `${baseClass} border-green-400 bg-green-50 text-green-800`
      default:
        return `${baseClass} border-gray-400 bg-gray-50 text-gray-800`
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">Application Logs</h3>
          {isLoading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Auto-scroll</span>
          </label>
          
          <button
            onClick={handleRefresh}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            title="Refresh logs"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleDownload}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            title="Download logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div 
        ref={logContainerRef}
        onScroll={handleScroll}
        className="h-96 overflow-y-auto bg-gray-900 text-green-400 font-mono text-sm"
      >
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            {isLoading ? 'Loading logs...' : 'No logs available'}
          </div>
        ) : (
          <div className="p-4 space-y-1">
            {logs.map((log, index) => (
              <div key={index} className="flex">
                <span className="text-gray-500 mr-3 flex-shrink-0">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="text-blue-400 mr-3 flex-shrink-0 min-w-0 truncate">
                  [{log.source}]
                </span>
                <span className={log.type === 'stderr' ? 'text-red-400' : 'text-green-400'}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {logs.length > 0 && (
        <div className="p-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">
          Showing {logs.length} log entries
          {!autoScroll && (
            <button
              onClick={() => {
                setAutoScroll(true)
                if (logContainerRef.current) {
                  logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
                }
              }}
              className="ml-3 text-blue-600 hover:text-blue-800"
            >
              Scroll to bottom
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default LogViewer