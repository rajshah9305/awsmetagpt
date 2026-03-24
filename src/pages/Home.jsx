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
    <section className="py-20 sm:py-28 bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="mb-12"
        >
          <p className="section-label mb-3">Capabilities</p>
          <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-display mb-3">Powered by Advanced AI</h2>
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
    <section className="py-20 sm:py-28 bg-white border-y border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <p className="section-label mb-3">Why Choose Us</p>
            <h2 className="text-2xl sm:text-3xl font-bold text-neutral-900 font-display mb-5">
              Built for Modern Development Teams
            </h2>
            <p className="text-neutral-500 mb-10 leading-relaxed text-base sm:text-lg">
              Experience the future of software development with AI-powered automation
              that doesn't compromise on quality or security.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {benefits.map((b, i) => (
                <motion.div
                  key={b}
                  initial={{ opacity: 0, x: -12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: i * 0.04 }}
                  className="flex items-center gap-2.5"
                >
                  <CheckCircle className="h-4 w-4 text-success-500 flex-shrink-0" />
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
            <div className="card p-7 sm:p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-success-500 animate-pulse" />
                  <span className="text-xs font-semibold text-neutral-600">Agents Collaborating</span>
                </div>
                <span className="badge-primary">Live</span>
              </div>

              <h3 className="text-base font-semibold text-neutral-900 mb-2">Real-time Generation</h3>
              <p className="text-sm text-neutral-500 mb-7 leading-relaxed">
                Watch AI agents work together to build your application, each contributing
                specialized expertise in real-time.
              </p>

              <div className="space-y-4">
                {[
                  { label: 'Architecture Design', pct: 100 },
                  { label: 'Code Generation',     pct: 75 },
                  { label: 'Testing & QA',        pct: 45 },
                ].map(({ label, pct }) => (
                  <div key={label}>
                    <div className="flex justify-between text-xs mb-2">
                      <span className="font-medium text-neutral-700">{label}</span>
                      <span className="text-neutral-500">{pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div
                        className="progress-fill"
                        initial={{ width: 0 }}
                        whileInView={{ width: `${pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-7 pt-5 border-t border-neutral-100 grid grid-cols-2 gap-2.5">
                {techStack.map(({ icon: Icon, label }) => (
                  <div key={label} className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-neutral-50 border border-neutral-200">
                    <Icon className="w-3.5 h-3.5 text-primary-600 flex-shrink-0" />
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
    <section className="py-20 sm:py-28 bg-surface">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="card p-10 sm:p-16 bg-primary-600 border-primary-700"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-white font-display mb-4">
            Ready to Build Your Next App?
          </h2>
          <p className="text-primary-200 mb-10 max-w-md mx-auto text-base sm:text-lg">
            Join thousands of developers already using AI to accelerate their development process.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/generate" className="inline-flex items-center justify-center px-7 py-3 rounded-lg bg-white text-primary-700 text-sm font-semibold hover:bg-primary-50 transition-colors shadow-sm">
              Get Started Now
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link to="/about" className="inline-flex items-center justify-center px-7 py-3 rounded-lg border border-primary-400 text-white text-sm font-semibold hover:bg-primary-700 transition-colors">
              Learn More
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  </AnimatedBackground>
)

export default Home
