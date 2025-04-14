<template>
    <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
      <div class="flex flex-col gap-6 bg-white p-6 rounded-lg shadow-lg w-1/3 transform translate-y-8" @click.self="deselectRow">
        <h2 class="text-lg font-bold mb-4 text-center">Adresses email</h2>
        <button 
            v-if="canEdit"
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
            <tr v-if="emails.length === 0">
              <td class="border border-gray-300 px-4 py-2 text-center" colspan="2">Aucun email</td>
            </tr>
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
            v-if="canEdit"
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

  </template>
  
  <script>
import ConfirmationModal from "@/components/commun/ConfirmationModal.vue";
import { useAuthStore } from "@/store/auth.js";
import axiosInstance from "@/AxiosInstance";

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
      emailToEdit: null, // Garde l'email sélectionné pour l'édition
      isAdding: false, // Gère l'affichage du modal d'ajout
    };
  },
  computed: {
    authStore() {
      return useAuthStore();
    },
    canEdit() {
      // Autoriser l'édition si le rôle est 2 ou si listname est "Blacklist Perso"
      return this.authStore.role === "Admin" || this.listname === "Blacklist Perso";
    }
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },
    selectRow(email) {
      this.selectedEmail = email;
      console.log(this.authStore.role)
    },
    deselectRow() {
      this.selectedEmail = null;
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
        user_email: this.authStore.email
      };

      if (this.listname === 'Blacklist') {
        this.addToBlacklist(newEntry);
      } else if (this.listname === 'Whitelist') {
        this.addToWhitelist(newEntry);
      } else if (this.listname === 'Blacklist Perso') {
        console.log(this.authStore.id);
        this.addTouserBlacklist(newEntry);
      }

      // Réinitialise les champs de saisie et ferme le modal
      this.EmailAdressToAdd = '';
      this.ExplicationToAdd = '';
      this.CloseAdding();
    },
    async addToBlacklist(entry) {
      try {
        const response = await axiosInstance.post('/main_blacklist', entry);
        if (!response.status === 200) {
          throw new Error('Erreur lors de l\'ajout à la blacklist');
        }
        else
        {
          this.emails.push({
            address: entry.email,
            description: entry.reason
          });
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async addToWhitelist(entry) {
      try {
        const response = await axiosInstance.post('/whitelist', entry);
        if (!response.status === 200) {
          throw new Error('Erreur lors de l\'ajout à la whitelist');
        }
        else
        {
          this.emails.push({
            address: entry.email,
            description: entry.reason
          });
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async addTouserBlacklist(entry) {
      try {
        const response = await axiosInstance.post('/user_blacklist', entry);
        if (!response.status === 200) {
          throw new Error('Erreur lors de l\'ajout à la blacklist');
        }
        else
        {
          this.emails.push({
            address: entry.email,
            description: entry.reason
          });
        }

      } catch (error) {
        console.error(error.message);
      }
    },
    async deleteEmail() {
      try {
        let endpoint = '';
        if (this.listname === 'Blacklist') {
            endpoint = '/blacklist';
        } else if (this.listname === 'Whitelist') {
            endpoint = '/whitelist';
        } else if (this.listname === 'Blacklist Perso') {
            endpoint = '/user_blacklist';
        }
        const response = await axiosInstance.delete(`${endpoint}?email=${encodeURIComponent(this.selectedEmail.address)}`)
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

    
  },
};
</script>

  