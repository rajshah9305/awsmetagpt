import React from 'react'
import { motion } from 'framer-motion'
import { 
  Bot, Brain, Cloud, Code, Users, Zap, 
  ArrowRight, CheckCircle, ExternalLink
} from 'lucide-react'
import { Link } from 'react-router-dom'
import AnimatedBackground from '../components/AnimatedBackground'
import GlassCard from '../components/GlassCard'

const About = () => {
  const technologies = [
    {
      name: 'MetaGPT',
      description: 'Multi-agent framework for collaborative AI development',
      icon: Users,
      link: 'https://github.com/geekan/MetaGPT'
    },
    {
      name: 'AWS Bedrock',
      description: 'Foundation models from leading AI companies',
      icon: Cloud,
      link: 'https://aws.amazon.com/bedrock/'
    },
    {
      name: 'React',
      description: 'Modern frontend framework for interactive UIs',
      icon: Code,
      link: 'https://react.dev/'
    },
    {
      name: 'FastAPI',
      description: 'High-performance Python web framework',
      icon: Zap,
      link: 'https://fastapi.tiangolo.com/'
    }
  ]

  const features = [
    'Natural language to application generation',
    'Multi-agent collaborative development',
    'Real-time generation progress tracking',
    'Multiple AI model support (Claude, Llama, Nova)',
    'Complete project documentation',
    'Ready-to-use code structure',
    'WebSocket-based live updates',
    'Customizable agent selection'
  ]

  const agents = [
    {
      role: 'Product Manager',
      description: 'Creates comprehensive product requirements, user stories, and business analysis',
      responsibilities: ['Requirements gathering', 'User story creation', 'Competitive analysis', 'Success metrics'],
      color: 'from-primary-400 to-primary-600'
    },
    {
      role: 'System Architect',
      description: 'Designs technical architecture, selects technology stack, and creates system specifications',
      responsibilities: ['Architecture design', 'Technology selection', 'System integration', 'Scalability planning'],
      color: 'from-secondary-400 to-secondary-600'
    },
    {
      role: 'Project Manager',
      description: 'Creates project plans, manages timelines, and coordinates development activities',
      responsibilities: ['Project planning', 'Timeline management', 'Resource allocation', 'Risk assessment'],
      color: 'from-success-400 to-success-600'
    },
    {
      role: 'Software Engineer',
      description: 'Provides technical implementation details, code structure, and development guidelines',
      responsibilities: ['Code architecture', 'Implementation details', 'Technical specifications', 'Best practices'],
      color: 'from-accent-400 to-accent-600'
    },
    {
      role: 'QA Engineer',
      description: 'Creates comprehensive testing strategies, test cases, and quality assurance plans',
      responsibilities: ['Test strategy', 'Test case creation', 'Quality metrics', 'Automation planning'],
      color: 'from-warning-400 to-warning-600'
    },
    {
      role: 'DevOps Engineer',
      description: 'Designs infrastructure and operational procedures',
      responsibilities: ['Infrastructure design', 'Monitoring setup', 'CI/CD pipelines', 'System architecture'],
      color: 'from-dark-400 to-dark-600'
    }
  ]

  const steps = [
    {
      number: '1',
      title: 'Describe Your App',
      description: 'Simply describe your application idea in natural language. Our system understands complex requirements and user needs.'
    },
    {
      number: '2',
      title: 'AI Agents Collaborate',
      description: 'Multiple specialized AI agents work together, each contributing their expertise like a real development team.'
    },
    {
      number: '3',
      title: 'Get Complete App',
      description: 'Receive a complete application with code, documentation, tests, and setup instructions ready for development.'
    }
  ]

  return (
    <AnimatedBackground variant="grid">
      <div className="min-h-screen py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow">
                  <Bot className="h-10 w-10 text-white" />
                </div>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                  className="absolute -top-2 -right-2"
                >
                  <Brain className="h-7 w-7 text-accent-500" />
                </motion.div>
              </div>
            </div>

            <h1 className="display-lg text-neutral-900 mb-6">
              About MetaGPT + Bedrock
            </h1>

            <p className="body-xl text-neutral-600 max-w-3xl mx-auto">
              A platform that combines MetaGPT&apos;s multi-agent framework with AWS Bedrock&apos;s
              foundation models to generate complete applications from natural language descriptions.
            </p>
          </motion.div>

          {/* How It Works */}
          <section className="mb-20">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="display-md text-neutral-900 text-center mb-12"
            >
              How It Works
            </motion.h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {steps.map((step, index) => (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <GlassCard hover={false} className="text-center h-full">
                    <div className="w-14 h-14 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-glow">
                      <span className="text-white font-display font-bold text-xl">{step.number}</span>
                    </div>
                    <h3 className="body-lg font-semibold text-neutral-900 mb-3">
                      {step.title}
                    </h3>
                    <p className="body-md text-neutral-600">
                      {step.description}
                    </p>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Technologies */}
          <section className="mb-20">
            <GlassCard hover={false} className="p-10">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="display-md text-neutral-900 text-center mb-12"
              >
                Built With Leading Technologies
              </motion.h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {technologies.map((tech, index) => (
                  <motion.div
                    key={tech.name}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="text-center group"
                  >
                    <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-gradient-to-br group-hover:from-primary-400 group-hover:to-secondary-500 transition-all duration-300 shadow-elevation-1">
                      {React.createElement(tech.icon, { className: "h-8 w-8 text-primary-600 group-hover:text-white transition-colors duration-300" })}
                    </div>
                    <h3 className="label text-neutral-900 mb-2">
                      {tech.name}
                    </h3>
                    <p className="caption text-neutral-600 mb-3">
                      {tech.description}
                    </p>
                    <a
                      href={tech.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-primary-600 hover:text-primary-700 caption font-medium"
                    >
                      Learn More
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </a>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </section>

          {/* AI Agents */}
          <section className="mb-20">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="display-md text-neutral-900 text-center mb-12"
            >
              Meet Our AI Agents
            </motion.h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.role}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="card hover:shadow-glow transition-all duration-300 hover:-translate-y-1"
                >
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-4 shadow-elevation-1`}>
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="body-lg font-semibold text-neutral-900 mb-2">
                    {agent.role}
                  </h3>
                  <p className="body-md text-neutral-600 mb-4">
                    {agent.description}
                  </p>
                  <div>
                    <h4 className="caption text-neutral-700 mb-2 font-semibold">
                      Key Responsibilities:
                    </h4>
                    <ul className="space-y-1">
                      {agent.responsibilities.map((responsibility, idx) => (
                        <li key={idx} className="flex items-center caption text-neutral-600">
                          <CheckCircle className="h-3 w-3 text-success-600 mr-2 flex-shrink-0" />
                          {responsibility}
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Features */}
          <section className="mb-20">
            <GlassCard hover={false} className="p-10">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="display-md text-neutral-900 text-center mb-12"
              >
                Platform Features
              </motion.h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: index * 0.05 }}
                    className="flex items-center space-x-3"
                  >
                    <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0" />
                    <span className="body-md text-neutral-700">{feature}</span>
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </section>

          {/* CTA */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard hover={false} className="text-center bg-gradient-to-br from-primary-500/10 to-secondary-500/10 border-primary-400/20 p-12">
              <h2 className="display-md text-neutral-900 mb-4">
                Ready to Experience the Future of Development?
              </h2>
              <p className="body-xl text-neutral-600 mb-8 max-w-2xl mx-auto">
                Join the revolution in application development. Generate your first app
                in minutes, not months.
              </p>
              <Link
                to="/generate"
                className="btn-primary body-lg px-8 py-4 inline-flex items-center shadow-glow"
              >
                <span className="relative z-10">Start Building Now</span>
                <ArrowRight className="ml-2 h-5 w-5 relative z-10" />
              </Link>
            </GlassCard>
          </motion.section>
        </div>
      </div>
    </AnimatedBackground>
  )
}

export default About
