<template>
  <div class="mb-2 flex items-center justify-between space-x-4">
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Rechercher..."
      class="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:focus:ring-blue-600"
    />
    <button
      @click="captureSearch"
      class="bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 focus:outline-none dark:bg-blue-700 dark:hover:bg-blue-800"
    >
      Rechercher
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: '', // La requête de recherche
    };
  },
  methods: {
    captureSearch() {
      // Capture le texte saisi et l'affiche dans la console (à remplacer par logique de requête)
      console.log('Texte recherché:', this.searchQuery);
    },
  },
};
</script>

<style scoped>
/* Style personnalisé pour la barre de recherche */
input {
  width: 500px;
}
</style>