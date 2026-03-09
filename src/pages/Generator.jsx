import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Bot, Zap, Settings, Play, Loader,
  Users, Code, Database, TestTube, Cloud, Briefcase,
  ChevronDown, AlertCircle
} from 'lucide-react'

import { generateApp, getModels, getAgentRoles } from '../services/api'
import AnimatedBackground from '../components/AnimatedBackground'

const AGENT_ICONS = {
  product_manager: Briefcase,
  architect: Settings,
  project_manager: Users,
  engineer: Code,
  qa_engineer: TestTube,
  devops: Cloud,
}

const APP_TYPE_ICONS = {
  web_app: Code,
  mobile_app: Bot,
  api_service: Database,
  desktop_app: Settings,
  cli_tool: Zap,
}

// Provider colour tokens — no purple
const PROVIDER_STYLES = {
  Amazon:    { border: 'border-accent-400',    bg: 'bg-accent-50',    text: 'text-accent-700',    badge: 'bg-accent-100 text-accent-700' },
  Meta:      { border: 'border-secondary-400', bg: 'bg-secondary-50', text: 'text-secondary-700', badge: 'bg-secondary-100 text-secondary-700' },
  Anthropic: { border: 'border-primary-400',   bg: 'bg-primary-50',   text: 'text-primary-700',   badge: 'bg-primary-100 text-primary-700' },
}
const DEFAULT_PROVIDER_STYLE = PROVIDER_STYLES.Amazon

