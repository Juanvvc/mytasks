<template>
  <div id="app">
    <v-app id="inspire">
      <v-alert
        v-model="showAlertMessage"
        dismissible
        :type="alertType"
        transition="$primary-transition"
        >
          {{ alertMessage }}
      </v-alert>
      <router-view @showError="showMessage('error', $event)" @showWarning="showMessage('warning', $event)"/>

    </v-app>
  </div>
</template>

<script>
export default {
  data: () => ({
    errorMessage: null,
    showAlertMessage: false,
    alertType: 'error'
  }),
  methods: {
    showMessage(alertType, errorMessage) {
      this.alertMessage = errorMessage
      this.showAlertMessage = true
      this.alertType = alertType
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

.application--wrap {
  background-color: #ccccde;
}

.header  {
  font-family: 'Roboto Slab', serif !important;
}
</style>
