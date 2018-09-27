<template>
  <v-layout row wrap>


    <v-flex xs12 sm10 offset-sm1>
      <div v-if="checklist !== null">
        <v-card >
          <v-img src="toolbar.jpg"  max-height="80px">
            <v-container fill-height fluid>
              <v-layout fill-height>
                <v-flex xs12 align-end flexbox>
                  <span class="white--text headline">{{checklist.name}}</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-img>

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
          <v-card-actions>

          </v-card-actions>
        </v-card>

        <br />

        <v-card>
          <v-card-title>
            Management
          </v-card-title>
          <v-card-text>
            <v-flex xs12 md6>
              <v-text-field
                label="Name, only saved after pressing ENTER"
                placeholder="Name"
                v-model="checklist.name"
                @keyup.enter="$emit('changeMetadata', {name: checklist.name})">
              </v-text-field>
            </v-flex>
            <v-flex xs12 md6>
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
            <v-switch
              v-model="checklist.hide_done_items"
              label="Hide done items"
              @change="$emit('changeMetadata', {hide_done_items: checklist.hide_done_items})">>
            </v-switch>
            <v-switch
              v-model="checklist.hide_done_date"
              label="Hide completed on"
              @change="$emit('changeMetadata', {hide_done_date: checklist.hide_done_date})">
            </v-switch>
          </v-card-text>
          <v-card-actions>
            <v-tooltip top>
              <v-btn flat slot="activator" @click="$emit('duplicateChecklist')"><v-icon>file_copy</v-icon> Duplicate</v-btn>
              <span>Duplicate the current checklist in the same group.</span>
            </v-tooltip>
            <v-tooltip top>
              <v-btn flat slot="activator" color="warning" @click="$emit('clearChecklist')"><v-icon>clear_all</v-icon> Clear</v-btn>
              <span>Clear done items from the checklist</span>
            </v-tooltip>
            <v-tooltip top>
              <v-btn flat slot="activator" color="error" @click="$emit('deleteChecklist')"><v-icon>delete</v-icon> Delete</v-btn>
              <span>Delete the checklist</span>
            </v-tooltip>
          </v-card-actions>
        </v-card>


      </div>
      <div v-else>
        <v-card>
          <v-img src="toolbar.jpg" max-height="80px">
            <v-container fill-height fluid>
              <v-layout>
                <v-flex xs12 align-end flexbox>
                  <span class="white--text headline" v-if="group !== null">No checklist selected in group "{{ group.name }}"</span>
                  <span class="white--text headline" v-else>No group or checklist selected</span>
                </v-flex>
              </v-layout>
            </v-container>
          </v-img>
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
