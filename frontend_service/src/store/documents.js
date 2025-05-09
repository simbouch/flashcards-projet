import { defineStore } from 'pinia'
import { documentsAPI } from '../api'

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    documents: [],
    currentDocument: null,
    extractedText: null,
    loading: false,
    error: null
  }),
  
  getters: {
    getDocumentById: (state) => (id) => {
      return state.documents.find(doc => doc.id === id)
    }
  },
  
  actions: {
    async fetchDocuments() {
      this.loading = true
      this.error = null
      
      try {
        const response = await documentsAPI.getDocuments()
        this.documents = response.data
        this.loading = false
        return this.documents
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch documents'
        return []
      }
    },
    
    async fetchDocument(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await documentsAPI.getDocument(id)
        this.currentDocument = response.data
        this.loading = false
        return this.currentDocument
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch document'
        return null
      }
    },
    
    async uploadDocument(file) {
      this.loading = true
      this.error = null
      
      try {
        const response = await documentsAPI.uploadDocument(file)
        // Add the new document to the list
        this.documents.push(response.data)
        this.loading = false
        return response.data
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to upload document'
        return null
      }
    },
    
    async fetchDocumentText(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await documentsAPI.getDocumentText(id)
        this.extractedText = response.data
        this.loading = false
        return this.extractedText
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to fetch document text'
        return null
      }
    },
    
    async deleteDocument(id) {
      this.loading = true
      this.error = null
      
      try {
        await documentsAPI.deleteDocument(id)
        // Remove the document from the list
        this.documents = this.documents.filter(doc => doc.id !== id)
        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Failed to delete document'
        return false
      }
    },
    
    clearError() {
      this.error = null
    }
  }
})
