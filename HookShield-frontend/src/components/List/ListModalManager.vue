<template>
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" @click.self="deselectRow">
      <div class="flex flex-col gap-6 bg-white p-6 rounded-lg shadow-lg w-1/3" @click.self="deselectRow">
        <h2 class="text-lg font-bold mb-4 text-center">Email Addresses</h2>
        <table class="w-full border-collapse border border-gray-300 " >
          <thead>
            <tr class="bg-gray-100">
              <th class="border border-gray-300 px-4 py-2 text-left">Email</th>
              <th class="border border-gray-300 px-4 py-2 text-left">Description</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(email, index) in emails"
              :key="index"
              class="border-t cursor-pointer hover:bg-gray-200"
              :class="{ 'bg-blue-100': selectedEmail === email }"
              @click="selectRow(email)"
            >
              <td class="border border-gray-300 px-4 py-2">{{ email.address }}</td>
              <td class="border border-gray-300 px-4 py-2">{{ email.description }}</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4 flex gap-2 justify-end">
          <button 
            @click="closeModal" 
            class="bg-red-500 text-white px-4 py-2 rounded"
          >
            Fermer
          </button>
          <button 
            @click="edit" 
            :disabled="!selectedEmail" 
            class="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Éditer
          </button>
          <button 
            @click="confirmDelete" 
            :disabled="!selectedEmail" 
            class="bg-red-600 text-white px-4 py-2 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  
    <!-- Modal de confirmation -->
    <div v-if="isConfirming" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <ConfirmationModal 
        question="Êtes-vous sûr de vouloir supprimer cet email ?"
        @close="isConfirming = false"
        @delete="deleteEmail"/>
    </div>

     <!-- Modal d'édition -->
  <div v-if="isEditing" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3">
      <h3 class="text-lg font-bold mb-4 text-center">Éditer Email</h3>
      <div>
        <label for="email" class="block mb-2">Adresse Email</label>
        <input 
          id="email"
          v-model="emailToEdit.address"
          type="email"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>
      <div>
        <label for="description" class="block mb-2">Description</label>
        <input 
          id="description"
          v-model="emailToEdit.description"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="CloseEditing" class="bg-gray-400 text-white px-4 py-2 rounded">
          Annuler
        </button>
        <button @click="saveEmail" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>
  </template>
  
  <script>
import ConfirmationModal from "@/components/commun/ConfirmationModal.vue";


export default {
  components: {
    ConfirmationModal,
  },
  props: {
    emails: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedEmail: null,
      isConfirming: false,
      isEditing: false, // Gère l'affichage du modal d'édition
      emailToEdit: null, // Garde l'email sélectionné pour l'édition
    };
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    selectRow(email) {
      this.selectedEmail = email;
    },
    deselectRow() {
      this.selectedEmail = null;
    },
    edit() {
      if (this.selectedEmail) {
        this.emailToEdit = { ...this.selectedEmail }; // Crée une copie de l'email pour l'édition
        this.isEditing = true; // Affiche le modal d'édition
      }
    },
    confirmDelete() {
      this.isConfirming = true; // Affiche le modal de confirmation
    },
    deleteEmail() {
      if (this.selectedEmail) {
        this.$emit("delete", this.selectedEmail);
        this.selectedEmail = null;
        this.isConfirming = false;
      }
    },
    saveEmail() {
      if (this.emailToEdit) {
        this.$emit("edit", this.emailToEdit); // Émet l'événement avec l'email modifié
        this.isEditing = false; // Ferme le modal d'édition
        this.emailToEdit = null; // Réinitialise l'email à éditer
      }
    },
    CloseEditing() {
      this.isEditing = false; // Ferme le modal d'édition
      this.emailToEdit = null; // Réinitialise l'email à éditer
    },
  },
};
</script>

  