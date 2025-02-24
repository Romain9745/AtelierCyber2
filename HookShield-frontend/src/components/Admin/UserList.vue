<template>
<div>
    <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
      <div class="flex flex-col gap-6 bg-white p-6 rounded-lg shadow-lg w-1/3 transform translate-y-8" @click.self="deselectRow">
        <h2 class="text-lg font-bold mb-4 text-center">Liste d'utilisateurs</h2>
        <button 
            @click="confirmAdd" 
            class="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Ajouter
          </button>
        <table class="w-full border-collapse border border-gray-300 " >
          <thead>
            <tr class="bg-gray-100">
              <th class="border border-gray-300 px-4 py-2 text-left">Utilisateur</th>
              <th class="border border-gray-300 px-4 py-2 text-left">Niveau de permission</th>
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
              <td class="border border-gray-300 px-4 py-2">{{ email.username }}</td>
              <td class="border border-gray-300 px-4 py-2">{{ email.permission }}</td>
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
    <div v-if="isConfirming" class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);">
      <div class="bg-white p-4 rounded-lg shadow-lg w-1/4">
        <h3 class="text-lg font-bold mb-2">Confirmer la suppression</h3>
        <p>Voulez-vous vraiment supprimer cet utilisateur ?</p>
        <div class="mt-4 flex justify-end space-x-2">
          <button @click="isConfirming = false" class="bg-gray-400 text-white px-4 py-2 rounded">
            Non
          </button>
          <button @click="deleteEmail" class="bg-red-500 text-white px-4 py-2 rounded">
            Oui
          </button>
        </div>
      </div>
    </div>

     <!-- Modal d'édition -->
  <div v-if="isEditing" class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="CloseEditing">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
      <h3 class="text-lg font-bold mb-4 text-center">Éditer l'utilisateur</h3>
      <div>
        <label for="email" class="block mb-2">Nom de l'utilisateur</label>
        <input 
        id="email"
        :value="selectedEmail.username"
        type="email"
        class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        />
      </div>
      <div>
        <label for="description" class="block mb-2">Permission</label>
        <select 
        id="permission"
        v-model="selectedEmail.permission"
        class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
      >
        <option value="Utilisateur">Utilisateur</option>
        <option value="Administrateur">Administrateur</option>
      </select>
      </div>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="CloseEditing" class="bg-red-500 text-white px-4 py-2 rounded">
          Annuler
        </button>
        <button @click="saveEmail" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>

  <!-- Modal d'ajout d'utilisateur -->
  <div v-if=isAdding class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="CloseAdding">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
      <h3 class="text-lg font-bold mb-4 text-center">Ajouter une adresse email </h3>
      <div>
        <label for="user" class="block mb-2">Utilisateur</label>
        <input 
          id="user"
          v-model="UserToAdd"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="Jean-Christine Nomdefamille"
        />
        <label for="explication"  class="block mb-2">Permission</label>
        <select 
        id="permission"
        v-model="PermissionToAdd"
        class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
      >
        <option value="Utilisateur">Utilisateur</option>
        <option value="Administrateur">Administrateur</option>
      </select>
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button @click="CloseAdding" class="bg-red-500 text-white px-4 py-2 rounded">
          Annuler
        </button>
        <button @click="saveUserToAdd" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>

  </div>
  </template>
  
  <script>
export default {
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
      isAdding: false, // Gère l'affichage du modal d'ajout d'utilisateur
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
      console.log(this.selectedEmail.permission)
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
    confirmAdd() {
      this.isAdding = true;
    },
    CloseAdding() {
      this.isAdding=false;
    }
  },
  stopPropagation(event) {
    event.stopPropagation(); // Empêche la propagation du clic vers les parents
  },
};
</script>

  