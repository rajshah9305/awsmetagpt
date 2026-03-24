import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Square, AlertCircle, CheckCircle, ExternalLink, Loader } from 'lucide-react'
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
    if (generationId) loadSandboxInfo()
  }, [generationId])

  const loadSandboxInfo = async () => {
    try {
      const info = await getSandboxInfo(generationId)
      setSandboxInfo(info)
      const state = info?.state || 'idle'
      setSandboxStatus(state)
      onStatusChange?.(state)
    } catch (error) {
      console.error('Failed to load sandbox info:', error)
    }
  }

  const handleCreateSandbox = async () => {
    setIsLoading(true)
    try {
      await createSandbox(generationId)
      setSandboxStatus('ready')
      toast.success('Sandbox created')
      await loadSandboxInfo()
    } catch (error) {
      toast.error('Failed to create sandbox')
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
        toast.success('Application started')
        await loadSandboxInfo()
      } else {
        toast.error('Failed to start application')
      }
    } catch (error) {
      toast.error('Failed to run application')
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
      }
    } catch (error) {
      toast.error('Failed to stop application')
    } finally {
      setIsLoading(false)
    }
  }

  const statusConfig = {
    idle: { label: 'Not created', color: 'text-neutral-500', bg: 'bg-neutral-100' },
    creating: { label: 'Creating...', color: 'text-primary-600', bg: 'bg-primary-50' },
    ready: { label: 'Ready', color: 'text-accent-600', bg: 'bg-accent-50' },
    files_ready: { label: 'Files written', color: 'text-accent-600', bg: 'bg-accent-50' },
    running: { label: 'Running', color: 'text-success-600', bg: 'bg-success-50' },
    stopped: { label: 'Stopped', color: 'text-neutral-600', bg: 'bg-neutral-100' },
    error: { label: 'Error', color: 'text-error-600', bg: 'bg-error-50' },
  }

  const current = statusConfig[sandboxStatus] || statusConfig.idle

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {sandboxStatus === 'running' ? (
            <CheckCircle className="w-5 h-5 text-success-600" />
          ) : sandboxStatus === 'error' ? (
            <AlertCircle className="w-5 h-5 text-error-600" />
          ) : isLoading ? (
            <Loader className="w-5 h-5 text-primary-600 animate-spin" />
          ) : (
            <div className={`w-5 h-5 rounded-full ${sandboxStatus === 'idle' ? 'bg-neutral-300' : 'bg-primary-400'}`} />
          )}
          <div>
            <h3 className="body-lg font-semibold text-neutral-900">Sandbox Control</h3>
            <span className={`caption font-medium ${current.color}`}>{current.label}</span>
          </div>
        </div>

        {sandboxInfo?.preview_url && (
          <a
            href={sandboxInfo.preview_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Open Preview
          </a>
        )}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
        <motion.button
          onClick={handleCreateSandbox}
          disabled={isLoading || sandboxStatus !== 'idle'}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-primary text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4 mr-1.5 flex-shrink-0" />
          Create
        </motion.button>

        <motion.button
          onClick={handleWriteFiles}
          disabled={isLoading || !['ready', 'stopped'].includes(sandboxStatus)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-outline text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Write Files
        </motion.button>

        <motion.button
          onClick={handleRunApplication}
          disabled={isLoading || !['files_ready', 'stopped'].includes(sandboxStatus)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-secondary text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4 mr-1.5 flex-shrink-0" />
          Run App
        </motion.button>

        <motion.button
          onClick={handleStopApplication}
          disabled={isLoading || sandboxStatus !== 'running'}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn text-sm py-2.5 bg-error-500 text-white hover:bg-error-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Square className="w-4 h-4 mr-1.5 flex-shrink-0" />
          Stop
        </motion.button>
      </div>

      {sandboxInfo && (
        <div className="mt-5 sm:mt-6 grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          {[
            { label: 'Project Type', value: sandboxInfo.project_type || 'Unknown' },
            { label: 'Files', value: sandboxInfo.file_count || 0 },
            { label: 'Processes', value: sandboxInfo.running_processes || 0 },
            { label: 'Created', value: sandboxInfo.created_at ? new Date(sandboxInfo.created_at).toLocaleTimeString() : 'N/A' },
          ].map(({ label, value }) => (
            <div key={label} className="bg-neutral-50 rounded-xl p-3">
              <p className="caption text-neutral-500 mb-1">{label}</p>
              <p className="label text-neutral-900">{value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SandboxController
