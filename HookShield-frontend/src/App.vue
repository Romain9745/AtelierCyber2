<script setup>
import Sidebar from "@/components/Sidebar.vue";
import Navbar from "./components/Navbar.vue";
import { RouterView } from 'vue-router';
</script>

<template>
  <div class="layout">
    <header>
      <Navbar />
    </header>
    <main>
      <div class="sidebar">
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
  height: 100vh;
  overflow: hidden;
}

header {
  height: 80px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

main {
  display: grid;
  grid-template-columns: 250px 1fr;
  height: 100%;
  overflow: hidden;
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