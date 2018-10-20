<template>
   <v-dialog v-model="visible" max-width="500" ref="popup">
       <v-card>
           <v-card-title class="headline">{{ title }}</v-card-title>

           <v-layout column class="px-3">
             <v-text-field
              label="Name"
              placeholder="Name"
              v-model="name"
              clearable
              hint="Start with # to convert to a section."
              @keyup.enter="click(true)"
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
                  clearable
                ></v-text-field>
                <v-date-picker
                  v-model="due_date"
                  first-day-of-week="1"
                  no-title
                  @input="menuDate = false" />
              </v-menu>
            </v-flex>
            <v-text-field
              placeholder="RRULE"
              label="RRULE"
              hint="RRULE, as defined in RFC5545"
              v-model="rrule"
              clearable
              prepend-icon="repeat" />
           </v-layout>

           <v-card-actions>
             <!-- Setting to name to empy will delet the item. TODO: look for a nicer way to do this -->
             <v-btn color="warning darken-1" flat @click="name=''; click(true)">Delete</v-btn>
             <v-spacer></v-spacer>
             <v-btn color="primary darken-1" flat @click="click(false)">Cancel</v-btn>
             <v-btn color="primary darken-1" flat @click="click(true)">Save</v-btn>
           </v-card-actions>
       </v-card>
   </v-dialog>
</template>

<script>
export default {
  data: () => ({
    visible: false,
    title: 'Edit Item',
    due_date: '',
    name: '',
    comment: '',
    menuDate: false,
    rrule: ''
  }),

  methods: {
    show(config) {
      this.resolve = undefined
      this.reject = undefined
      this.title = ( config.title === undefined ? this.title : config.title )

      this.name = ( config.name === undefined ? this.name : config.name )
      this.comment = ( config.comment === undefined ? this.comment : config.comment )
      this.due_date = ( config.due_date === undefined ? this.due_date : config.due_date )
      this.rrule = (config.rrule === undefined ? this.rrule : config.rrule)

      this.visible = true;

      return new Promise((resolve, reject) => { this.resolve = resolve; this.reject = reject });
    },

    click(result) {
      this.visible = false
      if(!this.resolve) return

      if(result) {
        this.resolve({
          name: (this.name!==null?this.name.trim():''),
          comment: (this.comment!==null?this.comment.trim():''),
          due_date: (this.due_date!==null?this.due_date.trim():''),
          rrule: this.rrule
        })
        this.name = ''
        this.comment = ''
        this.due_date = ''
        this.rrule = ''
      } else {
        this.resolve(null)
      }
    }
  }
}
</script>
