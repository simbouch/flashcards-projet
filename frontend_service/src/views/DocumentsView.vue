<template>
  <div class="documents-view">
    <v-container class="py-8">
      <!-- Page Header -->
      <div class="text-center mb-8 animate-fade-in">
        <v-avatar size="80" class="gradient-info mb-4 animate-pulse">
          <v-icon size="40" color="white">mdi-file-document-multiple</v-icon>
        </v-avatar>
        <h1 class="text-h3 font-weight-bold mb-2">My Documents</h1>
        <p class="text-h6 text-medium-emphasis">Upload and manage your documents for AI-powered flashcard generation</p>
      </div>

      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <!-- Upload Section -->
          <v-card class="modern-card mb-6 animate-slide-in-up">
            <v-card-text class="pa-6 text-center">
              <v-avatar size="64" class="gradient-primary mb-4">
                <v-icon size="32" color="white">mdi-upload</v-icon>
              </v-avatar>
              <h3 class="text-h5 font-weight-bold mb-3">Upload New Document</h3>
              <p class="text-body-2 text-medium-emphasis mb-4">
                Upload PDFs or images to automatically generate flashcards using AI
              </p>
              <v-btn
                class="modern-btn"
                color="primary"
                size="large"
                @click="showUploadDialog = true"
                prepend-icon="mdi-upload"
              >
                Upload Document
              </v-btn>
            </v-card-text>
          </v-card>

          <!-- Error Alert -->
          <v-alert
            v-if="documentsStore.error"
            type="error"
            variant="tonal"
            class="modern-card mb-6 animate-slide-in-up animate-delay-200"
            closable
            @click:close="documentsStore.clearError()"
          >
            {{ documentsStore.error }}
          </v-alert>

          <!-- Documents Table -->
          <v-card class="modern-card animate-slide-in-up animate-delay-400">
            <v-card-title class="pa-6 pb-4">
              <div class="d-flex align-center">
                <v-avatar size="48" class="gradient-secondary mr-4">
                  <v-icon size="24" color="white">mdi-file-document</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h5 font-weight-bold">Document Library</h3>
                  <p class="text-caption text-medium-emphasis mb-0">{{ documentsStore.documents.length }} documents</p>
                </div>
              </div>
            </v-card-title>

            <v-card-text class="pa-0">
              <v-data-table
                :headers="headers"
                :items="documentsStore.documents"
                :loading="documentsStore.loading"
                :items-per-page="10"
                class="modern-table"
                :no-data-text="documentsStore.loading ? 'Loading documents...' : 'No documents found'"
              >
                <template #[`item.status`]="{ item }">
                  <v-chip
                    :color="getStatusColor(item.status)"
                    size="small"
                    variant="flat"
                  >
                    <v-icon start size="16">{{ getStatusIcon(item.status) }}</v-icon>
                    {{ formatStatus(item.status) }}
                  </v-chip>
                </template>

                <template #[`item.created_at`]="{ item }">
                  <div class="d-flex align-center">
                    <v-icon size="16" class="text-medium-emphasis mr-2">mdi-calendar</v-icon>
                    {{ formatDate(item.created_at) }}
                  </div>
                </template>

                <template #[`item.actions`]="{ item }">
                  <div class="d-flex gap-2">
                    <v-btn
                      class="modern-btn"
                      color="primary"
                      size="small"
                      @click="viewDocument(item)"
                      :disabled="!isProcessingComplete(item)"
                      prepend-icon="mdi-eye"
                    >
                      View
                    </v-btn>

                    <v-btn
                      class="modern-btn"
                      color="error"
                      size="small"
                      variant="outlined"
                      @click="deleteDocument(item)"
                      icon="mdi-delete"
                    ></v-btn>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>

          <!-- Back to Main Button -->
          <div class="text-center mt-8 animate-fade-in animate-delay-600">
            <v-btn
              class="modern-btn"
              color="secondary"
              size="large"
              @click="goToMain"
              prepend-icon="mdi-arrow-left"
            >
              Back to Main
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!-- Upload Dialog -->
    <v-dialog
      v-model="showUploadDialog"
      max-width="500px"
      class="glass-effect"
    >
      <v-card class="modern-card">
        <v-card-title class="pa-6 pb-4">
          <div class="d-flex align-center">
            <v-avatar size="48" class="gradient-primary mr-4">
              <v-icon size="24" color="white">mdi-upload</v-icon>
            </v-avatar>
            <div>
              <h3 class="text-h5 font-weight-bold">Upload Document</h3>
              <p class="text-caption text-medium-emphasis mb-0">PDF or image files supported</p>
            </div>
          </div>
        </v-card-title>

        <v-card-text class="pa-6 pt-0">
          <v-file-input
            v-model="fileToUpload"
            label="Select Document"
            accept="image/jpeg,image/png,application/pdf"
            prepend-inner-icon="mdi-file-document"
            variant="outlined"
            show-size
            class="mb-4"
            :rules="[v => !!v || 'Please select a file to upload']"
          ></v-file-input>

          <v-alert
            v-if="uploadError"
            type="error"
            variant="tonal"
            closable
            @click:close="uploadError = null"
            class="mb-4"
          >
            {{ uploadError }}
          </v-alert>

          <div class="text-caption text-medium-emphasis">
            <v-icon size="16" class="mr-1">mdi-information</v-icon>
            Supported formats: PDF, JPEG, PNG (max 10MB)
          </div>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            class="modern-btn"
            color="grey"
            variant="outlined"
            @click="showUploadDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            class="modern-btn ml-2"
            color="primary"
            @click="uploadDocument"
            :loading="uploading"
            :disabled="!fileToUpload || uploading"
            prepend-icon="mdi-upload"
          >
            Upload Document
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Document Dialog -->
    <v-dialog
      v-model="showViewDialog"
      max-width="800px"
    >
      <v-card v-if="selectedDocument">
        <v-card-title class="text-h5">
          {{ selectedDocument.filename }}
        </v-card-title>

        <v-card-text>
          <v-tabs v-model="activeTab">
            <v-tab>Document Info</v-tab>
            <v-tab>Extracted Text</v-tab>
            <v-tab>Generated Flashcards</v-tab>
          </v-tabs>

          <v-tabs-items v-model="activeTab">
            <v-tab-item>
              <v-list>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Filename</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedDocument.filename }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Status</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip
                        :color="getStatusColor(selectedDocument.status)"
                        small
                      >
                        {{ formatStatus(selectedDocument.status) }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Uploaded</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(selectedDocument.created_at) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>

                <v-list-item v-if="selectedDocument.error_message">
                  <v-list-item-content>
                    <v-list-item-title>Error</v-list-item-title>
                    <v-list-item-subtitle class="text-error">{{ selectedDocument.error_message }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-tab-item>

            <v-tab-item>
              <div v-if="extractedText" class="pa-4">
                <pre class="extracted-text">{{ extractedText.content }}</pre>
              </div>
              <div v-else class="pa-4 text-center">
                <v-progress-circular
                  v-if="loadingText"
                  indeterminate
                  color="primary"
                ></v-progress-circular>
                <p v-else>No text extracted yet.</p>
              </div>
            </v-tab-item>

            <v-tab-item>
              <div v-if="flashcards && flashcards.length > 0" class="pa-4">
                <v-card
                  v-for="(card, index) in flashcards"
                  :key="index"
                  class="mb-4"
                  outlined
                >
                  <v-card-title>{{ card.question }}</v-card-title>
                  <v-card-text>{{ card.answer }}</v-card-text>
                </v-card>
              </div>
              <div v-else class="pa-4 text-center">
                <v-progress-circular
                  v-if="loadingFlashcards"
                  indeterminate
                  color="primary"
                ></v-progress-circular>
                <p v-else>No flashcards generated yet.</p>
              </div>
            </v-tab-item>
          </v-tabs-items>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="showViewDialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog
      v-model="showDeleteDialog"
      max-width="400px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Confirm Delete
        </v-card-title>

        <v-card-text>
          Are you sure you want to delete this document?
          <strong>{{ selectedDocument?.filename }}</strong>
          This action cannot be undone.
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="confirmDelete"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useDocumentsStore } from '../store/documents'
import { useFlashcardsStore } from '../store/flashcards'
import { documentsAPI } from '../api'

export default {
  name: 'DocumentsView',
  data() {
    return {
      documentsStore: useDocumentsStore(),
      flashcardsStore: useFlashcardsStore(),
      headers: [
        { text: 'Filename', value: 'filename' },
        { text: 'Status', value: 'status' },
        { text: 'Uploaded', value: 'created_at' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      showUploadDialog: false,
      showViewDialog: false,
      showDeleteDialog: false,
      fileToUpload: null,
      uploading: false,
      uploadError: null,
      selectedDocument: null,
      activeTab: 0,
      extractedText: null,
      loadingText: false,
      flashcards: [],
      loadingFlashcards: false,
      deleting: false
    }
  },
  created() {
    this.fetchDocuments()
  },
  methods: {
    async fetchDocuments() {
      await this.documentsStore.fetchDocuments()
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    formatStatus(status) {
      if (!status) return ''
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    getStatusColor(status) {
      if (!status) return 'grey'

      const statusMap = {
        'uploaded': 'blue',
        'ocr_processing': 'info',
        'ocr_complete': 'light-blue',
        'flashcard_generating': 'primary',
        'flashcard_complete': 'green',
        'error': 'red'
      }

      return statusMap[status] || 'grey'
    },

    getStatusIcon(status) {
      if (!status) return 'mdi-help-circle'

      const iconMap = {
        'uploaded': 'mdi-upload',
        'ocr_processing': 'mdi-eye-scan',
        'ocr_complete': 'mdi-text-recognition',
        'flashcard_generating': 'mdi-robot',
        'flashcard_complete': 'mdi-check-circle',
        'error': 'mdi-alert-circle'
      }

      return iconMap[status] || 'mdi-help-circle'
    },

    isProcessingComplete(document) {
      return document.status === 'flashcard_complete' || document.status === 'error'
    },

    async uploadDocument() {
      if (!this.fileToUpload) {
        this.uploadError = 'Please select a file to upload'
        return
      }

      this.uploading = true
      this.uploadError = null

      try {
        await this.documentsStore.uploadDocument(this.fileToUpload)
        this.showUploadDialog = false
        this.fileToUpload = null
      } catch (error) {
        this.uploadError = error.message || 'Failed to upload document'
      } finally {
        this.uploading = false
      }
    },

    async viewDocument(document) {
      this.selectedDocument = document
      this.showViewDialog = true
      this.activeTab = 0
      this.extractedText = null
      this.flashcards = []

      // Fetch extracted text when tab is changed to text
      this.$watch('activeTab', async (newVal) => {
        if (newVal === 1 && !this.extractedText) {
          await this.fetchExtractedText()
        } else if (newVal === 2 && this.flashcards.length === 0) {
          await this.fetchFlashcards()
        }
      })
    },

    async fetchExtractedText() {
      if (!this.selectedDocument) return

      this.loadingText = true

      try {
        const response = await documentsAPI.getDocumentText(this.selectedDocument.id)
        this.extractedText = response.data
      } catch (error) {
        console.error('Failed to fetch extracted text:', error)
      } finally {
        this.loadingText = false
      }
    },

    async fetchFlashcards() {
      if (!this.selectedDocument) return

      this.loadingFlashcards = true

      try {
        // Find decks associated with this document
        const decksResponse = await this.documentsStore.fetchDocument(this.selectedDocument.id)
        if (decksResponse && decksResponse.decks && decksResponse.decks.length > 0) {
          // Get flashcards for the first deck
          const deckId = decksResponse.decks[0].id
          const flashcardsResponse = await this.flashcardsStore.fetchFlashcards(deckId)
          this.flashcards = flashcardsResponse || []
        }
      } catch (error) {
        console.error('Failed to fetch flashcards:', error)
      } finally {
        this.loadingFlashcards = false
      }
    },

    deleteDocument(document) {
      this.selectedDocument = document
      this.showDeleteDialog = true
    },

    async confirmDelete() {
      if (!this.selectedDocument) return

      this.deleting = true

      try {
        const result = await this.documentsStore.deleteDocument(this.selectedDocument.id)

        if (result) {
          console.log(`Successfully deleted document: ${this.selectedDocument.id}`)
          this.showDeleteDialog = false
          // Refresh the documents list
          await this.documentsStore.fetchDocuments()
        } else {
          console.error('Failed to delete document: API returned false')
          this.documentsStore.error = 'Failed to delete document. Please try again.'
        }
      } catch (error) {
        console.error('Failed to delete document:', error)
        this.documentsStore.error = error.message || 'Failed to delete document. Please try again.'
      } finally {
        this.deleting = false
      }
    },

    goToMain() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.documents-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.v-theme--dark .documents-view {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.extracted-text {
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 16px;
  border-radius: var(--border-radius-lg);
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.v-theme--dark .extracted-text {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-color: rgba(71, 85, 105, 0.3);
}

.modern-table {
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.modern-table :deep(.v-data-table__wrapper) {
  border-radius: var(--border-radius-lg);
}

.modern-table :deep(.v-data-table-header) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.v-theme--dark .modern-table :deep(.v-data-table-header) {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
}

.modern-table :deep(.v-data-table__tr:hover) {
  background-color: rgba(59, 130, 246, 0.05);
}

/* Animation classes */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-in-up {
  animation: slideInUp 0.6s ease-out;
}

.animate-pulse {
  animation: pulse 2s infinite;
}

.animate-delay-200 { animation-delay: 0.2s; }
.animate-delay-400 { animation-delay: 0.4s; }
.animate-delay-600 { animation-delay: 0.6s; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
