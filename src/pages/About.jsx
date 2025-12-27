import React from 'react'
import { motion } from 'framer-motion'
import { 
  Bot, Brain, Cloud, Code, Users, Zap, 
  ArrowRight, CheckCircle, ExternalLink 
} from 'lucide-react'

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
    'Multiple AI model support (Claude, Llama, Titan)',
    'Complete project documentation',
    'Ready-to-deploy code structure',
    'WebSocket-based live updates',
    'Customizable agent selection'
  ]

  const agents = [
    {
      role: 'Product Manager',
      description: 'Creates comprehensive product requirements, user stories, and business analysis',
      responsibilities: ['Requirements gathering', 'User story creation', 'Competitive analysis', 'Success metrics']
    },
    {
      role: 'System Architect',
      description: 'Designs technical architecture, selects technology stack, and creates system specifications',
      responsibilities: ['Architecture design', 'Technology selection', 'System integration', 'Scalability planning']
    },
    {
      role: 'Project Manager',
      description: 'Creates project plans, manages timelines, and coordinates development activities',
      responsibilities: ['Project planning', 'Timeline management', 'Resource allocation', 'Risk assessment']
    },
    {
      role: 'Software Engineer',
      description: 'Provides technical implementation details, code structure, and development guidelines',
      responsibilities: ['Code architecture', 'Implementation details', 'Technical specifications', 'Best practices']
    },
    {
      role: 'QA Engineer',
      description: 'Creates comprehensive testing strategies, test cases, and quality assurance plans',
      responsibilities: ['Test strategy', 'Test case creation', 'Quality metrics', 'Automation planning']
    },
    {
      role: 'DevOps Engineer',
      description: 'Designs deployment strategies, infrastructure, and operational procedures',
      responsibilities: ['Deployment planning', 'Infrastructure design', 'Monitoring setup', 'CI/CD pipelines']
    }
  ]

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <div className="flex justify-center mb-6">
            <div className="relative">
              <Bot className="h-16 w-16 text-primary-600" />
              <Brain className="h-6 w-6 text-warning-500 absolute -top-1 -right-1" />
            </div>
          </div>
          
          <h1 className="text-4xl font-bold text-secondary-900 mb-6">
            About MetaGPT + Bedrock
          </h1>
          
          <p className="text-xl text-secondary-600 max-w-3xl mx-auto">
            A revolutionary platform that combines MetaGPT's multi-agent framework with AWS Bedrock's 
            foundation models to generate complete applications from natural language descriptions.
          </p>
        </motion.div>

        {/* How It Works */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-secondary-900 text-center mb-12">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="card text-center"
            >
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-600 font-bold text-lg">1</span>
              </div>
              <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                Describe Your App
              </h3>
              <p className="text-secondary-600">
                Simply describe your application idea in natural language. 
                Our system understands complex requirements and user needs.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="card text-center"
            >
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-600 font-bold text-lg">2</span>
              </div>
              <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                AI Agents Collaborate
              </h3>
              <p className="text-secondary-600">
                Multiple specialized AI agents work together, each contributing 
                their expertise like a real development team.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="card text-center"
            >
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-primary-600 font-bold text-lg">3</span>
              </div>
              <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                Get Complete App
              </h3>
              <p className="text-secondary-600">
                Receive a complete application with code, documentation, 
                tests, and deployment instructions ready for production.
              </p>
            </motion.div>
          </div>
        </section>
        {/* Technologies */}
        <section className="mb-16 bg-white rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-secondary-900 text-center mb-12">
            Built With Leading Technologies
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {technologies.map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center group"
              >
                <div className="w-16 h-16 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-primary-200 transition-colors">
                  <tech.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="font-semibold text-secondary-900 mb-2">
                  {tech.name}
                </h3>
                <p className="text-sm text-secondary-600 mb-3">
                  {tech.description}
                </p>
                <a
                  href={tech.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Learn More
                  <ExternalLink className="h-3 w-3 ml-1" />
                </a>
              </motion.div>
            ))}
          </div>
        </section>

        {/* AI Agents */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-secondary-900 text-center mb-12">
            Meet Our AI Agents
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.role}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="card hover:shadow-glow transition-shadow"
              >
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                  {agent.role}
                </h3>
                <p className="text-secondary-600 mb-4">
                  {agent.description}
                </p>
                <div>
                  <h4 className="text-sm font-medium text-secondary-700 mb-2">
                    Key Responsibilities:
                  </h4>
                  <ul className="space-y-1">
                    {agent.responsibilities.map((responsibility, idx) => (
                      <li key={idx} className="flex items-center text-sm text-secondary-600">
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
        <section className="mb-16 bg-secondary-50 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-secondary-900 text-center mb-12">
            Platform Features
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="flex items-center space-x-3"
              >
                <CheckCircle className="h-5 w-5 text-success-600 flex-shrink-0" />
                <span className="text-secondary-700">{feature}</span>
              </motion.div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-12 text-white"
        >
          <h2 className="text-3xl font-bold mb-4">
            Ready to Experience the Future of Development?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join the revolution in application development. Generate your first app 
            in minutes, not months.
          </p>
          <a
            href="/generate"
            className="btn bg-white text-primary-600 hover:bg-secondary-50 text-lg px-8 py-4 inline-flex items-center"
          >
            Start Building Now
            <ArrowRight className="ml-2 h-5 w-5" />
          </a>
        </motion.section>
      </div>
    </div>
  )
}

export default About