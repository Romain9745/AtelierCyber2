<template>
  <header class="h-[10vh] bg-blue-600 text-white p-4 flex justify-between items-center">
    <img class="h-full mr-2" src="/HookShield_logo.svg" alt="logo">

    <div class="flex items-center gap-3">
      <div class="h-full flex flex-col items-center">
        <img
          :src="avatarUrl"
          class="rounded-full w-10 h-10 mb-2"
          alt="Avatar"
        />
        <span>{{ authStore.email }}</span> <!-- Dynamically display username -->
      </div>
      <button class="h-full px-4 py-2 bg-red-500 rounded hover:bg-red-600" @click="handleLogout">
        Déconnexion
      </button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'; 

const authStore = useAuthStore();


const avatarUrl = "https://images.pexels.com/photos/2071882/pexels-photo-2071882.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"; 

const handleLogout = () => {
  authStore.logout();  // Call the logout action from the auth store
};
</script>

