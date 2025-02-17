
<template>
<div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3">
      <h3 class="text-lg font-bold mb-4 text-center">Éditer </h3>
      <div>
        <label for="emailadress" class="block mb-2">Adresse Email</label>
        <input 
          id="email"
          v-model="EmailAdressToEdit"
          type="email"
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
export default {
  props: {
    emailToEdit: {
      type: String,
      required: true
    }
  },
  data() {
    return {
    EmailAdressToEdit: this.emailToEdit }
  },
  methods: {
    CloseEditing() {
      this.$emit('close');
    },
    saveEmail() {
      this.$emit('save', this.EmailAdressToEdit);
    }
  }
}

</script>