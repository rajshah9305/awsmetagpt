import { motion } from 'framer-motion'

const FeatureCard = ({ icon: Icon, title, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, delay }}
    className="group"
  >
    <div className="card-interactive h-full p-6">
      <div className="w-12 h-12 rounded-xl bg-primary-50 group-hover:bg-gradient-to-br group-hover:from-primary-400 group-hover:to-secondary-500 flex items-center justify-center mb-5 transition-all duration-300 shadow-sm">
        <Icon className="h-6 w-6 text-primary-500 group-hover:text-white transition-colors duration-300" />
      </div>
      <h3 className="text-base font-semibold text-neutral-900 mb-2 group-hover:text-primary-600 transition-colors">
        {title}
      </h3>
      <p className="text-sm text-neutral-500 leading-relaxed">
        {description}
      </p>
    </div>
  </motion.div>
)

export default FeatureCard
