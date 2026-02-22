<template>
  <div class="admin-view">
    <v-container class="py-8">
      <div class="text-center mb-8 animate-fade-in">
        <v-avatar size="80" class="gradient-secondary mb-4 animate-pulse">
          <v-icon size="40" color="white">mdi-shield-account</v-icon>
        </v-avatar>
        <h1 class="text-h3 font-weight-bold mb-2">Admin</h1>
        <p class="text-h6 text-medium-emphasis">System stats and user management</p>
      </div>

      <v-row justify="center">
        <v-col cols="12" md="11" lg="10">
          <v-alert v-if="errorMessage" type="error" variant="tonal" class="modern-card mb-6" closable @click:close="errorMessage = ''">
            {{ errorMessage }}
          </v-alert>
          <v-alert v-if="successMessage" type="success" variant="tonal" class="modern-card mb-6" closable @click:close="successMessage = ''">
            {{ successMessage }}
          </v-alert>

          <v-card class="modern-card mb-6">
            <v-card-title class="pa-6 pb-4 d-flex align-center">
              <v-avatar size="48" class="gradient-info mr-4"><v-icon size="24" color="white">mdi-chart-bar</v-icon></v-avatar>
              <div class="flex-grow-1">
                <h3 class="text-h5 font-weight-bold">System Stats</h3>
                <p class="text-caption text-medium-emphasis mb-0">Overview</p>
              </div>
              <v-btn class="modern-btn" variant="outlined" prepend-icon="mdi-refresh" @click="loadAll" :loading="loading">Refresh</v-btn>
            </v-card-title>
            <v-card-text class="pa-6 pt-0">
              <v-row>
                <v-col v-for="s in statsCards" :key="s.key" cols="6" sm="4" md="2">
                  <div class="stat-card text-center">
                    <p class="text-h4 font-weight-bold mb-1">{{ stats[s.key] ?? 0 }}</p>
                    <p class="text-caption text-medium-emphasis mb-0">{{ s.label }}</p>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <v-card class="modern-card">
            <v-card-title class="pa-6 pb-4">
              <div class="d-flex align-center">
                <v-avatar size="48" class="gradient-primary mr-4"><v-icon size="24" color="white">mdi-account-multiple</v-icon></v-avatar>
                <div>
                  <h3 class="text-h5 font-weight-bold">Users</h3>
                  <p class="text-caption text-medium-emphasis mb-0">{{ users.length }} users</p>
                </div>
              </div>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-data-table :headers="headers" :items="users" :loading="loadingUsers" :items-per-page="10" class="modern-table">
                <template #[`item.role`]="{ item }">
                  <v-chip :color="item.role === 'admin' ? 'purple' : 'blue'" size="small" variant="flat">{{ item.role }}</v-chip>
                </template>
                <template #[`item.is_active`]="{ item }">
                  <v-chip :color="item.is_active ? 'green' : 'red'" size="small" variant="flat">{{ item.is_active ? 'active' : 'inactive' }}</v-chip>
                </template>
                <template #[`item.actions`]="{ item }">
                  <div class="d-flex gap-2">
                      <v-btn class="modern-btn" size="small" color="primary" prepend-icon="mdi-pencil" :disabled="isSystem(item)" @click="openEdit(item)">Edit</v-btn>
                      <v-btn class="modern-btn" size="small" variant="outlined" prepend-icon="mdi-lock-reset" :disabled="isSystem(item)" @click="openReset(item)">Reset</v-btn>
                      <v-btn class="modern-btn" size="small" color="error" variant="outlined" icon="mdi-delete" :disabled="isSelf(item) || isSystem(item)" @click="openDelete(item)"></v-btn>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-dialog v-model="showEditDialog" max-width="520px">
        <v-card class="modern-card">
          <v-card-title class="pa-6 pb-4"><h3 class="text-h6 font-weight-bold">Edit user: {{ editForm.username }}</h3></v-card-title>
          <v-card-text class="pa-6 pt-0">
              <v-text-field v-model="editForm.email" label="Email" type="email" variant="outlined" class="mb-3" :disabled="isSystem(editForm)" />
              <v-text-field v-model="editForm.full_name" label="Full name" variant="outlined" class="mb-3" :disabled="isSystem(editForm)" />
              <v-select v-model="editForm.role" :items="['user','admin']" label="Role" variant="outlined" class="mb-3" :disabled="isSelf(editForm) || isSystem(editForm)" />
              <v-switch v-model="editForm.is_active" label="Active" color="primary" :disabled="isSelf(editForm) || isSystem(editForm)" />
          </v-card-text>
          <v-card-actions class="pa-6 pt-0">
            <v-spacer />
            <v-btn class="modern-btn" variant="outlined" @click="showEditDialog=false">Cancel</v-btn>
              <v-btn class="modern-btn ml-2" color="primary" :loading="saving" prepend-icon="mdi-content-save" :disabled="isSystem(editForm)" @click="saveEdit">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="showResetDialog" max-width="520px">
        <v-card class="modern-card">
          <v-card-title class="pa-6 pb-4"><h3 class="text-h6 font-weight-bold">Reset password: {{ resetUser?.username }}</h3></v-card-title>
          <v-card-text class="pa-6 pt-0">
            <v-text-field v-model="resetPassword" label="New password" type="password" variant="outlined" />
            <p class="text-caption text-medium-emphasis mt-2">Min 8 chars, 1 uppercase, 1 lowercase, 1 digit.</p>
          </v-card-text>
          <v-card-actions class="pa-6 pt-0">
            <v-spacer />
            <v-btn class="modern-btn" variant="outlined" @click="showResetDialog=false">Cancel</v-btn>
              <v-btn class="modern-btn ml-2" color="primary" :loading="saving" prepend-icon="mdi-lock-reset" :disabled="!resetPassword || isSystem(resetUser)" @click="confirmReset">Reset</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="showDeleteDialog" max-width="420px">
        <v-card class="modern-card">
          <v-card-title class="pa-6 pb-4"><h3 class="text-h6 font-weight-bold">Confirm delete</h3></v-card-title>
          <v-card-text class="pa-6 pt-0">
            Delete user <strong>{{ deleteUser?.username }}</strong>? This cannot be undone.
          </v-card-text>
          <v-card-actions class="pa-6 pt-0">
            <v-spacer />
            <v-btn class="modern-btn" variant="outlined" @click="showDeleteDialog=false">Cancel</v-btn>
              <v-btn class="modern-btn ml-2" color="error" :loading="saving" :disabled="isSystem(deleteUser)" @click="confirmDelete">Delete</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth'
