<template>
  <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400 mt-4">
    <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
      <tr>
        <th
  v-for="(header, index) in headers"
  :key="index"
  class="px-6 py-3 cursor-pointer relative"
  @click="sortData(index)"
  :class="{
    'text-blue-600': sortIndex === index,
    'bg-gray-200': sortIndex === index,
    'dark:bg-gray-800': sortIndex === index,
  }"
>
  <div class="flex items-center space-x-2">
    <span>{{ header }}</span>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      class="w-3 h-3 inline-block"
      :class="{
        'font-bold': sortIndex === index && sortOrder === 'desc',
        'scale-120': sortIndex === index && sortOrder === 'desc'
      }"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M19 9l-7 7-7-7"
      />
    </svg>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      class="w-3 h-3 inline-block"
      :class="{
        'font-bold': sortIndex === index && sortOrder === 'asc',
        'scale-120': sortIndex === index && sortOrder === 'asc'
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
        @click="VizualiseRow(row)"
        class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600"
      >
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
    headers: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      sortIndex: null,  // Utilise l'index au lieu du header
      sortOrder: 'asc',
      sorted: [...this.data],
    };
  },
  methods: {
    // Fonction pour trier les données dans le tableau
    sortData(index) {
      if (this.sortIndex === index) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortIndex = index;
        this.sortOrder = 'asc';
      }

      this.sorted.sort((a, b) => {
        const aKey = Object.keys(a)[this.sortIndex];
        const bKey = Object.keys(b)[this.sortIndex];
        let aValue = a[aKey];
        let bValue = b[bKey];

        if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase();
        }
        if (typeof bValue === 'string') {
          bValue = bValue.toLowerCase();
        }

        // Si ce sont des nombres, on peut aussi les comparer directement
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return this.sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        }

        // Sinon, comparer par chaîne
        const comparison = aValue.localeCompare(bValue, undefined, { sensitivity: 'base' });
        return this.sortOrder === 'asc' ? comparison : -comparison;
      });
    },
    // Fonction pour visualiser une ligne
    VizualiseRow(row) {
      this.$emit('row-click', row);
    },
  },
};
</script>
  