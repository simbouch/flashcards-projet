<template>
  <div class="profile">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title class="text-h5">
              My Profile
            </v-card-title>
            
            <v-card-text>
              <v-alert
                v-if="authStore.error"
                type="error"
                dismissible
                @click:close="authStore.clearError()"
              >
                {{ authStore.error }}
              </v-alert>
              
              <v-alert
                v-if="successMessage"
                type="success"
                dismissible
                @click:close="successMessage = ''"
              >
                {{ successMessage }}
              </v-alert>
              
              <v-form @submit.prevent="updateProfile" ref="form">
                <v-text-field
                  v-model="profileForm.email"
                  label="Email"
                  type="email"
                  required
                  :rules="[
                    v => !!v || 'Email is required',
                    v => /.+@.+\..+/.test(v) || 'Email must be valid'
                  ]"
                  prepend-icon="mdi-email"
                  :disabled="!editMode"
                ></v-text-field>
                
                <v-text-field
                  v-model="profileForm.username"
                  label="Username"
                  required
                  prepend-icon="mdi-account"
                  disabled
                ></v-text-field>
                
                <v-text-field
                  v-model="profileForm.full_name"
                  label="Full Name"
                  prepend-icon="mdi-account-details"
                  :disabled="!editMode"
                ></v-text-field>
                
                <v-divider class="my-4"></v-divider>
                
                <v-expansion-panels v-if="editMode">
                  <v-expansion-panel>
                    <v-expansion-panel-header>
                      Change Password
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <v-text-field
                        v-model="passwordForm.current_password"
                        label="Current Password"
                        type="password"
                        prepend-icon="mdi-lock"
                        :rules="[
                          v => !changePassword || !!v || 'Current password is required to change password'
                        ]"
                      ></v-text-field>
                      
                      <v-text-field
                        v-model="passwordForm.new_password"
                        label="New Password"
                        type="password"
                        prepend-icon="mdi-lock-plus"
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
                        prepend-icon="mdi-lock-check"
                        :rules="[
                          v => !changePassword || !!v || 'Please confirm your password',
                          v => !changePassword || v === passwordForm.new_password || 'Passwords do not match'
                        ]"
                      ></v-text-field>
                      
                      <v-checkbox
                        v-model="changePassword"
                        label="I want to change my password"
                        color="primary"
                      ></v-checkbox>
                    </v-expansion-panel-content>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-form>
            </v-card-text>
            
            <v-card-actions>
              <v-spacer></v-spacer>
              
              <template v-if="editMode">
                <v-btn
                  color="grey darken-1"
                  text
                  @click="cancelEdit"
                >
                  Cancel
                </v-btn>
                
                <v-btn
                  color="primary"
                  @click="updateProfile"
                  :loading="authStore.loading"
                >
                  Save
                </v-btn>
              </template>
              
              <v-btn
                v-else
                color="primary"
                @click="startEdit"
              >
                Edit Profile
              </v-btn>
            </v-card-actions>
          </v-card>
          
          <v-card class="mt-6">
            <v-card-title class="text-h5">
              Account Statistics
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4">
                    <div class="text-h4 primary--text">{{ stats.documents }}</div>
                    <div class="text-subtitle-1">Documents</div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4">
                    <div class="text-h4 primary--text">{{ stats.decks }}</div>
                    <div class="text-subtitle-1">Decks</div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" sm="4">
                  <v-card outlined class="text-center pa-4">
                    <div class="text-h4 primary--text">{{ stats.flashcards }}</div>
                    <div class="text-subtitle-1">Flashcards</div>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-row class="mt-4">
                <v-col cols="12" sm="6">
                  <v-card outlined class="text-center pa-4">
                    <div class="text-h4 primary--text">{{ stats.studySessions }}</div>
                    <div class="text-subtitle-1">Study Sessions</div>
                  </v-card>
                </v-col>
                
                <v-col cols="12" sm="6">
                  <v-card outlined class="text-center pa-4">
                    <div class="text-h4 primary--text">{{ stats.cardsStudied }}</div>
                    <div class="text-subtitle-1">Cards Studied</div>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          
          <v-card class="mt-6">
            <v-card-title class="text-h5">
              Privacy & Data
            </v-card-title>
            
            <v-card-text>
              <p>
                Your data is stored securely and is only used to provide the flashcard service.
                We do not share your personal information with third parties.
              </p>
              
              <v-divider class="my-4"></v-divider>
              
              <v-btn
                color="error"
                outlined
                @click="showDeleteAccountDialog = true"
              >
                Delete My Account
              </v-btn>
              
              <v-btn
                color="primary"
                outlined
                class="ml-4"
                @click="showExportDataDialog = true"
              >
                Export My Data
              </v-btn>
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
