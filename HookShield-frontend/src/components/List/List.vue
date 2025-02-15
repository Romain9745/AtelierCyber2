<template>
    <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
      
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Listes</h1>
      </div>
      <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />
      </div>
      <ListModal :emails="selectedList" v-if="selectedList" @close="selectedList = null" />
  </template>
  
  <script>
  import ListModal from "./ListModal.vue";
  import Table from "@/components/commun/Table.vue";
  
  export default {
    components: {
      Table,
      ListModal,
    },
    data() {
      return {
        tableData: [
          { name: 'Blacklist', description: 'adresses mails bloquées'},
          { name: 'Withelist', sender: 'Aucune verification sur ces adresses'},
          { name: 'Blacklist Perso', sender: 'Liste adresses mails à bloquer'},
        ],
        blacklist: [
          { address: 'r.arg@gmail.com', description: 'spam' },
          { address: 'junkmail123@outlook.com', description: 'newsletter' },
          { address: 'scammer@fakeemail.com', description: 'scam' },
          { address: 'no-reply@companyxyz.com', description: 'marketing' },
          { address: 'sales@randomstore.com', description: 'promotion' },
          { address: 'alerts@bankxyz.com', description: 'phishing' },
          { address: 'admin@socialmedia.com', description: 'advertisement' },
          { address: 'bot@automatedservices.com', description: 'auto-generated' },
          { address: 'support@untrusted.com', description: 'spam' },
          { address: 'info@fraudsite.com', description: 'fraud' },
        ],

        headers: ['Nom de la liste', 'description'],
        selectedList: null,
      };
    },
    methods: {
      handleRowClick(rowData) {
        this.selectedList = this.blacklist;
      },
    },
  };
  </script>