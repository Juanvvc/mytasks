<template>
  <v-container>
       <v-layout>
           <v-dialog v-model="visible" max-width="290" ref="popup">
               <v-card>
                   <v-card-title class="headline">{{ title }}</v-card-title>
                   <v-card-text>{{  message }}</v-card-text>
                   <v-card-actions>
                       <v-spacer></v-spacer>
                       <v-btn color="primary darken-1" flat="flat" @click.native="click(true)">{{ yes }}</v-btn>
                       <v-btn color="primary darken-1" flat="flat" @click.native="click(false)">{{ no }}</v-btn>
                   </v-card-actions>
               </v-card>
           </v-dialog>
       </v-layout>
   </v-container>
</template>

<script>
export default {
  data: () => ({
    visible: false,
    resolve: null,
    title: 'Confirm',
    yes: 'Yes',
    no: 'No',
    message: 'Are you sure?'
  }),

  methods: {
    confirm(config) {
       this.title = ( config.title === undefined ? 'Confirm' : config.title )
       this.message = ( config.message === undefined ? 'Are you sure?' : config.message )
       this.yes = ( config.yes === undefined ? 'Yes' : config.yes )
       this.no = ( config.no === undefined ? 'No' : config.no )

       this.visible = true;

       return new Promise((resolve, reject) => { this.resolve = resolve });
    },

    click(result) {
      this.visible = false
      this.resolve(result)
    }
  }
}
</script>
