<template>
    <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900" >
      
      <div class="flex items-center justify-between mb-4" @click="selectedEmail = null">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Gestionnaire d'adresses mail</h1>
        <button @click="Add" class="px-4 py-2 bg-blue-500 rounded hover:bg-blue-600">Ajouter</button>
      </div>
      <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />
      <div class="flex gap-2">
        <button type="button" @click="isEditing = true" :disabled="!selectedEmail" class="disabled:bg-gray-400 disabled:cursor-not-allowed text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Modifier</button>
        <button type="button" @click="ConfirmSupress" :disabled="!selectedEmail" class="disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">Supprimer</button>
      </div>
      </div>
      <MailModifierModal v-if="isEditing" :email-to-edit="selectedEmail.mail" @close="isEditing = false" @save="Edit"/>
      <ConfirmationModal v-if="isConfirming" question="Êtes-vous sûr de vouloir supprimer cette adresse email ?" @close="isConfirming = false" @delete="SupressEmailAdress" />
      <MailConnexionModal v-if="isAdding" @close="isAdding = false" />
  </template>

    <script>
    import Table from "@/components/commun/Table.vue";
    import MailConnexionModal from "./MailConnexionModal.vue";
    import ConfirmationModal from "../commun/ConfirmationModal.vue";
    import MailModifierModal from "./MailModifierModal.vue";

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
            {mail: 'r.arg@gmail.com'},
            {mail: 'r@outlook.com'}
          ],
            headers: ['Adresse mail'],
            selectedEmail: null,
            isAdding : false,
            isConfirming: false,
            isEditing: false,
        };
        },
        methods: {
          handleRowClick(rowData) {
            this.selectedEmail = rowData;
          },
          Add(){
            this.isAdding = true;
          },
          Edit(NewMailAdress){
            console.log('Modifier email:', NewMailAdress);
            this.isEditing = false;
          },
          ConfirmSupress(){
            this.isConfirming = true;
          },
          SupressEmailAdress(){
            console.log('Supprimer email:', this.selectedEmail);
            this.isConfirming = false;
          }
        },
        };
    </script>
          
