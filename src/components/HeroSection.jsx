import { motion } from 'framer-motion'
import { ArrowRight, Cpu, Shield, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => (
  <section className="relative py-24 sm:py-32 lg:py-40 overflow-hidden bg-white border-b border-neutral-200">
    {/* Dot background */}
    <div className="absolute inset-0 bg-dots opacity-50 pointer-events-none" />

    {/* Subtle radial glow */}
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        background: 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(37,99,235,0.06) 0%, transparent 70%)',
      }}
    />

    <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center">

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center gap-2 mb-8"
        >
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-primary-50 text-primary-700 ring-1 ring-primary-200">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse" />
            Powered by AWS Bedrock &amp; MetaGPT
          </span>
        </motion.div>

        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.08 }}
          className="font-display text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-neutral-900 mb-6 tracking-tight leading-[1.08]"
        >
          Transform Ideas Into
          <span className="block text-primary-600 mt-2">Production-Ready Apps</span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="text-lg sm:text-xl text-neutral-500 max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Harness specialized AI agents collaborating with AWS Bedrock foundation models
          to generate complete, scalable applications from natural language.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.22 }}
          className="flex flex-col sm:flex-row gap-3 justify-center items-center"
        >
          <Link to="/generate" className="btn-primary px-7 py-3 text-sm w-full sm:w-auto">
            Start Building
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <Link to="/about" className="btn-secondary px-7 py-3 text-sm w-full sm:w-auto">
            Learn More
          </Link>
        </motion.div>

        {/* Trust indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.35 }}
          className="mt-14 flex flex-wrap justify-center gap-6 sm:gap-10 text-xs text-neutral-400 font-medium"
        >
          {[
            { icon: Shield, label: 'Enterprise Security' },
            { icon: Zap,    label: 'Sub-5 Minute Generation' },
            { icon: Cpu,    label: 'Multi-Model Support' },
          ].map(({ icon: Icon, label }) => (
            <span key={label} className="flex items-center gap-1.5">
              <Icon className="h-3.5 w-3.5 text-neutral-400" />
              {label}
            </span>
          ))}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.45 }}
          className="mt-12 pt-10 border-t border-neutral-200 grid grid-cols-3 gap-6 max-w-sm mx-auto"
        >
          {[
            { value: '10K+',  label: 'Apps Generated' },
            { value: '99.9%', label: 'Uptime' },
            { value: '<5min', label: 'Avg. Build Time' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold text-neutral-900 font-display">{stat.value}</div>
              <div className="text-xs text-neutral-400 mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>

      </div>
    </div>
  </section>
)

export default HeroSection
