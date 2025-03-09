<template>
  <!-- Modal d'ajout d'utilisateur -->
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="CloseAdding">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3" @click="stopPropagation">
      <h3 class="text-lg font-bold mb-4 text-center">Ajouter un utilisateur</h3>

      <!-- Email -->
      <div>
        <label for="email" class="block mb-2">Email</label>
        <input 
          id="email"
          v-model="UserToAdd.email"
          type="email"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="exemple@email.com"
        />
      </div>

      <!-- Prénom -->
      <div>
        <label for="first_name" class="block mb-2">Prénom</label>
        <input 
          id="first_name"
          v-model="UserToAdd.first_name"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="Jean"
        />
      </div>

      <!-- Nom -->
      <div>
        <label for="last_name" class="block mb-2">Nom</label>
        <input 
          id="last_name"
          v-model="UserToAdd.last_name"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="Dupont"
        />
      </div>

      <!-- Nom d'utilisateur -->
      <div>
        <label for="username" class="block mb-2">Nom d'utilisateur</label>
        <input 
          id="username"
          v-model="UserToAdd.username"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="jean.dupont"
        />
      </div>

      <!-- Mot de passe -->
      <div>
        <label for="password" class="block mb-2">Mot de passe</label>
        <input 
          id="password"
          v-model="UserToAdd.password"
          type="password"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="********"
        />
      </div>

      <!-- Confirmation du mot de passe -->
      <div>
        <label for="confirm_password" class="block mb-2">Confirmer le mot de passe</label>
        <input 
          id="confirm_password"
          v-model="confirmPassword"
          type="password"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          placeholder="********"
        />
      </div>

      <!-- Permission -->
      <div>
        <label for="permission" class="block mb-2">Permission</label>
        <select 
          id="permission"
          v-model="permission"
          class="w-full px-4 py-2 border border-gray-300 rounded mb-4"
        >
          <option value="Utilisateur">Utilisateur</option>
          <option value="Administrateur">Administrateur</option>
        </select>
      </div>

      <!-- Boutons -->
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
</template>

<script>
export default {
  data() {
    return {
      UserToAdd: {
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        password: '',
        role: 2
      },
      confirmPassword: '',
      permission: 'Utilisateur'
    };
  },
  methods: {
    CloseAdding() {
      this.$emit("close"); // Émettre un événement pour fermer le modal
      this.resetForm();
    },
    stopPropagation(event) {
      event.stopPropagation();
    },
    saveUserToAdd() {
      if (!this.UserToAdd.email.trim() || !this.UserToAdd.first_name.trim() || !this.UserToAdd.last_name.trim() || !this.UserToAdd.password.trim() || !this.confirmPassword.trim() || !this.UserToAdd.username.trim()) { 
        alert("Veuillez remplir tous les champs.");
        return;
      }

      if (this.UserToAdd.password !== this.confirmPassword) {
        alert("Les mots de passe ne correspondent pas.");
        return;
      }

      if (this.UserToAdd.password.length < 8) {
        alert("Le mot de passe doit contenir au moins 8 caractères.");
        return;
      }

      if (this.permission === 'Administrateur') {
        this.UserToAdd.role_id = 1;
      } else {
        this.UserToAdd.role_id = 2;
      }

      // Émettre l'utilisateur ajouté au composant parent
      this.$emit('user-added', { ...this.UserToAdd });

      // Réinitialiser le formulaire et fermer
      this.CloseAdding();
    },
    resetForm() {
      this.UserToAdd = {
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        password: '',
        role: 2
      };
      this.confirmPassword = '';
      this.permission = 'Utilisateur';
    }
  }
};
</script>
