import React from 'react'
import { motion } from 'framer-motion'
import {
  Bot, Brain, Cloud, Code, Users, Zap,
  ArrowRight, CheckCircle, ExternalLink
} from 'lucide-react'
import { Link } from 'react-router-dom'
import AnimatedBackground from '../components/AnimatedBackground'
import GlassCard from '../components/GlassCard'

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.55, delay },
})

const technologies = [
  { name: 'MetaGPT',   description: 'Multi-agent framework for collaborative AI development', icon: Users, link: 'https://github.com/geekan/MetaGPT' },
  { name: 'AWS Bedrock', description: 'Foundation models from leading AI companies',          icon: Cloud, link: 'https://aws.amazon.com/bedrock/' },
  { name: 'React',     description: 'Modern frontend framework for interactive UIs',          icon: Code,  link: 'https://react.dev/' },
  { name: 'FastAPI',   description: 'High-performance Python web framework',                  icon: Zap,   link: 'https://fastapi.tiangolo.com/' },
]

const features = [
  'Natural language to application generation',
  'Multi-agent collaborative development',
  'Real-time generation progress tracking',
  'Multiple AI model support (Claude, Llama, Nova)',
  'Complete project documentation',
  'Ready-to-use code structure',
  'WebSocket-based live updates',
  'Customizable agent selection',
]

const agents = [
  { role: 'Product Manager',   description: 'Creates product requirements, user stories, and business analysis.',          responsibilities: ['Requirements gathering', 'User story creation', 'Competitive analysis', 'Success metrics'],   color: 'from-primary-400 to-primary-600' },
  { role: 'System Architect',  description: 'Designs technical architecture and selects the technology stack.',             responsibilities: ['Architecture design', 'Technology selection', 'System integration', 'Scalability planning'], color: 'from-secondary-400 to-secondary-600' },
  { role: 'Project Manager',   description: 'Creates project plans, manages timelines, and coordinates activities.',        responsibilities: ['Project planning', 'Timeline management', 'Resource allocation', 'Risk assessment'],         color: 'from-success-400 to-success-600' },
  { role: 'Software Engineer', description: 'Provides implementation details, code structure, and development guidelines.', responsibilities: ['Code architecture', 'Implementation details', 'Technical specs', 'Best practices'],          color: 'from-accent-400 to-accent-600' },
  { role: 'QA Engineer',       description: 'Creates testing strategies, test cases, and quality assurance plans.',         responsibilities: ['Test strategy', 'Test case creation', 'Quality metrics', 'Automation planning'],              color: 'from-warning-400 to-warning-600' },
  { role: 'DevOps Engineer',   description: 'Designs infrastructure, CI/CD pipelines, and operational procedures.',         responsibilities: ['Infrastructure design', 'Monitoring setup', 'CI/CD pipelines', 'System architecture'],         color: 'from-neutral-500 to-neutral-700' },
]

const steps = [
  { number: '01', title: 'Describe Your App',      description: 'Describe your application idea in natural language. Our system understands complex requirements and user needs.' },
  { number: '02', title: 'AI Agents Collaborate',  description: 'Multiple specialized AI agents work together, each contributing their expertise like a real development team.' },
  { number: '03', title: 'Get Complete App',        description: 'Receive a complete application with code, documentation, tests, and setup instructions ready for development.' },
]

