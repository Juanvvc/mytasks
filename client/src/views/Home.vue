<template>
  <div>
    <!--  navigation drawer: shows the group list !-->
    <v-navigation-drawer
      v-model="showDrawer"
      clipped
      fixed
      app
    >
      <v-list dense>
        <v-list-group
          v-for="group in groups"
          v-model="group.active"
          :key="group.id"
          @click="loadGroup(group.id)"
          prepend-icon="view_agenda">
          <!-- group name -->
          <v-list-tile slot="activator">
            <v-list-tile-content>
              <v-list-tile-title>{{group.name}}</v-list-tile-title>
            </v-list-tile-content>
            <!-- add checklists or delete the group. if it is the active group -->
            <v-list-tile-action v-if="isGroupActive(group.id)">
              <v-flex xs12>
                <v-tooltip bottom>
                  <v-btn
                    flat icon color="primary"
                    slot="activator"
                    @click.stop="newChecklist(group.id, 'New checklist')">
                    <v-icon>add</v-icon>
                  </v-btn>
                  <span>Add a new checklist to the group</span>
                </v-tooltip>
                <!-- you can only delete the group if not empty -->
                <v-tooltip bottom>
                  <v-btn
                    flat icon color="error"
                    slot="activator"
                    :disabled="group.checklists !== undefined && group.checklists.length != 0"
                    @click.stop="deleteGroup(group.id)">
                    <v-icon>delete</v-icon>
                  </v-btn>
                  <span>If empty, delete the group</span>
                </v-tooltip>
              </v-flex>
            </v-list-tile-action>
          </v-list-tile>
          <!-- List of checklist in group -->
          <v-list-tile
            v-if="isGroupActive(group.id)"
            v-for="checklist in group.checklists"
            :key="checklist.id"
          >
            <v-list-tile-content>
              <v-list-tile-title
                @click="loadChecklist(group.id, checklist.id)"
                class="pointable">
                {{checklist.name}}
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list-group>

        <!-- Add a new group-->
        <v-text-field
          label="Solo"
          placeholder="New group"
          v-model="newGroupName"
          @keyup.enter="newGroup(newGroupName)"
          @blur="newGroupName = ''"
          @keyup.escape="newGroupName = ''"
          solo
        ></v-text-field>

      </v-list>
      <v-input />
    </v-navigation-drawer>

    <!--  Title and toolbar !-->
    <v-toolbar app fixed clipped-left color="primary darken-2" dark>
        <v-toolbar-side-icon @click.stop="showDrawer = !showDrawer"></v-toolbar-side-icon>
        <v-toolbar-title>MyTasks</v-toolbar-title>

        <v-spacer></v-spacer>

        <v-tooltip bottom>
          <v-btn icon slot="activator" @click="logout">
            <v-icon>exit_to_app</v-icon>
          </v-btn>
          <span>Logout</span>
        </v-tooltip>
    </v-toolbar>

    <!-- Main content -->
    <v-content>
      <check-list
        :checklist="activeChecklist"
        :group="activeGroup"
        :available-groups="groups"
        @newItem="newItem"
        @checkItem="checkItem"
        @clearChecklist="clearChecklist"
        @deleteChecklist="deleteChecklist"
        @changeMetadata="changeMetadata"
        @changeChecklistGroup="changeChecklistGroup"
        @duplicateChecklist="duplicateChecklist"
        />
    </v-content>

    <confirm-dialog ref="confirmDialog" />
  </div>
</template>

<script>
// @ is an alias to /src
import CheckList from '@/components/CheckList.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import MyTasksClient from '@/libs/mytasksclient.js'

var MYTASKS_SERVER = 'http://127.0.0.1:5000' ///mytasks/api/v1.0'

