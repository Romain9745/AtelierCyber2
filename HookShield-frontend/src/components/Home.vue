<template>
    <div class="p-4 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Emails Bloqués</h1>
      <SearchBar :data="tableData" @update:data="tableData = $event" />
      <Table :data="tableData" />
    </div>
  </template>
  
  <script>
  import Table from "@/components/Table.vue";
  import SearchBar from "./SearchBar.vue";
  
  export default {
  components: {
    Table,
    SearchBar,
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