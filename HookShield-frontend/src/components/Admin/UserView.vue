<template>
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
      <h3 class="text-lg font-bold mb-4 text-center">Éditer l'utilisateur</h3>

      <div>
        <label for="email" class="block mb-2">Email de l'utilisateur</label>
        <input 
          id="email"
          v-model="userToEdit.email"
          type="email"
          :disabled="!isEditing"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>

      <div>
        <label class="block mb-2">Nom de l'utilisateur</label>
        <input 
          v-model="userToEdit.last_name"
          type="text"
          :disabled="!isEditing"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>

      <div>
        <label class="block mb-2">Prénom de l'utilisateur</label>
        <input 
          v-model="userToEdit.first_name"
          type="text"
          :disabled="!isEditing"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>

      <div>
        <label class="block mb-2">Permission</label>
        <div class="flex gap-4">
          <label class="flex items-center">
            <input 
              type="radio"
              v-model="userToEdit.role_id"
              :value="2"
              :disabled="!isEditing"
              class="mr-2"
            />
            Utilisateur
          </label>

          <label class="flex items-center">
            <input 
              type="radio"
              v-model="userToEdit.role_id"
              :value="1"
              :disabled="!isEditing"
              class="mr-2"
            />
            Administrateur
          </label>
        </div>
      </div>

      <div class="mt-4 flex justify-end space-x-2">
        <button @click="closeModal" class="bg-red-500 text-white px-4 py-2 rounded">
          Annuler
        </button>

        <button v-if="!isEditing" @click="isEditing = true" class="bg-gray-500 text-white px-4 py-2 rounded">
          Modifier
        </button>

        <button v-if="isEditing" @click="saveUser" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>

    <!-- Modal de confirmation -->
    <div v-if="isConfirming" class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);">
      <div class="bg-white p-4 rounded-lg shadow-lg w-1/4">
        <h3 class="text-lg font-bold mb-2">Confirmer la suppression</h3>
        <p>Voulez-vous vraiment supprimer cet utilisateur ?</p>
        <div class="mt-4 flex justify-end space-x-2">
          <button @click="isConfirming = false" class="bg-gray-400 text-white px-4 py-2 rounded">
            Non
          </button>
          <button @click="deleteUser" class="bg-red-500 text-white px-4 py-2 rounded">
            Oui
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    selectedUser: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      userToEdit: { ...this.selectedUser }, // Copie de l'utilisateur sélectionné pour édition
      isEditing: false, // Désactiver l'édition au départ
      isConfirming: false,
    };
  },
  watch: {
    selectedUser(newUser) {
      this.userToEdit = { ...newUser }; // Met à jour la copie à chaque sélection
      this.isEditing = false; // Réinitialise l'état d'édition
    },
  },
  methods: {
    closeModal() {
      this.$emit("close"); // Émet l'événement pour fermer le modal
    },
    saveUser() {
      if (!this.userToEdit.email.trim()) {
        alert("Veuillez entrer une adresse email.");
        return;
      }
      this.$emit("save", this.userToEdit); // Émet l'événement avec les modifications
      this.isEditing = false; // Désactive l'édition après la sauvegarde
    },
    confirmDelete() {
      this.isConfirming = true;
    },
    deleteUser() {
      this.$emit("delete", this.userToEdit.email);
      this.isConfirming = false;
      this.closeModal();
    },
    stopPropagation(event) {
      event.stopPropagation(); // Empêche la propagation des clics sur l'overlay
    },
  },
};
</script>
