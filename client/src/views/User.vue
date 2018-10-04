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
        <!-- items for today -->
        <v-list-tile>
          <v-list-tile-content>
            <v-list-tile-title
              class="pointable"
              @click.stop="activeChecklistId = 'today'"
              ><v-icon>today</v-icon> Today
            </v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>

        <v-list-group
          v-for="group in groups"
          v-model="group._active"
          :key="group._id"
          @click="loadGroup(group)"
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
        :available-groups="groups"
        @checklistDeleted="loadGroup(activeGroup)"
        @checklistMoved="checklistMoved"
        @checklistDuplicated="checklistDuplicated"
        @showError="$emit('showError', $event)"
        @showWarning="$emit('showWarning', $event)"
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

const DEFAULT_CHECKLIST = 'today'

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
      mytasks.onError(message => {
        this.$emit('showError', message)
      })
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
      for(let i=0; i<this.groups.length; i++) {
        let g = this.groups[i]
        if(g._id === groupId) {
          return g
        }
      }
      return null
    },

    loadUser(useruri) {
      // loads a user from its uri
      mytasks.get(useruri).then(response => {
        this.activeUser = response.data
        this.groups = response.data.groups
        this.activeChecklistId = DEFAULT_CHECKLIST
      }, error => {
        this.$emit('showError', error)
      })
    },

    loadGroup(group, checklistId) {
      /* get data about a group from the server, and set it as active.

      If a checklistIf is passed, load also the checklist */

      if(!group._id || !group.uri) {
        // it is a special group: do not request additional informatio, use what you have in the memory
        for(var i=0; i<this.groups.length; i++) {
          if(this.groups[i].name === group.name) {
            // we must set this because it is set in the v-list v-model
            this.groups[i]._active = true

            // set activegroup
            this.activeGroup = this.groups[i]
            this.activeChecklistId = checklistId
          } else {
            this.groups[i].active = false
          }
        }
        return
      }

      mytasks.get(group.uri).then( response => {
        for(var i=0; i<this.groups.length; i++) {
          if(this.groups[i]._id === group._id) {
            // set data
            this.groups[i] = response.data

            // we must set this because it is set in the v-list v-model
            this.groups[i]._active = true

            // set activegroup
            this.activeGroup = this.groups[i]
            this.activeChecklistId = checklistId
          } else {
            this.groups[i].active = false
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
        this.groups.push(response.data)
      }, error => {
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

    checklistDuplicated(newChecklist) {
      this.loadGroup(this.activeGroup, newChecklist._id)
    },

    checklistDeleted() {
      this.loadGroup(this.activeGroup)
    },

    checklistMoved(checklist, toGroupId) {
      this.loadGroup(this.getGroupById(toGroupId), checklist._id)
    },

    logout() {
      sessionStorage.clear()
      localStorage.clear()
      this.$router.push({name: 'login'})
    }
  }
}
</script>
