<template>
   <v-dialog v-model="visible" max-width="500" ref="popup">
       <v-card>
           <v-card-title class="headline">{{ title }}</v-card-title>

           <v-layout column>
             <v-text-field
              label="Name"
              placeholder="Name"
              v-model="name"
              hint="Start with # to convert to a section. Empty to delete item."
              prepend-icon="translate" />
             <v-textarea
              label="Comment"
              hint="Comment"
              placeholder="Comment"
              v-model="comment"
              prepend-icon="comment" />
             <v-flex xs12 lg6>
              <v-menu
                ref="menuDate"
                :close-on-content-click="false"
                v-model="menuDate"
                :nudge-right="40"
                lazy
                transition="scale-transition"
                offset-y
                full-width
                max-width="290px"
                min-width="290px"
              >
                <v-text-field
                  slot="activator"
                  v-model="due_date"
                  label="Due date"
                  persistent-hint
                  prepend-icon="event"
                ></v-text-field>
                <v-date-picker v-model="due_date" no-title @input="menuDate = false"></v-date-picker>
              </v-menu>
            </v-flex>
           </v-layout>

           <v-card-actions>
               <v-spacer></v-spacer>
               <v-btn color="primary darken-1" flat="flat" @click="click(true)">{{ yes }}</v-btn>
               <v-btn color="primary darken-1" flat="flat" @click="click(false)">{{ no }}</v-btn>
           </v-card-actions>
       </v-card>
   </v-dialog>
</template>

<script>
export default {
  data: () => ({
    visible: false,
    title: 'Edit Item',
    yes: 'OK',
    no: 'Cancel',
    due_date: '',
    name: '',
    comment: '',
    menuDate: false
  }),

  methods: {
    show(config) {
      this.resolve = undefined
      this.reject = undefined
      this.title = ( config.title === undefined ? this.title : config.title )
      this.yes = ( config.yes === undefined ? this.yes : config.yes )
      this.no = ( config.no === undefined ? this.no : config.no )

      this.name = ( config.name === undefined ? this.name : config.name )
      this.comment = ( config.comment === undefined ? this.comment : config.comment )
      this.due_date = ( config.due_date === undefined ? this.due_date : config.due_date )

      this.visible = true;

      return new Promise((resolve, reject) => { this.resolve = resolve; this.reject = reject });
    },

    click(result) {
      this.visible = false

      if(result && this.resolve !== undefined) {
        this.resolve({
          name: this.name.trim(),
          comment: this.comment.trim(),
          due_date: this.due_date.trim()
        })
        this.name = ''
        this.comment = ''
      }
    }
  }
}
</script>
