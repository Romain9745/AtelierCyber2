<template>
    <div class="flex flex-col items-center justify-center bg-gray-100 p-4 h-full rounded-lg shadow-md gap-2">
        <h1 class="text-lg font-semibold text-gray-800 mb-4 text-center mb-4">Statistiques du compte</h1>
      <PieChart :data="chartData" :title="title"/>
    </div>
  </template>
  
  <script>
  import PieChart from "../components/PieChart.vue";
  
  export default {
    components: {
      PieChart,
    },
    data() {
      return {
        chartData: [
          { label: "Mails Phishing", value: 30 },
          { label: "Mails Non-Phising", value: 700 },
        ],
        title: "Répartition des mails",
      };
    },
  };
  </script>