const About = () => (
  <AnimatedBackground>
    <div className="py-16 sm:py-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* ── Hero ── */}
        <motion.div {...fadeUp()} className="text-center mb-20 sm:mb-24">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
                className="absolute -top-1.5 -right-1.5"
              >
                <Brain className="h-5 w-5 text-accent-500" />
              </motion.div>
            </div>
          </div>
          <h1 className="display-lg text-neutral-900 mb-5">About MetaGPT + Bedrock</h1>
          <p className="body-lg text-neutral-500 max-w-2xl mx-auto">
            A platform that combines MetaGPT's multi-agent framework with AWS Bedrock's
            foundation models to generate complete applications from natural language descriptions.
          </p>
        </motion.div>

        {/* ── How It Works ── */}
        <section className="mb-20 sm:mb-24">
          <motion.h2 {...fadeUp()} className="display-md text-neutral-900 text-center mb-12">
            How It Works
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {steps.map((step, i) => (
              <motion.div key={step.number} {...fadeUp(i * 0.1)}>
                <GlassCard hover={false} className="text-center h-full">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-xl flex items-center justify-center mx-auto mb-5 shadow-glow">
                    <span className="text-white font-display font-bold text-sm">{step.number}</span>
                  </div>
                  <h3 className="text-base font-semibold text-neutral-900 mb-3">{step.title}</h3>
                  <p className="text-sm text-neutral-500 leading-relaxed">{step.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Technologies ── */}
        <section className="mb-20 sm:mb-24">
          <GlassCard hover={false} className="p-8 sm:p-10">
            <motion.h2 {...fadeUp()} className="display-md text-neutral-900 text-center mb-12">
              Built With Leading Technologies
            </motion.h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {technologies.map((tech, i) => (
                <motion.div key={tech.name} {...fadeUp(i * 0.08)} className="text-center group">
                  <div className="w-14 h-14 bg-primary-50 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-gradient-to-br group-hover:from-primary-400 group-hover:to-secondary-500 transition-all duration-300 shadow-sm">
                    {React.createElement(tech.icon, { className: 'h-7 w-7 text-primary-500 group-hover:text-white transition-colors duration-300' })}
                  </div>
                  <h3 className="text-sm font-semibold text-neutral-900 mb-1.5">{tech.name}</h3>
                  <p className="text-xs text-neutral-500 mb-3 leading-relaxed">{tech.description}</p>
                  <a href={tech.link} target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center text-xs text-primary-600 hover:text-primary-700 font-medium">
                    Learn More <ExternalLink className="h-3 w-3 ml-1" />
                  </a>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </section>

        {/* ── AI Agents ── */}
        <section className="mb-20 sm:mb-24">
          <motion.h2 {...fadeUp()} className="display-md text-neutral-900 text-center mb-12">
            Meet Our AI Agents
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {agents.map((agent, i) => (
              <motion.div key={agent.role} {...fadeUp(i * 0.08)}
                className="card hover:border-primary-200 hover:shadow-glow transition-all duration-300">
                <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-4 shadow-sm`}>
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-base font-semibold text-neutral-900 mb-2">{agent.role}</h3>
                <p className="text-sm text-neutral-500 mb-4 leading-relaxed">{agent.description}</p>
                <ul className="space-y-1.5">
                  {agent.responsibilities.map((r) => (
                    <li key={r} className="flex items-center text-xs text-neutral-500">
                      <CheckCircle className="h-3 w-3 text-success-500 mr-2 flex-shrink-0" />
                      {r}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Platform Features ── */}
        <section className="mb-20 sm:mb-24">
          <GlassCard hover={false} className="p-8 sm:p-10">
            <motion.h2 {...fadeUp()} className="display-md text-neutral-900 text-center mb-12">
              Platform Features
            </motion.h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-3xl mx-auto">
              {features.map((f, i) => (
                <motion.div key={f} {...fadeUp(i * 0.04)} className="flex items-center space-x-3">
                  <CheckCircle className="h-4 w-4 text-success-500 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{f}</span>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </section>

        {/* ── CTA ── */}
        <motion.section {...fadeUp()}>
          <GlassCard hover={false} className="text-center bg-gradient-to-br from-primary-400/8 to-secondary-500/8 border-primary-200/60 p-10 sm:p-14">
            <h2 className="display-md text-neutral-900 mb-4">
              Ready to Experience the Future of Development?
            </h2>
            <p className="body-lg text-neutral-500 mb-10 max-w-xl mx-auto">
              Generate your first app in minutes, not months.
            </p>
            <Link to="/generate" className="btn-primary body-md px-8 py-4 inline-flex items-center shadow-glow">
              <span className="relative z-10">Start Building Now</span>
              <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
            </Link>
          </GlassCard>
        </motion.section>

      </div>
    </div>
  </AnimatedBackground>
)

export default About
