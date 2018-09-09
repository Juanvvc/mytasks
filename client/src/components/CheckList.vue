<template>
  <div>
    <div v-if="checklist !== null">
      <h1>{{ group.name}} : {{checklist.name}}</h1>

      <p v-if="checklist.description !== undefined">
        {{ checklist.description }}
      </p>

      <v-tooltip top>
        <v-btn slot="activator"><v-icon>assignment_return</v-icon> Move to</v-btn>
        <span>Move the checklist to a different group</span>
      </v-tooltip>
      <v-tooltip top>
        <v-btn slot="activator"><v-icon>file_copy</v-icon> Copy to</v-btn>
        <span>Copy the checklist to a new group</span>
      </v-tooltip>
      <v-tooltip top>
        <v-btn slot="activator" color="warning" @click="$emit('clearChecklist')"><v-icon>clear_all</v-icon> Clear</v-btn>
        <span>Clear done items from the checklist</span>
      </v-tooltip>
      <v-tooltip top>
        <v-btn slot="activator" color="error" @click="$emit('deleteChecklist')"><v-icon>delete</v-icon> Delete</v-btn>
        <span>Delete the checklist</span>
      </v-tooltip>


      <v-list>
        <v-list-tile
          v-for="(item, index) in checklist.items"
          :key="item.name"
          class="pointable">
          <v-list-tile-action @click="checkItem(index)">
            <v-icon v-if="item.checked">check_box</v-icon>
            <v-icon v-else>check_box_outline_blank</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>
            <span v-if="item.checked" class="checked">{{ item.name }}</span>
            <span v-else class="unchecked">{{ item.name }}</span>
          </v-list-tile-title>
        </v-list-tile>
        <v-list-tile>
          <v-list-tile-action>
            <v-icon>check_box_outline_blank</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-text-field
              v-model="newItemName"
              placeholder="Text"
              @keyup.enter="newItem"
              @keyup.escape="newItemName = ''"
              @blur="newItemName = ''"
              full-width
              ></v-text-field>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>

    </div>
    <div v-else>
      <h1>No checklist selected</h1>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    checklist: {
      type: Object,
      mandatory: true
    },
    group: {
      type: Object,
      mandatory: true
    }
  },
  data: () => ({
    newItemName: ''
  }),
  methods: {
    newItem () {
      this.$emit('newItem', this.newItemName)
      this.newItemName = ''
    },

    checkItem (itemIndex) {
      this.$emit('checkItem', itemIndex)
    }
  }
}
</script>

<style scoped>
.checked {
  color: #aaa;
  text-decoration: line-through;
}
</style>
