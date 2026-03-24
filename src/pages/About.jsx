import React from 'react'
import { motion } from 'framer-motion'
import {
  Bot, Cloud, Code, Users, Zap,
  ArrowRight, CheckCircle, ExternalLink, Cpu
} from 'lucide-react'
import { Link } from 'react-router-dom'

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.4, delay },
})

const technologies = [
  { name: 'MetaGPT',     description: 'Multi-agent framework for collaborative AI development', icon: Users, link: 'https://github.com/geekan/MetaGPT' },
  { name: 'AWS Bedrock', description: 'Foundation models from leading AI companies',            icon: Cloud, link: 'https://aws.amazon.com/bedrock/' },
  { name: 'React',       description: 'Modern frontend framework for interactive UIs',          icon: Code,  link: 'https://react.dev/' },
  { name: 'FastAPI',     description: 'High-performance Python web framework',                  icon: Zap,   link: 'https://fastapi.tiangolo.com/' },
]

const features = [
  'Natural language to application generation',
  'Multi-agent collaborative development',
  'Real-time generation progress tracking',
  'Multiple AI model support (Claude, Llama, Mistral)',
  'Complete project documentation',
  'Ready-to-use code structure',
  'SSE-based live updates',
  'Customizable agent selection',
]

const agents = [
  { role: 'Product Manager',   description: 'Creates product requirements, user stories, and business analysis.',          color: 'bg-primary-600' },
  { role: 'System Architect',  description: 'Designs technical architecture and selects the technology stack.',             color: 'bg-blue-600' },
  { role: 'Project Manager',   description: 'Creates project plans, manages timelines, and coordinates activities.',        color: 'bg-success-600' },
  { role: 'Software Engineer', description: 'Provides implementation details, code structure, and development guidelines.', color: 'bg-accent-600' },
  { role: 'QA Engineer',       description: 'Creates testing strategies, test cases, and quality assurance plans.',         color: 'bg-warning-600' },
  { role: 'DevOps Engineer',   description: 'Designs infrastructure, CI/CD pipelines, and operational procedures.',         color: 'bg-neutral-600' },
]

const steps = [
  { number: '01', title: 'Describe Your App',     description: 'Describe your application idea in natural language. Our system understands complex requirements and user needs.' },
  { number: '02', title: 'AI Agents Collaborate', description: 'Multiple specialized AI agents work together, each contributing their expertise like a real development team.' },
  { number: '03', title: 'Get Complete App',       description: 'Receive a complete application with code, documentation, tests, and setup instructions ready for development.' },
]

const About = () => (
  <div className="min-h-screen bg-surface">
    {/* Page header */}
    <div className="bg-white border-b border-neutral-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <motion.div {...fadeUp()}>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
              <Cpu className="h-5 w-5 text-white" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400">About</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-neutral-900 font-display mb-3">MetaGPT + AWS Bedrock</h1>
          <p className="text-neutral-500 max-w-2xl text-base sm:text-lg leading-relaxed">
            A platform combining MetaGPT's multi-agent framework with AWS Bedrock's foundation models
            to generate complete applications from natural language descriptions.
          </p>
        </motion.div>
      </div>
    </div>

    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 space-y-14">

      {/* How It Works */}
      <section>
        <motion.div {...fadeUp()} className="mb-8">
          <p className="section-label mb-2">Process</p>
          <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 font-display">How It Works</h2>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {steps.map((step, i) => (
            <motion.div key={step.number} {...fadeUp(i * 0.08)}>
              <div className="card p-6 sm:p-7 h-full">
                <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center mb-5">
                  <span className="text-white font-bold text-xs">{step.number}</span>
                </div>
                <h3 className="text-sm font-semibold text-neutral-900 mb-2.5">{step.title}</h3>
                <p className="text-sm text-neutral-500 leading-relaxed">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Technologies */}
      <section>
        <motion.div {...fadeUp()} className="mb-8">
          <p className="section-label mb-2">Stack</p>
          <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 font-display">Built With Leading Technologies</h2>
        </motion.div>
        <div className="card p-7 sm:p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {technologies.map((tech, i) => (
              <motion.div key={tech.name} {...fadeUp(i * 0.06)}>
                <div className="w-11 h-11 bg-primary-50 rounded-xl flex items-center justify-center mb-4">
                  {React.createElement(tech.icon, { className: 'h-5 w-5 text-primary-600' })}
                </div>
                <h3 className="text-sm font-semibold text-neutral-900 mb-1.5">{tech.name}</h3>
                <p className="text-xs text-neutral-500 mb-3 leading-relaxed">{tech.description}</p>
                <a href={tech.link} target="_blank" rel="noopener noreferrer"
                  className="inline-flex items-center text-xs text-primary-600 hover:text-primary-700 font-medium transition-colors">
                  Learn More <ExternalLink className="h-3 w-3 ml-1" />
                </a>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Agents */}
      <section>
        <motion.div {...fadeUp()} className="mb-8">
          <p className="section-label mb-2">Team</p>
          <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 font-display">AI Agent Roles</h2>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {agents.map((agent, i) => (
            <motion.div key={agent.role} {...fadeUp(i * 0.06)}>
              <div className="card p-6 h-full hover:shadow-md hover:border-neutral-300 transition-all duration-200">
                <div className={`w-8 h-8 rounded-lg ${agent.color} flex items-center justify-center mb-4`}>
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-sm font-semibold text-neutral-900 mb-2">{agent.role}</h3>
                <p className="text-xs text-neutral-500 leading-relaxed">{agent.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Platform Features */}
      <section>
        <motion.div {...fadeUp()} className="mb-8">
          <p className="section-label mb-2">Features</p>
          <h2 className="text-xl sm:text-2xl font-bold text-neutral-900 font-display">Platform Capabilities</h2>
        </motion.div>
        <div className="card p-7 sm:p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
            {features.map((f, i) => (
              <motion.div key={f} {...fadeUp(i * 0.04)} className="flex items-center gap-3">
                <CheckCircle className="h-4 w-4 text-success-500 flex-shrink-0" />
                <span className="text-sm text-neutral-700">{f}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <motion.section {...fadeUp()}>
        <div className="card p-10 sm:p-14 bg-primary-600 border-primary-700 text-center">
          <h2 className="text-2xl sm:text-3xl font-bold text-white font-display mb-3">
            Ready to Experience the Future of Development?
          </h2>
          <p className="text-primary-200 mb-8 max-w-md mx-auto text-sm sm:text-base leading-relaxed">
            Generate your first app in minutes, not months.
          </p>
          <Link to="/generate" className="inline-flex items-center justify-center px-7 py-3 rounded-lg bg-white text-primary-700 text-sm font-semibold hover:bg-primary-50 transition-colors shadow-sm">
            Start Building Now
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </div>
      </motion.section>

    </div>
  </div>
)

export default About
