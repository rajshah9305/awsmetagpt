import { motion } from 'framer-motion'
import { Sparkles, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => {
  return (
    <section className="relative py-20 sm:py-32 overflow-hidden">
      {/* Floating illustrations */}
      <motion.div
        className="absolute top-20 left-10 opacity-10"
        animate={{ y: [0, -20, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      >
        <img 
          src="/illustrations/neural-network-1.svg" 
          alt="" 
          className="w-64 h-64"
          style={{ width: '16rem', height: '16rem' }}
        />
      </motion.div>
      
      <motion.div
        className="absolute bottom-20 right-10 opacity-10"
        animate={{ y: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      >
        <img 
          src="/illustrations/ai-brain.svg" 
          alt="" 
          className="w-72 h-72"
          style={{ width: '18rem', height: '18rem' }}
        />
      </motion.div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <motion.div 
              className="inline-flex items-center gap-2 mb-8"
              whileHover={{ scale: 1.05 }}
            >
              <span className="badge-glass backdrop-blur-md px-4 py-2">
                <Sparkles className="w-4 h-4 inline-block mr-2 text-accent-500" />
                Powered by AWS Bedrock & MetaGPT
              </span>
            </motion.div>
            
            {/* Main Heading */}
            <h1 className="display-xl font-display font-bold text-neutral-900 mb-6 leading-tight">
              Transform Ideas Into
              <span className="block text-gradient mt-2">
                Production-Ready Apps
              </span>
            </h1>
            
            {/* Subheading */}
            <p className="body-xl text-neutral-600 max-w-3xl mx-auto mb-10 leading-relaxed">
              Harness the power of AI agents collaborating with AWS Bedrock to generate 
              complete, scalable applications from natural language descriptions.
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link to="/generate" className="btn-primary body-md px-8 py-4 shadow-glow">
              <span className="relative z-10">Start Building Now</span>
              <ArrowRight className="ml-2 h-5 w-5 relative z-10 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/about" className="btn-outline body-md px-8 py-4">
              Explore Features
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-3xl mx-auto"
          >
            {[
              { value: '10,000+', label: 'Apps Generated' },
              { value: '99.9%', label: 'Success Rate' },
              { value: '<5min', label: 'Avg. Generation Time' },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="text-center"
              >
                <div className="display-sm font-display font-bold text-gradient mb-1">
                  {stat.value}
                </div>
                <div className="overline text-neutral-600">
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