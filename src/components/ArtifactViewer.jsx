import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Copy, Download, Eye, Code, CheckCircle, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'

const ArtifactViewer = ({ artifact }) => {
  const [viewMode, setViewMode] = useState('rendered')
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content)
      setCopied(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy')
    }
  }

  const handleDownload = () => {
    const blob = new Blob([artifact.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = artifact.name || 'artifact.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('File downloaded')
  }

  const isCode = artifact.type === 'code' || ['py', 'js', 'ts', 'jsx', 'tsx', 'html', 'css', 'json', 'yaml', 'sh'].some(
    ext => artifact.name?.endsWith(`.${ext}`)
  )

  const renderContent = () => {
    if (viewMode === 'raw' || isCode) {
      return (
        <pre className="whitespace-pre-wrap body-sm text-green-400 font-mono bg-neutral-900 p-5 rounded-xl overflow-auto max-h-96 custom-scrollbar leading-relaxed">
          {artifact.content}
        </pre>
      )
    }

    return (
      <div className="prose prose-neutral max-w-none p-2">
        <ReactMarkdown
          components={{
            code({ inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <pre className="bg-neutral-900 text-green-400 p-4 rounded-xl overflow-x-auto">
                  <code className={`language-${match[1]}`}>
                    {String(children).replace(/\n$/, '')}
                  </code>
                </pre>
              ) : (
                <code className="bg-neutral-100 text-primary-700 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              )
            },
            h1: ({ children }) => <h1 className="display-sm text-neutral-900 mb-4">{children}</h1>,
            h2: ({ children }) => <h2 className="body-xl font-semibold text-neutral-900 mb-3 mt-6">{children}</h2>,
            h3: ({ children }) => <h3 className="body-lg font-semibold text-neutral-900 mb-2 mt-4">{children}</h3>,
            p: ({ children }) => <p className="body-md text-neutral-700 mb-3">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3">{children}</ul>,
            li: ({ children }) => <li className="body-md text-neutral-700">{children}</li>,
          }}
        >
          {artifact.content}
        </ReactMarkdown>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-5 border-b border-neutral-200/60">
        <div className="flex items-center space-x-3 min-w-0">
          <div className="w-9 h-9 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <FileText className="h-5 w-5 text-primary-600" />
          </div>
          <div className="min-w-0">
            <h3 className="label text-neutral-900 truncate">{artifact.name}</h3>
            <p className="caption text-neutral-500">
              {artifact.agent_role?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              {artifact.size && ` · ${(artifact.size / 1024).toFixed(1)}KB`}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 flex-shrink-0">
          {/* View Mode Toggle - only for non-code */}
          {!isCode && (
            <div className="flex rounded-xl border border-neutral-200 overflow-hidden">
              <button
                onClick={() => setViewMode('rendered')}
                className={`px-3 py-1.5 caption font-medium transition-colors ${
                  viewMode === 'rendered'
                    ? 'bg-primary-500 text-white'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                }`}
              >
                <Eye className="h-3.5 w-3.5 inline mr-1" />
                Preview
              </button>
              <button
                onClick={() => setViewMode('raw')}
                className={`px-3 py-1.5 caption font-medium transition-colors ${
                  viewMode === 'raw'
                    ? 'bg-primary-500 text-white'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
                }`}
              >
                <Code className="h-3.5 w-3.5 inline mr-1" />
                Raw
              </button>
            </div>
          )}

          <button
            onClick={handleCopy}
            className="btn-ghost p-2 rounded-lg"
            title="Copy to clipboard"
          >
            {copied ? (
              <CheckCircle className="h-4 w-4 text-success-600" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </button>

          <button
            onClick={handleDownload}
            className="btn-ghost p-2 rounded-lg"
            title="Download file"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-96 overflow-auto custom-scrollbar">
        {renderContent()}
      </div>
    </motion.div>
  )
}

export default ArtifactViewer
