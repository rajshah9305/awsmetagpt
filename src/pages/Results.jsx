import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { 
  ArrowLeft, Download, CheckCircle, 
  Clock, AlertCircle, Loader, Bot, FileText
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

  // Polling function for status updates
  const pollStatus = useCallback(async () => {
    try {
      const statusData = await getGenerationStatus(generationId)
      setStatus(statusData)
      
      // Load artifacts if generation is completed
      if (statusData.status === 'completed') {
        const artifactsData = await getGenerationArtifacts(generationId)
        setArtifacts(artifactsData)
        
        // Auto-select first artifact if none selected
        if (artifactsData.length > 0 && !selectedArtifact) {
          setSelectedArtifact(artifactsData[0])
        }
        
        // Stop polling when completed
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
      // Load initial status
      const statusData = await getGenerationStatus(generationId)
      setStatus(statusData)
      
      // Load artifacts if generation is completed
      if (statusData.status === 'completed') {
        const artifactsData = await getGenerationArtifacts(generationId)
        setArtifacts(artifactsData)
        
        // Auto-select first artifact if none selected
        if (artifactsData.length > 0) {
          setSelectedArtifact(artifactsData[0])
        }
      } else if (statusData.status === 'running' || statusData.status === 'started') {
        // Start WebSocket connection for real-time updates
        await connectWebSocket()
        
        // Start polling as fallback
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
    // Poll every 2 seconds for status updates
    const interval = setInterval(pollStatus, 2000)
    setPollingInterval(interval)
  }

  const connectWebSocket = async () => {
    try {
      const clientId = generationId
      
      await wsService.connect(clientId)
      
      // Handle different message types
      wsService.on('progress', handleProgressUpdate)
      wsService.on('agent_update', handleAgentUpdate)
      wsService.on('artifact_update', handleArtifactUpdate)
      wsService.on('streaming_content', handleStreamingContent)
      wsService.on('message', handleGenericMessage)
      wsService.on('error', handleWebSocketError)
      wsService.on('close', handleWebSocketClose)
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      // Fallback to polling if WebSocket fails
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
      estimated_time: data.estimated_time
    }))
    
    // If completed, load artifacts
    if (data.status === 'completed') {
      loadArtifacts()
    }
  }

  const handleAgentUpdate = (data) => {
    // Update status with agent-specific information
    setStatus(prev => ({
      ...prev,
      current_agent: data.agent_role,
      message: data.current_task || data.thinking || prev?.message
    }))
  }

  const handleArtifactUpdate = (data) => {
    const artifact = data.artifact
    
    // Update or add artifact
    setArtifacts(prev => {
      const existing = prev.find(a => a.name === artifact.name)
      if (existing) {
        return prev.map(a => 
          a.name === artifact.name ? { ...a, ...artifact } : a
        )
      } else {
        return [...prev, artifact]
      }
    })
    
    // Auto-select first artifact if none selected
    if (!selectedArtifact && artifact) {
      setSelectedArtifact(artifact)
    }
  }

  const handleStreamingContent = (data) => {
    // Handle streaming content updates
    // This could be used to show real-time content generation
  }

  const handleGenericMessage = (data) => {
    
    // Handle different message formats
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data)
      } catch (e) {
        return
      }
    }
    
    // Route based on message type
    switch (data.type) {
      case 'progress_update':
        handleProgressUpdate(data)
        break
      case 'agent_update':
        handleAgentUpdate(data)
        break
      case 'artifact_update':
        handleArtifactUpdate(data)
        break
      case 'streaming_content':
        handleStreamingContent(data)
        break
      case 'connection':
        break
      case 'heartbeat':
        // Heartbeat received, connection is alive
        break
      default:
        break
    }
  }

  const handleWebSocketError = (error) => {
    console.error('WebSocket error:', error)
    toast.error('Real-time connection lost, using polling instead')
    
    // Start polling as fallback
    if (!pollingInterval) {
      startPolling()
    }
  }

  const handleWebSocketClose = () => {
    
    // Start polling as fallback if generation is still running
    if (status && (status.status === 'running' || status.status === 'started') && !pollingInterval) {
      startPolling()
    }
  }

  const loadArtifacts = async () => {
    try {
      const artifactsData = await getGenerationArtifacts(generationId)
      setArtifacts(artifactsData)
      
      // Auto-select first artifact if none selected
      if (artifactsData.length > 0 && !selectedArtifact) {
        setSelectedArtifact(artifactsData[0])
      }
    } catch (error) {
      console.error('Failed to load artifacts:', error)
    }
  }

  const handleSandboxReady = (sandbox) => {
    // Sandbox ready
  }

  const handlePreviewUpdate = (info) => {
    toast.success(`Live preview ready: ${info.type} application`)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-600" />
      case 'running':
      case 'started':
        return <Loader className="h-5 w-5 text-primary-600 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-error-600" />
      default:
        return <Clock className="h-5 w-5 text-secondary-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-success-600 bg-success-50 border-success-200'
      case 'running':
      case 'started':
        return 'text-primary-600 bg-primary-50 border-primary-200'
      case 'failed':
        return 'text-error-600 bg-error-50 border-error-200'
      default:
        return 'text-secondary-600 bg-secondary-50 border-secondary-200'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-secondary-600">Loading generation results...</p>
        </div>
      </div>
    )
  }

  // Show progress while generation is in progress
  if (status && (status.status === 'running' || status.status === 'started')) {
    return (
      <div className="min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <Link 
              to="/generate" 
              className="inline-flex items-center text-secondary-600 hover:text-secondary-900 mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Generator
            </Link>
            
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-secondary-900">
                  AI Agents at Work
                </h1>
                <p className="text-secondary-600 mt-1">
                  Generation ID: {generationId}
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-sm text-secondary-600">Live</span>
                </div>
                <div className="text-sm text-secondary-600">
                  {Math.round(status.progress || 0)}% Complete
                </div>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${status.progress || 0}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              />
            </div>
            {status.message && (
              <p className="text-secondary-700 mt-2 text-center">{status.message}</p>
            )}
            {status.current_agent && (
              <p className="text-primary-600 mt-1 text-center text-sm">
                Current Agent: {status.current_agent.replace('_', ' ').toUpperCase()}
              </p>
            )}
          </div>

          {/* Show artifacts as they become available */}
          {artifacts.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Generated Artifacts ({artifacts.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {artifacts.map((artifact, index) => (
                  <div key={index} className="card p-4">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-primary-500" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-secondary-900 truncate">
                          {artifact.name}
                        </p>
                        <p className="text-sm text-secondary-600">
                          {artifact.agent_role?.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* E2B Sandbox Preview */}
          <E2BSandboxPreview
            artifacts={artifacts}
            generationId={generationId}
            onSandboxReady={handleSandboxReady}
            onPreviewUpdate={handlePreviewUpdate}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link 
            to="/generate" 
            className="inline-flex items-center text-secondary-600 hover:text-secondary-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Generator
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">
                Generation Results
              </h1>
              <p className="text-secondary-600 mt-1">
                Generation ID: {generationId}
              </p>
            </div>
            
            {status && (
              <div className={`inline-flex items-center px-3 py-1 rounded-full border ${getStatusColor(status.status)}`}>
                {getStatusIcon(status.status)}
                <span className="ml-2 text-sm font-medium capitalize">
                  {status.status}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        {artifacts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* E2B Live Preview - Main Content */}
            <div className="lg:col-span-2">
              <E2BSandboxPreview
                artifacts={artifacts}
                generationId={generationId}
                onSandboxReady={handleSandboxReady}
                onPreviewUpdate={handlePreviewUpdate}
              />
            </div>

            {/* Artifacts List */}
            <div className="lg:col-span-1">
              <div className="card">
                <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                  Generated Artifacts ({artifacts.length})
                </h2>
                <div className="space-y-2">
                  {artifacts.map((artifact, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedArtifact(artifact)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedArtifact?.name === artifact.name
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-secondary-200 hover:border-secondary-300 hover:bg-secondary-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-secondary-500" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-secondary-900 truncate">
                            {artifact.name}
                          </p>
                          <p className="text-sm text-secondary-600">
                            {artifact.agent_role?.replace('_', ' ')}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
                
                {artifacts.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-secondary-200">
                    <button className="btn-outline w-full">
                      <Download className="h-4 w-4 mr-2" />
                      Download All
                    </button>
                  </div>
                )}
              </div>

              {/* Selected Artifact Viewer */}
              {selectedArtifact && (
                <div className="mt-6">
                  <ArtifactViewer artifact={selectedArtifact} />
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="card text-center py-12">
            <Bot className="h-16 w-16 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              No Artifacts Generated Yet
            </h3>
            <p className="text-secondary-600 mb-6">
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