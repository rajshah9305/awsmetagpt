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
      console.log('Loading initial data...')
      const [modelsData, rolesData] = await Promise.all([
        getModels(),
        getAgentRoles()
      ])
      
      console.log('Models data:', modelsData)
      console.log('Roles data:', rolesData)
      
      setModels(modelsData.models || [])
      setAgentRoles(rolesData.roles || [])
      
      // Set default active agents to all roles
      setFormData(prev => ({
        ...prev,
        active_agents: rolesData.roles?.map(role => role.id) || []
      }))
      
      console.log('Initial data loaded successfully')
    } catch (error) {
      console.error('Failed to load initial data:', error)
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
    <div className="min-h-screen py-16 mesh-gradient">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Header */}
          <div className="text-center mb-16">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, type: "spring" }}
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl shadow-glow mb-6"
            >
              <Bot className="w-8 h-8 text-white" />
            </motion.div>
            <h1 className="display-lg text-neutral-900 mb-4">
              Generate Your App
            </h1>
            <p className="body-xl text-neutral-600 max-w-2xl mx-auto">
              Describe your application idea and watch AI agents collaborate to build it.
            </p>
          </div>

          {/* Main Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* App Description */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="glass-card p-8">
                <h2 className="display-sm text-neutral-900 mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Code className="w-5 h-5 text-primary-600" />
                  </span>
                  Describe Your App
                </h2>
                <textarea
                  value={formData.requirement}
                  onChange={(e) => setFormData(prev => ({ ...prev, requirement: e.target.value }))}
                  placeholder="Describe your app idea in detail. What should it do? Who will use it? What features do you need?

Example: Create a task management app with user authentication, real-time updates, and team collaboration features."
                  className="input-glass w-full h-40 resize-none"
                  required
                />
              </div>
            </motion.div>

            {/* App Type Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <div className="glass-card p-8">
                <h2 className="display-sm text-neutral-900 mb-6 flex items-center gap-3">
                  <span className="w-8 h-8 bg-secondary-100 rounded-lg flex items-center justify-center">
                    <Settings className="w-5 h-5 text-secondary-600" />
                  </span>
                  Application Type
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {Object.entries(appTypeIcons).map(([type, Icon]) => {
                  const isSelected = formData.app_type === type
                  return (
                    <motion.button
                      key={type}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, app_type: type }))}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      className={`p-5 rounded-xl border-2 transition-all ${
                        isSelected
                          ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-glow'
                          : 'border-neutral-200 hover:border-primary-300 bg-white/50'
                      }`}
                    >
                      <Icon className={`h-8 w-8 mx-auto mb-3 ${
                        isSelected ? 'text-primary-600' : 'text-neutral-600'
                      }`} />
                      <div className={`body-sm font-semibold ${
                        isSelected ? 'text-primary-600' : 'text-neutral-700'
                      }`}>
                        {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                    </motion.button>
                  )
                })}
              </div>
              </div>
            </motion.div>

            {/* Agent Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="glass-card p-8">
              <h2 className="display-sm text-neutral-900 mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-success-600" />
                </span>
                Select AI Agents
              </h2>
              <p className="body-md text-neutral-600 mb-6">
                Choose which AI agents will collaborate on your project. Each agent brings specialized expertise.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {agentRoles.map((role) => {
                  const Icon = agentIcons[role.id] || Bot
                  const isSelected = formData.active_agents.includes(role.id)
                  
                  return (
                    <motion.button
                      key={role.id}
                      type="button"
                      onClick={() => toggleAgent(role.id)}
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      className={`p-5 rounded-xl border-2 text-left transition-all ${
                        isSelected
                          ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-md'
                          : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                      }`}
                    >
                      <div className="flex items-center space-x-3 mb-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          isSelected ? 'bg-primary-100' : 'bg-neutral-100'
                        }`}>
                          <Icon className={`h-5 w-5 ${isSelected ? 'text-primary-600' : 'text-neutral-600'}`} />
                        </div>
                        <span className={`label ${isSelected ? 'text-primary-900' : 'text-neutral-900'}`}>
                          {role.name}
                        </span>
                      </div>
                      <p className={`body-sm ${isSelected ? 'text-primary-700' : 'text-neutral-600'}`}>
                        {role.description}
                      </p>
                    </motion.button>
                  )
                })}
              </div>
              </div>
            </motion.div>

            {/* Advanced Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <div className="glass-card p-8">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center justify-between w-full text-left"
              >
                <h2 className="display-sm text-neutral-900">
                  Advanced Settings
                </h2>
                <Settings className={`h-6 w-6 text-neutral-500 transition-transform ${showAdvanced ? 'rotate-90' : ''}`} />
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
                    <label className="label mb-2">
                      Preferred AI Model
                    </label>
                    <select
                      value={formData.preferred_model}
                      onChange={(e) => setFormData(prev => ({ ...prev, preferred_model: e.target.value }))}
                      className="input-glass"
                    >
                      {models.map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name} - {model.provider}
                        </option>
                      ))}
                    </select>
                    <p className="caption mt-2">
                      Different models excel at different tasks. Nova Pro is recommended for most applications.
                    </p>
                  </div>

                  {/* Additional Requirements */}
                  <div>
                    <label className="label mb-2">
                      Additional Requirements
                    </label>
                    <textarea
                      value={formData.additional_requirements}
                      onChange={(e) => setFormData(prev => ({ ...prev, additional_requirements: e.target.value }))}
                      placeholder="Any specific requirements, constraints, or preferences..."
                      className="input-glass w-full h-24 resize-none"
                    />
                  </div>

                  {/* Tech Stack Preferences */}
                  <div>
                    <label className="label mb-2">
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
                      className="input-glass"
                    />
                  </div>
                </motion.div>
              )}
              </div>
            </motion.div>

            {/* Submit Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="flex justify-center"
            >
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="btn-primary body-lg px-12 py-5 shadow-glow-lg disabled:opacity-50 disabled:cursor-not-allowed relative"
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin h-6 w-6 mr-3 relative z-10" />
                    <span className="relative z-10 label">Starting Generation...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-6 w-6 mr-3 relative z-10" />
                    <span className="relative z-10 label">Generate My App</span>
                  </>
                )}
              </motion.button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </div>
  )
}

export default Generator