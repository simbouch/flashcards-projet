<template>
  <div class="profile-view">
    <v-container class="py-8">
      <!-- Page Header -->
      <div class="text-center mb-8 animate-fade-in">
        <v-avatar size="80" class="gradient-primary mb-4 animate-pulse">
          <v-icon size="40" color="white">mdi-account-circle</v-icon>
        </v-avatar>
        <h1 class="text-h3 font-weight-bold mb-2">My Profile</h1>
        <p class="text-h6 text-medium-emphasis">Manage your account settings and view your progress</p>
      </div>

      <v-row justify="center">
        <v-col cols="12" md="10" lg="8">
          <!-- Error and Success Alerts -->
          <v-alert
            v-if="authStore.error"
            type="error"
            variant="tonal"
            class="modern-card mb-6 animate-slide-in-up"
            closable
            @click:close="authStore.clearError()"
          >
            {{ authStore.error }}
          </v-alert>

          <v-alert
            v-if="successMessage"
            type="success"
            variant="tonal"
            class="modern-card mb-6 animate-slide-in-up"
            closable
            @click:close="successMessage = ''"
          >
            {{ successMessage }}
          </v-alert>

          <!-- Profile Information Card -->
          <v-card class="modern-card mb-6 animate-slide-in-up animate-delay-200">
            <v-card-title class="pa-6 pb-4">
              <div class="d-flex align-center">
                <v-avatar size="48" class="gradient-secondary mr-4">
                  <v-icon size="24" color="white">mdi-account</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h5 font-weight-bold">Profile Information</h3>
                  <p class="text-caption text-medium-emphasis mb-0">Your account details</p>
                </div>
              </div>
            </v-card-title>

            <v-card-text class="pa-6 pt-0">
              <v-form @submit.prevent="updateProfile" ref="form">
                <v-text-field
                  v-model="profileForm.email"
                  label="Email Address"
                  type="email"
                  variant="outlined"
                  class="mb-4"
                  prepend-inner-icon="mdi-email"
                  :disabled="!editMode"
                  :rules="[
                    v => !!v || 'Email is required',
                    v => /.+@.+\..+/.test(v) || 'Email must be valid'
                  ]"
                ></v-text-field>

                <v-text-field
                  v-model="profileForm.username"
                  label="Username"
                  variant="outlined"
                  class="mb-4"
                  prepend-inner-icon="mdi-account"
                  disabled
                  hint="Username cannot be changed"
                  persistent-hint
                ></v-text-field>

                <v-text-field
                  v-model="profileForm.full_name"
                  label="Full Name"
                  variant="outlined"
                  class="mb-4"
                  prepend-inner-icon="mdi-account-details"
                  :disabled="!editMode"
                ></v-text-field>

                <!-- Password Change Section -->
                <div v-if="editMode" class="password-section">
                  <v-divider class="my-6"></v-divider>
                  <h4 class="text-h6 font-weight-bold mb-4">Change Password</h4>

                  <v-text-field
                    v-model="passwordForm.current_password"
                    label="Current Password"
                    type="password"
                    variant="outlined"
                    class="mb-4"
                    prepend-inner-icon="mdi-lock"
                    :rules="[
                      v => !changePassword || !!v || 'Current password is required to change password'
                    ]"
                  ></v-text-field>

                  <v-text-field
                    v-model="passwordForm.new_password"
                    label="New Password"
                    type="password"
                    variant="outlined"
                    class="mb-4"
                    prepend-inner-icon="mdi-lock-plus"
                    :rules="[
                      v => !changePassword || !!v || 'New password is required',
                      v => !changePassword || v.length >= 8 || 'Password must be at least 8 characters',
                      v => !changePassword || /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
                      v => !changePassword || /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
                      v => !changePassword || /[0-9]/.test(v) || 'Password must contain at least one number'
                    ]"
                  ></v-text-field>

                  <v-text-field
                    v-model="passwordForm.confirm_password"
                    label="Confirm New Password"
                    type="password"
                    variant="outlined"
                    class="mb-4"
                    prepend-inner-icon="mdi-lock-check"
                    :rules="[
                      v => !changePassword || !!v || 'Please confirm your password',
                      v => !changePassword || v === passwordForm.new_password || 'Passwords do not match'
                    ]"
                  ></v-text-field>

                  <v-switch
                    v-model="changePassword"
                    label="I want to change my password"
                    color="primary"
                    class="mb-4"
                  ></v-switch>
                </div>
              </v-form>
            </v-card-text>

            <v-card-actions class="pa-6 pt-0">
              <v-spacer></v-spacer>

              <template v-if="editMode">
                <v-btn
                  class="modern-btn"
                  color="grey"
                  variant="outlined"
                  @click="cancelEdit"
                >
                  Cancel
                </v-btn>

                <v-btn
                  class="modern-btn ml-2"
                  color="primary"
                  @click="updateProfile"
                  :loading="authStore.loading"
                  prepend-icon="mdi-content-save"
                >
                  Save Changes
                </v-btn>
              </template>

              <v-btn
                v-else
                class="modern-btn"
                color="primary"
                @click="startEdit"
                prepend-icon="mdi-pencil"
              >
                Edit Profile
              </v-btn>
            </v-card-actions>
          </v-card>

          <!-- Account Statistics Card -->
          <v-card class="modern-card mb-6 animate-slide-in-up animate-delay-400">
            <v-card-title class="pa-6 pb-4">
              <div class="d-flex align-center">
                <v-avatar size="48" class="gradient-info mr-4">
                  <v-icon size="24" color="white">mdi-chart-line</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h5 font-weight-bold">Account Statistics</h3>
                  <p class="text-caption text-medium-emphasis mb-0">Your learning progress</p>
                </div>
              </div>
            </v-card-title>

            <v-card-text class="pa-6 pt-0">
              <v-row>
                <v-col cols="6" sm="3">
                  <div class="stat-card text-center">
                    <v-avatar size="64" class="gradient-primary mb-3">
                      <v-icon size="32" color="white">mdi-file-document</v-icon>
                    </v-avatar>
                    <p class="text-h4 font-weight-bold mb-1">{{ stats.documents }}</p>
                    <p class="text-caption text-medium-emphasis">Documents</p>
                  </div>
                </v-col>

                <v-col cols="6" sm="3">
                  <div class="stat-card text-center">
                    <v-avatar size="64" class="gradient-secondary mb-3">
                      <v-icon size="32" color="white">mdi-cards-outline</v-icon>
                    </v-avatar>
                    <p class="text-h4 font-weight-bold mb-1">{{ stats.decks }}</p>
                    <p class="text-caption text-medium-emphasis">Decks</p>
                  </div>
                </v-col>

                <v-col cols="6" sm="3">
                  <div class="stat-card text-center">
                    <v-avatar size="64" class="gradient-success mb-3">
                      <v-icon size="32" color="white">mdi-card-multiple</v-icon>
                    </v-avatar>
                    <p class="text-h4 font-weight-bold mb-1">{{ stats.flashcards }}</p>
                    <p class="text-caption text-medium-emphasis">Flashcards</p>
                  </div>
                </v-col>

                <v-col cols="6" sm="3">
                  <div class="stat-card text-center">
                    <v-avatar size="64" class="gradient-info mb-3">
                      <v-icon size="32" color="white">mdi-book-open-variant</v-icon>
                    </v-avatar>
                    <p class="text-h4 font-weight-bold mb-1">{{ stats.studySessions }}</p>
                    <p class="text-caption text-medium-emphasis">Study Sessions</p>
                  </div>
                </v-col>
              </v-row>

              <div class="text-center mt-6">
                <v-btn
                  class="modern-btn"
                  color="primary"
                  size="large"
                  to="/study-history"
                  prepend-icon="mdi-history"
                >
                  View Study History
                </v-btn>
              </div>
            </v-card-text>
          </v-card>

          <!-- Privacy & Data Card -->
          <v-card class="modern-card animate-slide-in-up animate-delay-600">
            <v-card-title class="pa-6 pb-4">
              <div class="d-flex align-center">
                <v-avatar size="48" class="gradient-secondary mr-4">
                  <v-icon size="24" color="white">mdi-shield-account</v-icon>
                </v-avatar>
                <div>
                  <h3 class="text-h5 font-weight-bold">Privacy & Data</h3>
                  <p class="text-caption text-medium-emphasis mb-0">Manage your data and privacy settings</p>
                </div>
              </div>
            </v-card-title>

            <v-card-text class="pa-6 pt-0">
              <p class="text-body-2 mb-6">
                Your data is stored securely and is only used to provide the flashcard service.
                We do not share your personal information with third parties.
              </p>

              <div class="d-flex flex-wrap gap-3">
                <v-btn
                  class="modern-btn"
                  color="primary"
                  variant="outlined"
                  @click="showExportDataDialog = true"
                  prepend-icon="mdi-download"
                >
                  Export My Data
                </v-btn>

                <v-btn
                  class="modern-btn"
                  color="error"
                  variant="outlined"
                  @click="showDeleteAccountDialog = true"
                  prepend-icon="mdi-delete"
                >
                  Delete My Account
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Delete Account Dialog -->
    <v-dialog
      v-model="showDeleteAccountDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Delete Account
        </v-card-title>

        <v-card-text>
          <p>
            Are you sure you want to delete your account? This action cannot be undone.
            All your data, including documents, decks, and flashcards will be permanently deleted.
          </p>

          <v-text-field
            v-model="deleteAccountPassword"
            label="Enter your password to confirm"
            type="password"
            required
          ></v-text-field>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showDeleteAccountDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            @click="deleteAccount"
            :loading="deletingAccount"
            :disabled="!deleteAccountPassword"
          >
            Delete My Account
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Export Data Dialog -->
    <v-dialog
      v-model="showExportDataDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title class="text-h5">
          Export My Data
        </v-card-title>

        <v-card-text>
          <p>
            You can export all your data in JSON format. This includes:
          </p>

          <ul>
            <li>Your profile information</li>
            <li>Your documents and extracted text</li>
            <li>Your flashcard decks</li>
            <li>Your study history</li>
          </ul>

          <v-checkbox
            v-model="exportOptions"
            label="Profile Information"
            value="profile"
          ></v-checkbox>

          <v-checkbox
            v-model="exportOptions"
            label="Documents & Extracted Text"
            value="documents"
          ></v-checkbox>

          <v-checkbox
            v-model="exportOptions"
            label="Flashcard Decks"
            value="decks"
          ></v-checkbox>

          <v-checkbox
            v-model="exportOptions"
            label="Study History"
            value="study"
          ></v-checkbox>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey darken-1"
            text
            @click="showExportDataDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="exportData"
            :loading="exporting"
            :disabled="exportOptions.length === 0"
          >
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'
import { useDocumentsStore } from '../store/documents'
import { useDecksStore } from '../store/decks'
import { useStudyStore } from '../store/study'

