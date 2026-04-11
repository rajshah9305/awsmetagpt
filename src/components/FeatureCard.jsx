import { motion } from 'framer-motion'

const FeatureCard = ({ icon: Icon, title, description, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.45, delay }}
    className="h-full"
  >
    <div className="card p-7 sm:p-8 h-full hover:shadow-elevation-2 hover:border-neutral-300 hover:-translate-y-0.5 transition-all duration-250 group">
      <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center mb-6 group-hover:from-primary-100 group-hover:to-primary-200 transition-all duration-200 shadow-sm">
        <Icon className="h-5 w-5 text-primary-600" />
      </div>
      <h3 className="text-sm font-semibold text-neutral-900 mb-2.5">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed">{description}</p>
    </div>
  </motion.div>
)

export default FeatureCard
