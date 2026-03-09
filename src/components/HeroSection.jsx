import { motion } from 'framer-motion'
import { Sparkles, ArrowRight, Bot, Code, Zap, Brain } from 'lucide-react'
import { Link } from 'react-router-dom'

const FloatingAgent = ({ icon: Icon, colorClass, delay, className }) => (
  <motion.div
    className={`hidden lg:flex absolute w-12 h-12 rounded-2xl ${colorClass} items-center justify-center shadow-elevation-3 ${className}`}
    animate={{
      y: [0, -16, 0],
      rotate: [0, 5, 0, -5, 0],
    }}
    transition={{
      duration: 4 + delay,
      repeat: Infinity,
      ease: 'easeInOut',
      delay,
    }}
  >
    <Icon className="w-6 h-6 text-white" />
  </motion.div>
)

const HeroSection = () => {
  return (
    <section className="relative py-16 sm:py-24 lg:py-32 overflow-hidden">
      {/* Floating agent icons — only visible on large screens to avoid mobile overflow */}
      <div className="absolute inset-0 pointer-events-none">
        <FloatingAgent icon={Bot} colorClass="bg-gradient-to-br from-primary-400 to-primary-600" delay={0} className="left-[8%] top-[20%]" />
        <FloatingAgent icon={Brain} colorClass="bg-gradient-to-br from-secondary-400 to-secondary-600" delay={1} className="right-[8%] top-[15%]" />
        <FloatingAgent icon={Code} colorClass="bg-gradient-to-br from-success-400 to-success-600" delay={0.5} className="left-[5%] bottom-[25%]" />
        <FloatingAgent icon={Zap} colorClass="bg-gradient-to-br from-accent-400 to-accent-600" delay={1.5} className="right-[6%] bottom-[30%]" />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div
              className="inline-flex items-center gap-2 mb-6 sm:mb-8"
              whileHover={{ scale: 1.05 }}
            >
              <span className="badge-glass backdrop-blur-md px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm">
                <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4 inline-block mr-1.5 text-accent-500" />
                Powered by AWS Bedrock &amp; MetaGPT
              </span>
            </motion.div>

            {/* Main Heading */}
            <h1 className="display-xl font-display font-bold text-neutral-900 mb-4 sm:mb-6 leading-tight">
              Transform Ideas Into
              <span className="block text-gradient mt-1 sm:mt-2">
                Production-Ready Apps
              </span>
            </h1>

            {/* Subheading */}
            <p className="body-lg sm:body-xl text-neutral-600 max-w-2xl mx-auto mb-8 sm:mb-10 leading-relaxed">
              Harness the power of AI agents collaborating with AWS Bedrock to generate
              complete, scalable applications from natural language descriptions.
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center"
          >
            <Link to="/generate" className="btn-primary body-md px-7 py-3.5 sm:px-8 sm:py-4 shadow-glow w-full sm:w-auto justify-center">
              <span className="relative z-10">Start Building Now</span>
              <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
            </Link>
            <Link to="/about" className="btn-outline body-md px-7 py-3.5 sm:px-8 sm:py-4 w-full sm:w-auto justify-center">
              Explore Features
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-12 sm:mt-16 grid grid-cols-3 gap-4 sm:gap-8 max-w-2xl mx-auto"
          >
            {[
              { value: '10,000+', label: 'Apps Generated' },
              { value: '99.9%', label: 'Success Rate' },
              { value: '<5min', label: 'Generation Time' },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="text-center"
              >
                <div className="text-xl sm:text-2xl lg:text-3xl font-display font-bold text-gradient mb-0.5 sm:mb-1">
                  {stat.value}
                </div>
                <div className="text-xs sm:text-xs font-semibold uppercase tracking-wider text-neutral-500">
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