import React from 'react'
import { Link } from 'react-router-dom'
import { Bot, Github, Twitter, Linkedin } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-dark-800 text-neutral-400 border-t border-dark-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 sm:gap-10">
          {/* Brand */}
          <div className="sm:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow flex-shrink-0">
                <Bot className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
              <span className="text-lg sm:text-xl font-display font-bold text-white">MetaGPT + Bedrock</span>
            </div>
            <p className="text-neutral-500 max-w-sm leading-relaxed text-sm sm:text-base">
              Generate complete applications from natural language using MetaGPT&apos;s multi-agent framework
              powered by AWS Bedrock AI models.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-display font-semibold mb-3 sm:mb-4 text-sm sm:text-base">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/generate" className="text-neutral-400 hover:text-white transition-colors text-sm sm:text-base">
                  Generator
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-neutral-400 hover:text-white transition-colors text-sm sm:text-base">
                  About
                </Link>
              </li>
              <li>
                <a href="#" className="text-neutral-400 hover:text-white transition-colors text-sm sm:text-base">
                  Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-white font-display font-semibold mb-3 sm:mb-4 text-sm sm:text-base">Connect</h3>
            <div className="flex space-x-4">
              <a href="#" aria-label="GitHub" className="text-neutral-400 hover:text-white transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" aria-label="Twitter" className="text-neutral-400 hover:text-white transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" aria-label="LinkedIn" className="text-neutral-400 hover:text-white transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-dark-700 mt-10 sm:mt-12 pt-6 sm:pt-8 text-center">
          <p className="text-neutral-500 text-sm">&copy; 2025 MetaGPT + Bedrock Generator. Built for developers.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer