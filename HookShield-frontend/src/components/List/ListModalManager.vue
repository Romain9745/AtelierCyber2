<template>
    <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
      <div class="flex flex-col gap-6 bg-white p-6 rounded-lg shadow-lg w-1/3 transform translate-y-8" @click.self="deselectRow">
        <h2 class="text-lg font-bold mb-4 text-center">Adresses email</h2>
        <button 
            @click="confirmAdd" 
            class="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Ajouter
          </button>
        <div style="overflow: auto; max-height: 300px; border: 1px solid gray;">
        <table class="w-full border-collapse border border-gray-300 ">
          <thead>
            <tr class="bg-gray-100">
              <th class="border border-gray-300 px-4 py-2 text-left">Email</th>
              <th class="border border-gray-300 px-4 py-2 text-left">Explication</th>
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
        </div>
        <div class="mt-4 flex gap-2 justify-end">
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
          <button 
            @click="closeModal" 
            class="bg-red-500 text-white px-4 py-2 rounded"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  
    <!-- Modal de confirmation -->
    <div v-if="isConfirming" class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);">
      <ConfirmationModal 
        question="Êtes-vous sûr de vouloir supprimer cet email ?"
        @close="isConfirming = false"
        @delete="deleteEmail"/>
    </div>

     <!-- Modal d'édition -->
  <div v-if="isEditing" class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click="CloseEditing">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
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
      <div class="mt-4 flex justify-end gap-2">
        <button @click="CloseEditing" class="bg-red-500 text-white px-4 py-2 rounded">
          Annuler
        </button>
        <button @click="saveEmail" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>

  <!-- Modal d'ajout de mail -->
  <div v-if=isAdding class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click="CloseAdding">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
      <h3 class="text-lg font-bold mb-4 text-center">Ajouter une adresse email </h3>
      <div>
        <label for="emailadress" class="block mb-2">Adresse Email</label>
        <input 
          id="email"
          v-model="EmailAdressToAdd"
          type="email"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          :placeholder="listname === 'Whitelist' ? 'adresse@mail.com' : 'fraude@maiI.com'"
        />
        <label for="explication"  class="block mb-2">Explication</label>
        <input 
          id="explication"
          v-model="ExplicationToAdd"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          :placeholder="listname === 'Whitelist' ? 'non spam, mal classé...' : 'Fraude, scam, spam...'"
        />
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button @click="CloseAdding" class="bg-red-500 text-white px-4 py-2 rounded">
          Annuler
        </button>
        <button @click="saveEmailToAdd" class="bg-blue-500 text-white px-4 py-2 rounded">
          Sauvegarder
        </button>
      </div>
    </div>
  </div>
  <div></div>

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
    listname: {
    type: String,
    required: true,
    },
  },
  data() {
    return {
      selectedEmail: null,
      isConfirming: false,
      isEditing: false, // Gère l'affichage du modal d'édition
      emailToEdit: null, // Garde l'email sélectionné pour l'édition
      isAdding: false, // Gère l'affichage du modal d'ajout
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
    confirmAdd() {
      this.isAdding = true;
    },
    confirmDelete() {
      this.isConfirming = true; // Affiche le modal de confirmation
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
    CloseAdding() {
      this.isAdding=false;
    },
    stopPropagation(event) {
    event.stopPropagation(); // Empêche la propagation du clic vers les parents
    },
    saveEmailToAdd() {
      const newEntry = {
        email: this.EmailAdressToAdd,
        reason: this.ExplicationToAdd,
      };

      if (this.listname === 'Blacklist') {
        this.addToBlacklist(newEntry);
      } else if (this.listname === 'Whitelist') {
        this.addToWhitelist(newEntry);
      } else if (this.listname === 'Blacklist Perso') {
        this.addTouserBlacklist(newEntry);
      }

      // Réinitialise les champs de saisie et ferme le modal
      this.EmailAdressToAdd = '';
      this.ExplicationToAdd = '';
      this.CloseAdding();
    },
    async addToBlacklist(entry) {
      try {
        const response = await fetch('http://localhost:8000/main_blacklist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(entry),
        });

        if (!response.ok) {
          throw new Error('Erreur lors de l\'ajout à la blacklist');
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async addToWhitelist(entry) {
      try {
        const response = await fetch('http://localhost:8000/whitelist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(entry),
        });

        if (!response.ok) {
          throw new Error('Erreur lors de l\'ajout à la whitelist');
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async addTouserBlacklist(entry) {
      try {
        const response = await fetch('http://localhost:8000/user_blacklist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(entry),
        });

        if (!response.ok) {
          throw new Error('Erreur lors de l\'ajout à la blacklist');
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async deleteEmail() {
      try {
        let endpoint = '';
        if (this.listname === 'Blacklist') {
            endpoint = 'http://localhost:8000/main_blacklist';
        } else if (this.listname === 'Whitelist') {
            endpoint = 'http://localhost:8000/whitelist';
        } else if (this.listname === 'Blacklist Perso') {
            endpoint = 'http://localhost:8000/user_blacklist';
        }
        const response = await fetch(`${endpoint}?email=${encodeURIComponent(this.selectedEmail.address)}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error('Erreur lors de la suppression de l\'email');
        }
        
        // Mets à jour la liste après la suppression
        this.fetchList();

        // Ferme le modal et réinitialise l'email sélectionné
        this.isConfirming = false;
        this.selectedEmail = '';
      } catch (error) {
        console.error(error.message);
      }
      this.$emit("delete", this.selectedEmail);
      this.selectedEmail = null;
      this.isConfirming = false;
    },

    async fetchList() {
      try {
        let endpoint = '';
        if (this.listname === 'Blacklist') {
            endpoint = 'http://localhost:8000/main_blacklist';
        } else if (this.listname === 'Whitelist') {
            endpoint = 'http://localhost:8000/whitelist';
        } else if (this.listname === 'Blacklist Perso') {
            endpoint = 'http://localhost:8000/user_blacklist';
        }        const response = await fetch(endpoint);

        if (!response.ok) {
          throw new Error('Erreur lors de la récupération de la liste');
        }

        const data = await response.json();
        if (this.listname === 'Blacklist') {
          this.blacklist = data.map(item => ({ address: item.email, description: item.reason }));
        } else if (this.listname === 'Whitelist') {
          this.whitelist = data.map(item => ({ address: item.email, description: item.reason }));
        }
      } catch (error) {
        console.error(error.message);
      }
    },
  },
};
</script>

  