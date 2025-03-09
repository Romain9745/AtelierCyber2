<template>
  <div style="overflow: auto;">
    <!-- Premier tableau : Liste des utilisateurs -->
    <div class="flex flex-col gap-3 h-full p-8 bg-gray-100 dark:bg-gray-900">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white" @click="hideOrShowData('userTable')">Liste des utilisateurs</h1>
        <div class="flex items-center gap-2">
          <button class="bg-blue-500 text-white px-4 py-2 rounded-lg" @click="ShowAddModal = true">Ajouter un utilisateur</button>
        </div>
      </div>
      <Table class="userTable" :data="userData" :headers="headers" @row-click="handleRowClick"/>
    

    <!-- Deuxième tableau : Historique -->
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white" @click="hideOrShowData('logTable')">Historique</h1>
      </div>
      <Table class="logTable" :data="logData" :headers="headersLogs" />
    </div>

    <!-- Liste d'utilisateurs sélectionnés (UserList) -->
    <UserView :selectedUser="selectedUser" v-if="selectedUser" @close="selectedUser = null" @save ="SaveUser"/>
    <CreateUserModal v-if="ShowAddModal" @close="ShowAddModal = false" @user-added = "AddUSer"/>
  </div>
</template>

<script>
import Table from "@/components/commun/Table.vue";
import UserView from "./UserView.vue";
import CreateUserModal from "./CreateUserModal.vue";
import axiosInstance from "@/AxiosInstance";

export default {
  components: {
    Table,
    UserView,
    CreateUserModal,
  },

  data() {
    return {
      userData: [],
      logData: [
        { author: 'Alice Opéhidémervèye', description: 'Fermeture ticket 6966642', date: '28-10-2024' },
        { author: 'Mr. Indestructible', description: 'Ajout de tiboinshape@fraud.com dans la blacklist', date: '27-10-2024' },
        { author: 'Charlie Chaplin', description: 'A été promu administrateur', date: '27-10-2024' },
        { author: 'Frank Dubosc', description: 'pasunefraude@gmail.com a été retiré de la blacklist', date: '27-10-2024' },
      ],
      headers: ['Utilisateur', 'Niveau de permission', "Date d'ajout"],
      headersLogs: ['Auteur', 'Description', 'Date'],
      selectedUser: null,
      ShowAddModal: false,
    };
  },

  mounted() {
    axiosInstance.get('http://localhost:8000/admin/users')
      .then(response => {
        this.userData = response.data.map(user => ({
          email: user.email,
          permission: (user.role_id == 1) ? 'Administrateur' : 'Utilisateur' ,
          date: user.last_login,
        }));
        console.log(this.userData);
      })
      .catch(error => {
        console.error("Error while fetching users:", error);
      });
  },

  methods: {
    handleRowClick(rowData) {
      axiosInstance.get(`http://localhost:8000/admin/user/${rowData.email}`)
        .then(response => {
          this.selectedUser = response.data;
          console.log("Selected user:", this.selectedUser);
        })
        .catch(error => {
          console.error("Error while fetching user details:", error);
        });
    },
    SaveUser(User) {
      console.log("User to save:", User);
      axiosInstance.post('/admin/update_user',User)
        .then(response => {
          console.log("User saved:", response.data);
        })
        .catch(error => {
          console.error("Error while saving user:", error);
        });
    },
    AddUSer(User) {
      console.log("User to add:", User);
      axiosInstance.post('/admin/create_user',User)
        .then(response => {
          console.log("User added:", response.data);
        })
        .catch(error => {
          console.error("Error while adding user:", error);
        });
    },
  },
};
</script>