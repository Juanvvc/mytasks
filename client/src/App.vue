<template>
  <div id="app">
    <v-app id="inspire">
      <v-alert
        v-model="showErrorMessage"
        dismissible
        type="error"
        transition="$primary-transition"
        >
          {{ errorMessage }}
      </v-alert>
      <router-view @showError="showError"/>
      <v-footer app fixed>
        <span>&copy; 2018, Juanvi Vera</span>
      </v-footer>
    </v-app>
  </div>
</template>

<script>
export default {
  data: () => ({
    errorMessage: null,
    showErrorMessage: false
  }),
  methods: {
    showError(errorMessage) {
      this.errorMessage = errorMessage
      this.showErrorMessage = true
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.pointable {
  cursor: pointer;
}
</style>
