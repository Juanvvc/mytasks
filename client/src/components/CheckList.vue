<template>
  <v-layout row wrap>


    <v-flex xs12 sm10 offset-sm1>
      <div v-if="checklist !== undefined && checklist !== null">
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
              <v-text-field v-if="editingName" label="Name" v-model="newName" @keyup.enter="saveName()"></v-text-field>
              <span v-else  class="white--text headline"  @dblclick="editName()">{{checklist.name}}</span>
            </v-toolbar-title>
            <v-spacer />
            <!-- Select group -->
            <v-flex sm3>
              <v-select
               placeholder="GROUP"
               v-model="checklist._parentid"
               :items="availableGroups"
               item-text="name"
               item-value="_id"
               @change="$emit('changeChecklistGroup', group._id, checklist._parentid)"
               >
              </v-select>
            </v-flex>
            <!-- toggles -->
            <v-tooltip bottom>
              <v-btn slot="activator" :dark="!checklist.hide_done_items" icon @click="$emit('changeMetadata', {hide_done_items: !checklist.hide_done_items})">
                <v-icon>done_outline</v-icon>
              </v-btn>
              <span>Show/hide done items</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn slot="activator" :dark="!checklist.hide_done_date" icon @click="$emit('changeMetadata', {hide_done_date: !checklist.hide_done_date})">
                <v-icon>today</v-icon>
              </v-btn>
              <span>Show/hide done dates in items</span>
            </v-tooltip>

            <v-menu bottom left>
              <v-btn
                slot="activator"
                dark
                icon
              >
                <v-icon>more_vert</v-icon>
              </v-btn>

              <v-list>
                <v-list-tile class="pointable"><v-list-tile-title @click="$emit('duplicateChecklist', checklist)">Duplicate checklist</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="clearChecklist">Remove done items</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="$emit('deleteChecklist', checklist)">Delete checklist</v-list-tile-title></v-list-tile>
              </v-list>
            </v-menu>
          </v-toolbar>

          <v-divider />

          <v-card-text>
            <v-textarea v-if="editingDescription" label="Description" v-model="newDescription" @keyup.enter="saveDescription()"></v-textarea>
            <p v-else-if="checklist.description" @dblclick="editDescription()"><b>Description:</b> {{checklist.description}}</p>
            <p v-else @dblclick="editDescription()"><b>No description</b></p>

            <v-list>
              <vue-draggable v-model="checklist.items" @start="drag=true" @end="finishItemDrag()" :options="{handle:'.handle'}">
                <!-- normal items -->
                <v-list-tile
                  v-if="!item.checked || !checklist.hide_done_items"
                  v-for="(item, index) in checklist.items"
                  :key="item.name"
                  avatar
                  class="pointable">
                  <v-list-tile-avatar @click="checkItem(item)" v-if="!isSection(item)">
                    <v-icon v-if="item.checked">check_box</v-icon>
                    <v-icon v-else>check_box_outline_blank</v-icon>
                  </v-list-tile-avatar>
                  <v-list-tile-content class="handle" v-if="!isSection(item)">
                    <v-list-tile-title>
                      <span v-if="item.checked" class="checked" @dblclick="editItem(item)">{{ item.name }}</span>
                      <span v-else class="unchecked" @dblclick="editItem(item)">{{ item.name }}</span>
                    </v-list-tile-title>
                    <v-list-tile-sub-title>
                      <span v-if="item.done_date && !checklist.hide_done_date">Completed on: {{item.done_date}}. </span>
                      <span v-if="item.due_date">Due date: {{item.due_date}}. </span>
                      <span v-if="item.comment">{{item.comment}}</span>
                    </v-list-tile-sub-title>
                  </v-list-tile-content>
                  <!-- items that are actually a section -->
                  <v-list-tile-content class="handle" v-else>
                    <span color="secondary" class="header orange--text ligthen-1" @dblclick="editItem(item)">{{ item.name }}</span>
                  </v-list-tile-content>
                </v-list-tile>
              </vue-draggable>
            </v-list>
            <!-- Final row: Add a new item -->
            <v-text-field
                v-model="newItemName"
                placeholder="New item"
                @keyup.enter="newItem(newItemName); newItemName=''"
                @keyup.escape="newItemName = ''"
                @blur="newItemName = ''"
                solo />
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

    <item-dialog ref="itemDialog"/>
    <confirm-dialog ref="confirmDialog" />

  </v-layout>
