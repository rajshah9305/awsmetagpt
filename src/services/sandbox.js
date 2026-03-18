/**
 * Sandbox API service — uses the shared axios instance from api.js
 */
import api from './api'

export const createSandbox = (generationId, template = 'base') =>
  api.post(`/e2b/sandbox/${generationId}/create?template=${template}`)

export const writeFiles = (generationId, artifacts) =>
  api.post(`/e2b/sandbox/${generationId}/files`, artifacts)

export const runApplication = (generationId, command = null) =>
  api.post(`/e2b/sandbox/${generationId}/run`, command ? { command } : undefined)

export const stopApplication = (generationId) =>
  api.post(`/e2b/sandbox/${generationId}/stop`)

export const getSandboxLogs = (generationId, lines = 100) =>
  api.get(`/e2b/sandbox/${generationId}/logs?lines=${lines}`)

export const getSandboxInfo = (generationId) =>
  api.get(`/e2b/sandbox/${generationId}/info`).catch((err) => {
    if (err.message?.includes('404') || err.message?.includes('not found')) return null
    throw err
  })

export const cleanupSandbox = (generationId) =>
  api.delete(`/e2b/sandbox/${generationId}`)
