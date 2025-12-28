import React, { useState, useEffect } from 'react'
import { Play, Square, RotateCcw, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

import { 
  createSandbox, 
  writeFiles, 
  runApplication, 
  stopApplication,
  getSandboxInfo 
} from '../../services/sandbox'

const SandboxController = ({ generationId, artifacts, onStatusChange }) => {
  const [sandboxStatus, setSandboxStatus] = useState('idle')
  const [sandboxInfo, setSandboxInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (generationId) {
      loadSandboxInfo()
    }
  }, [generationId])

  const loadSandboxInfo = async () => {
    try {
      const info = await getSandboxInfo(generationId)
      setSandboxInfo(info)
      setSandboxStatus(info?.state || 'idle')
      onStatusChange?.(info?.state || 'idle')
    } catch (error) {
      console.error('Failed to load sandbox info:', error)
    }
  }

  const handleCreateSandbox = async () => {
    setIsLoading(true)
    try {
      await createSandbox(generationId)
      setSandboxStatus('ready')
      toast.success('Sandbox created successfully')
      await loadSandboxInfo()
    } catch (error) {
      toast.error('Failed to create sandbox')
      console.error('Sandbox creation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleWriteFiles = async () => {
    if (!artifacts || artifacts.length === 0) {
      toast.error('No files to write')
      return
    }

    setIsLoading(true)
    try {
      const result = await writeFiles(generationId, artifacts)
      if (result.success) {
        toast.success(`Wrote ${result.files_written} files`)
        setSandboxStatus('files_ready')
        await loadSandboxInfo()
      } else {
        toast.error('Failed to write some files')
      }
    } catch (error) {
      toast.error('Failed to write files')
      console.error('File write error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRunApplication = async () => {
    setIsLoading(true)
    try {
      const result = await runApplication(generationId)
      if (result.success) {
        setSandboxStatus('running')
        toast.success('Application started successfully')
        await loadSandboxInfo()
      } else {
        toast.error('Failed to start application')
      }
    } catch (error) {
      toast.error('Failed to run application')
      console.error('Application run error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStopApplication = async () => {
    setIsLoading(true)
    try {
      const result = await stopApplication(generationId)
      if (result.success) {
        setSandboxStatus('stopped')
        toast.success('Application stopped')
        await loadSandboxInfo()
      } else {
        toast.error('Failed to stop application')
      }
    } catch (error) {
      toast.error('Failed to stop application')
      console.error('Application stop error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = () => {
    switch (sandboxStatus) {
      case 'running':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'ready':
      case 'files_ready':
        return <CheckCircle className="w-5 h-5 text-blue-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusText = () => {
    switch (sandboxStatus) {
      case 'idle':
        return 'Not created'
      case 'creating':
        return 'Creating...'
      case 'ready':
        return 'Ready'
      case 'files_ready':
        return 'Files written'
      case 'running':
        return 'Running'
      case 'stopped':
        return 'Stopped'
      case 'error':
        return 'Error'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Sandbox Control</h3>
            <p className="text-sm text-gray-500">Status: {getStatusText()}</p>
          </div>
        </div>
        
        {sandboxInfo?.preview_url && (
          <a
            href={sandboxInfo.preview_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Open Preview
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <button
          onClick={handleCreateSandbox}
          disabled={isLoading || sandboxStatus !== 'idle'}
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4 mr-2" />
          Create Sandbox
        </button>

        <button
          onClick={handleWriteFiles}
          disabled={isLoading || !['ready', 'stopped'].includes(sandboxStatus)}
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Write Files
        </button>

        <button
          onClick={handleRunApplication}
          disabled={isLoading || !['files_ready', 'stopped'].includes(sandboxStatus)}
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4 mr-2" />
          Run App
        </button>

        <button
          onClick={handleStopApplication}
          disabled={isLoading || sandboxStatus !== 'running'}
          className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Square className="w-4 h-4 mr-2" />
          Stop App
        </button>
      </div>

      {sandboxInfo && (
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Project Type:</span>
            <p className="font-medium">{sandboxInfo.project_type || 'Unknown'}</p>
          </div>
          <div>
            <span className="text-gray-500">Files:</span>
            <p className="font-medium">{sandboxInfo.file_count || 0}</p>
          </div>
          <div>
            <span className="text-gray-500">Processes:</span>
            <p className="font-medium">{sandboxInfo.running_processes || 0}</p>
          </div>
          <div>
            <span className="text-gray-500">Created:</span>
            <p className="font-medium">
              {sandboxInfo.created_at ? new Date(sandboxInfo.created_at).toLocaleTimeString() : 'N/A'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default SandboxController