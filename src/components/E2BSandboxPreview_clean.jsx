import React, { useState, useEffect } from 'react'
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

  const handleStatusChange = (status) => {
    setSandboxStatus(status)
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'control':
        return (
          <SandboxController
            generationId={generationId}
            artifacts={artifacts}
            onStatusChange={handleStatusChange}
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
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sandbox Information</h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Generation ID</h4>
                <code className="bg-gray-100 px-2 py-1 rounded text-sm">{generationId}</code>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Artifacts</h4>
                <p className="text-gray-600">{artifacts.length} files ready for deployment</p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Status</h4>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  sandboxStatus === 'running' 
                    ? 'bg-green-100 text-green-800'
                    : sandboxStatus === 'ready' || sandboxStatus === 'files_ready'
                    ? 'bg-blue-100 text-blue-800'
                    : sandboxStatus === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {sandboxStatus}
                </span>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Features</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Isolated execution environment</li>
                  <li>• Real-time log streaming</li>
                  <li>• Automatic dependency installation</li>
                  <li>• Live preview URL</li>
                  <li>• Process management</li>
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
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className={`mr-2 h-5 w-5 ${
                  activeTab === tab.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {renderTabContent()}
      </div>

      {/* Quick Actions */}
      {sandboxStatus === 'running' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <Globe className="w-5 h-5 text-green-500 mr-2" />
            <div>
              <h4 className="text-sm font-medium text-green-800">
                Application is running!
              </h4>
              <p className="text-sm text-green-700">
                Your application is live and accessible via the preview URL.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default E2BSandboxPreview