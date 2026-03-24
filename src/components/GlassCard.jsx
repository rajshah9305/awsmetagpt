import { motion } from 'framer-motion'

const GlassCard = ({ children, className = '', hover = true, onClick, ...props }) => {
  const base = `card p-6 ${hover ? 'hover:shadow-md hover:border-neutral-300' : ''} ${onClick ? 'cursor-pointer' : ''} ${className}`

  if (onClick) {
    return (
      <motion.button
        className={base}
        whileTap={hover ? { scale: 0.99 } : {}}
        onClick={onClick}
        {...props}
      >
        {children}
      </motion.button>
    )
  }

  return (
    <div className={base} {...props}>
      {children}
    </div>
  )
}

export default GlassCard
