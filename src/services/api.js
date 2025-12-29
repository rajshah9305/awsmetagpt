import axios from 'axios'

const API_BASE_URL = '/api/v1'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    
    // Handle different error scenarios
    let message = 'An error occurred'
    
    if (error.response) {
      // Server responded with error status
      const data = error.response.data
      if (data?.detail) {
        // FastAPI validation error format
        if (Array.isArray(data.detail)) {
          message = data.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ')
        } else {
          message = data.detail
        }
      } else if (data?.message) {
        message = data.message
      } else if (data?.error) {
        message = data.error
      } else {
        message = `Server error: ${error.response.status}`
      }
    } else if (error.request) {
      // Network error
      message = 'Network error - please check your connection'
    } else {
      // Other error
      message = error.message || 'An unexpected error occurred'
    }
    
    return Promise.reject(new Error(message))
  }
)

// API functions
export const generateApp = async (requestData) => {
  return await api.post('/generate', requestData)
}

export const getGenerationStatus = async (generationId) => {
  return await api.get(`/generate/${generationId}/status`)
}

export const getGenerationArtifacts = async (generationId) => {
  return await api.get(`/generate/${generationId}/artifacts`)
}

export const getSpecificArtifact = async (generationId, artifactName) => {
  return await api.get(`/generate/${generationId}/artifact/${encodeURIComponent(artifactName)}`)
}

export const getModels = async () => {
  return await api.get('/models/bedrock')
}

export const getAgentRoles = async () => {
  return await api.get('/agents/roles')
}

export const healthCheck = async () => {
  return await api.get('/health')
}

export default api