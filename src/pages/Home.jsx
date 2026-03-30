import { motion } from 'framer-motion'
import {
  Brain, Users, Code, Cloud, Zap, ArrowRight,
  CheckCircle, Bot, Cpu, GitBranch, Database, Shield
} from 'lucide-react'
import { Link } from 'react-router-dom'

import AnimatedBackground from '../components/AnimatedBackground'
import HeroSection from '../components/HeroSection'
import FeatureCard from '../components/FeatureCard'

const features = [
  { icon: Brain,  title: 'AI-Powered Generation',     description: 'Leverage AWS Bedrock foundation models for intelligent, context-aware application creation.' },
  { icon: Users,  title: 'Multi-Agent Collaboration', description: 'Specialized AI agents work together like a real dev team — each with domain expertise.' },
  { icon: Code,   title: 'Complete Applications',     description: 'Generate production-ready full-stack apps with documentation and tests included.' },
  { icon: Cloud,  title: 'Cloud-Native Architecture', description: 'Built for modern development with scalability and security baked in from the start.' },
  { icon: Zap,    title: 'Lightning Fast',            description: 'From idea to working prototype in minutes, not weeks.' },
  { icon: Shield, title: 'Enterprise Ready',          description: 'Security-first design with industry-standard practices and compliance considerations.' },
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

    {/* Features */}
    <section className="py-24 sm:py-32 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="mb-14"
        >
          <p className="section-label mb-3">Capabilities</p>
          <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-display mb-4">Powered by Advanced AI</h2>
          <p className="text-neutral-500 max-w-xl text-base sm:text-lg">
            Combining MetaGPT's multi-agent framework with AWS Bedrock's foundation models.
          </p>
        </motion.div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <FeatureCard key={f.title} {...f} delay={i * 0.06} />
          ))}
        </div>
      </div>
    </section>

    {/* Benefits */}
    <section className="py-24 sm:py-32 bg-white border-y border-neutral-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-28 items-center">
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <p className="section-label mb-3">Why Choose Us</p>
            <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-display mb-6">
              Built for Modern Development Teams
            </h2>
            <p className="text-neutral-500 mb-10 leading-relaxed text-base sm:text-lg">
              Experience the future of software development with AI-powered automation
              that doesn't compromise on quality or security.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {benefits.map((b, i) => (
                <motion.div
                  key={b}
                  initial={{ opacity: 0, x: -12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: i * 0.04 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-5 h-5 rounded-full bg-success-50 flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="h-3.5 w-3.5 text-success-500" />
                  </div>
                  <span className="text-sm text-neutral-600">{b}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Demo card */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="card p-8 sm:p-10 shadow-elevation-2">
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-success-500 animate-pulse" />
                  <span className="text-xs font-semibold text-neutral-600">Agents Collaborating</span>
                </div>
                <span className="badge-primary">Live</span>
              </div>

              <h3 className="text-base font-semibold text-neutral-900 mb-2.5">Real-time Generation</h3>
              <p className="text-sm text-neutral-500 mb-8 leading-relaxed">
                Watch AI agents work together to build your application, each contributing
                specialized expertise in real-time.
              </p>

              <div className="space-y-5">
                {[
                  { label: 'Architecture Design', pct: 100 },
                  { label: 'Code Generation',     pct: 75 },
                  { label: 'Testing & QA',        pct: 45 },
                ].map(({ label, pct }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-2.5">
                      <span className="font-medium text-neutral-700">{label}</span>
                      <span className="text-neutral-400 tabular-nums">{pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        whileInView={{ width: `${pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.1, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 pt-6 border-t border-neutral-100 grid grid-cols-2 gap-3">
                {techStack.map(({ icon: Icon, label }) => (
                  <div key={label} className="flex items-center gap-2.5 px-3.5 py-3 rounded-xl bg-neutral-50 border border-neutral-100">
                    <div className="w-6 h-6 rounded-lg bg-primary-50 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-3.5 h-3.5 text-primary-600" />
                    </div>
                    <span className="text-xs font-medium text-neutral-600">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>

    {/* CTA */}
    <section className="py-24 sm:py-32 bg-surface">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="relative overflow-hidden card p-12 sm:p-16 bg-gradient-to-br from-primary-600 to-primary-800 border-primary-700 shadow-elevation-3"
        >
          {/* Subtle pattern overlay */}
          <div className="absolute inset-0 bg-dots opacity-20 pointer-events-none" />
          <div className="relative">
            <h2 className="text-2xl sm:text-3xl font-bold text-white font-display mb-5">
              Ready to Build Your Next App?
            </h2>
            <p className="text-primary-200 mb-10 max-w-md mx-auto text-base sm:text-lg leading-relaxed">
              Join thousands of developers already using AI to accelerate their development process.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/generate" className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl bg-white text-primary-700 text-sm font-semibold hover:bg-primary-50 transition-colors shadow-md">
                Get Started Now
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link to="/about" className="inline-flex items-center justify-center px-8 py-3.5 rounded-xl border border-primary-400/60 text-white text-sm font-semibold hover:bg-primary-700/50 transition-colors">
                Learn More
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  </AnimatedBackground>
)

export default Home
