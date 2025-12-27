import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import {
  Play, Square, RotateCcw, ExternalLink, Download,
  Terminal, Globe, Code, FileText, Loader, AlertCircle,
  CheckCircle, Maximize2, Minimize2, Info
} from 'lucide-react'
import JSZip from 'jszip'
import toast from 'react-hot-toast'

import { healthCheck } from '../services/api'

// E2B Sandbox API functions
const createSandbox = async (generationId) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}/create`, {
    method: 'POST',
  })
  return response.json()
}

const writeFiles = async (generationId, artifacts) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}/files`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(artifacts),
  })
  return response.json()
}

const runApplication = async (generationId) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}/run`, {
    method: 'POST',
  })
  return response.json()
}

const stopApplication = async (generationId) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}/stop`, {
    method: 'POST',
  })
  return response.json()
}

const getLogs = async (generationId) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}/logs`)
  return response.json()
}

const cleanupSandbox = async (generationId) => {
  const response = await fetch(`/api/v1/e2b/sandbox/${generationId}`, {
    method: 'DELETE',
  })
  return response.json()
}

const E2BSandboxPreview = ({
  artifacts = [],
  generationId,
  onSandboxReady,
  onPreviewUpdate
}) => {
  const [sandboxReady, setSandboxReady] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [logs, setLogs] = useState([])
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('preview')
  const [isExpanded, setIsExpanded] = useState(false)
  const [filesCreated, setFilesCreated] = useState(false)
  const [e2bConfigured, setE2bConfigured] = useState(false)

  const iframeRef = useRef(null)
  const logsRef = useRef(null)

  // Auto-scroll logs
  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight
    }
  }, [logs])

  // Check E2B configuration on mount
  useEffect(() => {
    const checkConfiguration = async () => {
      try {
        const health = await healthCheck()
        setE2bConfigured(health.e2b_configured || false)
      } catch (err) {
        console.warn('Could not check E2B configuration:', err)
        setE2bConfigured(false)
      }
    }
    checkConfiguration()
  }, [])

  // Add log entry
  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${timestamp}] ${message}`])
  }

  // Initialize E2B sandbox
  const initializeSandbox = async () => {
    if (!e2bConfigured) {
      setError('E2B is not configured. Please set E2B_API_KEY in your environment.')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      addLog('🔧 Initializing E2B sandbox...')
      const result = await createSandbox(generationId)

      if (result.status === 'success') {
        setSandboxReady(true)
        addLog('✅ E2B sandbox initialized successfully')

        if (onSandboxReady) {
          onSandboxReady(generationId)
        }

        // Auto-write files if artifacts are available
        if (artifacts.length > 0) {
          await createFiles()
        }
      } else {
        throw new Error(result.detail || 'Failed to create sandbox')
      }
    } catch (err) {
      console.error('Failed to initialize E2B sandbox:', err)
      setError(`Failed to initialize sandbox: ${err.message}`)
      addLog(`❌ Sandbox initialization failed: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  // Create files from artifacts
  const createFiles = async () => {
    if (!sandboxReady || artifacts.length === 0) return

    setIsLoading(true)
    addLog('📁 Writing files to sandbox...')

    try {
      const result = await writeFiles(generationId, artifacts)

      if (result.status === 'success') {
        setFilesCreated(true)
        addLog(`✅ Successfully wrote ${artifacts.length} files to sandbox`)
      } else {
        throw new Error(result.detail || 'Failed to write files')
      }
    } catch (err) {
      console.error('Failed to write files:', err)
      setError(`Failed to write files: ${err.message}`)
      addLog(`❌ File creation failed: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  // Run the generated application
  const handleRunApplication = async () => {
    if (!sandboxReady || !filesCreated) return

    setIsRunning(true)
    setError(null)
    addLog('🚀 Starting application...')

    try {
      const result = await runApplication(generationId)

      if (result.status === 'success' && result.preview_url) {
        setPreviewUrl(result.preview_url)
        addLog(`✅ Application running at: ${result.preview_url}`)

        if (onPreviewUpdate) {
          onPreviewUpdate({ type: 'application', url: result.preview_url })
        }
      } else {
        throw new Error(result.detail || 'Failed to run application')
      }
    } catch (err) {
      console.error('Failed to run application:', err)
      setError(`Failed to run application: ${err.message}`)
      addLog(`❌ Application failed to start: ${err.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  // Stop the application
  const handleStopApplication = async () => {
    if (!sandboxReady) return

    setIsRunning(false)
    addLog('🛑 Stopping application...')

    try {
      const result = await stopApplication(generationId)

      if (result.status === 'success') {
        setPreviewUrl(null)
        addLog('✅ Application stopped successfully')
      } else {
        addLog('⚠️ Application may still be running')
      }
    } catch (err) {
      console.error('Failed to stop application:', err)
      addLog(`❌ Failed to stop application: ${err.message}`)
    }
  }

  // Restart the application
  const handleRestartApplication = async () => {
    await handleStopApplication()
    await new Promise(resolve => setTimeout(resolve, 2000))
    await handleRunApplication()
  }

  // Refresh logs
  const refreshLogs = async () => {
    if (!sandboxReady) return

    try {
      const result = await getLogs(generationId)
      if (result.status === 'success') {
        setLogs(result.logs.map(log => `[${new Date().toLocaleTimeString()}] ${log}`))
      }
    } catch (err) {
      console.error('Failed to refresh logs:', err)
    }
  }

  // Download generated files
  const downloadFiles = async () => {
    if (artifacts.length === 0) return

    addLog('📥 Preparing files for download...')

    try {
      const zip = new JSZip()

      artifacts.forEach((artifact) => {
        const filename = getFilenameFromArtifact(artifact)
        zip.file(filename, artifact.content)
      })

      const blob = await zip.generateAsync({ type: 'blob' })
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `generated-app-${generationId}.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      addLog('✅ Files downloaded successfully')
      toast.success('Files downloaded successfully')

    } catch (err) {
      console.error('Failed to download files:', err)
      addLog(`❌ Download failed: ${err.message}`)
      toast.error('Failed to download files')
    }
  }

  // Get appropriate filename from artifact
  const getFilenameFromArtifact = (artifact) => {
    const name = artifact.name.toLowerCase().replace(/\s+/g, '_')

    const extensionMap = {
      'product requirements document': 'requirements.md',
      'system architecture design': 'architecture.md',
      'project plan & timeline': 'project_plan.md',
      'technical implementation': 'implementation.md',
      'test strategy & cases': 'test_strategy.md',
      'deployment & infrastructure': 'deployment.md'
    }

    return extensionMap[artifact.name.toLowerCase()] || `${name}.md`
  }

  // Auto-initialize sandbox when artifacts are available
  useEffect(() => {
    if (artifacts.length > 0 && !sandboxReady && e2bConfigured) {
      initializeSandbox()
    }
  }, [artifacts, sandboxReady, e2bConfigured])

  if (!artifacts || artifacts.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="text-center">
          <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Artifacts Yet
          </h3>
          <p className="text-gray-600">
            Generated artifacts will appear here for live preview
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 transition-all duration-300 ${
      isExpanded ? 'fixed inset-4 z-50' : 'h-96'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">Live Preview</h3>
          </div>
          
          {sandbox && (
            <div className="flex items-center space-x-1 text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Sandbox Active</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Control Buttons */}
          {sandboxReady && (
            <>
              <button
                onClick={handleRunApplication}
                disabled={isLoading || isRunning || !filesCreated}
                className="btn-outline p-2"
                title="Run Application"
              >
                <Play className="h-4 w-4" />
              </button>

              <button
                onClick={handleStopApplication}
                disabled={isLoading || !isRunning}
                className="btn-outline p-2"
                title="Stop Application"
              >
                <Square className="h-4 w-4" />
              </button>

              <button
                onClick={handleRestartApplication}
                disabled={isLoading}
                className="btn-outline p-2"
                title="Restart Application"
              >
                <RotateCcw className="h-4 w-4" />
              </button>

              <button
                onClick={downloadFiles}
                disabled={artifacts.length === 0}
                className="btn-outline p-2"
                title="Download Files"
              >
                <Download className="h-4 w-4" />
              </button>
            </>
          )}
          
          {previewUrl && (
            <a
              href={previewUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-outline p-2"
              title="Open in New Tab"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="btn-outline p-2"
            title={isExpanded ? "Minimize" : "Maximize"}
          >
            {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border-b border-red-200">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">Error</span>
          </div>
          <p className="text-sm text-red-700 mt-1">{error}</p>
          
          {!sandbox && (
            <button
              onClick={initializeSandbox}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Retry Initialization
            </button>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200">
        {['preview', 'logs', 'files'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
              activeTab === tab
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab === 'preview' && <Globe className="h-4 w-4 inline mr-1" />}
            {tab === 'logs' && <Terminal className="h-4 w-4 inline mr-1" />}
            {tab === 'files' && <FileText className="h-4 w-4 inline mr-1" />}
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className={`${isExpanded ? 'h-full' : 'h-80'} overflow-hidden`}>
        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <div className="h-full">
            {isLoading && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <Loader className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                  <p className="text-gray-600">Initializing sandbox...</p>
                </div>
              </div>
            )}
            
            {previewUrl && !isLoading && (
              <iframe
                ref={iframeRef}
                src={previewUrl}
                className="w-full h-full border-0"
                title="Application Preview"
              />
            )}

            {!previewUrl && !isLoading && sandboxReady && filesCreated && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <Play className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    Ready to Preview
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Click the play button to start your application
                  </p>
                  <button
                    onClick={handleRunApplication}
                    disabled={isRunning}
                    className="btn-primary"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Start Application
                  </button>
                </div>
              </div>
            )}

            {!sandboxReady && !isLoading && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <Info className="h-12 w-12 text-blue-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 mb-2">
                    E2B Sandbox Required
                  </h4>
                  <p className="text-gray-600 mb-4">
                    Configure E2B API key to enable live previews
                  </p>
                  <button
                    onClick={initializeSandbox}
                    className="btn-primary"
                  >
                    Initialize Sandbox
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="h-full flex flex-col">
            <div className="p-2 border-b border-gray-200 flex justify-between items-center">
              <span className="text-sm text-gray-600">Sandbox Logs</span>
              <button
                onClick={refreshLogs}
                disabled={!sandboxReady}
                className="btn-outline p-1 text-xs"
                title="Refresh Logs"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
            </div>
            <div
              ref={logsRef}
              className="flex-1 p-4 bg-gray-900 text-green-400 font-mono text-sm overflow-y-auto"
            >
              {logs.length === 0 ? (
                <div className="text-gray-500">No logs yet...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Files Tab */}
        {activeTab === 'files' && (
          <div className="h-full p-4 overflow-y-auto">
            {!filesCreated ? (
              <div className="text-center text-gray-500 mt-8">
                <FileText className="h-8 w-8 mx-auto mb-2" />
                <p>Files not uploaded to sandbox yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {artifacts.map((artifact, index) => {
                  const filename = getFilenameFromArtifact(artifact)
                  return (
                    <div
                      key={index}
                      className="flex items-center space-x-2 p-3 rounded-lg border border-gray-200 hover:bg-gray-50"
                    >
                      <FileText className="h-4 w-4 text-gray-500" />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-gray-900">
                          {filename}
                        </span>
                        <p className="text-xs text-gray-500 truncate">
                          {artifact.name}
                        </p>
                      </div>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default E2BSandboxPreview