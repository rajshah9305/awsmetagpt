import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Terminal, Download, RotateCcw, Loader } from 'lucide-react'

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
        const allLogs = []
        result.processes.forEach(process => {
          process.output?.stdout?.forEach(line => {
            allLogs.push({ timestamp: new Date().toISOString(), source: process.command, message: line, type: 'stdout' })
          })
          process.output?.stderr?.forEach(line => {
            allLogs.push({ timestamp: new Date().toISOString(), source: process.command, message: line, type: 'stderr' })
          })
        })
        allLogs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        setLogs(allLogs)
      }
    } catch (error) {
      setLogs([{
        timestamp: new Date().toISOString(),
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
    intervalRef.current = setInterval(loadLogs, 2000)
  }

  const stopAutoRefresh = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const handleDownload = () => {
    const logText = logs.map(log =>
      `[${log.timestamp}] ${log.source}: ${log.message}`
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
      setAutoScroll(scrollTop + clientHeight >= scrollHeight - 10)
    }
  }

  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-neutral-200/60">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-neutral-900 rounded-lg flex items-center justify-center">
            <Terminal className="w-4 h-4 text-green-400" />
          </div>
          <h3 className="body-lg font-semibold text-neutral-900">Application Logs</h3>
          {isLoading && <Loader className="w-4 h-4 text-primary-600 animate-spin" />}
        </div>

        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-2 caption text-neutral-600 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Auto-scroll</span>
          </label>

          <button
            onClick={loadLogs}
            className="btn-ghost p-2 rounded-lg"
            title="Refresh logs"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={handleDownload}
            className="btn-ghost p-2 rounded-lg"
            title="Download logs"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Log output */}
      <div
        ref={logContainerRef}
        onScroll={handleScroll}
        className="h-96 overflow-y-auto bg-neutral-950 font-mono text-sm custom-scrollbar"
      >
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-neutral-500">
            {isLoading ? 'Loading logs...' : 'No logs available'}
          </div>
        ) : (
          <div className="p-4 space-y-0.5">
            {logs.map((log, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex text-xs leading-5"
              >
                <span className="text-neutral-600 mr-3 flex-shrink-0 select-none">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="text-primary-400 mr-3 flex-shrink-0 truncate max-w-[120px]">
                  [{log.source}]
                </span>
                <span className={log.type === 'stderr' ? 'text-error-400' : 'text-green-400'}>
                  {log.message}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {logs.length > 0 && (
        <div className="px-4 py-2 bg-neutral-900 border-t border-neutral-800 flex items-center justify-between">
          <span className="caption text-neutral-500">{logs.length} entries</span>
          {!autoScroll && (
            <button
              onClick={() => {
                setAutoScroll(true)
                if (logContainerRef.current) {
                  logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
                }
              }}
              className="caption text-primary-400 hover:text-primary-300"
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
