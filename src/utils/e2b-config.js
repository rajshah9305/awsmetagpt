// E2B Configuration based on official documentation
export const E2B_CONFIG = {
  // API Key from environment variables
  apiKey: process.env.REACT_APP_E2B_API_KEY,
  
  // Default sandbox configuration
  defaultConfig: {
    template: 'base', // Use base template for maximum flexibility
    metadata: {
      purpose: 'live-preview',
      source: 'metagpt-bedrock-generator'
    }
  },
  
  // Timeout settings (in milliseconds)
  timeouts: {
    initialization: 30000, // 30 seconds
    execution: 60000,      // 60 seconds
    connection: 10000      // 10 seconds
  },
  
  // Supported project types and their configurations
  projectTypes: {
    react: {
      ports: [3000],
      setupCommands: ['npm install'],
      startCommand: 'npm start',
      buildCommand: 'npm run build',
      dependencies: ['react', 'react-dom', 'react-scripts'],
      packageJson: {
        name: 'generated-react-app',
        version: '1.0.0',
        private: true,
        dependencies: {
          'react': '^18.2.0',
          'react-dom': '^18.2.0',
          'react-scripts': '5.0.1'
        },
        scripts: {
          'start': 'react-scripts start',
          'build': 'react-scripts build'
        }
      }
    },
    html: {
      ports: [8000],
      setupCommands: [],
      startCommand: 'python3 -m http.server 8000',
      buildCommand: null,
      dependencies: []
    },
    python: {
      ports: [5000, 8501, 8000],
      setupCommands: ['pip install flask fastapi uvicorn streamlit'],
      startCommand: 'python main.py',
      buildCommand: null,
      dependencies: ['flask', 'fastapi', 'streamlit', 'uvicorn']
    },
    node: {
      ports: [3000, 8000],
      setupCommands: ['npm install'],
      startCommand: 'npm start',
      buildCommand: 'npm run build',
      dependencies: ['express'],
      packageJson: {
        name: 'generated-node-app',
        version: '1.0.0',
        main: 'index.js',
        scripts: {
          'start': 'node index.js'
        },
        dependencies: {
          'express': '^4.18.0'
        }
      }
    }
  },
  
  // File type detection patterns
  filePatterns: {
    react: [/\.jsx?$/, /package\.json$/, /react/i],
    html: [/\.html?$/, /\.css$/, /\.js$/],
    python: [/\.py$/, /flask|fastapi|streamlit/i],
    node: [/\.js$/, /package\.json$/, /express|node/i]
  }
}

// Helper function to check if E2B is properly configured
export const isE2BConfigured = () => {
  return !!(process.env.REACT_APP_E2B_API_KEY && process.env.REACT_APP_E2B_API_KEY !== 'your_e2b_api_key_here')
}

// Helper function to get E2B API key
export const getE2BApiKey = () => {
  return E2B_CONFIG.apiKey
}

// Helper function to detect project type from files
export const detectProjectType = (files) => {
  // const { filePatterns } = E2B_CONFIG
  
  // Check for React
  if (files.some(f => 
    f.name === 'package.json' && f.artifact?.content?.includes('react')
  )) {
    return 'react'
  }
  
  // Check for Node.js
  if (files.some(f => 
    f.name === 'package.json' || f.name.endsWith('.js')
  )) {
    return 'node'
  }
  
  // Check for Python
  if (files.some(f => f.name.endsWith('.py'))) {
    return 'python'
  }
  
  // Check for HTML
  if (files.some(f => f.name.endsWith('.html'))) {
    return 'html'
  }
  
  return 'static'
}

export default E2B_CONFIG