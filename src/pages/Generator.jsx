import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Bot, Zap, Settings, Play, Loader,
  Users, Code, Database, TestTube, Cloud, Briefcase,
  ChevronDown, AlertCircle, Cpu, Sparkles, RefreshCcw
} from 'lucide-react'

import { generateApp } from '../services/api'

const STATIC_MODELS = [
  { id: 'anthropic.claude-3-haiku-20240307-v1:0',   name: 'Claude 3 Haiku',   provider: 'Anthropic' },
  { id: 'anthropic.claude-3-sonnet-20240229-v1:0',  name: 'Claude 3 Sonnet',  provider: 'Anthropic' },
  { id: 'anthropic.claude-3-5-sonnet-20240620-v1:0',name: 'Claude 3.5 Sonnet',provider: 'Anthropic' },
  { id: 'meta.llama3-8b-instruct-v1:0',             name: 'Llama 3 8B',       provider: 'Meta' },
  { id: 'meta.llama3-70b-instruct-v1:0',            name: 'Llama 3 70B',      provider: 'Meta' },
  { id: 'mistral.mistral-7b-instruct-v0:2',         name: 'Mistral 7B',       provider: 'Mistral AI' },
  { id: 'mistral.mistral-large-2402-v1:0',          name: 'Mistral Large',    provider: 'Mistral AI' },
]

const STATIC_ROLES = [
  { id: 'product_manager', name: 'Product Manager',  description: 'Analyzes requirements, creates user stories, and defines product specifications' },
  { id: 'architect',       name: 'System Architect',  description: 'Designs system architecture, selects tech stack, and creates technical specifications' },
  { id: 'project_manager', name: 'Project Manager',   description: 'Creates project plans, manages timelines, and coordinates development activities' },
  { id: 'engineer',        name: 'Software Engineer', description: 'Implements application code following architecture and best practices' },
  { id: 'qa_engineer',     name: 'QA Engineer',       description: 'Creates test strategies, writes test cases, and ensures quality standards' },
  { id: 'devops',          name: 'DevOps Engineer',   description: 'Designs infrastructure, CI/CD pipelines, and deployment configurations' },
]

const AGENT_ICONS = {
  product_manager: Briefcase,
  architect:       Settings,
  project_manager: Users,
  engineer:        Code,
  qa_engineer:     TestTube,
  devops:          Cloud,
}

const APP_TYPES = [
  { id: 'web_app',     label: 'Web App',     icon: Code },
  { id: 'mobile_app',  label: 'Mobile App',  icon: Bot },
  { id: 'api_service', label: 'API Service', icon: Database },
  { id: 'desktop_app', label: 'Desktop App', icon: Settings },
  { id: 'cli_tool',    label: 'CLI Tool',    icon: Zap },
]

const SectionHeader = ({ step, title, description }) => (
  <div className="mb-7">
    <div className="flex items-center gap-3 mb-2">
      <span className="w-6 h-6 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 shadow-sm">
        {step}
      </span>
      <h2 className="text-sm font-semibold text-neutral-900">{title}</h2>
    </div>
    {description && <p className="text-xs text-neutral-400 ml-9 leading-relaxed">{description}</p>}
  </div>
)

