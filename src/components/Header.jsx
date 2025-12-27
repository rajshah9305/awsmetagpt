import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Bot, Zap, Menu, X } from 'lucide-react'

const Header = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = React.useState(false)

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Generate', href: '/generate' },
    { name: 'About', href: '/about' },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-secondary-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="relative">
              <Bot className="h-8 w-8 text-primary-600 group-hover:text-primary-700 transition-colors" />
              <Zap className="h-4 w-4 text-warning-500 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div className="hidden sm:block">
              <span className="text-xl font-bold text-gradient">MetaGPT</span>
              <span className="text-sm text-secondary-600 ml-1">+ Bedrock</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`relative px-3 py-2 text-sm font-medium transition-colors ${
                  isActive(item.href)
                    ? 'text-primary-600'
                    : 'text-secondary-600 hover:text-secondary-900'
                }`}
              >
                {item.name}
                {isActive(item.href) && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-x-0 -bottom-px h-0.5 bg-primary-600"
                    initial={false}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </Link>
            ))}
          </nav>

          {/* CTA Button */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              to="/generate"
              className="btn-primary"
            >
              Start Generating
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 transition-colors"
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-secondary-200 py-4"
          >
            <div className="flex flex-col space-y-2">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
              <Link
                to="/generate"
                onClick={() => setIsMenuOpen(false)}
                className="btn-primary mt-4"
              >
                Start Generating
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </header>
  )
}

export default Header