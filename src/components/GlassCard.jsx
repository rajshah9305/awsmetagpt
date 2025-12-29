import { motion } from 'framer-motion'

const GlassCard = ({ 
  children, 
  className = '', 
  hover = true,
  onClick,
  variant = 'default',
  ...props 
}) => {
  const variants = {
    default: 'glass-card',
    dark: 'glass-card-dark',
    primary: 'glass-card-primary',
  }

  const baseClasses = `${variants[variant]} p-6 ${hover ? 'hover-lift cursor-pointer' : ''} ${className}`

  if (onClick) {
    return (
      <motion.button
        className={baseClasses}
        whileHover={hover ? { scale: 1.02, y: -4 } : {}}
        whileTap={hover ? { scale: 0.98 } : {}}
        onClick={onClick}
        {...props}
      >
        {children}
      </motion.button>
    )
  }

  return (
    <motion.div
      className={baseClasses}
      whileHover={hover ? { scale: 1.02, y: -4 } : {}}
      {...props}
    >
      {children}
    </motion.div>
  )
}

export default GlassCard