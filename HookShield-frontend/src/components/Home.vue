<template>
    <div class="p-4 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Tableau de Données</h1>
      <Table :data="tableData" />
    </div>
  </template>
  
  <script>
  import Table from "@/components/Table.vue";
  
  export default {
  components: {
    Table,
  },
  data() {
    return {
      tableData: [
        { id: 1, name: 'Alice', age: 25, skills: ['Vue', 'React'], active: true },
        { id: 2, name: 'Bob', age: 30, skills: ['Angular', 'TypeScript'], active: false },
        { id: 3, name: 'Charlie', age: 28, skills: ['Svelte', 'Go'], active: true },
        { id: 4, name: 'Diana', age: 22, skills: ['Python', 'Django'], active: false },
      ],
    };
  },
};
  </script>