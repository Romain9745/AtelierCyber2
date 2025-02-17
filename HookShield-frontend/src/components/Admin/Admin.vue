<template>
  <div>
    <!-- Premier tableau : Liste des utilisateurs -->
    <div class="flex flex-col gap-3 h-full p-8 bg-gray-100 dark:bg-gray-900">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white" @click="hideOrShowData('userTable')">Liste des utilisateurs</h1>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6" @click="handleRowClick">
          <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
        </svg>
      </div>
      <Table class="userTable" :data="userData" :headers="headers" />
    

    <!-- Deuxième tableau : Historique -->
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white" @click="hideOrShowData('logTable')">Historique</h1>
      </div>
      <Table class="logTable" :data="logData" :headers="headersLogs" />
    </div>

    <!-- Liste d'utilisateurs sélectionnés (UserList) -->
    <UserList :emails="userData" v-if="selectedUser" @close="selectedUser = null"/>
  </div>
</template>

<script>
import Table from "@/components/commun/Table.vue";
import UserList from "./UserList.vue";

export default {
  components: {
    Table,
    UserList,
  },
  data() {
    return {
      userData: [
        { username: 'Alice Opéhidémervèye', permission: 'Administrateur', date: '12-03-2024' },
        { username: 'Charlie Chaplin', permission: 'Administrateur', date: '12-03-2024' },
        { username: 'Eve Angile', permission: 'Utilisateur', date: '15-06-2024' },
        { username: 'Frank Dubosc', permission: 'Utilisateur', date: '27-06-2024' },
      ],
      logData: [
        { author: 'Alice Opéhidémervèye', description: 'Fermeture ticket 6966642', date: '28-10-2024'},
        { author: 'Mr. Indestructible', description: 'Ajout de tiboinshape@fraud.com dans la blacklist', date: '27-10-2024'},
        { author: 'Charlie Chaplin', description: 'A été promu administrateur', date: '27-10-2024'},
        { author: 'Frank Dubosc', description: 'pasunefrande@gmail.com a été retiré de la blacklist', date: '27-10-2024'},
      ],
      headers: ['Utilisateur', 'Niveau de permission', "Date d'ajout"],
      headersLogs: ['Auteur', 'Description', 'Date'],
      selectedUser: null,
      isHidden: false,
    };
  },
  methods: {
    handleRowClick(rowData) {
      this.selectedUser = rowData;
    },
    hideData(className) {
        console.log("data is hidden")
        const table = document.querySelector(`.${className}`);
        if (!table) return;

        const rows = table.querySelectorAll("tbody tr"); // Sélectionne toutes les lignes du tbody
        rows.forEach((row, index) => {
        row.style.display = index < 3 ? "" : "none"; // Cache toutes les lignes sauf les 3 premières
        });
        this.isHidden=true
    },
    showAllData(className) {
        const table = document.querySelector(`.${className}`);
        if (!table) return;

        const rows = table.querySelectorAll("tbody tr");
        rows.forEach((row) => {
        row.style.display = ""; // Affiche toutes les lignes
        });
        this.isHidden=false
    },
    hideOrShowData(className) {
    if (this.isHidden) {
      this.showAllData(className);
    } else {
      this.hideData(className);
    }
    },
  },
};
</script>