<template>
  <div class="flex flex-col items-center gap-8 w-full h-full p-8 bg-gray-100 dark:bg-gray-900 overflow-auto">
    <div class="flex flex-col items-center w-full max-w-3xl p-6 rounded-xl shadow-lg gap-3 transition-all duration-300" :class="{'bg-gray-800': !isDarkMode, 'bg-gray-900': isDarkMode}">
      <h1 class="text-3xl font-bold text-white">Statistiques du compte</h1>
      
      <!-- Affichage des statistiques personnelles -->
      <PieChart :data="chartData" :title="title" class="bg-white  transition-all duration-300" />
    </div>

    <!-- Section Admin -->
    <div v-if="authStore.role === 'Admin'" class="flex flex-col items-center w-full max-w-5xl p-6 rounded-xl shadow-lg mt-8 gap-3 transition-all duration-300" :class="{'bg-gray-800': !isDarkMode, 'bg-gray-900': isDarkMode}">
      <h2 class="text-2xl font-semibold text-white mb-6">Statistiques globales</h2>

      <!-- Statistiques globales -->
      <div v-if="globalStats" class="flex p-6 items-center justify-center gap-3 shadow-lg rounded-lg w-full transition-all duration-300" :class="{'bg-white': !isDarkMode, 'bg-gray-800': isDarkMode}">

<PieChart :data="totalStats" :title="title2" class="rounded-lg shadow-lg bg-white transition-all duration-300" />

<div class="flex flex-col gap-4 items-center"> <!-- Ajout de `items-center` pour centrer horizontalement -->
  <div class="flex items-center gap-4">
    <span class="text-xl font-semibold text-gray-900 dark:text-white">Nombre total d'utilisateurs : </span>
    <span class="text-xl font-semibold text-green-500">{{ globalStats.total_users }}</span>
  </div>
  
  <div class="flex items-center gap-4">
    <span class="text-xl font-semibold text-gray-900 dark:text-white">Nombre de faux négatif : </span>
    <span class="text-xl font-semibold text-red-500">{{ globalStats.total_false_negative }}</span>
  </div>
  
  <div class="flex items-center gap-4">
    <span class="text-xl font-semibold text-gray-900 dark:text-white">Nombre de fichiers scannés : </span>
    <span class="text-xl font-semibold text-green-500">{{ globalStats.total_files_scanned }}</span>
  </div>
</div>
</div>


      <!-- Recherche des stats d'un utilisateur -->
      <h2 class="text-2xl font-semibold text-white mb-4">Rechercher un utilisateur</h2>
      <div class="mt-6 w-full flex gap-4">
        
        <!-- Input Field taking 3/4 of the width -->
        <input  
          v-model="searchEmail" 
          @keyup.enter="fetchUserStats" 
          type="text" 
          placeholder="Rechercher un utilisateur par email..." 
          class="flex-3/4 p-3 border border-gray-300 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all duration-300"
        />
        
        <!-- Button taking 1/4 of the width -->
        <button 
          @click="fetchUserStats" 
          class="w-1/4 mt-4 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg shadow-lg transition-all duration-300"
        >
          Rechercher
        </button>
      </div>
      <!-- Résultats de la recherche -->
      <div v-if="userStats" class="mt-8 flex flex-col items-center w-full">
        <h3 class="text-xl font-semibold text-white mb-4">{{ title3 }}</h3>
        <PieChart v-if="userStats" :data="userStats" :title="title3" class="mt-6 rounded-lg shadow-lg bg-white transition-all duration-300" />
      </div>
    </div>
  </div>
</template>

<script>
import PieChart from "./PieChart.vue";
import { useAuthStore } from '@/store/auth'; 
import axiosInstance from "@/AxiosInstance";

export default {
  components: { PieChart },
  data() {
    return {
      authStore: useAuthStore(),
      chartData: [],
      title: "Répartition des mails",
      title2: "Répartion globale des mails",
      title3: "",
      totalStats: [],
      globalStats: null,
      userStats: [],
      searchEmail: "",
      isDarkMode: false, // Variable to track dark mode
    };
  },
  methods: {
    async fetchData() {
      try {
        if (this.authStore.role === "Admin") {
          const response = await axiosInstance.get('/stats');
          this.globalStats = response.data.global_stats;
          console.log(this.globalStats);
          this.totalStats = [
            { label: "Mails Phishing", value: this.globalStats.total_mails_blocked},
            {label: "Mails Non-Phishing", value: this.globalStats.total_mail_authentic}
          ]
        }
        const response = await axiosInstance.get('/stats/me');
        this.chartData = [
          { label: "Mails Phishing", value: response.data.mail_blocked },
          { label: "Mails Non-Phishing", value: response.data.mail_authentic },
        ];
        console.log(this.chartData);
      } catch (error) {
        console.error("Erreur lors de la récupération des statistiques :", error);
      }
    },
    async fetchUserStats() {
      if (!this.searchEmail) return;
      try {
        const response = await axiosInstance.get(`/stats/user/${this.searchEmail}`);
        this.userStats = [
          { label: "Mails Phishing", value: response.data.mail_blocked },
          { label: "Mails Non-Phishing", value: response.data.mail_authentic },
        ];
        this.title3 = `Répartition des mails de ${this.searchEmail}`;
      } catch (error) {
        console.error("Erreur lors de la recherche des stats utilisateur :", error);
      }
    }
  },
  mounted() {
    this.fetchData();
  }
};
</script>

