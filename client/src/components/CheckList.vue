<template>
  <v-layout row wrap>


    <v-flex xs12 sm10 offset-sm1>
      <div v-if="checklist !== undefined && checklist !== null">
        <v-card >
          <v-toolbar card prominent color="secondary" class="checklist-header">
            <!-- name -->
            <v-toolbar-title class="body-2">
              <v-text-field v-if="editingName" label="Name" v-model="newName" @keyup.enter="saveName()"></v-text-field>
              <span v-else  class="white--text headline"  @dblclick="editName()">{{checklist.name}}</span>
            </v-toolbar-title>
            <v-spacer />
            <!-- Select group, only if the checklist is editable -->
            <v-flex xs2 sm3>
              <v-select
               placeholder="GROUP"
               v-if="isEditable()"
               v-model="checklist._parentid"
               :items="availableGroups"
               item-text="name"
               item-value="_id"
               @change="moveChecklist(checklist._parentid)"
               />
            </v-flex>
            <!-- toggles -->
            <v-tooltip bottom v-if="isEditable()">
              <v-btn slot="activator" :dark="!checklist.hide_done_items" icon @click="updateChecklist({hide_done_items: !checklist.hide_done_items})">
                <v-icon>done_outline</v-icon>
              </v-btn>
              <span>Show/hide done items</span>
            </v-tooltip>
            <v-tooltip bottom>
              <v-btn slot="activator" :dark="showCalendar" icon @click="switchShowCalendar()">
                <v-icon>today</v-icon>
              </v-btn>
              <span>Show/hide calendar view</span>
            </v-tooltip>

            <v-menu bottom left v-if="isEditable()">
              <v-btn
                slot="activator"
                dark
                icon
              >
                <v-icon>more_vert</v-icon>
              </v-btn>

              <v-list>
                <v-list-tile class="pointable"><v-list-tile-title @click="duplicateChecklist">Duplicate checklist</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="clearChecklist">Remove done items</v-list-tile-title></v-list-tile>
                <v-list-tile class="pointable"><v-list-tile-title @click="deleteChecklist">Delete checklist</v-list-tile-title></v-list-tile>
              </v-list>
            </v-menu>
          </v-toolbar>

          <v-divider />

          <v-card-text v-if="showCalendar">
            <!-- calendar view -->
            <p>The calendar only shows undone items</p>
            <calendar-view
              :starting-day-of-week="1"
              class="theme-default"
              :events="calendarEvents"
              style="height: 600px"
              >
            </calendar-view>
          </v-card-text>
          <v-card-text v-else>
            <v-textarea v-if="editingDescription" label="Description" v-model="newDescription" @keyup.enter="saveDescription()"></v-textarea>
            <p v-else-if="checklist.description" @dblclick="editDescription()"><b>Description:</b> {{checklist.description}}</p>
            <p v-else @dblclick="editDescription()"><b>No description</b></p>

            <v-list class="nopadding">
              <vue-draggable v-model="checklist.items" @start="drag=true" @end="finishItemDrag()" :options="{handle:'.handle', disabled: !isEditable()}">
                <!-- normal items -->
                <v-list-tile
                  v-if="!item.checked || !checklist.hide_done_items"
                  v-for="item in checklist.items"
                  :key="item.id?item.id:item.name"
                  avatar>
                  <v-list-tile-avatar @click="checkItem(item)" v-if="!isSection(item)">
                    <!-- checkbox -->
                    <v-btn icon>
                      <v-icon v-if="item.checked" class="pointable">check_box</v-icon>
                      <v-icon v-else class="pointable">check_box_outline_blank</v-icon>
                    </v-btn>
                  </v-list-tile-avatar>
                  <v-list-tile-content v-if="!isSection(item)" @dblclick="editItem(item)">
                    <v-list-tile-title>
                      <v-hover>
                        <v-layout row slot-scope="{ hover }">
                          <span sm1 v-if="hover">
                            <v-tooltip bottom v-if="isEditable()" >
                              <v-icon slot="activator" class="handle movable">drag_indicator</v-icon>
                              <span>Move item</span>
                            </v-tooltip>
                            <span v-if="isEditable()">&nbsp;</span>
                          </span>
                          <span v-if="item.checked" class="checked">{{ item.name }}</span>
                          <span v-else class="unchecked">{{ item.name }}</span>
                        </v-layout>
                      </v-hover>
                    </v-list-tile-title>
                    <v-list-tile-sub-title>
                      <!-- due and complete dates and comments -->
                      <span v-if="item.done_date">Completed on: {{item.done_date}}. </span>
                      <span v-if="item.due_date && !item.checked">
                          <span class="red--text" v-if="item.due_date < (new Date().toISOString().slice(0,10))">OVERDUE: {{item.due_date}}.</span>
                          <span v-else>Due date: {{item.due_date}}.</span>
                          &nbsp;
                      </span>
                      <span v-if="item.comment">{{item.comment}}</span>
                    </v-list-tile-sub-title>
                  </v-list-tile-content>
                  <!-- items that are actually a section -->
                  <v-list-tile-content class="handle" @dblclick="editItem(item)" v-else>
                    <v-list-tile-title>
                      <v-hover>
                        <v-layout row slot-scope="{ hover }">
                          <span sm1 v-if="hover"> <!-- sections in special checklists cannot be edited -->
                            <v-tooltip bottom v-if="isEditable()" >
                              <v-icon color="secondary" slot="activator" class="handle movable">drag_indicator</v-icon>
                              <span>Move item</span>
                            </v-tooltip>
                            <v-tooltip bottom v-if="isItemEditable(item)">
                              <v-icon color="secondary" slot="activator" class="pointable" @click="promoteSection(item)">assignment</v-icon>
                              <span>Promote section to checklist</span>
                            </v-tooltip>
                            <span v-if="isEditable()">&nbsp;</span>
                          </span>
                          <span
                            color="secondary"
                            class="header orange--text ligthen-1">
                            {{ item.name }}
                          </span>
                        </v-layout>
                      </v-hover>
                    </v-list-tile-title>
                  </v-list-tile-content>
                </v-list-tile>
              </vue-draggable>
            </v-list>
            <!-- Final row: Add a new item -->
            <v-text-field
              v-if="isEditable()"
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
              <span class="white--text headline">No checklist selected</span>
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
import { CalendarView, CalendarViewHeader } from "vue-simple-calendar"
require("vue-simple-calendar/static/css/default.css")
import mytasks from '@/libs/mytasksclient'

