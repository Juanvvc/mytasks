<template>
  <v-dialog v-model="visible" max-width="500" ref="popup">
    <v-card>
      <v-card-title class="headline">{{ title }}</v-card-title>

      <v-layout column>
        <v-text-field
          label="Name"
          placeholder="Name"
          v-model="name"
          clearable
          @keyup.enter="click(true)"
          prepend-icon="translate" />
        <v-text-field
          placeholder="Priority"
          label="Priority"
          hint="Used to order checklists in a group. A higher number means a higher priority"
          v-model="order"
          clearable
          prepend-icon="mdi-priority-high" />
        <v-select
          placeholder="Group"
          label="Group"
          v-model="parentid"
          :items="availableGroups"
          item-text="name"
          item-value="_id"
          prepend-icon="mdi-tag" />
        <v-textarea
          label="Description"
          placeholder="Description"
          v-model="description"
          prepend-icon="mdi-comment-text" />
      </v-layout>

      <v-card-actions>
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
  props: {
    availableGroups: {
      type: Array,
      mandatory: true
    }
  },

  data: () => ({
    visible: false,
    title: 'Edit Checklist',
    name: '',
    description: '',
    parentid: 0,
    groups: [],
    order: null,
    menuDate: false
  }),

  methods: {
    show(config) {
      this.resolve = undefined
      this.reject = undefined
      this.title = ( config.title === undefined ? this.title : config.title )

      this.name = ( config.name === undefined ? this.name : config.name )
      this.description = ( config.description === undefined ? this.description : config.description )
      this.parentid = (config.parentid === undefined ? this.parentid : config.parentid)
      this.order = (config.order === undefined ? this.order : config.order)

      this.visible = true;

      return new Promise((resolve, reject) => { this.resolve = resolve; this.reject = reject });
    },

    click(result) {
      this.visible = false
      if(!this.resolve) return

      if(result) {
        this.resolve({
          name: (this.name!==null?this.name.trim():''),
          description: (this.description!==null?this.description.trim():''),
          parentid: this.parentid,
          order: this.order
        })
        this.name = ''
        this.comment = ''
        this.parentid = null
        this.order = null
      } else {
        this.resolve(null)
      }
    }
  }
}
</script>
