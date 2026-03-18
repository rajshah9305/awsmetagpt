import { Link } from 'react-router-dom'
import { Bot, Github, Twitter, Linkedin, Zap } from 'lucide-react'

const Footer = () => (
  <footer className="bg-neutral-900 text-neutral-400">
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10">

        {/* Brand */}
        <div className="sm:col-span-2">
          <div className="flex items-center space-x-3 mb-4">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <Zap className="h-3 w-3 text-accent-400 absolute -top-1 -right-1" />
            </div>
            <span className="text-lg font-display font-bold text-white">MetaGPT</span>
          </div>
          <p className="text-sm text-neutral-500 max-w-xs leading-relaxed">
            Generate complete applications from natural language using MetaGPT's multi-agent
            framework powered by AWS Bedrock.
          </p>
        </div>

        {/* Links */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-4">Product</h3>
          <ul className="space-y-2.5">
            {[
              { label: 'Generator',     href: '/generate' },
              { label: 'About',         href: '/about' },
              { label: 'Documentation', href: '#' },
            ].map((l) => (
              <li key={l.label}>
                <Link to={l.href} className="text-sm text-neutral-500 hover:text-white transition-colors">
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Social */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-4">Connect</h3>
          <div className="flex space-x-4">
            {[
              { icon: Github,   label: 'GitHub' },
              { icon: Twitter,  label: 'Twitter' },
              { icon: Linkedin, label: 'LinkedIn' },
            ].map(({ icon: Icon, label }) => (
              <a key={label} href="#" aria-label={label}
                className="text-neutral-500 hover:text-white transition-colors">
                <Icon className="h-5 w-5" />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-neutral-800 mt-12 pt-6 text-center">
        <p className="text-xs text-neutral-600">&copy; 2025 MetaGPT + Bedrock Generator. Built for developers.</p>
      </div>
    </div>
  </footer>
)

export default Footer
