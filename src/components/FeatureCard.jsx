import { motion } from 'framer-motion'

const FeatureCard = ({ icon: Icon, title, description, delay = 0, gradient = false }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="group"
    >
      <div className="card-interactive h-full">
        <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-5 ${
          gradient 
            ? 'bg-gradient-to-br from-primary-400 to-secondary-500 shadow-glow' 
            : 'bg-primary-100 group-hover:bg-gradient-to-br group-hover:from-primary-400 group-hover:to-secondary-500'
        } transition-all duration-300`}>
          <Icon className={`h-7 w-7 ${gradient ? 'text-white' : 'text-primary-600 group-hover:text-white'} transition-colors duration-300`} />
        </div>
        <h3 className="body-lg font-semibold text-neutral-900 mb-2 group-hover:text-primary-600 transition-colors">
          {title}
        </h3>
        <p className="body-md text-neutral-600">
          {description}
        </p>
      </div>
    </motion.div>
  )
}

export default FeatureCard