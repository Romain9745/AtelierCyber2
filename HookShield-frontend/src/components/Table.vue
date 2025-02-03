<template>
    <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
        <tr>
          <th scope="col" class="p-4">
            <div class="flex items-center">
              <input
                id="checkbox-all-search"
                type="checkbox"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <label for="checkbox-all-search" class="sr-only">checkbox</label>
            </div>
          </th>
          <th
            v-for="(header, index) in headers"
            :key="index"
            class="px-6 py-3 cursor-pointer relative"
            @click="sortData(header)"
            :class="{
              'text-blue-600': sortKey === header  // Highlight sorted column
            }"
          >
            <div class="flex items-center space-x-2">
              <span>{{ header }}</span>
              <!-- First Chevron (Ascending) -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                class="w-3 h-3 inline-block"
                :class="{
                  'font-bold': sortKey === header && sortOrder === 'desc',  // Make chevron bold if selected
                  'scale-120': sortKey === header && sortOrder === 'desc'// Optionally, scale chevron to make it bigger
                }"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
              <!-- Second Chevron (Descending) -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                class="w-3 h-3 inline-block"
                :class="{
                  'font-bold': sortKey === header && sortOrder === 'asc',  // Make chevron bold if selected
                  'scale-120': sortKey === header && sortOrder === 'asc'// Optionally, scale chevron to make it bigger
                }"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 15l7-7 7 7"
                />
              </svg>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, rowIndex) in sorted"
          :key="rowIndex"
          class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600"
        >
          <td class="w-4 p-4">
            <div class="flex items-center">
              <input
                id="checkbox-table-search-2"
                type="checkbox"
                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <label for="checkbox-table-search-2" class="sr-only">checkbox</label>
            </div>
          </td>
          <td
            v-for="(value, colIndex) in row"
            :key="colIndex"
            class="border border-gray-300 dark:border-gray-700 p-2"
          >
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
    data() {
      return {
        sortKey: '', // Column to sort by
        sortOrder: 'asc', // Sorting order (asc or desc)
        sorted: [...this.data], // Copy of the original data to sort
      };
    },
    computed: {
      headers() {
        return this.data.length > 0 ? Object.keys(this.data[0]) : [];
      },
    },
    methods: {
        sortData(header) {
            if (this.sortKey === header) {
                this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortKey = header;
                this.sortOrder = 'asc';
            }

            console.log(this.sortKey, this.sortOrder);

 
            this.sorted.sort((a, b) => {
                const aValue = a[this.sortKey] != null ? String(a[this.sortKey]) : '';
                const bValue = b[this.sortKey] != null ? String(b[this.sortKey]) : '';
                const comparison = aValue.localeCompare(bValue, undefined, {
                    sensitivity: 'base',
                });
                return this.sortOrder === 'asc' ? comparison : -comparison;
            });
        }
    },
  };
  </script>
  