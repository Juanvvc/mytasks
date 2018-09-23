<template>
  <v-layout row wrap>
    <v-flex xs12 sm10 offset-sm1>
      <v-card v-if="checklist !== null">
        <v-toolbar color="secondary">
            <v-flex xs12 sm6>
              <v-text-field
                label="Name, only saved after pressing ENTER"
                placeholder="Name"
                v-model="checklist.name"
                @keyup.enter="$emit('changeMetadata', {name: checklist.name})">
              </v-text-field>
            </v-flex>
          <v-spacer />
          <v-flex xs12 sm4>
            <v-select
              label="In group"
              placeholder="GROUP"
              v-model="checklist.groupid"
              :items="availableGroups"
              item-text="name"
              item-value="_id"
              @change="$emit('changeChecklistGroup', group._id, checklist.groupid)"
              >
            </v-select>
          </v-flex>
        </v-toolbar>

        <v-list>
          <v-list-tile
            v-for="(item, index) in checklist.items"
            :key="item.name"
            avatar
            class="pointable">
            <v-list-tile-avatar @click="checkItem(index)">
              <v-icon v-if="item.checked">check_box</v-icon>
              <v-icon v-else>check_box_outline_blank</v-icon>
            </v-list-tile-avatar>
            <v-list-tile-content>
              <v-list-tile-title>
                <span v-if="item.checked" class="checked" @dblclick="editItem(index)">{{ item.name }}</span>
                <span v-else class="unchecked" @dblclick="editItem(index)">{{ item.name }}</span>
              </v-list-tile-title>
              <v-list-tile-sub-title>
                <span v-if="item.due_date">Due date: {{item.due_date}}. </span>
                <span v-if="item.comment">{{item.comment}}</span>
              </v-list-tile-sub-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile avatar>
            <v-list-tile-avatar>
              <v-icon>check_box_outline_blank</v-icon>
            </v-list-tile-avatar>
            <v-list-tile-content>
              <v-list-tile-title>
                <v-text-field
                  v-model="newItemName"
                  placeholder="New item"
                  @keyup.enter="newItem"
                  @keyup.escape="newItemName = ''"
                  @blur="newItemName = ''"
                  full-width />
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>

        <v-tooltip top>
          <v-btn slot="activator" @click="$emit('duplicateChecklist')"><v-icon>file_copy</v-icon> Duplicate</v-btn>
          <span>Duplicate the current checklist in the same group.</span>
        </v-tooltip>
        <v-tooltip top>
          <v-btn slot="activator" color="warning" @click="$emit('clearChecklist')"><v-icon>clear_all</v-icon> Clear</v-btn>
          <span>Clear done items from the checklist</span>
        </v-tooltip>
        <v-tooltip top>
          <v-btn slot="activator" color="error" @click="$emit('deleteChecklist')"><v-icon>delete</v-icon> Delete</v-btn>
          <span>Delete the checklist</span>
        </v-tooltip>

      </v-card>

      <div v-else>
        <v-card>
          <v-toolbar color="secondary">
            <v-toolbar-title v-if="group !== null">No checklist selected in group "{{ group.name }}"</v-toolbar-title>
            <v-toolbar-title v-else>No group or checklist selected</v-toolbar-title>
          </v-toolbar>


          <v-btn
            color="primary"
            @click.stop="$emit('newChecklist')">
            <v-icon>add</v-icon> Add new checklist
          </v-btn>

        </v-card>
      </div>
    </v-flex>

    <item-dialog ref="editDialog"/>
  </v-layout>
</template>

<script>

import ItemDialog from '@/components/ItemDialog.vue'

export default {
  components: {
    ItemDialog
  },

  props: {
    checklist: {
      type: Object,
      mandatory: true
    },
    group: {
      type: Object,
      mandatory: true
    },
    availableGroups: {
      type: Array,
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
    },

    editItem (itemIndex) {
      let item = this.checklist.items[itemIndex]
      this.$refs.editDialog.show({
        name: item.name,
        comment: item.comment,
        due_date: item.due_date,
      }).then(result => {
        if(result !== null) {
          this.$emit('editItem', itemIndex, result)
        }
      })
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
