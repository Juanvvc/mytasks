<template>
  <div>
      <!--  Title and toolbar !-->
    <v-toolbar app fixed clipped-left color="primary darken-2" dark>
        <v-toolbar-title>Login to MyTasks</v-toolbar-title>
    </v-toolbar>

    <!-- Main content -->
      <v-content>
        <v-container>
          <v-layout column xs12 md6>
            <v-text-field
              placeholder="Username"
              label="Username"
              v-model="username"
              :rules="[rules.required]" />
            <v-text-field
              placeholder="password"
              label="Password"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              :append-icon="showPassword ? 'visibility_off' : 'visibility'"
              :rules="[rules.required]"
              counter
              @click:append="showPassword = !showPassword" />
          </v-layout>
          <v-layout align-center justify-center>
            <v-btn
              color="primary"
              @click="login">
              Login
            </v-btn>
          </v-layout>
        </v-container>
    </v-content>

  </div>
</template>

<script>

export default {
  name: 'home',

  data: () => ({
    username: '',
    password: '',
    showPassword: false,
    rules: {
      required: value => !!value || 'Required.'
    }
  }),

  methods: {
    login() {
      sessionStorage.setItem('username', this.username)
      sessionStorage.setItem('password', this.password)
      this.$router.push({ name: 'home' })
    }
  }
}
</script>
