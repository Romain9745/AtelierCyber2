<template>
    <table class="w-full border-collapse border border-gray-300 dark:border-gray-700">
      <thead>
        <tr class="bg-gray-200 dark:bg-gray-800">
          <th v-for="(header, index) in headers" :key="index" class="border border-gray-300 dark:border-gray-700 p-2 text-left">
            {{ header }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in data" :key="rowIndex" class="odd:bg-white even:bg-gray-100 dark:odd:bg-gray-700 dark:even:bg-gray-800">
          <td v-for="(value, colIndex) in row" :key="colIndex" class="border border-gray-300 dark:border-gray-700 p-2">
            {{ value }}
          </td>
        </tr>
      </tbody>
    </table>
  </template>
  
  <script>
  export default {
    props: {
      data: {
        type: Array,
        required: true,
      },
    },
    computed: {
      headers() {
        return this.data.length > 0 ? Object.keys(this.data[0]) : [];
      },
    },
  };
  </script>