export default {
  components: {
    ItemDialog,
    VueDraggable,
    ConfirmDialog,
    CalendarView,
    CalendarViewHeader
  },

  props: {
    checklistId: {
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
    drag: false,
    showCalendar: false,
    calendarEvents: []
  }),

  watch: {
    checklistId: function() {
      // when checklist_id changes, load a new checklist
      this.loadChecklist()
    }
  },

  methods: {
    loadChecklist () {
      if(!this.checklistId) {
        this.checklist = null
        return
      }
      /* Loads the information of a checklist in checklistId */
      mytasks.get(`/checklists/${this.checklistId}`).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.showCalendar = false
          this.checklist = response.data
        }
      })
    },

    duplicateChecklist() {
      if(!this.isEditable()) return
      /* Duplicates current checklist. */
      if(this.checklist === null) {
        this.$emit('showError', 'No active checklist')
        return
      }
      mytasks.post(`/checklists/${this.checklist._id}/duplicate`).then( response => {
        this.$emit('checklistDuplicated', response.data)
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    deleteChecklist() {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      this.$refs.confirmDialog.confirm({title: `Delete checklist "${this.checklist.name}"?`, yes: 'Delete', message: 'This action cannot be undone'}).then( confirm => {
        if(!confirm) {
          return
        }
        mytasks.delete(this.checklist.uri).then(() => {
          this.$emit('checklistDeleted')
        }).catch( error => {
          this.$emit('showError', error)
        })
      })
    },

    updateChecklist(newData) {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      // updates the information of the checklist with new data
      return mytasks.post(`/checklists/${this.checklistId}`, newData).then(response => {
        this.checklist = response.data
        return response
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    newItem(name) {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      let newItemInfo = {
        name: name,
        _parentid: this.checklistId
      }
      mytasks.post('/items/', newItemInfo).then( response => {
        if(this.checklist.items === null || this.checklist.items === undefined) {
          this.checklist.items = [response.data]
        } else {
          this.checklist.items.push(response.data)
        }
      })
      this.newItemName = ''
    },

    updateItem(item, newItemData) {
      if(!this.isItemEditable(item)) {
        this.$emit('showWarning', 'This item cannot be edited')
        return
      }
      mytasks.post(item.uri, newItemData).then(response => {
        this.$set(item, 'checked', response.data.checked)
        this.$set(item, 'name', response.data.name)
        this.$set(item, 'comment', response.data.comment)
        this.$set(item, 'done_date', response.data.done_date)
        this.$set(item, 'due_date', response.data.due_date)
      })
    },

    checkItem(item) {
      if(!this.isItemEditable(item)) {
        this.$emit('showWarning', 'This item cannot be edited')
        return
      }
      let today = (new Date()).toISOString().slice(0,10)
      let newItemData = {
        checked: !item.checked,
        done_date: (item.checked?'':today)
      }
      this.updateItem(item, newItemData)
    },

    deleteItem(item) {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }
      if(!this.isItemEditable(item)) {
        this.$emit('showWarning', 'This item cannot be edited')
        return
      }

      if(item.uri === undefined) {
        this.$emit('showError', 'The item is incomplete. Duplicate the checklist and try again!')
        return
      }
      mytasks.delete(item.uri).then(response => {
        if(response.data.status === 200) {
          let oldItemPos = -1
          for(let i=0; i<=this.checklist.items.length; i++) {
            if(this.checklist.items[i]._id === item._id) {
              oldItemPos = i
              break
            }
          }
          if(oldItemPos !== -1) {
            this.$delete(this.checklist.items, oldItemPos)
          }
        }
      })
    },

    editItem (item) {
      if(!this.isItemEditable(item)) {
        this.$emit('showWarning', 'This item cannot be edited')
        return
      }
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

    clearChecklist() {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      if(this.checklist === null) {
        this.$emit('showError', 'No active checklist to clear')
        return
      }
      this.$refs.confirmDialog.confirm({title: `Remove done items from "${this.checklist.name}"?`, message: "This action cannot be undone", yes: 'Remove'}).then( confirm => {
        if(!confirm) {
          return
        }
        mytasks.post(`/checklists/${this.checklist._id}/clear`).then( response => {
          this.checklist = response.data
        })
      })
    },

    moveChecklist(toGroupId) {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      this.updateChecklist({_parentid: toGroupId}).then( () => {
        this.$emit('checklistMoved', this.checklist, toGroupId)
      })
    },

    editDescription () {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      // active the edit description dialog
      this.editingDescription = true
      if(this.checklist !== undefined && this.checklist.description !== undefined) {
        this.newDescription = this.checklist.description
      } else {
        this.newDescription = ''
      }
    },

    saveDescription () {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      // save the new description
      this.updateChecklist({description: this.newDescription.trim()})
      this.updateCh
      this.editingDescription = false
    },

    editName () {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      // active the edit name dialog
      this.editingName = true
      this.newName = this.checklist.name
    },

    saveName () {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      // save the new name
      if(this.newName === '') {
        this.$emit('showError', 'The name cannot be empty')
        return
      }
      this.updateChecklist({name: this.newName.trim()})
      this.editingName = false
    },

    finishItemDrag() {
      if(!this.isEditable()){
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

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
    },

    promoteSection(item) {
      // promotes a section to a checklist
      if(!this.isEditable()) {
        this.$emit('showWarning', 'This checklist cannot be edited')
        return
      }

      this.$refs.confirmDialog.confirm({title: `Promote section "${item.name}"?`, yes: 'Promote', message: 'This action cannot be undone'}).then( confirm => {
        if(!confirm) {
          return
        }
        // get where the section starts and its length
        let indexOfItem = -1
        let numberOfItems = 1
        for(let i=0; i<this.checklist.items.length; i++){
          if(indexOfItem == -1) {
            if(this.checklist.items[i]._id === item._id) {
              indexOfItem = i
            }
          } else {
            if(this.isSection(this.checklist.items[i])) {
              break
            }
            numberOfItems++
          }
        }
        if(indexOfItem === -1) {
          this.$emit('showError', 'Section not found')
          return
        }

        // create the new checklist with the old items
        var new_items = []
        for(let i=indexOfItem + 1; i<indexOfItem + numberOfItems; i++) {
          new_items.push({_id: this.checklist.items[i]._id})
        }
        mytasks.post('/checklists/', {
          name: this.checklist.name + ' ' + this.checklist.items[indexOfItem].name,
          items: new_items,
          _parentid: this.checklist._parentid
        }).then( response => {
          if(!response) return
          // delete the items from the current checklist
          this.checklist.items.splice(indexOfItem, numberOfItems)
          mytasks.post(this.checklist.uri, {items: this.checklist.items})  // notice we ignore errors here
          // ask to load the new checklist
          this.$emit('checklistDuplicated', response.data)
        })
      })
    },

    isEditable() {
      // return true if the current checklist is editable
      return this.checklist && this.checklist.uri
    },

    isItemEditable(item) {
      return item && item.uri
    },

    switchShowCalendar() {
      this.showCalendar = !this.showCalendar
      if(this.showCalendar && this.checklist) {
        // update calendarEvents
        this.calendarEvents = []
        let now = (new Date()).toISOString().slice(0,10)
        for(let i=0; i<this.checklist.items.length; i++) {
          let item = this.checklist.items[i]
          if(!item.checked && item.due_date) {
            let overdue = (item.due_date<now)
            this.calendarEvents.push({
              title: item.name,
              startDate: (overdue?now:item.due_date),
              classes: (overdue?'calendar-overdue':'calendar-task'),
            })
          }
        }
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

.nopadding >>> .v-list__tile {
  padding: 0 !important;
}

.theme-default >>> .calendar-task {
	background-color:#f9aa33;
  border-radius:0;
}
.theme-default >>> .calendar-overdue {
	background-color:#ff0000;
  border-radius:0;
  color: white;
}
</style>
