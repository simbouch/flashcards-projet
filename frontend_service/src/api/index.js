import axios from 'axios'

// Create axios instance with base URL from environment
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8002/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle common errors
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  register(userData) {
    return apiClient.post('/auth/register', userData)
  },
  getProfile() {
    return apiClient.get('/users/me')
  },
  updateProfile(userData) {
    return apiClient.put('/users/me', userData)
  }
}

// Documents API
export const documentsAPI = {
  getDocuments() {
    return apiClient.get('/documents')
  },
  getDocument(id) {
    return apiClient.get(`/documents/${id}`)
  },
  uploadDocument(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  getDocumentText(id) {
    return apiClient.get(`/documents/${id}/text`)
  },
  deleteDocument(id) {
    return apiClient.delete(`/documents/${id}`)
  }
}

// Decks API
export const decksAPI = {
  getDecks() {
    return apiClient.get('/decks')
  },
  getDeck(id) {
    return apiClient.get(`/decks/${id}`)
  },
  createDeck(deckData) {
    return apiClient.post('/decks', deckData)
  },
  updateDeck(id, deckData) {
    return apiClient.put(`/decks/${id}`, deckData)
  },
  deleteDeck(id) {
    return apiClient.delete(`/decks/${id}`)
  },
  getPublicDecks() {
    return apiClient.get('/decks/public')
  },
  shareDeck(deckId, userId) {
    return apiClient.post(`/decks/${deckId}/share/${userId}`)
  }
}

// Flashcards API
export const flashcardsAPI = {
  getFlashcards(deckId) {
    return apiClient.get('/flashcards', {
      params: { deck_id: deckId }
    })
  },
  getFlashcard(id) {
    return apiClient.get(`/flashcards/${id}`)
  },
  createFlashcard(flashcardData) {
    return apiClient.post('/flashcards', flashcardData)
  },
  updateFlashcard(id, flashcardData) {
    return apiClient.put(`/flashcards/${id}`, flashcardData)
  },
  deleteFlashcard(id) {
    return apiClient.delete(`/flashcards/${id}`)
  }
}

// Study API
export const studyAPI = {
  createStudySession(deckId) {
    return apiClient.post('/study/sessions', { deck_id: deckId })
  },
  getStudySessions() {
    return apiClient.get('/study/sessions')
  },
  getStudySession(id) {
    return apiClient.get(`/study/sessions/${id}`)
  },
  endStudySession(id) {
    return apiClient.put(`/study/sessions/${id}/end`)
  },
  createStudyRecord(sessionId, flashcardId, isCorrect) {
    return apiClient.post('/study/records', {
      session_id: sessionId,
      flashcard_id: flashcardId,
      is_correct: isCorrect
    })
  },
  getStudyRecords(sessionId) {
    return apiClient.get('/study/records', {
      params: { session_id: sessionId }
    })
  }
}

export default {
  auth: authAPI,
  documents: documentsAPI,
  decks: decksAPI,
  flashcards: flashcardsAPI,
  study: studyAPI
}