export default {
  name: 'home',
  components: {
    CheckList,
    ConfirmDialog
  },
  data: () => ({
    showDrawer: true,
    newGroupName: '',
    activeChecklist: null,
    activeGroup: null,
    activeUser: null,
    groups: []
  }),

  mounted () {
    // get the login information. If not logged, show the login dialog
    var username = sessionStorage.getItem('username')
    var password = sessionStorage.getItem('password')

    if(username === undefined || username === null) {
      this.$router.push({ path: 'login' })
    }

    this.mytasks = new MyTasksClient(MYTASKS_SERVER,  {username, password})
    this.loadUser(0)
  },

  methods: {
    isGroupActive(groupId) {
      return this.activeGroup !== null && this.activeGroup.id === groupId
    },

    getGroupById(groupId) {
      if(this.groups === null) {
        return null
      }
      for(let i=0; i<this.groups.length; i++) {
        if(this.groups[i].id === groupId) {
          return this.groups[i]
        }
      }
      return null
    },

    loadUser(userId) {
      this.mytasks.get(`${userId}`).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.activeUser = response.data
          this.groups = response.data.groups
        }
      }).catch(() => {
        this.$emit('showError', 'Cannot connect to the server')
      })
    },

    loadGroup(groupId, checklistId) {
      /* get data about a group from the server, and set it as active.

      If a checklistIf is passed, load also the chccklist */
      this.mytasks.get(`${this.activeUser.id}/groups/${groupId}`).then( response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          for(var i=0; i<this.groups.length; i++) {
            if(this.groups[i].id === groupId) {
              this.$set(this.groups, i, response.data)
              this.groups[i].active = true
              this.activeGroup = this.groups[i]
              if(checklistId === undefined) {
                this.activeChecklist = null
              } else {
                this.loadChecklist(groupId, checklistId)
              }
            } else {
              this.groups[i].active = false
            }
          }
        }
      })
    },

    newGroup(name) {
      this.mytasks.post(`${this.activeUser.id}/groups/`, {
        name: name,
        description: '',
        checklists: []
      }).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.groups.push(response.data)
        }
      }).catch( () => {
        this.$emit('showError', 'Error connecting to server')
      })
      this.newGroupName = ''
    },

    deleteGroup(groupId) {
      if(this.activeGroup !== null && this.activeGroup.id === groupId) {
        this.activeGroup = null
        this.activeChecklist = null
      }
      let group = this.getGroupById(groupId)
      this.$refs.confirmDialog.confirm({message: 'Are you sure you want to delete group "' + group.name + '"?'}).then( confirm => {
        if(!confirm) {
          return
        }
        this.mytasks.delete(group.uri).then(response => {
          if(response.data.error_message !== undefined) {
            this.$emit('showError', response.data.error_message)
          } else {
            this.loadUser(this.activeUser.id)
          }
        })
      })
    },

    loadChecklist (groupId, checklistId) {
      /* Set a group and a checklist as active. */
      this.mytasks.get(`${this.activeUser.id}/groups/${groupId}/checklists/${checklistId}`).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.activeGroup = this.getGroupById(groupId)
          this.activeChecklist = response.data
        }
      })
    },

    newChecklist(groupId, name) {
      /* Create a new checklist in the groupId.

      If everyting was OK, active the group and the checklist */
      var group = this.getGroupById(groupId)
      if(group === null) {
        this.$emit('showError', 'Cannot find group ' + groupId)
        return
      }
      this.mytasks.post(`${group.uri}/checklists/`, {
        name: (name === undefined ? 'EMPTY NAME' : name),
        description: '',
        items: []
      }).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          var group = this.getGroupById(groupId)
          if(group.checklists === undefined) {
            group.checklists = []
          }
          group.checklists.push(response.data)
          this.activeGroup = group
          this.activeChecklist = response.data
        }
      }).catch( () => {
        this.$emit('showError', 'Network error')
      })
    },

    updateChecklist(userId, groupId, checklistId, newData) {
      this.mytasks.post(`${this.activeUser.id}/groups/${groupId}/checklists/${checklistId}`, newData).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.activeChecklist = response.data
        }
      }).catch( () => {
        this.$emit('showError', 'Network error')
      })
    },

    newItem(name) {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to add an item')
      }
      var newChecklistData = {
        items: (this.activeChecklist.items===undefined?[]:this.activeChecklist.items),
      }
      newChecklistData.items.push({name: name, checked: false})
      this.updateChecklist(this.activeUser.id, this.activeGroup.id, this.activeChecklist.id, newChecklistData)
    },

    checkItem(index) {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to check item')
      }
      var newChecklistData = {
        items: this.activeChecklist.items
      }
      newChecklistData.items[index].checked = !newChecklistData.items[index].checked
      this.updateChecklist(this.activeUser.id, this.activeGroup.id, this.activeChecklist.id, newChecklistData)
    },

    clearChecklist() {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to clear')
      }
      this.$refs.confirmDialog.confirm({message: 'Are you sure you want to clear list "' + this.activeChecklist.name + '"?'}).then( confirm => {
        if(!confirm) {
          return
        }
        var newItems = []
        for(var i=0; i<this.activeChecklist.items.length; i++) {
          if(!this.activeChecklist.items[i].checked) {
            newItems.push(this.activeChecklist.items[i])
          }
        }
        var newChecklistData = {
          items: newItems
        }
        this.updateChecklist(this.activeUser.id, this.activeGroup.id, this.activeChecklist.id, newChecklistData)
      })
    },

    changeMetadata(metadata) {
      this.updateChecklist(this.activeUser.id, this.activeGroup.id, this.activeChecklist.id, metadata)
    },

    deleteChecklist() {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to delete')
      }
      this.$refs.confirmDialog.confirm({message: 'Are you sure you want to delete checklist "' + this.activeChecklist.name + '"?'}).then( confirm => {
        if(!confirm) {
          return
        }
        this.mytasks.delete(this.activeChecklist.uri).then(response => {
          if(response.data.error_message !== undefined) {
            this.$emit('showError', response.data.error_message)
          } else {
            this.loadGroup(this.activeGroup.id)
          }
        })
      })
    },

    changeChecklistGroup(fromGroupId, toGroupId) {
      /* Change activeChecklist fromGroupId toGroupId. Activate the new group and checklist */
      if(fromGroupId === toGroupId || this.activeChecklist === null) {
        return
      }
      var toGroup = this.getGroupById(toGroupId)
      if(toGroup === null) {
        this.$emit('showError', 'Cannot find group ' + toGroupId)
        return
      }
      var newData = {
        name: this.activeChecklist.name,
        description: this.activeChecklist.description,
        items: this.activeChecklist.items
      }
      // create a new checklist in toGroup with this data
      this.mytasks.post(`${toGroup.uri}/checklists/`, newData).then( response => {
        if(response.data.errorMessage !== undefined) {
          this.$emit('showError', response.data.errorMessage)
        } else {
          // remove the old checklist
          this.mytasks.delete(this.activeChecklist.uri).then(response => {
            if(response.data.status !== 200) {
              this.$emit('Cannot delete old checklist: ' + response.data.showError)
            }
          })
          // load the group and checklist
          this.loadGroup(toGroupId, response.data.id)
        }
      }).catch( () => {
        this.$emit('showError', 'Network error')
      })
    },

    duplicateChecklist() {
      /* Duplicates the current checklist in the current group.

      The new checklist is actived */
      if(this.activeGroup === null || this.activeChecklist === null) {
        return
      }
      var newData = {
        name: this.activeChecklist.name,
        description: this.activeChecklist.description,
        items: this.activeChecklist.items
      }
      this.mytasks.post(`${this.activeGroup.uri}/checklists/`, newData).then( response => {
        if(response.data.errorMessage !== undefined) {
          this.$emit('showError', response.data.errorMessage)
        } else {
          // load the group and the new checklist
          this.loadGroup(this.activeGroup.id, response.data.id)
        }
      }).catch( () => {
        this.$emit('showError', 'Network error')
      })
    },

    logout() {
      sessionStorage.clear()
      this.$router.push({name: 'login'})
    }
  }
}
</script>
