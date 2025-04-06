<template>
  <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Emails Bloqués</h1>
      <SearchBar :data="tableData" @update:data="tableData = $event" />
    </div>
    
    <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />

<!-- Modal du détail du mail 
    <div v-if="selectedEmail" class="mt-8 p-4 bg-gray-200 dark:bg-gray-800 rounded-lg">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Aperçu du Mail</h2>
      <div class="mt-4">
        <p><strong>Destinataire:</strong> {{ selectedEmail.recipient }}</p>
        <p><strong>Expéditeur:</strong> {{ selectedEmail.sender }}</p>
        <p><strong>Sujet:</strong> {{ selectedEmail.subject }}</p>
        <p><strong>Raison du blocage:</strong> {{ selectedEmail.blockReason }}</p> 
        </div>
        </div> -->
        <MailDetail v-if="selectedEmail" :selectedEmail="selectedEmail" :email_body="email_body" @close="closeMailDetail" class="mt-8 p-4 bg-gray-200 dark:bg-gray-800 rounded-lg" />
      
    
  </div>
</template>

<script>
import Table from "@/components/commun/Table.vue";
import SearchBar from "./commun/SearchBar.vue";
import MailDetail from "./MailDetail.vue";
import axiosInstance from "@/AxiosInstance";import { useAuthStore } from '@/store/auth'; 

export default {
  components: {
    Table,
    SearchBar,
    MailDetail,
  },
  data() {
    return {
      tableData: [],
      headers: ['Destinataire', 'Expéditeur', 'Sujet', 'Raison'],
      selectedEmail: null,
      email_body: "",
    };
  },
  mounted() {
    this.fetchBlockedEmails();
  },
  methods: {
    async fetchBlockedEmails() {
      try {
        const authStore = useAuthStore();
        console.log(authStore.email)
        const response = await axiosInstance.get('/blocked_emails', {params: {mail: authStore.email,},});
        console.log("The answer is "+response.data.subject);
        this.tableData = response.data.map(email => ({
          recipient: email.recipient,
          sender: email.source,
          subject: email.subject,
          blockReason: email.explanation,
        }));
        console.log("the table is ", this.tableData)
      } catch (error) {
        console.error("Erreur lors de la récupération des emails bloqués :", error);
      }
    },
    async handleRowClick(rowData) {
      console.log("Données de la ligne sélectionnée :", rowData);
      this.selectedEmail = rowData;
      this.email_body = ""; // Réinitialise le corps de l'email

      try {
        const response = await axiosInstance.get('/email_body', {
          params: {
            source: rowData.sender,
            recipient: rowData.recipient,
            subject: rowData.subject,
            explanation: rowData.blockReason,
          }
        });
        
        console.log("Corps de l'email récupéré :", response.data.email_body);
        this.email_body = response.data.email_body; // Stocke le corps de l'email
        
      } catch (error) {
        console.error("Erreur lors de la récupération du corps de l'email :", error);
        if (error.response && error.response.status === 404) {
            alert("Aucun corps d'email trouvé pour cette entrée.");
        } else {
            alert("Une erreur s'est produite lors de la récupération du corps de l'email.");
        }
      }
    },
    closeMailDetail() {
      this.selectedEmail = null;
      this.email_body = "";
    }
  },
  
};
</script>