export default {
  name: 'ProfileView',
  data() {
    return {
      authStore: useAuthStore(),
      documentsStore: useDocumentsStore(),
      decksStore: useDecksStore(),
      studyStore: useStudyStore(),
      editMode: false,
      profileForm: {
        email: '',
        username: '',
        full_name: ''
      },
      passwordForm: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      changePassword: false,
      successMessage: '',
      stats: {
        documents: 0,
        decks: 0,
        flashcards: 0,
        studySessions: 0,
        cardsStudied: 0
      },
      showDeleteAccountDialog: false,
      showExportDataDialog: false,
      deleteAccountPassword: '',
      deletingAccount: false,
      exportOptions: ['profile', 'documents', 'decks', 'study'],
      exporting: false
    }
  },
  created() {
    this.loadUserProfile()
    this.loadStats()
  },
  methods: {
    async loadUserProfile() {
      const user = this.authStore.currentUser

      if (user) {
        this.profileForm = {
          email: user.email,
          username: user.username,
          full_name: user.full_name || ''
        }
      } else {
        await this.authStore.fetchUserProfile()
        const updatedUser = this.authStore.currentUser

        if (updatedUser) {
          this.profileForm = {
            email: updatedUser.email,
            username: updatedUser.username,
            full_name: updatedUser.full_name || ''
          }
        }
      }
    },

    async loadStats() {
      // Load documents
      await this.documentsStore.fetchDocuments()
      this.stats.documents = this.documentsStore.documents.length

      // Load decks
      await this.decksStore.fetchDecks()
      this.stats.decks = this.decksStore.decks.length

      // Count flashcards
      let flashcardCount = 0
      for (const deck of this.decksStore.decks) {
        if (deck.flashcards) {
          flashcardCount += deck.flashcards.length
        }
      }
      this.stats.flashcards = flashcardCount

      // Load study sessions
      await this.studyStore.fetchStudySessions()
      this.stats.studySessions = this.studyStore.sessions.length

      // Count cards studied
      let cardsStudied = 0
      for (const session of this.studyStore.sessions) {
        await this.studyStore.fetchStudyRecords(session.id)
        cardsStudied += this.studyStore.records.length
      }
      this.stats.cardsStudied = cardsStudied
    },

    startEdit() {
      this.editMode = true
    },

    cancelEdit() {
      this.editMode = false
      this.loadUserProfile()
      this.passwordForm = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      }
      this.changePassword = false
    },

    async updateProfile() {
      if (!this.editMode) return

      // Validate form
      if (!this.$refs.form.validate()) return

      // Prepare update data
      const updateData = {
        email: this.profileForm.email,
        full_name: this.profileForm.full_name
      }

      // Update profile
      const success = await this.authStore.updateProfile(updateData)

      if (success) {
        this.successMessage = 'Profile updated successfully'
        this.editMode = false
      }
    },

    async deleteAccount() {
      if (!this.deleteAccountPassword) return

      this.deletingAccount = true

      // TODO: Implement account deletion
      // This would require a backend endpoint

      this.deletingAccount = false
      this.showDeleteAccountDialog = false
    },

    async exportData() {
      if (this.exportOptions.length === 0) return

      this.exporting = true

      // Prepare export data
      const exportData = {}

      if (this.exportOptions.includes('profile')) {
        exportData.profile = this.authStore.currentUser
      }

      if (this.exportOptions.includes('documents')) {
        exportData.documents = this.documentsStore.documents
      }

      if (this.exportOptions.includes('decks')) {
        exportData.decks = this.decksStore.decks
      }

      if (this.exportOptions.includes('study')) {
        exportData.studySessions = this.studyStore.sessions
        exportData.studyRecords = this.studyStore.records
      }

      // Create and download JSON file
      const dataStr = JSON.stringify(exportData, null, 2)
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)

      const exportFileDefaultName = 'flashcards-data.json'

      const linkElement = document.createElement('a')
      linkElement.setAttribute('href', dataUri)
      linkElement.setAttribute('download', exportFileDefaultName)
      linkElement.click()

      this.exporting = false
      this.showExportDataDialog = false
    }
  }
}
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.v-theme--dark .profile-view {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.stat-card {
  padding: 16px;
  border-radius: var(--border-radius-lg);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.v-theme--dark .stat-card {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-color: rgba(96, 165, 250, 0.2);
}

.password-section {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%);
  border-radius: var(--border-radius-lg);
  padding: 20px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.v-theme--dark .password-section {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border-color: rgba(96, 165, 250, 0.3);
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
