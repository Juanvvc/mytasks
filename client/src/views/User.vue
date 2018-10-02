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
          v-model="group._active"
          :key="group._id"
          @click="loadGroup(group._id)"
          prepend-icon="view_agenda">
          <!-- group name -->
          <v-list-tile slot="activator">
            <v-list-tile-content>
              <v-list-tile-title>{{group.name}}</v-list-tile-title>
            </v-list-tile-content>
            <!-- add checklists or delete the group. if it is the active group -->
            <v-list-tile-action v-if="isGroupActive(group._id)">
              <v-flex xs12>
                <v-tooltip bottom>
                  <v-btn
                    flat icon color="primary"
                    slot="activator"
                    @click.stop="newChecklist(group._id, 'New checklist')">
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
                    @click.stop="deleteGroup(group._id)">
                    <v-icon>delete</v-icon>
                  </v-btn>
                  <span>If empty, delete the group</span>
                </v-tooltip>
              </v-flex>
            </v-list-tile-action>
          </v-list-tile>
          <!-- List of checklist in group -->
          <v-list-tile
            v-if="isGroupActive(group._id)"
            v-for="checklist in group.checklists"
            :key="checklist._id"
          >
            <v-list-tile-content>
              <v-list-tile-title
                @click="activeChecklistId = checklist._id"
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
          @keyup.enter="newGroup(newGroupName); newGroupName=''"
          @blur="newGroupName = ''"
          @keyup.escape="newGroupName = ''"
          solo
        ></v-text-field>

      </v-list>
    </v-navigation-drawer>

    <!--  Title and toolbar !-->
    <v-toolbar app fixed clipped-left color="primary darken-4" dark>
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
        :checklist-id="activeChecklistId"
        :group="activeGroup"
        :available-groups="groups"
        @deleteChecklist="deleteChecklist"
        @changeChecklistGroup="changeChecklistGroup"
        @duplicateChecklist="duplicateChecklist"
        @showError="$emit('showError', $event)"
        />
    </v-content>

    <confirm-dialog ref="confirmDialog" />
  </div>
</template>

<script>
// @ is an alias to /src
import CheckList from '@/components/CheckList.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import mytasks from '@/libs/mytasksclient.js'

