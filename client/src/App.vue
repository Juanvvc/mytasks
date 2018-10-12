<template>
  <div id="app">
    <v-app id="inspire">
      <v-snackbar
      v-model="showAlertMessage"
      :color="alertType"
      :timeout="6000"
      top
      >
        {{ alertMessage}}
      </v-snackbar>
      <router-view @showError="showMessage('error', $event)" @showWarning="showMessage('warning', $event)"/>

    </v-app>
  </div>
</template>

<script>
export default {
  data: () => ({
    alertMessage: null,
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
  /*margin-top: 60px;*/
}

.pointable {
  cursor: pointer;
}

.movable {
  cursor: move;
}

.header  {
  font-family: 'Roboto Slab', serif !important;
}
</style>
