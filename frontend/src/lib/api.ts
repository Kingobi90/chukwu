import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (moodleToken: string) =>
    api.post('/auth/login', { moodle_token: moodleToken }),
  
  logout: () => api.post('/auth/logout'),
  
  getCurrentUser: () => api.get('/auth/me'),
}

// Courses API
export const coursesAPI = {
  getCourses: () => api.get('/courses/'),
  
  getCourse: (courseId: string) => api.get(`/courses/${courseId}`),
  
  syncCourses: () => api.post('/courses/sync'),
  
  getCourseMaterials: (courseId: string) => api.get(`/courses/${courseId}/materials`),
}

// Flashcards API
export const flashcardsAPI = {
  getFlashcards: (courseId?: string) =>
    api.get('/flashcards/', { params: { course_id: courseId } }),
  
  getDueFlashcards: () => api.get('/flashcards/due'),
  
  createFlashcard: (data: {
    front: string
    back: string
    course_id: string
    source_file?: string
  }) => api.post('/flashcards/', data),
  
  reviewFlashcard: (flashcardId: string, quality: number) =>
    api.post(`/flashcards/${flashcardId}/review`, { quality }),
  
  deleteFlashcard: (flashcardId: string) => api.delete(`/flashcards/${flashcardId}`),
}

// Focus Mode API
export const focusAPI = {
  startSession: (data: { duration_minutes: number; ambient_sound?: string }) =>
    api.post('/focus/sessions', data),
  
  completeSession: (sessionId: string, interrupted: boolean = false) =>
    api.patch(`/focus/sessions/${sessionId}/complete`, null, {
      params: { interrupted },
    }),
  
  getSessions: (limit: number = 50) =>
    api.get('/focus/sessions', { params: { limit } }),
  
  getStats: () => api.get('/focus/stats'),
}

// Social API
export const socialAPI = {
  getGroups: (courseId?: number) =>
    api.get('/social/groups', { params: { course_id: courseId } }),
  
  createGroup: (data: {
    name: string
    description?: string
    moodle_course_id?: number
    max_members?: number
  }) => api.post('/social/groups', data),
  
  getResources: (courseId?: number) =>
    api.get('/social/resources', { params: { course_id: courseId } }),
  
  createResource: (data: {
    title: string
    description?: string
    resource_type: string
    file_url?: string
    moodle_course_id?: number
  }) => api.post('/social/resources', data),
  
  upvoteResource: (resourceId: string) =>
    api.post(`/social/resources/${resourceId}/upvote`),
}

// Notes API
export const notesAPI = {
  getNotes: (params?: { note_type?: string; tag?: string; limit?: number }) =>
    api.get('/notes/', { params }),
  
  createNote: (data: {
    title?: string
    content: string
    note_type?: string
    tags?: string[]
    color?: string
  }) => api.post('/notes/', data),
  
  updateNote: (noteId: string, data: {
    title?: string
    content: string
    note_type?: string
    tags?: string[]
    color?: string
  }) => api.put(`/notes/${noteId}`, data),
  
  deleteNote: (noteId: string) => api.delete(`/notes/${noteId}`),
  
  searchNotes: (query: string) =>
    api.get('/notes/search', { params: { q: query } }),
}
