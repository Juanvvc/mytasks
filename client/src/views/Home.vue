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
          prepend-icon="view_agenda">
          <!-- group name -->
          <v-list-tile slot="activator">
            <v-list-tile-content>
              <v-list-tile-title>{{group.name}}</v-list-tile-title>
            </v-list-tile-content>
            <!-- add checklists or delete the group -->
            <v-list-tile-action>
              <v-flex xs12>
                <v-tooltip bottom>
                  <v-btn
                    flat icon color="primary"
                    slot="activator"
                    @click.stop="newChecklist(group.id)">
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
          <!-- Lis of checklist in group -->
          <v-list-tile
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
    <v-toolbar app fixed clipped-left>
        <v-toolbar-side-icon @click.stop="showDrawer = !showDrawer"></v-toolbar-side-icon>
        <v-toolbar-title>MyTasks</v-toolbar-title>
    </v-toolbar>

    <!-- Main content -->
    <v-content>
      <check-list
        :checklist="activeChecklist"
        :group="activeGroup"
        @newItem="newItem"
        @checkItem="checkItem"
        @clearChecklist="clearChecklist"
        @deleteChecklist="deleteChecklist"
        />
    </v-content>
  </div>
</template>

<script>
// @ is an alias to /src
import CheckList from '@/components/CheckList.vue'

export default {
  name: 'home',
  components: {
    CheckList
  },
  data: () => ({
    showDrawer: true,
    newGroupName: '',
    activeChecklist: null,
    activeGroup: null,
    groups: [
      {
        name: 'One',
        active: true,
        id: 0,
        checklists: [
          {
            name: "1",
            id: 1,
            items: [
              {'name': 'item1', checked: true},
              {'name': 'item2', checked: false},
            ]
          },
          {name: "222", id: 2}
        ]
      },
      {name: 'Two', active: false, id: 1}
    ]
  }),

  methods: {
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

    getChecklistById(groupId, checklistId) {
      var group = this.getGroupById(groupId)
      if(group === null || group.checklists === undefined) {
        return null
      }

      for(let i=0; i<group.checklists.length; i++) {
        if(group.checklists[i].id === checklistId) {
          return group.checklists[i]
        }
      }
      return null
    },

    loadChecklist (groupId, checklistId) {
      this.activeGroup = this.getGroupById(groupId)
      this.activeChecklist = this.getChecklistById(groupId, checklistId)
    },

    newGroup(name) {
      this.groups.push({
        name: name,
        description: null,
        checklists: []
      })
    },

    deleteGroup(groupId) {
      if(this.activeGroup !== null && this.activeGroup.id === groupId) {
        this.activeGroup = null
        this.activeChecklist = null
      }
      for(var i=0; i<this.groups.length; i++) {
        if(this.groups[i].id === groupId) {
          if(this.groups[i].checklists === undefined || this.groups.checklists.length === 0) {
            this.groups.splice(i, 1)
          } else {
            this.$emit('showError', 'Cannot delete group: not empty')
          }
          return
        }
      }
    },

    newChecklist(groupId) {
      var group = this.getGroupById(groupId)
      if(group.checklists === undefined || group.checklists === null) {
        group.checklists = []
      }
      group.checklists.push({
        name: 'New checklist',
        description: '',
        items: []
      })
    },

    newItem(name) {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to add an item')
      }
      this.activeChecklist.items.push({'name': name, checked: false})
    },

    checkItem(index) {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to check item')
      }
      this.activeChecklist.items[index].checked = !this.activeChecklist.items[index].checked
    },

    clearChecklist() {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to clear')
      }
      var newItems = []
      for(var i=0; i<this.activeChecklist.items.length; i++) {
        if(!this.activeChecklist.items[i].checked) {
          newItems.push(this.activeChecklist.items[i])
        }
      }
      this.activeChecklist.items = newItems
    },

    deleteChecklist() {
      if(this.activeGroup === null || this.activeChecklist === null) {
        this.$emit('showError', 'No active checklist to delete')
      }
      for(var i=0; i<this.activeGroup.checklists.length; i++) {
        if(this.activeGroup.checklists[i].id === this.activeChecklist.id) {
          this.activeGroup.checklists.splice(i, 1)
          this.activeChecklist = null
          return
        }
      }
    }
  }
}
</script>
