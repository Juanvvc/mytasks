<template>
  <div>
    <v-toolbar app fixed clipped-left color="primary darken-4" dark>
        <v-toolbar-title>MyTasks</v-toolbar-title>
    </v-toolbar>

    <v-content>
      <v-layout justify-center align-center wrap xs12 md10>
        <v-card>
          <!--  Title and toolbar !-->
          <v-toolbar card prominent color="secondary" class="checklist-header">
            <v-toolbar-title class="body-2">
              <span class="white--text headline">Login to MyTasks</span>
            </v-toolbar-title>
          </v-toolbar>

          <v-card-text>
            <v-layout column xs12 md6>
              <v-text-field
                placeholder="Username"
                label="Username"
                v-model="username"
                prepend-icon="face"
                :rules="[rules.required]" />
              <v-text-field
                placeholder="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                :append-icon="showPassword ? 'visibility_off' : 'visibility'"
                :rules="[rules.required]"
                counter
                prepend-icon="fingerprint"
                @keyup.enter="login"
                @click:append="showPassword = !showPassword" />
              <v-switch
                label="Remember me"
                v-model="rememberMe" />

            </v-layout>
            <v-layout align-center justify-center>
              <v-btn
                color="primary"
                @click="login">
                Login
              </v-btn>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-layout>
    </v-content>

    <v-footer app height="auto">
      <v-layout
        justify-center
        row
        wrap
        >
        <span class="caption">&copy; 2018, Juanvi Vera. Under the GPL. <a href="https://github.com/Juanvvc/mytasks">Source code available in Github</a>.</span>
      </v-layout>
    </v-footer>
  </div>
</template>

<script>

import mytasks from '@/libs/mytasksclient.js'

export default {
  data: () => ({
    username: '',
    password: '',
    showPassword: false,
    rememberMe: false,
    rules: {
      required: value => !!value || 'Required.'
    }
  }),

  methods: {
    async login() {
      let response = await mytasks.login({username: this.username, password: this.password})
      if(!response) {
        this.$emit('showError', 'Cannot connect to the server')
        return
      }
      if(response.data.error_message !== undefined) {
        this.$emit('showError', response.data.error_message)
      } else {
        if(this.rememberMe) {
          // if user wants to be remembered, save token in local storage
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('useruri', response.data.uri)
        } else {
          // if user doesn't want to be remembered, save token in RAM
          sessionStorage.setItem('token', response.data.token)
          sessionStorage.setItem('useruri', response.data.uri)
        }
        this.$router.push({ name: 'user' })
      }
    }
  }
}
</script>
