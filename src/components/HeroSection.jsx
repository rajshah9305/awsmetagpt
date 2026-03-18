import { motion } from 'framer-motion'
import { Sparkles, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => {
  return (
    <section className="relative py-24 sm:py-32 lg:py-40 overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">

          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 mb-8"
          >
            <span className="badge-glass px-4 py-2 text-sm">
              <Sparkles className="w-3.5 h-3.5 inline-block mr-1.5 text-accent-500" />
              Powered by AWS Bedrock &amp; MetaGPT
            </span>
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="display-xl font-display font-bold text-neutral-900 mb-6 leading-tight"
          >
            Transform Ideas Into
            <span className="block text-gradient mt-2">
              Production-Ready Apps
            </span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="body-lg text-neutral-500 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Harness the power of AI agents collaborating with AWS Bedrock to generate
            complete, scalable applications from natural language descriptions.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-3 justify-center items-center"
          >
            <Link to="/generate" className="btn-primary body-md px-8 py-4 shadow-glow w-full sm:w-auto">
              <span className="relative z-10">Start Building Now</span>
              <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
            </Link>
            <Link to="/about" className="btn-outline body-md px-8 py-4 w-full sm:w-auto">
              Explore Features
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-16 sm:mt-20 grid grid-cols-3 gap-6 sm:gap-12 max-w-md mx-auto"
          >
            {[
              { value: '10,000+', label: 'Apps Generated' },
              { value: '99.9%',   label: 'Success Rate' },
              { value: '<5min',   label: 'Generation Time' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 + i * 0.1 }}
                className="text-center"
              >
                <div className="text-2xl sm:text-3xl font-display font-bold text-gradient mb-1">
                  {stat.value}
                </div>
                <div className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>

        </div>
      </div>
    </section>
  )
}

export default HeroSection
