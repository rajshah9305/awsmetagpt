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
    const message = error.response?.data?.detail || error.message || 'An error occurred'
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