import { adminAPI } from '../api'

export default {
  name: 'AdminView',
  data() {
    return {
      authStore: useAuthStore(),
      loading: false,
      loadingUsers: false,
      saving: false,
      errorMessage: '',
      successMessage: '',
      stats: {},
      users: [],
      headers: [
        { text: 'Username', value: 'username' },
        { text: 'Email', value: 'email' },
        { text: 'Full name', value: 'full_name' },
        { text: 'Role', value: 'role' },
        { text: 'Active', value: 'is_active' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      statsCards: [
        { key: 'users_total', label: 'Users' },
        { key: 'admins_total', label: 'Admins' },
        { key: 'documents_total', label: 'Docs' },
        { key: 'decks_total', label: 'Decks' },
        { key: 'flashcards_total', label: 'Cards' }
      ],
      showEditDialog: false,
      editForm: { id: '', username: '', email: '', full_name: '', role: 'user', is_active: true },
      showResetDialog: false,
      resetUser: null,
      resetPassword: '',
      showDeleteDialog: false,
      deleteUser: null
    }
  },
  async created() {
    if (this.authStore.isAuthenticated && !this.authStore.currentUser) {
      await this.authStore.fetchUserProfile()
    }
    await this.loadAll()
  },
  methods: {
      isSystem(user) {
        return !!user && (user.username || '').toLowerCase() === 'system'
      },
    isSelf(user) {
      const me = this.authStore.currentUser
      return !!me && !!user && me.id === user.id
    },
    async loadAll() {
      this.errorMessage = ''
      this.successMessage = ''
      this.loading = true
      try {
        await Promise.all([this.fetchStats(), this.fetchUsers()])
      } catch (e) {
        // errors handled inside
      } finally {
        this.loading = false
      }
    },
    async fetchStats() {
      try {
        const resp = await adminAPI.getStats()
        this.stats = resp.data || {}
      } catch (e) {
        this.errorMessage = e.response?.data?.detail || 'Failed to load stats'
      }
    },
    async fetchUsers() {
      this.loadingUsers = true
      try {
        const resp = await adminAPI.getUsers(0, 200)
        this.users = Array.isArray(resp.data) ? resp.data : []
      } catch (e) {
        this.errorMessage = e.response?.data?.detail || 'Failed to load users'
      } finally {
        this.loadingUsers = false
      }
    },
    openEdit(user) {
        if (this.isSystem(user)) {
          this.errorMessage = 'System user cannot be modified'
          return
        }
      this.editForm = { ...user }
      this.showEditDialog = true
    },
    async saveEdit() {
      this.saving = true
      this.errorMessage = ''
      try {
        const payload = {
          email: this.editForm.email,
          full_name: this.editForm.full_name,
          role: this.editForm.role,
          is_active: this.editForm.is_active
        }
        await adminAPI.updateUser(this.editForm.id, payload)
        this.successMessage = 'User updated'
        this.showEditDialog = false
        await this.fetchUsers()
      } catch (e) {
        this.errorMessage = e.response?.data?.detail || 'Failed to update user'
      } finally {
        this.saving = false
      }
    },
    openReset(user) {
        if (this.isSystem(user)) {
          this.errorMessage = 'System user password cannot be reset'
          return
        }
      this.resetUser = user
      this.resetPassword = ''
      this.showResetDialog = true
    },
    async confirmReset() {
      if (!this.resetUser) return
        if (this.isSystem(this.resetUser)) {
          this.errorMessage = 'System user password cannot be reset'
          return
        }
      this.saving = true
      this.errorMessage = ''
      try {
        await adminAPI.resetPassword(this.resetUser.id, this.resetPassword)
        this.successMessage = 'Password reset'
        this.showResetDialog = false
      } catch (e) {
        this.errorMessage = e.response?.data?.detail || 'Failed to reset password'
      } finally {
        this.saving = false
      }
    },
    openDelete(user) {
        if (this.isSystem(user)) {
          this.errorMessage = 'System user cannot be deleted'
          return
        }
      this.deleteUser = user
      this.showDeleteDialog = true
    },
    async confirmDelete() {
      if (!this.deleteUser) return
        if (this.isSystem(this.deleteUser)) {
          this.errorMessage = 'System user cannot be deleted'
          return
        }
      this.saving = true
      this.errorMessage = ''
      try {
        await adminAPI.deleteUser(this.deleteUser.id)
        this.successMessage = 'User deleted'
        this.showDeleteDialog = false
        await this.fetchUsers()
      } catch (e) {
        this.errorMessage = e.response?.data?.detail || 'Failed to delete user'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}
.v-theme--dark .admin-view {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.stat-card {
  padding: 14px;
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(59, 130, 246, 0.12);
  background: rgba(59, 130, 246, 0.04);
}
</style>


