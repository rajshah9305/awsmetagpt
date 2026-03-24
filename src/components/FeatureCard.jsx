import { motion } from 'framer-motion'

const FeatureCard = ({ icon: Icon, title, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.4, delay }}
    className="h-full"
  >
    <div className="card p-6 sm:p-7 h-full hover:shadow-md hover:border-neutral-300 transition-all duration-200 group">
      <div className="w-11 h-11 rounded-xl bg-primary-50 flex items-center justify-center mb-5 group-hover:bg-primary-100 transition-colors duration-200">
        <Icon className="h-5 w-5 text-primary-600" />
      </div>
      <h3 className="text-sm font-semibold text-neutral-900 mb-2">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed">{description}</p>
    </div>
  </motion.div>
)

export default FeatureCard
