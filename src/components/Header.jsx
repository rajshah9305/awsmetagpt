import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, Zap, Menu, X } from 'lucide-react'

const Header = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = React.useState(false)

  // Close menu on route change
  React.useEffect(() => {
    setIsMenuOpen(false)
  }, [location.pathname])

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Generate', href: '/generate' },
    { name: 'About', href: '/about' },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <header className="sticky top-0 z-50 glass border-b border-white/20 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group flex-shrink-0">
            <div className="relative">
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow group-hover:shadow-glow-lg transition-all duration-300">
                <Bot className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
              <Zap className="h-3.5 w-3.5 text-accent-500 absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div className="hidden sm:block">
              <div className="font-display text-lg sm:text-xl font-bold text-gradient leading-tight">MetaGPT</div>
              <div className="caption -mt-0.5 text-neutral-500">Powered by AWS Bedrock</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`relative px-4 py-2 body-sm font-semibold rounded-lg transition-colors ${
                  isActive(item.href)
                    ? 'text-primary-600'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100/60'
                }`}
              >
                {item.name}
                {isActive(item.href) && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-x-0 -bottom-px h-0.5 bg-gradient-to-r from-primary-400 to-secondary-500 rounded-full"
                    initial={false}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </Link>
            ))}
          </nav>

          {/* CTA Button */}
          <div className="hidden md:flex items-center">
            <Link to="/generate" className="btn-primary text-sm px-5 py-2.5">
              Start Generating
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 transition-colors"
            aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={isMenuOpen}
          >
            {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2, ease: 'easeInOut' }}
              className="md:hidden overflow-hidden border-t border-neutral-200/60"
            >
              <div className="flex flex-col space-y-1 py-3">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`px-4 py-2.5 body-sm font-semibold rounded-xl transition-colors ${
                      isActive(item.href)
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
                <div className="pt-2 pb-1 px-1">
                  <Link
                    to="/generate"
                    className="btn-primary w-full justify-center text-sm py-2.5"
                  >
                    Start Generating
                  </Link>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  )
}

export default Header