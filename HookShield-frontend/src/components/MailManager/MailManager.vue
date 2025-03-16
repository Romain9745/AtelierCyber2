<template>
    <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900" >
      
      <div class="flex items-center justify-between mb-4" @click="selectedEmail = null">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Gestionnaire d'adresses mail</h1>
        <button @click="Add" class="px-4 py-2 bg-blue-500 rounded hover:bg-blue-600">Ajouter</button>
      </div>
      <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />
      <div class="flex gap-2">
        <button type="button" @click="ConfirmSupress" :disabled="!selectedEmail" class="disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">Supprimer</button>
      </div>
      </div>
      <ConfirmationModal v-if="isConfirming" question="Êtes-vous sûr de vouloir supprimer cette adresse email ?" @close="isConfirming = false" @delete="SupressEmailAdress" />
      <MailConnexionModal v-if="isAdding" @close="Added" />
  </template>

    <script>
    import Table from "@/components/commun/Table.vue";
    import MailConnexionModal from "./MailConnexionModal.vue";
    import ConfirmationModal from "../commun/ConfirmationModal.vue";
    import MailModifierModal from "./MailModifierModal.vue";
    import axiosInstance from "@/AxiosInstance";

    export default {
      components: {
        Table,
        MailConnexionModal,
        ConfirmationModal,
        MailModifierModal
      },
      data() {
        return {
          tableData: [
          ],
            headers: ['Adresse mail'],
            selectedEmail: null,
            isAdding : false,
            isConfirming: false,
        };
        },
      mounted() {
        this.fetchEmailAccounts();
      },
      methods: {
        async fetchEmailAccounts() {
          try {
            const response = await axiosInstance.get('/email_accounts');
            this.tableData = response.data.map(email => ({
              mail: email.email,
            }));

            
          } catch (error) {
            console.error("Erreur lors de la récupération des emails bloqués :", error);
          }
        },
        handleRowClick(rowData) {
            this.selectedEmail = rowData;
          },
        Add(){
            this.isAdding = true;
          },
        Added(email){
            this.tableData.push({mail: email});
          },
        ConfirmSupress(){
            this.isConfirming = true;
          },
        SupressEmailAdress(){
          const data = { email: this.selectedEmail.mail };
            const response = axiosInstance.post('/delete/imap', data);
            if(response.status == 204){
              this.fetchEmailAccounts();
            }
            else{
              console.error("Erreur lors de la suppression de l'adresse mail");
            }
            this.isConfirming = false;
          },
        },
        };
    </script>
          
