import React from 'react'
import { motion } from 'framer-motion'
import {
  Brain, Users, Code, Cloud, Zap, ArrowRight,
  CheckCircle, Bot, Cpu, GitBranch, Database, Shield
} from 'lucide-react'
import { Link } from 'react-router-dom'

import AnimatedBackground from '../components/AnimatedBackground'
import HeroSection from '../components/HeroSection'
import FeatureCard from '../components/FeatureCard'
import GlassCard from '../components/GlassCard'

const features = [
  { icon: Brain,  title: 'AI-Powered Generation',      description: 'Leverage AWS Bedrock foundation models for intelligent, context-aware application creation.' },
  { icon: Users,  title: 'Multi-Agent Collaboration',  description: 'MetaGPT agents work together like a real dev team — each with specialized expertise.' },
  { icon: Code,   title: 'Complete Applications',      description: 'Generate production-ready full-stack apps with documentation and tests included.' },
  { icon: Cloud,  title: 'Cloud-Native Architecture',  description: 'Built for modern development with scalability and security baked in from the start.' },
  { icon: Zap,    title: 'Lightning Fast',             description: 'From idea to working prototype in minutes, not weeks.' },
  { icon: Shield, title: 'Enterprise Ready',           description: 'Security-first design with industry-standard practices and compliance considerations.' },
]

const benefits = [
  'Natural language to working application',
  'Multiple AI models for different tasks',
  'Real-time generation progress tracking',
  'Complete project documentation',
  'Ready-to-deploy code structure',
  'No coding experience required',
  'Customizable tech stack options',
  'Built-in testing & quality assurance',
]

const techStack = [
  { icon: Cpu,       label: 'AWS Bedrock' },
  { icon: Bot,       label: 'MetaGPT' },
  { icon: GitBranch, label: 'Git Ready' },
  { icon: Database,  label: 'Full Stack' },
]

const Home = () => (
  <AnimatedBackground>
    <HeroSection />

    {/* ── Features ── */}
    <section className="py-20 sm:py-28">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-14"
        >
          <h2 className="display-md text-neutral-900 mb-4">Powered by Advanced AI</h2>
          <p className="body-lg text-neutral-500 max-w-xl mx-auto">
            Combining MetaGPT's multi-agent framework with AWS Bedrock's foundation models
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <FeatureCard key={f.title} {...f} delay={i * 0.08} />
          ))}
        </div>
      </div>
    </section>

    {/* ── Benefits ── */}
    <section className="py-20 sm:py-28">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">

          {/* Left */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="display-md text-neutral-900 mb-5">Why Choose Our Platform?</h2>
            <p className="body-lg text-neutral-500 mb-8">
              Experience the future of software development with AI-powered automation
              that doesn't compromise on quality.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {benefits.map((b, i) => (
                <motion.div
                  key={b}
                  initial={{ opacity: 0, x: -16 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.04 }}
                  className="flex items-start space-x-2.5"
                >
                  <CheckCircle className="h-4 w-4 text-success-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-neutral-600">{b}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right — demo card */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard hover={false} className="overflow-hidden">
              {/* Agent avatars */}
              <div className="flex items-center space-x-4 mb-6">
                <div className="flex -space-x-2.5">
                  {[
                    { icon: Bot,  color: 'from-primary-400 to-primary-600' },
                    { icon: Code, color: 'from-secondary-400 to-secondary-600' },
                    { icon: Zap,  color: 'from-accent-400 to-accent-600' },
                  ].map((a, idx) => (
                    <motion.div
                      key={idx}
                      className={`w-9 h-9 bg-gradient-to-br ${a.color} rounded-full flex items-center justify-center border-2 border-white shadow-md`}
                      animate={{ y: [0, -4, 0] }}
                      transition={{ duration: 2.5, delay: idx * 0.3, repeat: Infinity }}
                    >
                      {React.createElement(a.icon, { className: 'h-4 w-4 text-white' })}
                    </motion.div>
                  ))}
                </div>
                <span className="badge-glass text-xs">
                  <span className="inline-block w-1.5 h-1.5 bg-success-500 rounded-full mr-1.5 animate-pulse" />
                  Agents Collaborating
                </span>
              </div>

              <h3 className="text-lg font-semibold text-neutral-900 mb-2">Real-time Generation</h3>
              <p className="text-sm text-neutral-500 mb-6 leading-relaxed">
                Watch as different AI agents work together to build your application,
                each contributing their specialized expertise in real-time.
              </p>

              {/* Progress bars */}
              <div className="space-y-4">
                {[
                  { label: 'Architecture Design', pct: 100, done: true },
                  { label: 'Code Generation',     pct: 75,  done: false },
                  { label: 'Testing & QA',        pct: 45,  done: false },
                ].map(({ label, pct, done }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="font-medium text-neutral-700">{label}</span>
                      <span className={done ? 'text-primary-600 font-semibold' : 'text-neutral-400'}>{pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        whileInView={{ width: `${pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.2, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Tech badges */}
              <div className="mt-6 pt-5 border-t border-neutral-100 grid grid-cols-2 gap-2">
                {techStack.map(({ icon: Icon, label }, idx) => (
                  <motion.div
                    key={label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.08 }}
                    className="badge-glass px-3 py-2 flex items-center gap-2"
                  >
                    <Icon className="w-3.5 h-3.5 text-primary-500 flex-shrink-0" />
                    <span className="text-xs font-semibold uppercase tracking-wide text-neutral-600">{label}</span>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </section>

    {/* ── CTA ── */}
    <section className="py-20 sm:py-28">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <GlassCard hover={false} className="text-center bg-gradient-to-br from-primary-400/8 to-secondary-500/8 border-primary-200/60 p-10 sm:p-14">
            <h2 className="display-md text-neutral-900 mb-4">Ready to Build Your Next App?</h2>
            <p className="body-lg text-neutral-500 mb-10 max-w-xl mx-auto">
              Join thousands of developers already using AI to accelerate their development process.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/generate" className="btn-primary body-md px-10 py-4 shadow-glow-lg">
                <span className="relative z-10">Get Started Now</span>
                <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
              </Link>
              <Link to="/about" className="btn-outline body-md px-10 py-4">
                Learn More
              </Link>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  </AnimatedBackground>
)

export default Home
