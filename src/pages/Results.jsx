import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { 
  ArrowLeft, Download, CheckCircle, 
  Clock, AlertCircle, Loader, Bot, FileText,
  Code, FileCode, BookOpen, Settings
} from 'lucide-react'

import { getGenerationStatus, getGenerationArtifacts } from '../services/api'
import WebSocketService from '../services/websocket'
import ArtifactViewer from '../components/ArtifactViewer'
import E2BSandboxPreview from '../components/E2BSandboxPreview'

const Results = () => {
  const { generationId } = useParams()
  const [status, setStatus] = useState(null)
  const [artifacts, setArtifacts] = useState([])
  const [selectedArtifact, setSelectedArtifact] = useState(null)
  const [wsService] = useState(() => new WebSocketService())
  const [isLoading, setIsLoading] = useState(true)
  const [pollingInterval, setPollingInterval] = useState(null)

  const pollStatus = useCallback(async () => {
    try {
      const statusData = await getGenerationStatus(generationId)
      setStatus(statusData)
      
      if (statusData.status === 'completed') {
        const artifactsData = await getGenerationArtifacts(generationId)
        setArtifacts(artifactsData)
        
        if (artifactsData.length > 0 && !selectedArtifact) {
          setSelectedArtifact(artifactsData[0])
        }
        
        if (pollingInterval) {
          clearInterval(pollingInterval)
          setPollingInterval(null)
        }
      }
    } catch (error) {
      console.error('Error polling status:', error)
    }
  }, [generationId, selectedArtifact, pollingInterval])

  useEffect(() => {
    if (generationId) {
      initializeResults()
    }
    
    return () => {
      wsService.disconnect()
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [generationId])

  const initializeResults = async () => {
    try {
      const statusData = await getGenerationStatus(generationId)
      setStatus(statusData)
      
      if (statusData.status === 'completed') {
        const artifactsData = await getGenerationArtifacts(generationId)
        setArtifacts(artifactsData)
        if (artifactsData.length > 0) {
          setSelectedArtifact(artifactsData[0])
        }
      } else if (statusData.status === 'running' || statusData.status === 'started' || statusData.status === 'initializing') {
        await connectWebSocket()
        startPolling()
      }
      
    } catch (error) {
      toast.error('Failed to load generation results')
      console.error('Error loading results:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const startPolling = () => {
    const interval = setInterval(pollStatus, 2000)
    setPollingInterval(interval)
  }

  const connectWebSocket = async () => {
    try {
      await wsService.connect(generationId)
      wsService.on('progress', handleProgressUpdate)
      wsService.on('agent_update', handleAgentUpdate)
      wsService.on('artifact_update', handleArtifactUpdate)
      wsService.on('message', handleGenericMessage)
      wsService.on('error', handleWebSocketError)
      wsService.on('close', handleWebSocketClose)
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      startPolling()
    }
  }

  const handleProgressUpdate = (data) => {
    setStatus(prev => ({
      ...prev,
      status: data.status,
      progress: data.progress,
      message: data.message,
      current_agent: data.current_agent,
    }))
    if (data.status === 'completed') loadArtifacts()
  }

  const handleAgentUpdate = (data) => {
    setStatus(prev => ({
      ...prev,
      current_agent: data.agent_role,
      message: data.current_task || data.thinking || prev?.message
    }))
  }

  const handleArtifactUpdate = (data) => {
    const artifact = data.artifact
    setArtifacts(prev => {
      const existing = prev.find(a => a.name === artifact.name)
      if (existing) {
        return prev.map(a => a.name === artifact.name ? { ...a, ...artifact } : a)
      }
      return [...prev, artifact]
    })
    if (!selectedArtifact && artifact) setSelectedArtifact(artifact)
  }

  const handleGenericMessage = (data) => {
    if (typeof data === 'string') {
      try { data = JSON.parse(data) } catch { return }
    }
    switch (data.type) {
      case 'progress_update': handleProgressUpdate(data); break
      case 'agent_update': handleAgentUpdate(data); break
      case 'artifact_update': handleArtifactUpdate(data); break
      default: break
    }
  }

  const handleWebSocketError = () => {
    if (!pollingInterval) startPolling()
  }

  const handleWebSocketClose = () => {
    if (status && (status.status === 'running' || status.status === 'started') && !pollingInterval) {
      startPolling()
    }
  }

  const loadArtifacts = async () => {
    try {
      const artifactsData = await getGenerationArtifacts(generationId)
      setArtifacts(artifactsData)
      if (artifactsData.length > 0 && !selectedArtifact) {
        setSelectedArtifact(artifactsData[0])
      }
    } catch (error) {
      console.error('Failed to load artifacts:', error)
    }
  }

  const getArtifactIcon = (artifact) => {
    const name = artifact.name?.toLowerCase() || ''
    const type = artifact.type?.toLowerCase() || ''
    if (type === 'documentation' || name.endsWith('.md')) return BookOpen
    if (type === 'configuration' || name.endsWith('.json') || name.endsWith('.yaml')) return Settings
    if (name.endsWith('.py') || name.endsWith('.js') || name.endsWith('.ts')) return FileCode
    return FileText
  }

  const getStatusIcon = (s) => {
    switch (s) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-success-600" />
      case 'running':
      case 'started':
      case 'initializing': return <Loader className="h-5 w-5 text-primary-600 animate-spin" />
      case 'failed': return <AlertCircle className="h-5 w-5 text-error-600" />
      default: return <Clock className="h-5 w-5 text-neutral-500" />
    }
  }

  const getStatusColor = (s) => {
    switch (s) {
      case 'completed': return 'text-success-600 bg-success-50 border-success-200'
      case 'running':
      case 'started':
      case 'initializing': return 'text-primary-600 bg-primary-50 border-primary-200'
      case 'failed': return 'text-error-600 bg-error-50 border-error-200'
      default: return 'text-neutral-600 bg-neutral-100 border-neutral-200'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center mesh-gradient">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-glow">
            <Loader className="h-8 w-8 text-white animate-spin" />
          </div>
          <p className="body-lg text-neutral-600">Loading generation results...</p>
        </div>
      </div>
    )
  }

  // In-progress view
  if (status && (status.status === 'running' || status.status === 'started' || status.status === 'initializing')) {
    return (
      <div className="min-h-screen py-8 mesh-gradient">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <Link to="/generate" className="inline-flex items-center text-neutral-600 hover:text-neutral-900 mb-6 group">
              <ArrowLeft className="h-4 w-4 mr-2 group-hover:-translate-x-1 transition-transform" />
              Back to Generator
            </Link>

            <div className="flex items-center justify-between">
              <div>
                <h1 className="display-md text-neutral-900">AI Agents at Work</h1>
                <p className="body-md text-neutral-500 mt-1 font-mono">ID: {generationId}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 badge-glass px-3 py-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                  <span className="caption text-neutral-700 font-semibold">Live</span>
                </div>
                <div className="badge-primary">
                  {Math.round(status.progress || 0)}% Complete
                </div>
              </div>
            </div>
          </div>

          {/* Progress */}
          <div className="glass-card p-6 mb-8">
            <div className="flex justify-between body-sm mb-3">
              <span className="text-neutral-700 font-medium">
                {status.current_agent
                  ? `Agent: ${status.current_agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`
                  : 'Processing...'}
              </span>
              <span className="text-primary-600 font-semibold">{Math.round(status.progress || 0)}%</span>
            </div>
            <div className="progress-bar mb-3">
              <motion.div
                className="progress-fill"
                initial={{ width: 0 }}
                animate={{ width: `${status.progress || 0}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              />
            </div>
            {status.message && (
              <p className="body-sm text-neutral-600 text-center">{status.message}</p>
            )}
          </div>

          {/* Artifacts appearing in real-time */}
          {artifacts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h2 className="body-xl font-semibold text-neutral-900 mb-4">
                Generated Files ({artifacts.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {artifacts.map((artifact, index) => {
                  const Icon = getArtifactIcon(artifact)
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="glass-card p-4"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-9 h-9 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Icon className="h-5 w-5 text-primary-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="label text-neutral-900 truncate">{artifact.name}</p>
                          <p className="caption text-neutral-500">
                            {artifact.agent_role?.replace(/_/g, ' ')}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}

          <E2BSandboxPreview artifacts={artifacts} generationId={generationId} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 mesh-gradient">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link to="/generate" className="inline-flex items-center text-neutral-600 hover:text-neutral-900 mb-6 group">
            <ArrowLeft className="h-4 w-4 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to Generator
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="display-md text-neutral-900">Generation Results</h1>
              <p className="body-md text-neutral-500 mt-1 font-mono">ID: {generationId}</p>
            </div>

            {status && (
              <div className={`inline-flex items-center px-4 py-2 rounded-full border ${getStatusColor(status.status)}`}>
                {getStatusIcon(status.status)}
                <span className="ml-2 caption font-semibold capitalize">{status.status}</span>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        {artifacts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* E2B Live Preview */}
            <div className="lg:col-span-2">
              <E2BSandboxPreview artifacts={artifacts} generationId={generationId} />
            </div>

            {/* Artifacts Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              <div className="glass-card p-6">
                <h2 className="body-xl font-semibold text-neutral-900 mb-4">
                  Generated Files ({artifacts.length})
                </h2>
                <div className="space-y-2 max-h-80 overflow-y-auto custom-scrollbar">
                  {artifacts.map((artifact, index) => {
                    const Icon = getArtifactIcon(artifact)
                    const isSelected = selectedArtifact?.name === artifact.name
                    return (
                      <motion.button
                        key={index}
                        onClick={() => setSelectedArtifact(artifact)}
                        whileHover={{ x: 2 }}
                        className={`w-full text-left p-3 rounded-xl border-2 transition-all ${
                          isSelected
                            ? 'border-primary-400 bg-primary-50'
                            : 'border-neutral-200 hover:border-primary-300 hover:bg-neutral-50'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                            isSelected ? 'bg-primary-100' : 'bg-neutral-100'
                          }`}>
                            <Icon className={`h-4 w-4 ${isSelected ? 'text-primary-600' : 'text-neutral-500'}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`label truncate ${isSelected ? 'text-primary-900' : 'text-neutral-900'}`}>
                              {artifact.name}
                            </p>
                            <p className="caption text-neutral-500">
                              {artifact.agent_role?.replace(/_/g, ' ')}
                            </p>
                          </div>
                        </div>
                      </motion.button>
                    )
                  })}
                </div>

                <div className="mt-4 pt-4 border-t border-neutral-200">
                  <button className="btn-outline w-full">
                    <Download className="h-4 w-4 mr-2" />
                    Download All
                  </button>
                </div>
              </div>

              {/* Selected Artifact Viewer */}
              {selectedArtifact && (
                <motion.div
                  key={selectedArtifact.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <ArtifactViewer artifact={selectedArtifact} />
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="glass-card text-center py-16">
            <div className="w-20 h-20 bg-neutral-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Bot className="h-10 w-10 text-neutral-400" />
            </div>
            <h3 className="body-xl font-semibold text-neutral-900 mb-2">
              No Artifacts Generated Yet
            </h3>
            <p className="body-md text-neutral-600 mb-8">
              {status?.status === 'failed'
                ? 'The generation process encountered an error.'
                : 'Artifacts will appear here once the generation is complete.'
              }
            </p>
            <Link to="/generate" className="btn-primary">
              Start New Generation
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default Results
