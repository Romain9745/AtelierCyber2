
<template>
    <div class="flex flex-col items-center gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Statistiques du compte</h1>
      <PieChart :data="chartData" :title="title"/>
    </div>
</template>
  
  <script>
  import PieChart from "./PieChart.vue";
  
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