import { Link } from 'react-router-dom'
import { Cpu, Github, Twitter, Linkedin } from 'lucide-react'

const Footer = () => (
  <footer className="bg-neutral-900 border-t border-neutral-800">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10 sm:gap-8">

        {/* Brand */}
        <div className="sm:col-span-2">
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <Cpu className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-bold text-white font-display">MetaGPT</span>
          </div>
          <p className="text-sm text-neutral-500 max-w-xs leading-relaxed">
            Generate complete applications from natural language using MetaGPT's
            multi-agent framework powered by AWS Bedrock.
          </p>
        </div>

        {/* Links */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-4">Product</p>
          <ul className="space-y-3">
            {[
              { label: 'Generator',     href: '/generate' },
              { label: 'About',         href: '/about' },
              { label: 'Documentation', href: '#' },
            ].map((l) => (
              <li key={l.label}>
                <Link to={l.href} className="text-sm text-neutral-400 hover:text-white transition-colors duration-150">
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Social */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-4">Connect</p>
          <div className="flex gap-3">
            {[
              { icon: Github,   label: 'GitHub' },
              { icon: Twitter,  label: 'Twitter' },
              { icon: Linkedin, label: 'LinkedIn' },
            ].map(({ icon: Icon, label }) => (
              <a key={label} href="#" aria-label={label}
                className="w-9 h-9 rounded-lg bg-neutral-800 flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-700 transition-all duration-150">
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-neutral-800 mt-12 pt-7 flex flex-col sm:flex-row justify-between items-center gap-3">
        <p className="text-xs text-neutral-600">&copy; 2025 MetaGPT + Bedrock Generator. All rights reserved.</p>
        <p className="text-xs text-neutral-600">Built for enterprise developers.</p>
      </div>
    </div>
  </footer>
)

export default Footer
