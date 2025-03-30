<script setup>
import Sidebar from "@/components/commun/Sidebar.vue";
import Navbar from "./components/commun/NavBar.vue";
import { RouterView, useRoute } from 'vue-router';
import { ref } from 'vue';
import { useAuthStore } from './store/auth';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const isAuthChecked = ref(false);


onMounted(async () => {
  console.log("Checking authentication...");
  
  try {
    await authStore.checkAuth();
    console.log("Auth checked. User authenticated:", authStore.isAuthenticated);
  } catch (error) {
    console.error("Error during authentication check:", error);
  } finally {
    isAuthChecked.value = true;
    console.log("Authentication check complete. Rendering app.");
  }
});

const route = useRoute();
const isSideBarVisible = ref(true);
</script>

<template>
  <div v-if="isAuthChecked" :class="route.path === '/login' ? 'flex justify-center items-center h-screen bg-gray-100' : 'grid grid-rows-[auto_1fr] h-screen overflow-hidden'">
    <!-- Navbar -->
    <header v-if="route.path !== '/login'" class="shadow-md z-50">
      <Navbar />
    </header>

    <main :class="route.path === '/login' ? 'flex justify-center items-center h-screen bg-gray-100' : 'grid grid-cols-[auto_1fr] h-full overflow-hidden bg-gray-100'">
      
       <div v-if="route.path !== '/login' && !isSideBarVisible" class="flex p-4 shadow-md z-50">
      <button 
        @click="isSideBarVisible = true" 
        class="p-2 h-[10vh] bg-white rounded-full shadow-md z-50 transition-all"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
        </svg>
      </button>
    </div>

      <div v-if="route.path !== '/login' && isSideBarVisible" class="bg-sidebar h-full overflow-y-auto shadow-md w-[250px] transition-all">
        <Sidebar @close="isSideBarVisible = false" />
      </div>

        <RouterView />
      
    </main>
  </div>
</template>
