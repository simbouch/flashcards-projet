<template>
  <div class="not-found">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8" class="text-center">
          <v-card>
            <v-card-title class="text-h4 justify-center">
              404 - Page Not Found
            </v-card-title>
            
            <v-card-text class="text-center">
              <v-icon size="100" color="primary">mdi-alert-circle-outline</v-icon>
              
              <p class="text-h6 mt-4">
                Oops! The page you're looking for doesn't exist.
              </p>
              
              <p class="text-body-1 mt-2">
                It seems you've followed a broken link or entered a URL that doesn't exist on this site.
              </p>
            </v-card-text>
            
            <v-card-actions class="justify-center pb-6">
              <v-btn
                color="primary"
                to="/"
                large
              >
                <v-icon left>mdi-home</v-icon>
                Go to Home
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>
