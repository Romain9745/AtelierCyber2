

<template>
<div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white p-4 rounded-lg shadow-lg w-1/4">
      <h3 class="text-lg font-bold mb-2">Confirmer la suppression</h3>
      <p>{{ question }}</p>
      <div class="mt-4 flex justify-end space-x-2">
        <button @click="close" class="bg-gray-400 text-white px-4 py-2 rounded">
          Non
        </button>
        <button @click="deleteObject" class="bg-red-500 text-white px-4 py-2 rounded">
          Oui
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    props: {
        question: {
        type: String,
        required: true
        }
    },
    methods: {
      deleteObject() {
      this.$emit('delete');
    },
    close() {
      this.$emit('close');
    }
  }
}
</script>

