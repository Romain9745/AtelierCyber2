<template>
    <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
      
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Gestionnaire d'adresses mail</h1>
        <button @click="Add" class="px-4 py-2 bg-blue-500 rounded hover:bg-blue-600">Ajouter</button>
      </div>
      <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />
      </div>
      <MailConnexionModal v-if="isAdding" @close="isAdding = false" />
  </template>

    <script>
    import Table from "@/components/commun/Table.vue";
    import MailConnexionModal from "./MailConnexionModal.vue";

    export default {
      components: {
        Table,
        MailConnexionModal,
      },
      data() {
        return {
          tableData: [
            {mail: 'r.arg@gmail.com'},
            {mail: 'r@outlook.com'}
          ],
            headers: ['Adresse mail'],
            selectedEmail: null,
            isAdding : false
        };
        },
        methods: {
          handleRowClick(rowData) {
            this.selectedEmail = rowData;
          },
          Add(){
            this.isAdding = true;
          }
        },
        };
    </script>
          