export default {
  components: {
    CheckList,
    ConfirmDialog
  },
  data: () => ({
    showDrawer: true,
    newGroupName: '',
    activeChecklistId: null,
    activeGroup: null,
    activeUser: null,
    groups: []
  }),

  mounted () {
    // get the login information. If not logged, show the login dialog
    var token = sessionStorage.getItem('token')
    var useruri = sessionStorage.getItem('useruri')

    // if these parameters are not in session storage, try in local storage
    if(token === undefined || token === null) {
      token = localStorage.getItem('token')
      useruri = localStorage.getItem('useruri')
    }

    // if they are still undefined, call login
    if(token === undefined || token === null) {
      this.$router.push({ path: 'login' })
    }

    if(token !== null && useruri !== null) {
      // create the authentication object and the callback in case of error
      mytasks.setAuth({username: token, password: ''}, () => {
        // callback in case of auth error: just call login
        this.$emit('showError', 'Authentication error. Session expired?')
        this.$router.push({ name: 'login' })
      })

      this.loadUser(useruri)
    }
  },

  methods: {
    isGroupActive(groupId) {
      // Returns True if the group identified wits its identifier is the currently actived group
      return this.activeGroup !== null && this.activeGroup._id === groupId
    },

    getGroupById(groupId) {
      // Returns a group from its group identifier
      if(this.groups === null) {
        return null
      }
      console.log(this.groups.length)
      for(let i=0; i<this.groups.length; i++) {
        let g = this.groups[i]
        if(g._id === groupId) {
          return g
        }
        console.log(`${g._id}: ${groupId}`)
      }
      return null
    },

    loadUser(useruri) {
      // loads a user from its uri
      mytasks.get(useruri).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.activeUser = response.data
          this.groups = response.data.groups
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    loadGroup(groupId, checklistId) {
      /* get data about a group from the server, and set it as active.

      If a checklistIf is passed, load also the chccklist */
      mytasks.get(`/groups/${groupId}`).then( response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          for(var i=0; i<this.groups.length; i++) {
            if(this.groups[i]._id === groupId) {
              // set data
              this.$set(this.groups, i, response.data)

              // we must set this because it is set in the v-list v-model
              this.groups[i]._active = true

              // set activegroup
              this.activeGroup = this.groups[i]
              this.activeChecklistId = checklistId
            } else {
              this.groups[i].active = false
            }
          }
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    newGroup(name) {
      // Creates a new group in this user with a provided name
      mytasks.post('/groups/', {
        name: name,
        description: '',
        checklists: []
      }).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          this.groups.push(response.data)
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    deleteGroup(groupId) {
      // delete a group given its identifier
      if(this.activeGroup !== null && this.activeGroup._id === groupId) {
        this.activeGroup = null
        this.activeChecklist = null
      }
      let group = this.getGroupById(groupId)
      if(group === null) {
        this.$emit('showError', `Group not found: ${groupId}`)
        return
      }
      this.$refs.confirmDialog.confirm({title: `Delete group "${group.name}"?`, message: 'This action cannot be undone', yes: 'Delete', no: 'Cancel'}).then( confirm => {
        if(!confirm) {
          return
        }
        mytasks.delete(group.uri).then(response => {
          if(response.data.error_message !== undefined) {
            this.$emit('showError', response.data.error_message)
          } else {
            this.loadUser(`/users/${this.activeUser._id}`)
          }
        })
      })
    },

    newChecklist(groupId, name) {
      /* Create a new checklist in the groupId.

      If everyting was OK, set the group and the checklist as active */
      var group = this.getGroupById(groupId)
      if(group === null) {
        this.$emit('showError', 'Cannot find group ' + groupId)
        return
      }
      mytasks.post(`/checklists/`, {
        name: (name === undefined ? 'EMPTY NAME' : name),
        description: '',
        _parentid: groupId,
        hide_done_date: false,
        hide_done_items: false,
        items: []
      }).then(response => {
        if(response.data.error_message !== undefined) {
          this.$emit('showError', response.data.error_message)
        } else {
          if(group.checklists === undefined) {
            group.checklists = []
          }
          group.checklists.push(response.data)
          this.activeGroup = group
          this.activeChecklistId = response.data._id
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    deleteChecklist(checklist) {
      this.$refs.confirmDialog.confirm({title: `Delete checklist "${checklist.name}"?`, yes: 'Delete', message: 'This action cannot be undone'}).then( confirm => {
        if(!confirm) {
          return
        }
        mytasks.delete(checklist.uri).then(response => {
          if(response.data.error_message !== undefined) {
            this.$emit('showError', response.data.error_message)
          } else if (checklist._parentid === this.activeGroup._id) {
            this.loadGroup(this.activeGroup._id)
          }
        }).catch( error => {
          this.$emit('showError', error)
        })
      })
    },

    changeChecklistGroup(fromGroupId, toGroupId) {
      /* Change activeChecklist fromGroupId toGroupId. Activate the new group and checklist */
      if(fromGroupId === toGroupId || this.activeChecklist === null) {
        return
      }
      var newData = {
        name: this.activeChecklist.name,
        description: this.activeChecklist.description,
        _parentid: toGroupId,
        items: this.activeChecklist.items
      }
      // create a new checklist in toGroup with this data
      mytasks.post(`/checklists/`, newData).then( response => {
        if(response.data.errorMessage !== undefined) {
          this.$emit('showError', response.data.errorMessage)
        } else {
          // remove the old checklist
          mytasks.delete(this.activeChecklist.uri).then(response => {
            if(response.data.status !== 200) {
              this.$emit('Cannot delete old checklist: ' + response.data.showError)
            }
          })
          // load the group and checklist
          this.loadGroup(toGroupId, response.data._id)
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    duplicateChecklist(checklist) {
      /* Duplicates a checklist in the current group.

      The new checklist is actived */
      if(this.activeGroup === null) {
        this.$emit('showError', 'No active group')
      }
      var newData = {
        name: checklist.name,
        description: checklist.description,
        items: checklist.items,
        _parentid: this.activeGroup._id
      }
      mytasks.post('/checklists/', newData).then( response => {
        if(response.data.errorMessage !== undefined) {
          this.$emit('showError', response.data.errorMessage)
        } else {
          // load the group and the new checklist
          this.loadGroup(this.activeGroup._id, response.data._id)
        }
      }).catch( error => {
        this.$emit('showError', error)
      })
    },

    logout() {
      sessionStorage.clear()
      localStorage.clear()
      this.$router.push({name: 'login'})
    }
  }
}
</script>
