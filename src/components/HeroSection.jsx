import { motion } from 'framer-motion'
import { ArrowRight, Cpu, Shield, Zap, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => (
  <section className="relative py-28 sm:py-36 lg:py-44 overflow-hidden bg-white">
    {/* Dot background */}
    <div className="absolute inset-0 bg-dots opacity-60 pointer-events-none" />

    {/* Radial glow top */}
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        background: 'radial-gradient(ellipse 90% 60% at 50% -5%, rgba(37,99,235,0.07) 0%, transparent 65%)',
      }}
    />

    {/* Soft bottom fade into surface */}
    <div
      className="absolute bottom-0 left-0 right-0 h-32 pointer-events-none"
      style={{ background: 'linear-gradient(to bottom, transparent, #F8FAFC)' }}
    />

    <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center">

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center gap-2 mb-10"
        >
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold bg-primary-50 text-primary-700 ring-1 ring-primary-200 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse" />
            Powered by AWS Bedrock &amp; MetaGPT
          </span>
        </motion.div>

        {/* Heading */}
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08 }}
          className="font-display text-5xl sm:text-6xl lg:text-7xl xl:text-[5rem] font-bold text-neutral-900 mb-7 tracking-tight leading-[1.06]"
        >
          Transform Ideas Into
          <span className="block text-gradient mt-2">Production-Ready Apps</span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.16 }}
          className="text-lg sm:text-xl text-neutral-500 max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          Harness specialized AI agents collaborating with AWS Bedrock foundation models
          to generate complete, scalable applications from natural language.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.24 }}
          className="flex flex-col sm:flex-row gap-3 justify-center items-center"
        >
          <Link to="/generate" className="btn-primary px-8 py-3.5 text-sm w-full sm:w-auto gap-2 shadow-md hover:shadow-lg">
            <Sparkles className="h-4 w-4" />
            Start Building
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/about" className="btn-secondary px-8 py-3.5 text-sm w-full sm:w-auto">
            Learn More
          </Link>
        </motion.div>

        {/* Trust indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.38 }}
          className="mt-16 flex flex-wrap justify-center gap-8 sm:gap-12 text-xs text-neutral-400 font-medium"
        >
          {[
            { icon: Shield, label: 'Enterprise Security' },
            { icon: Zap,    label: 'Sub-5 Minute Generation' },
            { icon: Cpu,    label: 'Multi-Model Support' },
          ].map(({ icon: Icon, label }) => (
            <span key={label} className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-neutral-100 flex items-center justify-center">
                <Icon className="h-3.5 w-3.5 text-neutral-400" />
              </span>
              {label}
            </span>
          ))}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.48 }}
          className="mt-14 pt-10 border-t border-neutral-100 grid grid-cols-3 gap-8 max-w-sm mx-auto"
        >
          {[
            { value: '10K+',  label: 'Apps Generated' },
            { value: '99.9%', label: 'Uptime' },
            { value: '<5min', label: 'Avg. Build Time' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-bold text-neutral-900 font-display">{stat.value}</div>
              <div className="text-xs text-neutral-400 mt-1.5">{stat.label}</div>
            </div>
          ))}
        </motion.div>

      </div>
    </div>
  </section>
)

export default HeroSection
