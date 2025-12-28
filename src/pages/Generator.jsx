import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { 
  Bot, Zap, Settings, Play, Loader, 
  Users, Code, Database, TestTube, Cloud, Briefcase 
} from 'lucide-react'

import { generateApp, getModels, getAgentRoles } from '../services/api'

const Generator = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    requirement: '',
    app_type: 'web_app',
    preferred_model: 'us.amazon.nova-pro-v1:0',
    active_agents: [],
    additional_requirements: '',
    tech_stack_preferences: []
  })
  
  const [models, setModels] = useState([])
  const [agentRoles, setAgentRoles] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const [modelsData, rolesData] = await Promise.all([
        getModels(),
        getAgentRoles()
      ])
      
      setModels(modelsData.models || [])
      setAgentRoles(rolesData.roles || [])
      
      // Set default active agents to all roles
      setFormData(prev => ({
        ...prev,
        active_agents: rolesData.roles?.map(role => role.id) || []
      }))
    } catch {
      toast.error('Failed to load initial data')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.requirement.trim()) {
      toast.error('Please describe your app idea')
      return
    }

    if (formData.active_agents.length === 0) {
      toast.error('Please select at least one agent')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await generateApp(formData)
      toast.success('Generation started! Redirecting to results...')
      navigate(`/results/${response.generation_id}`)
    } catch (error) {
      toast.error(error.message || 'Failed to start generation')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleAgent = (agentId) => {
    setFormData(prev => ({
      ...prev,
      active_agents: prev.active_agents.includes(agentId)
        ? prev.active_agents.filter(id => id !== agentId)
        : [...prev.active_agents, agentId]
    }))
  }

  const appTypeIcons = {
    web_app: Code,
    mobile_app: Bot,
    api_service: Database,
    desktop_app: Settings,
    cli_tool: Zap
  }

  const agentIcons = {
    product_manager: Briefcase,
    architect: Settings,
    project_manager: Users,
    engineer: Code,
    qa_engineer: TestTube,
    devops: Cloud
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-secondary-900 mb-4">
              Generate Your App
            </h1>
            <p className="text-lg text-secondary-600 max-w-2xl mx-auto">
              Describe your application idea and let our AI agents collaborate to build it for you.
            </p>
          </div>

          {/* Main Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* App Description */}
            <div className="card">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Describe Your App
              </h2>
              <textarea
                value={formData.requirement}
                onChange={(e) => setFormData(prev => ({ ...prev, requirement: e.target.value }))}
                placeholder="Describe your app idea in detail. What should it do? Who will use it? What features do you need?"
                className="textarea w-full h-32"
                required
              />
            </div>

            {/* App Type Selection */}
            <div className="card">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Application Type
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {Object.entries(appTypeIcons).map(([type, Icon]) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, app_type: type }))}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      formData.app_type === type
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-secondary-200 hover:border-secondary-300 text-secondary-600'
                    }`}
                  >
                    <Icon className="h-6 w-6 mx-auto mb-2" />
                    <div className="text-sm font-medium">
                      {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Agent Selection */}
            <div className="card">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">
                Select AI Agents
              </h2>
              <p className="text-secondary-600 mb-4">
                Choose which AI agents will collaborate on your project. Each agent brings specialized expertise.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {agentRoles.map((role) => {
                  const Icon = agentIcons[role.id] || Bot
                  const isSelected = formData.active_agents.includes(role.id)
                  
                  return (
                    <button
                      key={role.id}
                      type="button"
                      onClick={() => toggleAgent(role.id)}
                      className={`p-4 rounded-lg border-2 text-left transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-secondary-200 hover:border-secondary-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3 mb-2">
                        <Icon className={`h-5 w-5 ${isSelected ? 'text-primary-600' : 'text-secondary-500'}`} />
                        <span className={`font-medium ${isSelected ? 'text-primary-900' : 'text-secondary-900'}`}>
                          {role.name}
                        </span>
                      </div>
                      <p className={`text-sm ${isSelected ? 'text-primary-700' : 'text-secondary-600'}`}>
                        {role.description}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="card">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center justify-between w-full text-left"
              >
                <h2 className="text-xl font-semibold text-secondary-900">
                  Advanced Settings
                </h2>
                <Settings className={`h-5 w-5 text-secondary-500 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} />
              </button>
              
              {showAdvanced && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-6 space-y-6"
                >
                  {/* AI Model Selection */}
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Preferred AI Model
                    </label>
                    <select
                      value={formData.preferred_model}
                      onChange={(e) => setFormData(prev => ({ ...prev, preferred_model: e.target.value }))}
                      className="input"
                    >
                      {models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name} - {model.provider}
                        </option>
                      ))}
                    </select>
                    <p className="text-sm text-secondary-500 mt-1">
                      Different models excel at different tasks. Nova Pro is recommended for most applications.
                    </p>
                  </div>

                  {/* Additional Requirements */}
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Additional Requirements
                    </label>
                    <textarea
                      value={formData.additional_requirements}
                      onChange={(e) => setFormData(prev => ({ ...prev, additional_requirements: e.target.value }))}
                      placeholder="Any specific requirements, constraints, or preferences..."
                      className="textarea w-full h-24"
                    />
                  </div>

                  {/* Tech Stack Preferences */}
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      Technology Preferences (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={formData.tech_stack_preferences.join(', ')}
                      onChange={(e) => setFormData(prev => ({ 
                        ...prev, 
                        tech_stack_preferences: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                      }))}
                      placeholder="React, Node.js, PostgreSQL, MongoDB..."
                      className="input"
                    />
                  </div>
                </motion.div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-center">
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin h-5 w-5 mr-2" />
                    Starting Generation...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    Generate My App
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

export default Generator