const FormSkeleton = () => (
  <div className="space-y-5">
    {[1, 2, 3, 4].map(i => (
      <div key={i} className="card p-7">
        <div className="skeleton h-4 w-36 mb-7" />
        <div className="skeleton h-28 w-full rounded-xl" />
      </div>
    ))}
  </div>
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
      setModels(STATIC_MODELS)
      setAgentRoles(STATIC_ROLES)
      setFormData(prev => ({
        ...prev,
        preferred_model: STATIC_MODELS[0].id,
        active_agents: STATIC_ROLES.map(r => r.id),
      }))
    } catch (err) {
      const msg = typeof err === 'string'
        ? err
        : err?.message || err?.detail || 'Failed to load configuration'
      setLoadError(typeof msg === 'string' ? msg : 'Failed to load configuration')
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
    <div className="min-h-screen bg-surface">
      <div className="bg-white border-b border-neutral-100">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
          <div className="flex items-center gap-4">
            <div className="skeleton w-11 h-11 rounded-2xl" />
            <div className="space-y-2">
              <div className="skeleton h-4 w-44" />
              <div className="skeleton h-3 w-64" />
            </div>
          </div>
        </div>
      </div>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <FormSkeleton />
      </div>
    </div>
  )

  if (loadError) return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card p-12 max-w-sm w-full text-center shadow-elevation-2"
      >
        <div className="w-14 h-14 bg-error-50 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="h-7 w-7 text-error-500" />
        </div>
        <h2 className="text-base font-semibold text-neutral-900 mb-2.5">Could not load configuration</h2>
        <p className="text-sm text-neutral-500 mb-8 leading-relaxed">{String(loadError)}</p>
        <button onClick={loadInitialData} className="btn-primary w-full justify-center gap-2">
          <RefreshCcw className="h-4 w-4" />
          Retry
        </button>
      </motion.div>
    </div>
  )

  const modelsByProvider = models.reduce((acc, m) => {
    if (!acc[m.provider]) acc[m.provider] = []
    acc[m.provider].push(m)
    return acc
  }, {})

  return (
    <div className="min-h-screen bg-surface">
      {/* Page header */}
      <div className="bg-white border-b border-neutral-100">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-4"
          >
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center flex-shrink-0 shadow-sm">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-neutral-900 font-display leading-tight">Generate Application</h1>
              <p className="text-sm text-neutral-400 mt-0.5">Configure your AI agents and describe what you want to build</p>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Step 1 — Description */}
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
            <div className="card p-7 sm:p-8">
              <SectionHeader
                step="1"
                title="Describe Your Application"
                description="Be specific about features, users, and goals for best results."
              />
              <textarea
                value={formData.requirement}
                onChange={e => setFormData(p => ({ ...p, requirement: e.target.value }))}
                placeholder="Example: A project management tool with user authentication, kanban boards, real-time collaboration, and Slack notifications. Built for small engineering teams."
                className="input w-full h-36 resize-none"
                required
              />
              <div className="flex items-center justify-between mt-3">
                <p className="text-xs text-neutral-400">
                  {formData.requirement.length > 0
                    ? `${formData.requirement.length} characters`
                    : 'Describe your app in detail for best results'}
                </p>
                {formData.requirement.length > 100 && (
                  <span className="text-xs text-success-600 font-medium flex items-center gap-1.5">
                    <Sparkles className="h-3 w-3" /> Good detail
                  </span>
                )}
              </div>
            </div>
          </motion.div>

          {/* Step 2 — App Type */}
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <div className="card p-7 sm:p-8">
              <SectionHeader step="2" title="Application Type" />
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {APP_TYPES.map(({ id, label, icon: Icon }) => {
                  const sel = formData.app_type === id
                  return (
                    <button
                      key={id} type="button"
                      onClick={() => setFormData(p => ({ ...p, app_type: id }))}
                      className={`p-4 rounded-2xl border text-center transition-all duration-150 ${
                        sel
                          ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-400 shadow-sm'
                          : 'border-neutral-200 hover:border-neutral-300 bg-white hover:bg-neutral-50'
                      }`}
                    >
                      <Icon className={`h-5 w-5 mx-auto mb-2.5 ${sel ? 'text-primary-600' : 'text-neutral-400'}`} />
                      <div className={`text-xs font-medium leading-tight ${sel ? 'text-primary-700' : 'text-neutral-600'}`}>
                        {label}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </motion.div>

          {/* Step 3 — AI Model */}
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <div className="card p-7 sm:p-8">
              <SectionHeader step="3" title="AI Model" description="Select the foundation model to power your generation." />
              <div className="space-y-6">
                {Object.entries(modelsByProvider).map(([provider, pModels]) => (
                  <div key={provider}>
                    <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">{provider}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {pModels.map(model => {
                        const sel = formData.preferred_model === model.id
                        return (
                          <button
                            key={model.id} type="button"
                            onClick={() => setFormData(p => ({ ...p, preferred_model: model.id }))}
                            className={`p-4 rounded-2xl border text-left transition-all duration-150 ${
                              sel
                                ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-400 shadow-sm'
                                : 'border-neutral-200 hover:border-neutral-300 bg-white hover:bg-neutral-50'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className={`text-sm font-medium ${sel ? 'text-primary-700' : 'text-neutral-800'}`}>
                                {model.name}
                              </span>
                              {sel && (
                                <span className="w-4 h-4 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                                  <span className="w-1.5 h-1.5 rounded-full bg-white" />
                                </span>
                              )}
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Step 4 — Agents */}
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <div className="card p-7 sm:p-8">
              <div className="flex items-start justify-between mb-7">
                <SectionHeader step="4" title="AI Agent Team" description="Select which agents collaborate on your project." />
                <button
                  type="button"
                  onClick={() => setFormData(p => ({
                    ...p,
                    active_agents: p.active_agents.length === agentRoles.length ? [] : agentRoles.map(r => r.id),
                  }))}
                  className="text-xs font-medium text-primary-600 hover:text-primary-800 flex-shrink-0 mt-0.5 transition-colors"
                >
                  {formData.active_agents.length === agentRoles.length ? 'Deselect all' : 'Select all'}
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {agentRoles.map(role => {
                  const Icon = AGENT_ICONS[role.id] ?? Bot
                  const sel  = formData.active_agents.includes(role.id)
                  return (
                    <button
                      key={role.id} type="button"
                      onClick={() => toggleAgent(role.id)}
                      className={`p-4 rounded-2xl border text-left transition-all duration-150 ${
                        sel
                          ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-400 shadow-sm'
                          : 'border-neutral-200 hover:border-neutral-300 bg-white hover:bg-neutral-50'
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2.5">
                        <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${sel ? 'bg-primary-100' : 'bg-neutral-100'}`}>
                          <Icon className={`h-4 w-4 ${sel ? 'text-primary-600' : 'text-neutral-500'}`} />
                        </div>
                        <span className={`text-sm font-semibold ${sel ? 'text-primary-900' : 'text-neutral-900'}`}>{role.name}</span>
                      </div>
                      <p className={`text-xs leading-relaxed ml-11 ${sel ? 'text-primary-600' : 'text-neutral-500'}`}>{role.description}</p>
                    </button>
                  )
                })}
              </div>
              <p className="text-xs text-neutral-400 mt-5">
                {formData.active_agents.length} of {agentRoles.length} agents selected
              </p>
            </div>
          </motion.div>

          {/* Advanced Settings */}
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <div className="card overflow-hidden">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center justify-between w-full text-left px-7 sm:px-8 py-5 hover:bg-neutral-50 transition-colors"
              >
                <span className="text-sm font-semibold text-neutral-700">Advanced Settings</span>
                <ChevronDown className={`h-4 w-4 text-neutral-400 transition-transform duration-200 ${showAdvanced ? 'rotate-180' : ''}`} />
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
                    <div className="px-7 sm:px-8 pb-7 sm:pb-8 pt-3 border-t border-neutral-100 space-y-6">
                      <div>
                        <label className="label block mb-2.5">Additional Requirements</label>
                        <textarea
                          value={formData.additional_requirements}
                          onChange={e => setFormData(p => ({ ...p, additional_requirements: e.target.value }))}
                          placeholder="Any specific constraints, preferences, or requirements..."
                          className="input w-full h-24 resize-none"
                        />
                      </div>
                      <div>
                        <label className="label block mb-2.5">Technology Preferences</label>
                        <input
                          type="text"
                          value={formData.tech_stack_preferences.join(', ')}
                          onChange={e => setFormData(p => ({
                            ...p,
                            tech_stack_preferences: e.target.value.split(',').map(s => s.trim()).filter(Boolean),
                          }))}
                          placeholder="React, Node.js, PostgreSQL, Docker..."
                          className="input"
                        />
                        <p className="text-xs text-neutral-400 mt-2">Comma-separated list of preferred technologies</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

          {/* Submit */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 pb-12"
          >
            <p className="text-xs text-neutral-400 order-2 sm:order-1">
              Generation typically takes 2–5 minutes
            </p>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary px-8 py-3.5 text-sm w-full sm:w-auto order-1 sm:order-2 gap-2 shadow-md hover:shadow-lg"
            >
              {isSubmitting
                ? <><Loader className="animate-spin h-4 w-4" />Starting...</>
                : <><Play className="h-4 w-4" />Generate App</>
              }
            </button>
          </motion.div>

        </form>
      </div>
    </div>
  )
}

export default Generator
