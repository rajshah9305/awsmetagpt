import React from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, Users, Code, Cloud, Zap, ArrowRight, 
  CheckCircle, Sparkles, Rocket, Bot, 
  Cpu, GitBranch, Database, Shield
} from 'lucide-react'

import AnimatedBackground from '../components/AnimatedBackground'
import HeroSection from '../components/HeroSection'
import FeatureCard from '../components/FeatureCard'
import GlassCard from '../components/GlassCard'
import { Link } from 'react-router-dom'

const Home = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Generation',
      description: 'Leverage cutting-edge AWS Bedrock foundation models for intelligent, context-aware application creation.'
    },
    {
      icon: Users,
      title: 'Multi-Agent Collaboration',
      description: 'Watch MetaGPT agents work together like a real development team - each with specialized expertise.'
    },
    {
      icon: Code,
      title: 'Complete Applications',
      description: 'Generate production-ready, full-stack applications with comprehensive documentation and tests.'
    },
    {
      icon: Cloud,
      title: 'Cloud-Native Architecture',
      description: 'Built for modern development with scalability, security, and best practices baked in.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'From idea to working prototype in minutes. No more weeks of development for MVPs.'
    },
    {
      icon: Shield,
      title: 'Enterprise Ready',
      description: 'Security-first design with industry-standard practices and compliance considerations.'
    }
  ]

  const benefits = [
    'Natural language to working application',
    'Multiple AI models for different tasks',
    'Real-time generation progress tracking',
    'Complete project documentation',
    'Ready-to-deploy code structure',
    'No coding experience required',
    'Customizable tech stack options',
    'Built-in testing & quality assurance'
  ]

  const techStack = [
    { icon: Cpu, label: 'AWS Bedrock' },
    { icon: Bot, label: 'MetaGPT' },
    { icon: GitBranch, label: 'Git Ready' },
    { icon: Database, label: 'Full Stack' },
  ]

  return (
    <AnimatedBackground variant="default">
      {/* Hero Section */}
      <HeroSection />

      {/* Features Section */}
      <section className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="display-md text-neutral-900 mb-4">
              Powered by Advanced AI
            </h2>
            <p className="body-xl text-neutral-600 max-w-2xl mx-auto">
              Combining MetaGPT's multi-agent framework with AWS Bedrock's foundation models
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <FeatureCard
                key={feature.title}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                delay={index * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section with Glass Card */}
      <section className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="display-md text-neutral-900 mb-6">
                Why Choose Our Platform?
              </h2>
              <p className="body-lg text-neutral-600 mb-8">
                Experience the future of software development with AI-powered automation that doesn't compromise on quality.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={benefit}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: index * 0.05 }}
                    className="flex items-start space-x-3"
                  >
                    <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0 mt-1" />
                    <span className="body-md text-neutral-700">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <GlassCard className="overflow-hidden">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="flex -space-x-3">
                    {[
                      { icon: Bot, color: 'from-primary-400 to-primary-600' },
                      { icon: Code, color: 'from-success-400 to-success-600' },
                      { icon: Zap, color: 'from-accent-400 to-accent-600' },
                    ].map((agent, idx) => (
                      <motion.div
                        key={idx}
                        className={`w-10 h-10 bg-gradient-to-br ${agent.color} rounded-full flex items-center justify-center border-2 border-white shadow-lg`}
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 2, delay: idx * 0.2, repeat: Infinity }}
                      >
                        {React.createElement(agent.icon, { className: "h-5 w-5 text-white" })}
                      </motion.div>
                    ))}
                  </div>
                  <div>
                    <div className="badge-glass">
                      <span className="status-indicator inline-block w-2 h-2 bg-success-500 rounded-full mr-2"></span>
                      Agents Collaborating
                    </div>
                  </div>
                </div>
                <h3 className="body-xl font-display font-semibold text-neutral-900 mb-3">
                  Real-time Generation
                </h3>
                <p className="body-md text-neutral-600 mb-6">
                  Watch as different AI agents work together to build your application, 
                  each contributing their specialized expertise in real-time.
                </p>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between body-sm mb-2">
                      <span className="text-neutral-700 font-medium">Architecture Design</span>
                      <span className="text-primary-600 font-semibold">100%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill w-full"></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between body-sm mb-2">
                      <span className="text-neutral-700 font-medium">Code Generation</span>
                      <span className="text-primary-600 font-semibold">75%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div 
                        className="progress-fill" 
                        initial={{ width: 0 }}
                        animate={{ width: '75%' }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                      ></motion.div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between body-sm mb-2">
                      <span className="text-neutral-700 font-medium">Testing & QA</span>
                      <span className="text-neutral-500 font-semibold">45%</span>
                    </div>
                    <div className="progress-bar">
                      <motion.div 
                        className="progress-fill" 
                        initial={{ width: 0 }}
                        animate={{ width: '45%' }}
                        transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
                      ></motion.div>
                    </div>
                  </div>
                </div>
              </GlassCard>

              {/* Floating tech stack badges */}
              <div className="absolute -bottom-6 -right-6 grid grid-cols-2 gap-3">
                {techStack.map((tech, idx) => (
                  <motion.div
                    key={tech.label}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: idx * 0.1 }}
                    className="badge-glass backdrop-blur-lg px-3 py-2 shadow-elevation-2"
                  >
                    {React.createElement(tech.icon, { className: "w-4 h-4 inline-block mr-2 text-primary-600" })}
                    <span className="overline">{tech.label}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard className="text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/10 border-primary-400/20 p-12">
              <motion.div
                animate={{ rotate: [0, 10, 0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="inline-block mb-6"
              >
                <Rocket className="h-16 w-16 text-primary-600" />
              </motion.div>
              <h2 className="display-md text-neutral-900 mb-4">
                Ready to Build Your Next App?
              </h2>
              <p className="body-xl text-neutral-600 mb-8 max-w-2xl mx-auto">
                Join thousands of developers who are already using AI to accelerate their development process and bring ideas to life faster than ever.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/generate" className="btn-primary body-lg px-10 py-4 shadow-glow-lg">
                  <span className="relative z-10">Get Started Now</span>
                  <ArrowRight className="ml-2 h-6 w-6 relative z-10 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link to="/about" className="btn-outline body-lg px-10 py-4">
                  Learn More
                </Link>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </section>
    </AnimatedBackground>
  )
}

export default Home