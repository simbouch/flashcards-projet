<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Flashcards App</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="!isAuthenticated" to="/login" text>Login</v-btn>
      <v-btn v-if="!isAuthenticated" to="/register" text>Register</v-btn>
      <v-btn v-if="isAuthenticated" @click="logout" text>Logout</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" app temporary>
      <v-list>
        <v-list-item to="/" link>
          <v-list-item-icon>
            <v-icon>mdi-home</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Home</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item v-if="isAuthenticated" to="/documents" link>
          <v-list-item-icon>
            <v-icon>mdi-file-document</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Documents</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item v-if="isAuthenticated" to="/decks" link>
          <v-list-item-icon>
            <v-icon>mdi-cards</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>My Decks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item to="/public-decks" link>
          <v-list-item-icon>
            <v-icon>mdi-cards-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Public Decks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item v-if="isAuthenticated" to="/profile" link>
          <v-list-item-icon>
            <v-icon>mdi-account</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app color="primary" dark>
      <v-row justify="center" no-gutters>
        <v-col class="text-center" cols="12">
          {{ new Date().getFullYear() }} — <strong>Flashcards App</strong>
        </v-col>
      </v-row>
    </v-footer>
  </v-app>
</template>

<script>
import { useAuthStore } from './store/auth'
import { mapState } from 'pinia'

export default {
  name: 'App',
  data() {
    return {
      drawer: false
    }
  },
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated'])
  },
  methods: {
    logout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
}
</style>
