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
          v-for="section in sections"
          v-model="section.active"
          :key="section.name"
          prepend-icon="view_agenda"
          no-action>
          <v-list-tile slot="activator">
            <v-list-tile-content>
              <v-list-tile-title>{{section.name}}</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile
            v-for="checklist in section.checklists"
            :key="checklist.name"
          >
            <v-list-tile-content>
              <v-list-tile-title
                @click="loadChecklist(section.id, checklist.id)"
                class="pointable">
                {{checklist.name}}
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>

        </v-list-group>

        <v-text-field
          label="Solo"
          placeholder="New group"
          v-model="newSectionName"
          @keyup.enter="createSection(newSectionName)"
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
        @newItem="newItem"
        @checkItem="checkItem"
        @clearChecklist="clearChecklist"
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
    newSectionName: '',
    activeChecklist: null,
    sections: [
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
    loadChecklist (sectionId, checklistId) {
      for(var i=0; i<this.sections.length; i++) {
        if(this.sections[i].id === sectionId) {
          let currentSection = this.sections[i]
          for(var j=0; j<currentSection.checklists.length; j++) {
            if(currentSection.checklists[j].id === checklistId) {
              this.activeChecklist = currentSection.checklists[j]
              return
            }
          }
        }
      }
      this.$emit('showError', 'No checklist ' + sectionId + '/' + checklistId)
    },

    newItem(name) {
      this.activeChecklist.items.push({'name': name, checked: false})
    },

    checkItem(index) {
      this.activeChecklist.items[index].checked = !this.activeChecklist.items[index].checked
    },

    clearChecklist() {
      var newChecklist = {}
      newChecklist.id = this.activeChecklist.id
      newChecklist.name = this.activeChecklist.name
      newChecklist.description = this.activeChecklist.description
      newChecklist.items = []
      for(var i=0; i<this.activeChecklist.items.length; i++) {
        if(!this.activeChecklist.items[i].checked) {
          newChecklist.items.push(this.activeChecklist.items[i])
        }
      }
      this.activeChecklist = newChecklist
      // TODO: save newChecklist in checklists
    }
  }
}
</script>
