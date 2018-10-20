<template>
  <v-container>
       <v-layout>
           <v-dialog v-model="visible" max-width="390" ref="popup">
               <v-card>
                   <v-card-title class="headline">{{ title }}</v-card-title>
                   <v-card-text>{{  message }}</v-card-text>
                   <v-card-actions>
                       <v-spacer></v-spacer>
                       <v-btn color="primary" flat="flat" @click.native="click(false)">{{ no }}</v-btn>
                       <v-btn color="primary" flat="flat" @click.native="click(true)">{{ yes }}</v-btn>
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
    yes: 'OK',
    no: 'Cancel',
    message: 'Are you sure?'
  }),

  methods: {
    confirm(config) {
       this.title = ( config.title === undefined ? this.title : config.title )
       this.message = ( config.message === undefined ? this.message : config.message )
       this.yes = ( config.yes === undefined ? this.yes : config.yes )
       this.no = ( config.no === undefined ? this.no : config.no )

       this.visible = true;

       return new Promise((resolve) => { this.resolve = resolve });
    },

    click(result) {
      this.visible = false
      if(this.resolve) this.resolve(result)
    }
  }
}
</script>
