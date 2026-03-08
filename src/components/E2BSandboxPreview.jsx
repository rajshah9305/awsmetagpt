import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Globe, Code, Terminal, Info } from 'lucide-react'

import SandboxController from './sandbox/SandboxController'
import LogViewer from './sandbox/LogViewer'

const E2BSandboxPreview = ({ generationId, artifacts = [] }) => {
  const [activeTab, setActiveTab] = useState('control')
  const [sandboxStatus, setSandboxStatus] = useState('idle')

  const tabs = [
    { id: 'control', label: 'Control', icon: Code },
    { id: 'logs', label: 'Logs', icon: Terminal },
    { id: 'info', label: 'Info', icon: Info }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'control':
        return (
          <SandboxController
            generationId={generationId}
            artifacts={artifacts}
            onStatusChange={setSandboxStatus}
          />
        )
      case 'logs':
        return (
          <LogViewer
            generationId={generationId}
            isActive={activeTab === 'logs'}
          />
        )
      case 'info':
        return (
          <div className="glass-card p-6">
            <h3 className="body-lg font-semibold text-neutral-900 mb-6">Sandbox Information</h3>
            <div className="space-y-5">
              <div>
                <p className="caption text-neutral-500 mb-1">Generation ID</p>
                <code className="bg-neutral-100 px-3 py-1.5 rounded-lg body-sm font-mono text-neutral-800">{generationId}</code>
              </div>
              <div>
                <p className="caption text-neutral-500 mb-1">Artifacts</p>
                <p className="body-md text-neutral-700">{artifacts.length} files ready for deployment</p>
              </div>
              <div>
                <p className="caption text-neutral-500 mb-1">Status</p>
                <span className={`badge ${
                  sandboxStatus === 'running'
                    ? 'badge-success'
                    : sandboxStatus === 'ready' || sandboxStatus === 'files_ready'
                    ? 'badge-primary'
                    : sandboxStatus === 'error'
                    ? 'badge-error'
                    : 'bg-neutral-100 text-neutral-700 border border-neutral-200'
                }`}>
                  {sandboxStatus}
                </span>
              </div>
              <div>
                <p className="caption text-neutral-500 mb-2">Features</p>
                <ul className="space-y-2">
                  {[
                    'Isolated execution environment',
                    'Real-time log streaming',
                    'Automatic dependency installation',
                    'Live preview URL',
                    'Process management',
                  ].map(f => (
                    <li key={f} className="flex items-center body-sm text-neutral-600">
                      <div className="w-1.5 h-1.5 bg-primary-400 rounded-full mr-2 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-4">
      {/* Tab Navigation */}
      <div className="glass-card p-1 flex space-x-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          return (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`flex-1 inline-flex items-center justify-center py-2.5 px-4 rounded-xl body-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-primary-400 to-secondary-500 text-white shadow-glow'
                  : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'
              }`}
            >
              <Icon className={`mr-2 h-4 w-4 ${isActive ? 'text-white' : 'text-neutral-400'}`} />
              {tab.label}
            </motion.button>
          )
        })}
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="min-h-[400px]"
      >
        {renderTabContent()}
      </motion.div>

      {/* Running indicator */}
      {sandboxStatus === 'running' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card-primary p-4"
        >
          <div className="flex items-center">
            <div className="w-3 h-3 bg-success-500 rounded-full mr-3 animate-pulse" />
            <div>
              <p className="label text-success-700">Application is running</p>
              <p className="caption text-success-600">Your application is live and accessible via the preview URL.</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default E2BSandboxPreview
