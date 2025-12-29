import React from 'react'
import { Bot, Github, Twitter, Linkedin } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-dark-800 text-neutral-400 border-t border-dark-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-secondary-500 flex items-center justify-center shadow-glow">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-display font-bold text-white">MetaGPT + Bedrock</span>
            </div>
            <p className="text-neutral-500 max-w-md leading-relaxed">
              Generate complete applications from natural language using MetaGPT&apos;s multi-agent framework 
              powered by AWS Bedrock AI models.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-display font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              <li><a href="/generate" className="hover:text-white transition-colors">Generator</a></li>
              <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-white font-display font-semibold mb-4">Connect</h3>
            <div className="flex space-x-4">
              <a href="#" className="hover:text-white transition-colors">
                <Github className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-white transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="hover:text-white transition-colors">
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-dark-700 mt-12 pt-8 text-center">
          <p className="text-neutral-500">&copy; 2025 MetaGPT + Bedrock Generator. Built with ❤️ for developers.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer