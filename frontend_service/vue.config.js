const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // Disable eslint errors during build
  lintOnSave: false
})
