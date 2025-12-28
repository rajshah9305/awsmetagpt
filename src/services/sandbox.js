/**
 * Sandbox API service functions
 */

const API_BASE = '/api/v1'

// Helper function for API calls
const apiCall = async (url, options = {}) => {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }))
    throw new Error(error.message || `HTTP ${response.status}`)
  }

  return response.json()
}

// Sandbox management functions
export const createSandbox = async (generationId, template = 'base') => {
  return apiCall(`/e2b/sandbox/${generationId}/create?template=${template}`, {
    method: 'POST'
  })
}

export const writeFiles = async (generationId, artifacts) => {
  return apiCall(`/e2b/sandbox/${generationId}/files`, {
    method: 'POST',
    body: JSON.stringify(artifacts)
  })
}

export const runApplication = async (generationId, command = null) => {
  const body = command ? JSON.stringify({ command }) : undefined
  
  return apiCall(`/e2b/sandbox/${generationId}/run`, {
    method: 'POST',
    body
  })
}

export const stopApplication = async (generationId) => {
  return apiCall(`/e2b/sandbox/${generationId}/stop`, {
    method: 'POST'
  })
}

export const getSandboxLogs = async (generationId, lines = 100) => {
  return apiCall(`/e2b/sandbox/${generationId}/logs?lines=${lines}`)
}

export const getSandboxInfo = async (generationId) => {
  try {
    return await apiCall(`/e2b/sandbox/${generationId}/info`)
  } catch (error) {
    if (error.message.includes('404')) {
      return null // Sandbox doesn't exist yet
    }
    throw error
  }
}

export const cleanupSandbox = async (generationId) => {
  return apiCall(`/e2b/sandbox/${generationId}`, {
    method: 'DELETE'
  })
}