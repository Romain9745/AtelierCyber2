<script setup>
import Sidebar from "@/components/commun/Sidebar.vue";
import Navbar from "./components/commun/NavBar.vue";
import { RouterView, useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <div v-bind:class="[route.path === '/login' ? 'login_layout' : 'layout']">
    <header v-if="route.path !== '/login'">
      <Navbar />
    </header>
    <main v-bind:class="[route.path === '/login' ? 'login_layout' : 'main']">
      <div class="sidebar" v-if="route.path !== '/login'">
        <Sidebar />
      </div>
      <div class="content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  grid-template-rows: auto 1fr;
  grid-template-columns: 1fr;
  height: 100vh;
  overflow: hidden;
}

.login_layout {
  display: flex;
  justify-content: center;
  align-items: center; 
  height: 100vh; 
  background-color: #f4f4f4; 
}

header {
  height: 80px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

.main {
  display: grid;
  grid-template-columns: 250px 1fr;
  height: 100%;
  overflow: hidden;
  background-color: #f4f4f4;
}

.sidebar {
  background: var(--color-sidebar-bg);
  height: 100%;
  overflow-y: auto;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.content {
  overflow-y: auto;
  padding: 10px;
}
</style>