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
  architect:       Settings,
  project_manager: Users,
  engineer:        Code,
  qa_engineer:     TestTube,
  devops:          Cloud,
}

const APP_TYPE_ICONS = {
  web_app:     Code,
  mobile_app:  Bot,
  api_service: Database,
  desktop_app: Settings,
  cli_tool:    Zap,
}

const PROVIDER_STYLES = {
  Amazon:    { border: 'border-accent-300',    bg: 'bg-accent-50',    text: 'text-accent-700',    pill: 'bg-accent-100 text-accent-700' },
  Meta:      { border: 'border-secondary-300', bg: 'bg-secondary-50', text: 'text-secondary-700', pill: 'bg-secondary-100 text-secondary-700' },
  Anthropic: { border: 'border-primary-300',   bg: 'bg-primary-50',   text: 'text-primary-700',   pill: 'bg-primary-100 text-primary-700' },
}
const DEFAULT_STYLE = PROVIDER_STYLES.Amazon

const SectionTitle = ({ icon: Icon, color = 'bg-primary-50 text-primary-500', children }) => (
  <h2 className="text-lg font-display font-semibold text-neutral-900 mb-6 flex items-center gap-3">
    <span className={`w-8 h-8 ${color} rounded-lg flex items-center justify-center flex-shrink-0`}>
      <Icon className="w-4 h-4" />
    </span>
    {children}
  </h2>
)

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

  useEffect(() => { loadInitialData() }, [])

  const loadInitialData = async () => {
    setIsLoadingData(true)
    setLoadError(null)
    try {
      const [modelsData, rolesData] = await Promise.all([getModels(), getAgentRoles()])
      const fetchedModels = modelsData.models ?? []
      const fetchedRoles  = rolesData.roles  ?? []
      if (!fetchedModels.length) throw new Error('No models returned from server')
      if (!fetchedRoles.length)  throw new Error('No agent roles returned from server')
      setModels(fetchedModels)
      setAgentRoles(fetchedRoles)
      setFormData(prev => ({
        ...prev,
        preferred_model: fetchedModels[0].id,
        active_agents:   fetchedRoles.map(r => r.id),
      }))
    } catch (err) {
      const msg = typeof err === 'string' ? err : err?.message || 'Failed to load configuration from server'
      setLoadError(typeof msg === 'string' ? msg : 'Failed to load configuration from server')
    } finally {
      setIsLoadingData(false)
    }
  }

  const toggleAgent = (id) =>
    setFormData(prev => ({
      ...prev,
      active_agents: prev.active_agents.includes(id)
        ? prev.active_agents.filter(a => a !== id)
        : [...prev.active_agents, id],
    }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.requirement.trim()) { toast.error('Please describe your app idea'); return }
    if (!formData.preferred_model)    { toast.error('Please select an AI model');     return }
    if (!formData.active_agents.length) { toast.error('Please select at least one agent'); return }
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

  if (isLoadingData) return (
    <AnimatedBackground>
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="h-7 w-7 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-sm text-neutral-500">Loading configuration...</p>
        </div>
      </div>
    </AnimatedBackground>
  )

  if (loadError) return (
    <AnimatedBackground>
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="glass-card p-8 max-w-sm w-full text-center">
          <div className="w-12 h-12 bg-error-50 rounded-xl flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="h-6 w-6 text-error-500" />
          </div>
          <h2 className="text-lg font-semibold text-neutral-900 mb-2">Could not load configuration</h2>
          <p className="text-sm text-neutral-500 mb-6">{loadError}</p>
          <button onClick={loadInitialData} className="btn-primary w-full justify-center">Retry</button>
        </div>
      </div>
    </AnimatedBackground>
  )

  const modelsByProvider = models.reduce((acc, m) => {
    if (!acc[m.provider]) acc[m.provider] = []
    acc[m.provider].push(m)
    return acc
  }, {})

  return (
    <AnimatedBackground>
      <div className="py-14 sm:py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>

            <div className="text-center mb-12">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, type: 'spring' }}
                className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl shadow-glow mb-5"
              >
                <Bot className="w-7 h-7 text-white" />
              </motion.div>
              <h1 className="display-md text-neutral-900 mb-3">Generate Your App</h1>
              <p className="body-lg text-neutral-500 max-w-xl mx-auto">
                Describe your application idea and watch AI agents collaborate to build it.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Description */}
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <div className="glass-card p-6 sm:p-8">
                  <SectionTitle icon={Code}>Describe Your App</SectionTitle>
                  <textarea
                    value={formData.requirement}
                    onChange={e => setFormData(p => ({ ...p, requirement: e.target.value }))}
                    placeholder={`Describe your app idea in detail. What should it do? Who will use it?\n\nExample: A task management app with user authentication, real-time updates, and team collaboration.`}
                    className="input-glass w-full h-36 resize-none"
                    required
                  />
                </div>
              </motion.div>

              {/* App Type */}
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <div className="glass-card p-6 sm:p-8">
                  <SectionTitle icon={Settings} color="bg-secondary-50 text-secondary-500">Application Type</SectionTitle>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                    {Object.entries(APP_TYPE_ICONS).map(([type, Icon]) => {
                      const sel = formData.app_type === type
                      return (
                        <motion.button
                          key={type} type="button"
                          onClick={() => setFormData(p => ({ ...p, app_type: type }))}
                          whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}
                          className={`p-4 rounded-xl border-2 transition-all text-center ${
                            sel ? 'border-primary-400 bg-primary-50 shadow-glow' : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                          }`}
                        >
                          <Icon className={`h-6 w-6 mx-auto mb-2 ${sel ? 'text-primary-500' : 'text-neutral-400'}`} />
                          <div className={`text-xs font-semibold leading-tight ${sel ? 'text-primary-600' : 'text-neutral-600'}`}>
                            {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              </motion.div>

              {/* AI Model */}
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                <div className="glass-card p-6 sm:p-8">
                  <SectionTitle icon={Zap} color="bg-accent-50 text-accent-600">AI Model</SectionTitle>
                  <div className="space-y-5">
                    {Object.entries(modelsByProvider).map(([provider, pModels]) => {
                      const style = PROVIDER_STYLES[provider] ?? DEFAULT_STYLE
                      return (
                        <div key={provider}>
                          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-2">{provider}</p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                            {pModels.map(model => {
                              const sel = formData.preferred_model === model.id
                              return (
                                <motion.button
                                  key={model.id} type="button"
                                  onClick={() => setFormData(p => ({ ...p, preferred_model: model.id }))}
                                  whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }}
                                  className={`p-3.5 rounded-xl border-2 text-left transition-all ${
                                    sel ? `${style.border} ${style.bg}` : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                                  }`}
                                >
                                  <div className="flex items-center justify-between">
                                    <span className={`text-sm font-semibold ${sel ? style.text : 'text-neutral-800'}`}>{model.name}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sel ? style.pill : 'bg-neutral-100 text-neutral-500'}`}>
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

              {/* Agents */}
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                <div className="glass-card p-6 sm:p-8">
                  <div className="flex items-start justify-between mb-6">
                    <SectionTitle icon={Users} color="bg-success-50 text-success-600">AI Agents</SectionTitle>
                    <button
                      type="button"
                      onClick={() => setFormData(p => ({
                        ...p,
                        active_agents: p.active_agents.length === agentRoles.length ? [] : agentRoles.map(r => r.id),
                      }))}
                      className="text-xs font-medium text-primary-600 hover:text-primary-800 underline underline-offset-2 mt-1"
                    >
                      {formData.active_agents.length === agentRoles.length ? 'Deselect all' : 'Select all'}
                    </button>
                  </div>
                  <p className="text-sm text-neutral-500 -mt-4 mb-5">Choose which AI agents collaborate on your project.</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {agentRoles.map(role => {
                      const Icon = AGENT_ICONS[role.id] ?? Bot
                      const sel  = formData.active_agents.includes(role.id)
                      return (
                        <motion.button
                          key={role.id} type="button"
                          onClick={() => toggleAgent(role.id)}
                          whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }}
                          className={`p-4 rounded-xl border-2 text-left transition-all ${
                            sel ? 'border-primary-400 bg-primary-50' : 'border-neutral-200 hover:border-neutral-300 bg-white/50'
                          }`}
                        >
                          <div className="flex items-center space-x-3 mb-2">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${sel ? 'bg-primary-100' : 'bg-neutral-100'}`}>
                              <Icon className={`h-4 w-4 ${sel ? 'text-primary-600' : 'text-neutral-500'}`} />
                            </div>
                            <span className={`text-sm font-semibold ${sel ? 'text-primary-900' : 'text-neutral-900'}`}>{role.name}</span>
                          </div>
                          <p className={`text-xs leading-relaxed ${sel ? 'text-primary-600' : 'text-neutral-500'}`}>{role.description}</p>
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              </motion.div>

              {/* Advanced */}
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
                <div className="glass-card p-6 sm:p-8">
                  <button type="button" onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center justify-between w-full text-left">
                    <h2 className="text-lg font-display font-semibold text-neutral-900">Advanced Settings</h2>
                    <ChevronDown className={`h-5 w-5 text-neutral-400 transition-transform duration-300 ${showAdvanced ? 'rotate-180' : ''}`} />
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
                        <div className="mt-6 space-y-5">
                          <div>
                            <label className="label block mb-2">Additional Requirements</label>
                            <textarea
                              value={formData.additional_requirements}
                              onChange={e => setFormData(p => ({ ...p, additional_requirements: e.target.value }))}
                              placeholder="Any specific requirements, constraints, or preferences..."
                              className="input-glass w-full h-24 resize-none"
                            />
                          </div>
                          <div>
                            <label className="label block mb-2">Technology Preferences (comma-separated)</label>
                            <input
                              type="text"
                              value={formData.tech_stack_preferences.join(', ')}
                              onChange={e => setFormData(p => ({
                                ...p,
                                tech_stack_preferences: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
                              }))}
                              placeholder="React, Node.js, PostgreSQL..."
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
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                className="flex justify-center pb-6">
                <motion.button
                  type="submit" disabled={isSubmitting}
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  className="btn-primary text-base px-12 py-4 shadow-glow-lg disabled:opacity-50 w-full sm:w-auto justify-center"
                >
                  {isSubmitting
                    ? <><Loader className="animate-spin h-5 w-5 mr-2.5" /><span className="font-semibold">Starting Generation...</span></>
                    : <><Play className="h-5 w-5 mr-2.5" /><span className="font-semibold">Generate My App</span></>
                  }
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
