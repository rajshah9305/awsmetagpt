import React from 'react'
import { Bot, Github, Twitter, Linkedin } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-secondary-900 text-secondary-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <Bot className="h-8 w-8 text-primary-400" />
              <span className="text-xl font-bold text-white">MetaGPT + Bedrock</span>
            </div>
            <p className="text-secondary-400 max-w-md">
              Generate complete applications from natural language using MetaGPT's multi-agent framework 
              powered by AWS Bedrock AI models.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Product</h3>
            <ul className="space-y-2">
              <li><a href="/generate" className="hover:text-white transition-colors">Generator</a></li>
              <li><a href="/about" className="hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h3 className="text-white font-semibold mb-4">Connect</h3>
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

        <div className="border-t border-secondary-800 mt-8 pt-8 text-center">
          <p>&copy; 2024 MetaGPT + Bedrock Generator. Built with ❤️ for developers.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer