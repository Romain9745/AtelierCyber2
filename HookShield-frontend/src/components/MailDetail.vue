<template>
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
    <!-- Boîte du mail -->
    <div v-if="selectedEmail" class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg w-96">
      <!-- Bouton pour fermer la fenêtre -->
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Détails</h2>
        <button @click="closeModal" class="text-gray-500 hover:text-gray-900 dark:hover:text-gray-300 text-xl">&times;</button>
      </div>

      <!-- Informations du mail -->
      <div class="text-gray-700 dark:text-gray-300">
        <p><strong>De :</strong> {{ selectedEmail.sender }}</p>
        <p><strong>À :</strong> {{ selectedEmail.recipient }}</p>
        <p><strong>Objet :</strong> {{ selectedEmail.subject }}</p>
        <p><strong>Contenu :</strong></p>
        
        <!-- Contenu du mail avec scroll si trop long -->
        <div class="border rounded-md p-2 bg-gray-100 dark:bg-gray-700 mt-2 max-h-40 overflow-y-auto text-sm">
          {{ selectedEmail.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    selectedEmail: {
      type: Object,
      required: true,
    },
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    stopPropagation(event) {
    event.stopPropagation(); // Empêche la propagation du clic vers les parents
  },
  },
};
</script>
