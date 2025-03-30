<template>
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
    <!-- Boîte de détails du mail -->
    <div 
      v-if="selectedEmail" 
      class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-2xl w-96 transform transition-all scale-95 hover:scale-100"
    >
      <!-- En-tête avec bouton de fermeture -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Détails du Mail</h2>
        <button 
          @click="closeModal" 
          class="text-gray-500 hover:text-red-500 dark:hover:text-red-400 text-2xl transition"
          title="Fermer"
        >
          &times;
        </button>
      </div>

      <!-- Contenu détaillé du mail -->
      <div class="space-y-3 text-gray-700 dark:text-gray-300">
        <div class="flex items-center gap-2">
          <span class="font-semibold">De :</span>
          <span class="truncate">{{ selectedEmail.sender }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="font-semibold">À :</span>
          <span class="truncate">{{ selectedEmail.recipient }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="font-semibold">Objet :</span>
          <span class="truncate">{{ selectedEmail.subject }}</span>
        </div>

        <div class="mt-4">
          <p class="font-semibold mb-1">Contenu :</p>
          <div 
            class="border border-gray-300 dark:border-gray-600 rounded-md p-3 bg-gray-50 dark:bg-gray-700 max-h-48 overflow-y-auto text-sm text-gray-800 dark:text-gray-200"
          >
            {{ email_body }}
          </div>
        </div>
      </div>

      <!-- Bouton de fermeture supplémentaire -->
      <button 
        @click="closeModal" 
        class="mt-6 w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded-lg transition-colors"
      >
        Fermer
      </button>
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
    email_body: String,
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
  },
};
</script>