</template>

<script>

import ItemDialog from '@/components/ItemDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import VueDraggable from 'vuedraggable'
import mytasks from '@/libs/mytasksclient'

export default {
  components: {
    ItemDialog,
    VueDraggable,
    ConfirmDialog
  },

  props: {
    checklistId: {
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
    checklist: null,
    newItemName: '',
    editingName: false,
    newName: '',
    editingDescription: false,
    newDescription: '',
    drag: false
  }),

  watch: {
    checklistId: function() {
      // when checklist_id changes, load a new checklist
      this.loadChecklist()
    }
  },

  methods: {
    loadChecklist () {
      if(this.checklistId === undefined || this.checlistId === null) {
        this.checklist = null
        return
      }
      /* Loads the information of a checklist in checklistId */
      mytasks.get(`/checklists/${this.checklistId}`).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.checklist = response.data
        }
      })
    },

    updateChecklist(newData) {
      // updates the information of the checklist with new data
      mytasks.post(`/checklists/${this.checklistId}`, newData).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.activeChecklist = response.data
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    newItem(name) {
      let newItemInfo = {
        name: name,
        _parentid: this.checklistId
      }
      mytasks.post('/items/', newItemInfo).then( response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          if(this.checklist.items === null || this.checklist.items === undefined) {
            this.checklist.items = [response.data]
          } else {
            this.checklist.items.push(response.data)
          }
        }
      })
      this.newItemName = ''
    },

    updateItem(item, newItemData) {
      mytasks.put(item.uri, newItemData).then(response => {
        if(response.data.error_message !== undefined ) {
          this.$emit('showError', response.data.message)
        } else {
          this.$set(item, 'checked', response.data.checked)
          this.$set(item, 'name', response.data.name)
          this.$set(item, 'comment', response.data.comment)
          this.$set(item, 'done_date', response.data.done_date)
          this.$set(item, 'due_date', response.data.due_date)
        }
      })
    },

    checkItem(item) {
      let today = (new Date()).toISOString().slice(0,10)
      let newItemData = {
        checked: !item.checked,
        done_date: (item.checked?'':today)
      }
      this.updateItem(item, newItemData)
    },

    deleteItem(item) {
      mytasks.delete(item.uri).then(response => {
        if(response.data.error_message !== undefined ) {
          this.$emit('showError', response.data.message)
        } else {
          // TODO: pop the item from the checklist
        }
      })
    },

    clearChecklist() {
      if(this.checklist === null) {
        this.$emit('showError', 'No active checklist to clear')
      }
      this.$refs.confirmDialog.confirm({title: `Clear list "${this.checklist.name}"?`, message: "Clearing a list removes all items done", yes: 'Clear'}).then( confirm => {
        if(!confirm) {
          return
        }
        for(var i=0; i<this.checklist.items.length; i++) {
          if(this.checklist.items[i].checked) {
            this.deleteItem(this.checklist.items[i])
          }
        }
      })
    },

    editItem (item) {
      this.$refs.itemDialog.show({
        name: item.name,
        comment: item.comment,
        due_date: item.due_date,
      }).then(result => {
        if(result !== null) {
          if(result.name === null || result.name === '') {
            // if the name is empty, delete the item
            this.deleteItem(item)
          } else {
            // otherwise, save the item
            this.updateItem(item, result)
          }
        }
      })
    },

    editDescription () {
      // active the edit description dialog
      this.editingDescription = true
      if(this.checklist !== undefined && this.checklist.description !== undefined) {
        this.newDescription = this.checklist.description
      } else {
        this.newDescription = ''
      }
    },

    saveDescription () {
      // save the new description
      this.updateChecklist({description: this.newDescription.trim()})
      this.updateCh
      this.editingDescription = false
    },

    editName () {
      // active the edit name dialog
      this.editingName = true
      this.newName = this.checklist.name
    },

    saveName () {
      // save the new name
      if(this.newName === '') {
        this.$emit('showError', 'The name cannot be empty')
        return
      }
      this.updateChecklist({name: this.newName.trim()})
      this.editingName = false
    },

    finishItemDrag() {
      this.drag = false
      this.updateChecklist({items: this.checklist.items})
    },

    isSection(item) {
      // returns true if the item is a section
      // A section is just a normal item which names starts with #
      try {
        return item.name.startsWith('#')
      } catch (e){
        return false
      }
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
