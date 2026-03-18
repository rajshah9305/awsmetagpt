import { motion } from 'framer-motion'

const AnimatedBackground = ({ children, className = '' }) => {
  return (
    <div className={`relative min-h-screen mesh-gradient ${className}`}>
      {/* Soft ambient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-[600px] h-[600px] bg-primary-400/6 rounded-full blur-3xl"
          animate={{ x: [0, 60, 0], y: [0, -60, 0] }}
          transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
          style={{ top: '-10%', left: '-5%' }}
        />
        <motion.div
          className="absolute w-[500px] h-[500px] bg-secondary-500/6 rounded-full blur-3xl"
          animate={{ x: [0, -50, 0], y: [0, 80, 0] }}
          transition={{ duration: 28, repeat: Infinity, ease: 'easeInOut' }}
          style={{ top: '40%', right: '-5%' }}
        />
        <motion.div
          className="absolute w-[400px] h-[400px] bg-accent-400/4 rounded-full blur-3xl"
          animate={{ x: [0, 40, 0], y: [0, -40, 0] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          style={{ bottom: '10%', left: '25%' }}
        />
      </div>

      <div className="relative z-10">{children}</div>
    </div>
  )
}

export default AnimatedBackground
