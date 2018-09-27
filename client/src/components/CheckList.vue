<template>
  <v-layout row wrap>


    <v-flex xs12 sm10 offset-sm1>
      <div v-if="checklist !== null">
        <v-card >
          <!--v-img src="toolbar.jpg"  max-height="80px">
            <v-container fill-height fluid>
              <v-layout fill-height>
                <v-flex xs12 align-end flexbox>
                  <span class="white--text headline">{{checklist.name}}</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-img-->
          <v-toolbar card prominent color="secondary" class="checklist-header">
            <!-- name -->
            <v-toolbar-title class="body-2">
              <v-text-field v-if="editing_name" label="Name" v-model="new_name" @keyup.enter="saveName()"></v-text-field>
              <span v-else  class="white--text headline"  @dblclick="editName()">{{checklist.name}}</span>
            </v-toolbar-title>
            <v-spacer />
            <!-- Select group -->
            <v-select
             placeholder="GROUP"
             v-model="checklist.groupid"
             :items="availableGroups"
             item-text="name"
             item-value="_id"
             @change="$emit('changeChecklistGroup', group._id, checklist.groupid)"
             >
            </v-select>
            <!-- toggles -->
            <v-btn :dark="checklist.hide_done_items" flat @click="$emit('changeMetadata', {hide_done_items: !checklist.hide_done_items})">
             <v-icon>done_outline</v-icon>
            </v-btn>
            <v-btn :dark="checklist.hide_done_date" flat @click="$emit('changeMetadata', {hide_done_date: !checklist.hide_done_date})">
              <v-icon>today</v-icon>
            </v-btn>

            <v-menu bottom left>
              <v-btn
                slot="activator"
                dark
                icon
              >
                <v-icon>more_vert</v-icon>
              </v-btn>

              <v-list>
                <v-list-tile class="pointable"><v-list-tile-title @click="$emit('duplicateChecklist')">Duplicate</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="$emit('clearChecklist')">Clear</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="$emit('deleteChecklist')">Delete</v-list-tile-title></v-list-tile>
              </v-list>
            </v-menu>
          </v-toolbar>

          <v-divider />

          <v-card-text>
            <v-textarea v-if="editing_description" label="Description" v-model="new_description" @keyup.enter="saveDescription()"></v-textarea>
            <p v-else-if="checklist.description" @dblclick="editDescription()"><b>Description:</b> {{checklist.description}}</p>
            <p v-else @dblclick="editDescription()"><b>No description</b></p>

            <v-list>
              <vue-draggable v-model="checklist.items" @start="drag=true" @end="finishItemDrag()" :options="{handle:'.handle'}">
                <!-- existing items -->
                <v-list-tile
                  v-for="(item, index) in checklist.items"
                  :key="item.name"
                  avatar
                  v-if="!item.checked || !checklist.hide_done_items"
                  class="pointable">
                  <v-list-tile-avatar @click="checkItem(index)">
                    <v-icon v-if="item.checked">check_box</v-icon>
                    <v-icon v-else>check_box_outline_blank</v-icon>
                  </v-list-tile-avatar>
                  <v-list-tile-content class="handle">
                    <v-list-tile-title>
                      <span v-if="item.checked" class="checked" @dblclick="editItem(index)">{{ item.name }}</span>
                      <span v-else class="unchecked" @dblclick="editItem(index)">{{ item.name }}</span>
                    </v-list-tile-title>
                    <v-list-tile-sub-title>
                      <span v-if="item.done_date && !checklist.hide_done_date">Completed on: {{item.done_date}}. </span>
                      <span v-if="item.due_date">Due date: {{item.due_date}}. </span>
                      <span v-if="item.comment">{{item.comment}}</span>
                    </v-list-tile-sub-title>
                  </v-list-tile-content>
                </v-list-tile>
                <!-- Add a new item -->
                <v-list-tile
                  avatar
                  slot="footer">
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
              </vue-draggable>
            </v-list>
          </v-card-text>
        </v-card>
      </div>

      <div v-else>
        <!-- No checklist selected -->
        <v-card>
          <v-toolbar card prominent color="secondary" class="checklist-header">
            <v-toolbar-title class="body-2">
              <span class="white--text headline" v-if="group !== null">No checklist selected in group "{{ group.name }}"</span>
              <span class="white--text headline" v-else>No group or checklist selected</span>
            </v-toolbar-title>
          </v-toolbar>
        </v-card>
      </div>
    </v-flex>



    <item-dialog ref="editDialog"/>
  </v-layout>
</template>

<script>

import ItemDialog from '@/components/ItemDialog.vue'
import VueDraggable from 'vuedraggable'

export default {
  components: {
    ItemDialog,
    VueDraggable
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
    newItemName: '',
    editing_name: false,
    new_name: '',
    editing_description: false,
    new_description: '',
    drag: false
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
    },

    editDescription () {
      this.editing_description = true
      if(this.checklist !== undefined && this.checklist.description !== undefined) {
        this.new_description = this.checklist.description
      } else {
        this.new_description = ''
      }
    },

    saveDescription () {
      this.$emit('changeMetadata', {description: this.new_description.trim()})
      this.editing_description = false
    },

    editName () {
      this.editing_name = true
      this.new_name = this.checklist.name
    },

    saveName () {
      if(this.new_name === '') {
        this.$emit('showError', 'The name cannot be empty')
        return
      }
      this.$emit('changeMetadata', {name: this.new_name.trim()})
      this.editing_name = false
    },

    finishItemDrag() {
      this.drag = false
      this.$emit('changeMetadata', {items: this.checklist.items})
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
