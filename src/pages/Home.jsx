import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Bot, Zap, Code, Users, Rocket, ArrowRight, 
  CheckCircle, Sparkles, Brain, Cloud 
} from 'lucide-react'

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Generation',
      description: 'Leverage AWS Bedrock\'s foundation models for intelligent app creation'
    },
    {
      icon: Users,
      title: 'Multi-Agent Collaboration',
      description: 'MetaGPT agents work together like a real development team'
    },
    {
      icon: Code,
      title: 'Complete Applications',
      description: 'Generate full-stack applications with documentation and tests'
    },
    {
      icon: Cloud,
      title: 'Cloud-Native',
      description: 'Built for modern cloud deployment and scalability'
    }
  ]

  const benefits = [
    'Natural language to working application',
    'Multiple AI models for different tasks',
    'Real-time generation progress',
    'Complete project documentation',
    'Ready-to-deploy code structure',
    'No coding experience required'
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="mb-8"
            >
              <div className="flex justify-center mb-6">
                <div className="relative">
                  <Bot className="h-16 w-16 text-primary-600" />
                  <Sparkles className="h-6 w-6 text-warning-500 absolute -top-1 -right-1 animate-pulse" />
                </div>
              </div>
              
              <h1 className="text-4xl sm:text-6xl font-bold text-secondary-900 mb-6">
                From Idea to
                <span className="text-gradient block">Working App</span>
                in Minutes
              </h1>
              
              <p className="text-xl text-secondary-600 max-w-3xl mx-auto mb-8">
                Describe your app in plain English and watch as MetaGPT agents collaborate 
                with AWS Bedrock AI models to generate complete, production-ready applications.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link to="/generate" className="btn-primary text-lg px-8 py-4">
                Start Generating
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link to="/about" className="btn-outline text-lg px-8 py-4">
                Learn More
              </Link>
            </motion.div>
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-secondary-900 mb-4">
              Powered by Advanced AI
            </h2>
            <p className="text-lg text-secondary-600 max-w-2xl mx-auto">
              Combining MetaGPT's multi-agent framework with AWS Bedrock's foundation models
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card text-center hover:shadow-glow transition-shadow"
              >
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mb-4">
                  <feature.icon className="h-6 w-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-secondary-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-secondary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-secondary-900 mb-6">
                Why Choose Our Platform?
              </h2>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0" />
                    <span className="text-secondary-700">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="card bg-gradient-to-br from-primary-50 to-secondary-50 p-8">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="flex -space-x-2">
                    <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="w-8 h-8 bg-success-500 rounded-full flex items-center justify-center">
                      <Code className="h-4 w-4 text-white" />
                    </div>
                    <div className="w-8 h-8 bg-warning-500 rounded-full flex items-center justify-center">
                      <Zap className="h-4 w-4 text-white" />
                    </div>
                  </div>
                  <span className="text-sm font-medium text-secondary-600">
                    Agents Collaborating
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                  Real-time Generation
                </h3>
                <p className="text-secondary-600 mb-4">
                  Watch as different AI agents work together to build your application, 
                  each contributing their specialized expertise.
                </p>
                <div className="progress-bar">
                  <div className="progress-fill w-3/4"></div>
                </div>
                <p className="text-sm text-secondary-500 mt-2">Generation in progress...</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Rocket className="h-12 w-12 text-white mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Build Your Next App?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Join thousands of developers who are already using AI to accelerate their development process.
            </p>
            <Link to="/generate" className="btn bg-white text-primary-600 hover:bg-secondary-50 text-lg px-8 py-4">
              Get Started Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Home