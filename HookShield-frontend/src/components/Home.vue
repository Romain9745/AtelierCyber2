<template>
  <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Emails Bloqués</h1>
      <SearchBar :data="tableData" @update:data="tableData = $event" />
    </div>
    
    <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />

        <MailDetail v-if="selectedEmail" :selectedEmail="selectedEmail" :email_body="email_body" @close="closeMailDetail" class="mt-8 p-4 bg-gray-200 dark:bg-gray-800 rounded-lg" />
        <!-- Deuxième tableau : Tickets -->
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white" @click="hideOrShowData('TicketTable')">Tickets</h1>
      </div>
      <Table class="TicketTable" :data="TicketData" :headers="headersTickets" @row-click="handleTicketClick"/>

      <TicketModal :selectedTicket="selectedTicket" :state=state v-if="selectedTicket" @close="selectedTicket = null"/>

    
  </div>
</template>

<script>
import Table from "@/components/commun/Table.vue";
import SearchBar from "./commun/SearchBar.vue";
import MailDetail from "./MailDetail.vue";
import TicketModal from "./commun/TicketModal.vue";
import axiosInstance from "@/AxiosInstance"; 

export default {
  components: {
    Table,
    SearchBar,
    MailDetail,
    TicketModal,
  },
  data() {
    return {
      tableData: [],
      headers: ['Destinataire', 'Expéditeur', 'Sujet', 'Raison'],
      selectedEmail: null,
      email_body: "",
      TicketData: [],
      headersTickets: ['Auteur', 'Etat', 'Créé le / Modifié le'],
      selectedTicket: null,
    };
  },
  mounted() {
    this.fetchBlockedEmails();

    axiosInstance.get('http://localhost:8000/tickets')
      .then(response => {
        this.TicketData = response.data.map(ticket => ({
          mail_address: ticket.user_mail,
          state: (ticket.state == 1) 
            ? 'En cours de vérification' 
            : (ticket.state == 2) 
              ? 'Modification approuvée' 
              : (ticket.state == 3) 
                ? 'Modification refusée' 
                : 'Etat inconnu',
          date: ticket.last_modification_at,

        }));
        console.log(this.TicketData);
      })
      .catch(error => {
        console.error("Error while fetching users:", error);
      });
  },
  methods: {
    async fetchBlockedEmails() {
      try {
        const response = await axiosInstance.get('/blocked_emails');
        this.tableData = response.data.map(email => ({
          recipient: email.recipient,
          sender: email.source,
          subject: email.subject,
          blockReason: email.explanation,
        }));
      } catch (error) {
        console.error("Erreur lors de la récupération des emails bloqués :", error);
      }
    },
    async handleRowClick(rowData) {
      this.selectedEmail = rowData;
      this.email_body = "";

      try {
        const response = await axiosInstance.get('/email_body', {
          params: {
            source: rowData.sender,
            recipient: rowData.recipient,
            subject: rowData.subject,
            explanation: rowData.blockReason,
          }
        });
        
        this.email_body = response.data.email_body; // Stocke le corps de l'email
        
      } catch (error) {
        console.error("Erreur lors de la récupération du corps de l'email :", error);
        if (error.response && error.response.status === 404) {
            console.log("Aucun corps d'email trouvé pour cette entrée.");
        } else {
          console.log("Une erreur s'est produite lors de la récupération du corps de l'email.");
        }
      }
    },
    async handleTicketClick(rowData) {
      this.state=3;
      if (rowData.state=="En cours de vérification") {
        this.state = 1;
      } else if (rowData.state=="Modification approuvée"){
        this.state = 2;
      }
      let mailData= await axiosInstance.get('/get_ticket_data', {
          params: {
            mail: rowData.mail_address,
            state: this.state,
            user_explanation: rowData.user_explanation,
            date: rowData.date,
          },
        });
      this.selectedTicket=mailData.data
      console.log(this.selectedTicket)
    },
    closeMailDetail() {
      this.selectedEmail = null;
      this.email_body = "";
    }
  },
  
};
</script>