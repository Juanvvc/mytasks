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
      <v-footer app fixed height="auto">
        <v-layout
          justify-center
          row
          wrap
          >
          <span class="caption">&copy; 2018, Juanvi Vera. <a href="https://github.com/Juanvvc/mytasks">Check me in Github</a>.</span>
        </v-layout>
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
      console.log(errorMessage)
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
