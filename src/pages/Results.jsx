import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  ArrowLeft, Download, CheckCircle,
  Clock, AlertCircle, Loader, Bot, FileText,
  FileCode, BookOpen, Settings
} from 'lucide-react'

import { getGenerationStatus, getGenerationArtifacts } from '../services/api'
import SSEService from '../services/sse'
import ArtifactViewer from '../components/ArtifactViewer'
import E2BSandboxPreview from '../components/E2BSandboxPreview'

// Skeleton for loading state
const ResultsSkeleton = () => (
  <div className="space-y-5">
    <div className="card p-7">
      <div className="flex items-center justify-between mb-5">
        <div className="skeleton h-4 w-32" />
        <div className="skeleton h-4 w-12" />
      </div>
      <div className="skeleton h-2 w-full rounded-full" />
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map(i => (
        <div key={i} className="card p-5 flex items-center gap-3">
          <div className="skeleton w-9 h-9 rounded-xl flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="skeleton h-3 w-3/4" />
            <div className="skeleton h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  </div>
)

const Results = () => {
  const { generationId } = useParams()
  const [status, setStatus] = useState(null)
  const [artifacts, setArtifacts] = useState([])
  const [selectedArtifact, setSelectedArtifact] = useState(null)
  const [sseService] = useState(() => new SSEService())
  const [isLoading, setIsLoading] = useState(true)
  const pollingIntervalRef = useRef(null)
  const [pollingInterval, setPollingInterval] = useState(null)

  const pollStatus = useCallback(async () => {
    try {
      const statusData = await getGenerationStatus(generationId)
      setStatus(statusData)
      if (statusData.status === 'completed') {
        const artifactsData = await getGenerationArtifacts(generationId)
        setArtifacts(artifactsData)
        if (artifactsData.length > 0 && !selectedArtifact) setSelectedArtifact(artifactsData[0])
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
          setPollingInterval(null)
        }
      }
    } catch (error) { console.error('Error polling status:', error) }
  }, [generationId, selectedArtifact])

  useEffect(() => {
    if (generationId) initializeResults()
    return () => {
      sseService.disconnect()
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current)
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
        if (artifactsData.length > 0) setSelectedArtifact(artifactsData[0])
      } else if (['running', 'started', 'initializing'].includes(statusData.status)) {
        await connectSSE()
        startPolling()
      }
    } catch (error) {
      toast.error('Failed to load generation results')
    } finally {
      setIsLoading(false)
    }
  }

  const startPolling = () => {
    if (pollingIntervalRef.current) return
    const interval = setInterval(pollStatus, 2000)
    pollingIntervalRef.current = interval
    setPollingInterval(interval)
  }

  const connectSSE = async () => {
    try {
      await sseService.connect(generationId)
      sseService.on('progress', handleProgressUpdate)
      sseService.on('agent_update', handleAgentUpdate)
      sseService.on('artifact_update', handleArtifactUpdate)
      sseService.on('message', handleGenericMessage)
      sseService.on('error', () => { if (!pollingIntervalRef.current) startPolling() })
      sseService.on('close', () => {
        if (status && ['running', 'started'].includes(status.status) && !pollingIntervalRef.current) startPolling()
      })
    } catch { startPolling() }
  }

  const handleProgressUpdate = (data) => {
    setStatus(prev => ({ ...prev, status: data.status, progress: data.progress, message: data.message, current_agent: data.current_agent }))
    if (data.status === 'completed') loadArtifacts()
  }

  const handleAgentUpdate = (data) => {
    setStatus(prev => ({ ...prev, current_agent: data.agent_role, message: data.current_task || data.thinking || prev?.message }))
  }

  const handleArtifactUpdate = (data) => {
    const artifact = data.artifact
    setArtifacts(prev => {
      const existing = prev.find(a => a.name === artifact.name)
      return existing ? prev.map(a => a.name === artifact.name ? { ...a, ...artifact } : a) : [...prev, artifact]
    })
    if (!selectedArtifact && artifact) setSelectedArtifact(artifact)
  }

  const handleGenericMessage = (data) => {
    if (typeof data === 'string') { try { data = JSON.parse(data) } catch { return } }
    switch (data.type) {
      case 'progress_update': handleProgressUpdate(data); break
      case 'agent_update': handleAgentUpdate(data); break
      case 'artifact_update': handleArtifactUpdate(data); break
      default: break
    }
  }

  const loadArtifacts = async () => {
    try {
      const artifactsData = await getGenerationArtifacts(generationId)
      setArtifacts(artifactsData)
      if (artifactsData.length > 0 && !selectedArtifact) setSelectedArtifact(artifactsData[0])
    } catch (error) { console.error('Failed to load artifacts:', error) }
  }

  const getArtifactIcon = (artifact) => {
    const name = artifact.name?.toLowerCase() || ''
    const type = artifact.type?.toLowerCase() || ''
    if (type === 'documentation' || name.endsWith('.md')) return BookOpen
    if (type === 'configuration' || name.endsWith('.json') || name.endsWith('.yaml')) return Settings
    if (name.endsWith('.py') || name.endsWith('.js') || name.endsWith('.ts')) return FileCode
    return FileText
  }

  const getStatusBadge = (s) => {
    const map = {
      completed:    'badge-success',
      running:      'badge-primary',
      started:      'badge-primary',
      initializing: 'badge-primary',
      failed:       'badge-error',
    }
    return map[s] || 'badge-neutral'
  }

  const getStatusIcon = (s) => {
    switch (s) {
      case 'completed':    return <CheckCircle className="h-3.5 w-3.5" />
      case 'running':
      case 'started':
      case 'initializing': return <Loader className="h-3.5 w-3.5 animate-spin" />
      case 'failed':       return <AlertCircle className="h-3.5 w-3.5" />
      default:             return <Clock className="h-3.5 w-3.5" />
    }
  }

  if (isLoading) return (
    <div className="min-h-screen bg-surface">
      <div className="bg-white border-b border-neutral-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 sm:py-6">
          <div className="flex items-center gap-3">
            <div className="skeleton h-4 w-12" />
            <div className="skeleton h-4 w-px" />
            <div className="skeleton h-4 w-48" />
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        <ResultsSkeleton />
      </div>
    </div>
  )

  const isRunning = status && ['running', 'started', 'initializing'].includes(status.status)

  return (
    <div className="min-h-screen bg-surface">
      {/* Page header */}
      <div className="bg-white border-b border-neutral-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 sm:py-6">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <Link
                to="/generate"
                className="flex items-center gap-1.5 text-sm text-neutral-400 hover:text-neutral-900 transition-colors flex-shrink-0"
              >
                <ArrowLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Back</span>
              </Link>
              <span className="text-neutral-200 hidden sm:inline">|</span>
              <div className="min-w-0">
                <h1 className="text-sm font-semibold text-neutral-900 truncate">
                  {isRunning ? 'Generation in Progress' : 'Generation Results'}
                </h1>
                <p className="text-xs text-neutral-400 font-mono truncate hidden sm:block">ID: {generationId}</p>
              </div>
            </div>
            {status && (
              <div className={`${getStatusBadge(status.status)} flex items-center gap-1.5 flex-shrink-0`}>
                {getStatusIcon(status.status)}
                <span className="capitalize">{status.status}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">

        {/* Progress bar when running */}
        <AnimatePresence>
          {isRunning && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="card p-6 sm:p-7 mb-7"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
                  <span className="text-sm font-medium text-neutral-700">
                    {status.current_agent
                      ? status.current_agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                      : 'Processing...'}
                  </span>
                </div>
                <span className="text-sm font-semibold text-primary-600 tabular-nums">
                  {Math.round(status.progress || 0)}%
                </span>
              </div>
              <div className="progress-bar mb-4">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${status.progress || 0}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                />
              </div>
              {status.message && (
                <p className="text-xs text-neutral-500 leading-relaxed">{status.message}</p>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Artifacts appearing in real-time */}
        <AnimatePresence>
          {isRunning && artifacts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-7"
            >
              <h2 className="text-sm font-semibold text-neutral-700 mb-4">
                Generated Files ({artifacts.length})
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {artifacts.map((artifact, index) => {
                  const Icon = getArtifactIcon(artifact)
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.97 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.04 }}
                      className="card p-4 flex items-center gap-3"
                    >
                      <div className="w-9 h-9 bg-primary-50 rounded-xl flex items-center justify-center flex-shrink-0">
                        <Icon className="h-4 w-4 text-primary-600" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-neutral-900 truncate">{artifact.name}</p>
                        <p className="text-xs text-neutral-400">{artifact.agent_role?.replace(/_/g, ' ')}</p>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {isRunning && <E2BSandboxPreview artifacts={artifacts} generationId={generationId} />}

        {/* Completed view */}
        {!isRunning && artifacts.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-7"
          >
            <div className="lg:col-span-2">
              <E2BSandboxPreview artifacts={artifacts} generationId={generationId} />
            </div>
            <div className="space-y-5">
              <div className="card p-6 sm:p-7">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-sm font-semibold text-neutral-900">Generated Files</h2>
                  <span className="badge-neutral">{artifacts.length}</span>
                </div>
                <div className="space-y-1.5 max-h-72 overflow-y-auto custom-scrollbar pr-1">
                  {artifacts.map((artifact, index) => {
                    const Icon = getArtifactIcon(artifact)
                    const isSelected = selectedArtifact?.name === artifact.name
                    return (
                      <button
                        key={index}
                        onClick={() => setSelectedArtifact(artifact)}
                        className={`w-full text-left p-3 rounded-2xl border transition-all duration-150 ${
                          isSelected
                            ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-400'
                            : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                        }`}
                      >
                        <div className="flex items-center gap-2.5">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-primary-100' : 'bg-neutral-100'}`}>
                            <Icon className={`h-3.5 w-3.5 ${isSelected ? 'text-primary-600' : 'text-neutral-500'}`} />
                          </div>
                          <div className="min-w-0">
                            <p className={`text-xs font-medium truncate ${isSelected ? 'text-primary-900' : 'text-neutral-900'}`}>
                              {artifact.name}
                            </p>
                            <p className="text-xs text-neutral-400">{artifact.agent_role?.replace(/_/g, ' ')}</p>
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
                <div className="mt-5 pt-5 border-t border-neutral-100">
                  <button className="btn-secondary w-full text-sm gap-2">
                    <Download className="h-3.5 w-3.5" />
                    Download All
                  </button>
                </div>
              </div>

              <AnimatePresence mode="wait">
                {selectedArtifact && (
                  <motion.div
                    key={selectedArtifact.name}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ArtifactViewer artifact={selectedArtifact} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* Empty state */}
        {!isRunning && artifacts.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card p-16 sm:p-24 text-center"
          >
            <div className="w-16 h-16 bg-neutral-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Bot className="h-8 w-8 text-neutral-400" />
            </div>
            <h3 className="text-base font-semibold text-neutral-900 mb-2.5">No Artifacts Yet</h3>
            <p className="text-sm text-neutral-500 mb-10 max-w-xs mx-auto leading-relaxed">
              {status?.status === 'failed'
                ? 'The generation process encountered an error.'
                : 'Artifacts will appear here once generation is complete.'}
            </p>
            <Link to="/generate" className="btn-primary text-sm">
              Start New Generation
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default Results
