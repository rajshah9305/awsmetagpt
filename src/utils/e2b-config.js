// E2B Configuration - Backend Only
// All E2B operations should go through the backend API

export const E2B_CONFIG = {
  // All E2B operations are handled by the backend
  // This file exists for type definitions only
  
  // Supported project types (for UI display)
  projectTypes: {
    react: { name: 'React', icon: 'Code', color: 'blue' },
    html: { name: 'HTML', icon: 'Globe', color: 'orange' },
    python: { name: 'Python', icon: 'Terminal', color: 'green' },
    node: { name: 'Node.js', icon: 'Server', color: 'lime' }
  },
  
  // File type patterns (for detection)
  filePatterns: {
    react: /\.(jsx?|tsx?)$/,
    html: /\.html?$/,
    python: /\.py$/,
    node: /\.js$/
  }
}

// Helper function to detect project type from files
export const detectProjectType = (files) => {
  if (!files || files.length === 0) return 'unknown'
  
  const hasPackageJson = files.some(f => f.name === 'package.json')
  const hasReact = files.some(f => 
    f.name === 'package.json' && f.content?.includes('react')
  )
  const hasPython = files.some(f => f.name.endsWith('.py'))
  const hasHTML = files.some(f => f.name.endsWith('.html'))
  
  if (hasReact) return 'react'
  if (hasPackageJson) return 'node'
  if (hasPython) return 'python'
  if (hasHTML) return 'html'
  
  return 'static'
}

export default E2B_CONFIG

export default E2B_CONFIG