const Generator = () => {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    requirement: '',
    app_type: 'web_app',
    preferred_model: '',
    active_agents: [],
    additional_requirements: '',
    tech_stack_preferences: [],
  })

  const [models, setModels] = useState([])
  const [agentRoles, setAgentRoles] = useState([])
  const [loadError, setLoadError] = useState(null)
  const [isLoadingData, setIsLoadingData] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setIsLoadingData(true)
    setLoadError(null)
    try {
      const [modelsData, rolesData] = await Promise.all([
        getModels(),
        getAgentRoles(),
      ])

      const fetchedModels = modelsData.models ?? []
      const fetchedRoles = rolesData.roles ?? []

      if (!fetchedModels.length) throw new Error('No models returned from server')
      if (!fetchedRoles.length) throw new Error('No agent roles returned from server')

      setModels(fetchedModels)
      setAgentRoles(fetchedRoles)
      setFormData(prev => ({
        ...prev,
        preferred_model: fetchedModels[0].id,
        active_agents: fetchedRoles.map(r => r.id),
      }))
    } catch (err) {
      setLoadError(err.message || 'Failed to load configuration from server')
    } finally {
      setIsLoadingData(false)
    }
  }

  const toggleAgent = (agentId) => {
    setFormData(prev => ({
      ...prev,
      active_agents: prev.active_agents.includes(agentId)
        ? prev.active_agents.filter(id => id !== agentId)
        : [...prev.active_agents, agentId],
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.requirement.trim()) {
      toast.error('Please describe your app idea')
      return
    }
    if (!formData.preferred_model) {
      toast.error('Please select an AI model')
      return
    }
    if (formData.active_agents.length === 0) {
      toast.error('Please select at least one agent')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await generateApp(formData)
      toast.success('Generation started')
      navigate(`/results/${response.generation_id}`)
    } catch (err) {
      toast.error(err.message || 'Failed to start generation')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoadingData) {
    return (
      <AnimatedBackground variant="dots">
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <Loader className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-4" />
            <p className="body-md text-neutral-600">Loading configuration...</p>
          </div>
        </div>
      </AnimatedBackground>
    )
  }

  if (loadError) {
    return (
      <AnimatedBackground variant="dots">
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="glass-card p-8 max-w-md w-full text-center">
            <div className="w-14 h-14 bg-error-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-7 w-7 text-error-600" />
            </div>
            <h2 className="text-xl font-display font-semibold text-neutral-900 mb-2">
              Could not load configuration
            </h2>
            <p className="body-sm text-neutral-600 mb-6">{loadError}</p>
            <button onClick={loadInitialData} className="btn-primary">
              Retry
            </button>
          </div>
        </div>
      </AnimatedBackground>
    )
  }

  const modelsByProvider = models.reduce((acc, model) => {
    if (!acc[model.provider]) acc[model.provider] = []
    acc[model.provider].push(model)
    return acc
  }, {})

  return (
    <AnimatedBackground variant="dots">
      <div className="py-12 sm:py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Header */}
            <div className="text-center mb-10 sm:mb-16">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, type: 'spring' }}
                className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl shadow-glow mb-5 sm:mb-6"
              >
                <Bot className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
              </motion.div>
              <h1 className="display-md sm:display-lg text-neutral-900 mb-3 sm:mb-4">
                Generate Your App
              </h1>
              <p className="body-lg sm:body-xl text-neutral-600 max-w-2xl mx-auto">
                Describe your application idea and watch AI agents collaborate to build it.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-8">

              {/* App Description */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="glass-card p-5 sm:p-8">
                  <h2 className="text-lg sm:text-xl font-display font-semibold text-neutral-900 mb-4 sm:mb-6 flex items-center gap-3">
                    <span className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Code className="w-4 h-4 sm:w-5 sm:h-5 text-primary-600" />
                    </span>
                    Describe Your App
                  </h2>
                  <textarea
                    value={formData.requirement}
                    onChange={(e) => setFormData(prev => ({ ...prev, requirement: e.target.value }))}
                    placeholder={`Describe your app idea in detail. What should it do? Who will use it? What features do you need?\n\nExample: Create a task management app with user authentication, real-time updates, and team collaboration features.`}
                    className="input-glass w-full h-36 sm:h-40 resize-none"
                    required
                  />
                </div>
              </motion.div>

              {/* App Type */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <div className="glass-card p-5 sm:p-8">
                  <h2 className="text-lg sm:text-xl font-display font-semibold text-neutral-900 mb-4 sm:mb-6 flex items-center gap-3">
                    <span className="w-8 h-8 bg-secondary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Settings className="w-4 h-4 sm:w-5 sm:h-5 text-secondary-600" />
                    </span>
                    Application Type
                  </h2>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
                    {Object.entries(APP_TYPE_ICONS).map(([type, Icon]) => {
                      const isSelected = formData.app_type === type
                      return (
                        <motion.button
                          key={type}
                          type="button"
                          onClick={() => setFormData(prev => ({ ...prev, app_type: type }))}
                          whileHover={{ scale: 1.03, y: -2 }}
                          whileTap={{ scale: 0.97 }}
                          className={`p-3 sm:p-5 rounded-xl border-2 transition-all ${
                            isSelected
                              ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-glow'
                              : 'border-neutral-200 hover:border-primary-300 bg-white/50'
                          }`}
                        >
                          <Icon className={`h-6 w-6 sm:h-8 sm:w-8 mx-auto mb-2 sm:mb-3 ${
                            isSelected ? 'text-primary-600' : 'text-neutral-600'
                          }`} />
                          <div className={`text-xs sm:text-sm font-semibold leading-tight ${
                            isSelected ? 'text-primary-600' : 'text-neutral-700'
                          }`}>
                            {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              </motion.div>

              {/* AI Model Selection */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <div className="glass-card p-5 sm:p-8">
                  <h2 className="text-lg sm:text-xl font-display font-semibold text-neutral-900 mb-4 sm:mb-6 flex items-center gap-3">
                    <span className="w-8 h-8 bg-accent-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-accent-600" />
                    </span>
                    AI Model
                  </h2>
                  <div className="space-y-5">
                    {Object.entries(modelsByProvider).map(([provider, providerModels]) => {
                      const style = PROVIDER_STYLES[provider] ?? DEFAULT_PROVIDER_STYLE
                      return (
                        <div key={provider}>
                          <p className="caption text-neutral-500 mb-2">{provider}</p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {providerModels.map((model) => {
                              const isSelected = formData.preferred_model === model.id
                              return (
                                <motion.button
                                  key={model.id}
                                  type="button"
                                  onClick={() => setFormData(prev => ({ ...prev, preferred_model: model.id }))}
                                  whileHover={{ scale: 1.02, y: -1 }}
                                  whileTap={{ scale: 0.98 }}
                                  className={`p-3 sm:p-4 rounded-xl border-2 text-left transition-all ${
                                    isSelected
                                      ? `${style.border} ${style.bg} shadow-md`
                                      : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                                  }`}
                                >
                                  <div className="flex items-center justify-between">
                                    <span className={`text-sm font-semibold ${isSelected ? style.text : 'text-neutral-900'}`}>
                                      {model.name}
                                    </span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                      isSelected ? style.badge : 'bg-neutral-100 text-neutral-500'
                                    }`}>
                                      {provider}
                                    </span>
                                  </div>
                                </motion.button>
                              )
                            })}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </motion.div>

              {/* Agent Selection */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                <div className="glass-card p-5 sm:p-8">
                  <div className="flex items-center justify-between mb-2 sm:mb-3">
                    <h2 className="text-lg sm:text-xl font-display font-semibold text-neutral-900 flex items-center gap-3">
                      <span className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Users className="w-4 h-4 sm:w-5 sm:h-5 text-success-600" />
                      </span>
                      AI Agents
                    </h2>
                    <button
                      type="button"
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        active_agents: prev.active_agents.length === agentRoles.length
                          ? []
                          : agentRoles.map(r => r.id),
                      }))}
                      className="text-xs font-medium text-primary-600 hover:text-primary-800 underline underline-offset-2 flex-shrink-0"
                    >
                      {formData.active_agents.length === agentRoles.length ? 'Deselect all' : 'Select all'}
                    </button>
                  </div>
                  <p className="body-sm sm:body-md text-neutral-600 mb-4 sm:mb-6">
                    Choose which AI agents collaborate on your project.
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                    {agentRoles.map((role) => {
                      const Icon = AGENT_ICONS[role.id] ?? Bot
                      const isSelected = formData.active_agents.includes(role.id)
                      return (
                        <motion.button
                          key={role.id}
                          type="button"
                          onClick={() => toggleAgent(role.id)}
                          whileHover={{ scale: 1.02, y: -2 }}
                          whileTap={{ scale: 0.98 }}
                          className={`p-4 sm:p-5 rounded-xl border-2 text-left transition-all ${
                            isSelected
                              ? 'border-primary-400 bg-gradient-to-br from-primary-50 to-secondary-50 shadow-md'
                              : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                          }`}
                        >
                          <div className="flex items-center space-x-3 mb-2 sm:mb-3">
                            <div className={`w-9 h-9 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                              isSelected ? 'bg-primary-100' : 'bg-neutral-100'
                            }`}>
                              <Icon className={`h-4 w-4 sm:h-5 sm:w-5 ${isSelected ? 'text-primary-600' : 'text-neutral-600'}`} />
                            </div>
                            <span className={`text-sm font-semibold ${isSelected ? 'text-primary-900' : 'text-neutral-900'}`}>
                              {role.name}
                            </span>
                          </div>
                          <p className={`text-xs sm:text-sm leading-relaxed ${isSelected ? 'text-primary-700' : 'text-neutral-600'}`}>
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
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <div className="glass-card p-5 sm:p-8">
                  <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center justify-between w-full text-left"
                  >
                    <h2 className="text-lg sm:text-xl font-display font-semibold text-neutral-900">
                      Advanced Settings
                    </h2>
                    <ChevronDown className={`h-5 w-5 text-neutral-500 transition-transform duration-300 flex-shrink-0 ${showAdvanced ? 'rotate-180' : ''}`} />
                  </button>

                  <AnimatePresence>
                    {showAdvanced && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-5 sm:mt-6 space-y-5 sm:space-y-6">
                          <div>
                            <label className="label block mb-2">Additional Requirements</label>
                            <textarea
                              value={formData.additional_requirements}
                              onChange={(e) => setFormData(prev => ({ ...prev, additional_requirements: e.target.value }))}
                              placeholder="Any specific requirements, constraints, or preferences..."
                              className="input-glass w-full h-24 resize-none"
                            />
                          </div>
                          <div>
                            <label className="label block mb-2">Technology Preferences (comma-separated)</label>
                            <input
                              type="text"
                              value={formData.tech_stack_preferences.join(', ')}
                              onChange={(e) => setFormData(prev => ({
                                ...prev,
                                tech_stack_preferences: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
                              }))}
                              placeholder="React, Node.js, PostgreSQL, MongoDB..."
                              className="input-glass"
                            />
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>

              {/* Submit */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 }}
                className="flex justify-center pb-8"
              >
                <motion.button
                  type="submit"
                  disabled={isSubmitting}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-primary text-base px-10 sm:px-12 py-4 sm:py-5 shadow-glow-lg disabled:opacity-50 disabled:cursor-not-allowed relative w-full sm:w-auto justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <Loader className="animate-spin h-5 w-5 mr-3 relative z-10" />
                      <span className="relative z-10 font-semibold">Starting Generation...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5 mr-3 relative z-10" />
                      <span className="relative z-10 font-semibold">Generate My App</span>
                    </>
                  )}
                </motion.button>
              </motion.div>

            </form>
          </motion.div>
        </div>
      </div>
    </AnimatedBackground>
  )
}

export default Generator
