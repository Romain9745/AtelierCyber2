<template>
    <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
      
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Listes</h1>
      </div>
      <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />
      </div>
      <ListModalManager :listname="selectedListName" :emails="selectedList" v-if="selectedList" @close="selectedList = null" />
  </template>
  
  <script>
  import ListModalManager from "./ListModalManager.vue";
  import Table from "@/components/commun/Table.vue";
  import axiosInstance from '@/AxiosInstance'; // Import d'axiosInstance
  import axios from 'axios'; // Import d'axios
  
  export default {
    components: {
      Table,
      ListModalManager,
    },
    data() {
      return {
        tableData: [
          { name: 'Blacklist', description: 'adresses mails bloquées'},
          { name: 'Whitelist', sender: 'Aucune verification sur ces adresses'},
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
        whitelist: [
        { address: 'michel@gmail.com', description: "c'est un collègue" },
        { address: 'bot@automatedservices.com', description: 'ces mails sont drôles' },
        { address: 'associationdespecheurspros@outlook.com', description: 'fishing' },
        ],

        headers: ['Nom de la liste', 'description'],
        selectedList: null,
        selectedListName: null
      };
    },
    methods: {
    async handleRowClick(rowData) {
        try {
            if (rowData.name === "Blacklist") {
                this.selectedListName = "Blacklist";
                const response = await axios.get('http://localhost:8000/main_blacklist');
                this.selectedList = response.data.map(item => ({
                    address: item.email,  
                    description: item.reason 
                })); 
            } else if (rowData.name === "Whitelist") {
                this.selectedListName = "Whitelist";
                const response = await axios.get('http://localhost:8000/whitelist');
                this.selectedList = response.data.map(item => ({
                    address: item.email, 
                    description: item.reason 
                })); 
            } else if (rowData.name === "Blacklist Perso") {
                this.selectedListName = "Blacklist Perso";
                const response = await axios.get('http://localhost:8000/user_blacklist');
                this.selectedList = response.data.map(item => ({
                    address: item.email, 
                    description: item.reason 
                })); 
            }
        } catch (error) {
            console.error("Error fetching list:", error);
            this.selectedList = [];  // Clear the list in case of error
        }
      },
    },
  };
  </script>
