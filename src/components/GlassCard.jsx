import { motion } from 'framer-motion'

const GlassCard = ({ children, className = '', hover = true, onClick, ...props }) => {
  const base = `glass-card p-6 ${hover ? 'hover:-translate-y-0.5 hover:shadow-elevation-3' : ''} ${onClick ? 'cursor-pointer' : ''} ${className}`

  if (onClick) {
    return (
      <motion.button
        className={base}
        whileHover={hover ? { scale: 1.01 } : {}}
        whileTap={hover ? { scale: 0.99 } : {}}
        onClick={onClick}
        {...props}
      >
        {children}
      </motion.button>
    )
  }

  return (
    <motion.div className={base} {...props}>
      {children}
    </motion.div>
  )
}

export default GlassCard
