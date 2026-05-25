import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  // FormData must not use application/json (breaks multipart boundary)
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

export const register = (data) => api.post('/api/register', data)
export const login = (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return api.post('/api/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}
export const getMe = () => api.get('/api/me')
export const predict = (file) => {
  const form = new FormData()
  form.append('file', file)
  // Let axios set Content-Type with boundary (manual header breaks uploads)
  return api.post('/api/predict', form)
}
export const upload = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/api/upload', form)
}

/** Normalize FastAPI error detail for UI display */
export function formatApiError(err, fallback = 'Request failed') {
  const detail = err?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || d.message || JSON.stringify(d)).join(', ')
  }
  return JSON.stringify(detail)
}
export const getHistory = () => api.get('/api/history')
export const getPrediction = (id) => api.get(`/api/history/${id}`)
export const chat = (message, language = 'en') =>
  api.post('/api/chat', { message, language })
export const getAdminStats = () => api.get('/api/admin/stats')
export const getAdminPredictions = () => api.get('/api/admin/predictions')
export const downloadReport = (id) =>
  api.get(`/api/report/${id}`, { responseType: 'blob' })

export const processedImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  const base = API_URL || ''
  return `${base}${path}`
}

export default api
