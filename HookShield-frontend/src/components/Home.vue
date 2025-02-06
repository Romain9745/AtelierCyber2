<template>
  <div class="flex flex-col gap-3  h-full p-8 bg-gray-100 dark:bg-gray-900 ">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Emails Bloqués</h1>
      <SearchBar :data="tableData" @update:data="tableData = $event" />
    </div>
    
    <Table :data="tableData" :headers="headers" @row-click="handleRowClick" />

    <div v-if="selectedEmail" class="mt-8 p-4 bg-gray-200 dark:bg-gray-800 rounded-lg">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Aperçu du Mail</h2>
      <div class="mt-4">
        <p><strong>Destinataire:</strong> {{ selectedEmail.recipient }}</p>
        <p><strong>Expéditeur:</strong> {{ selectedEmail.sender }}</p>
        <p><strong>Sujet:</strong> {{ selectedEmail.subject }}</p>
        <p><strong>Raison du blocage:</strong> {{ selectedEmail.blockReason }}</p>
      </div>
      </div>

    </div>
</template>

<script>
import Table from "@/components/Table.vue";
import SearchBar from "./SearchBar.vue";

export default {
  components: {
    Table,
    SearchBar,
  },
  data() {
    return {
      tableData: [
        { recipient: 'alice@example.com', sender: 'bob@example.com', subject: 'Suspicious Activity', blockReason: 'Spam' },
        { recipient: 'charlie@example.com', sender: 'diana@example.com', subject: 'Marketing Update', blockReason: 'Phishing' },
        { recipient: 'eve@example.com', sender: 'alice@example.com', subject: 'Important Notice', blockReason: 'Spam' },
        { recipient: 'frank@example.com', sender: 'bob@example.com', subject: 'Account Suspended', blockReason: 'Malware' },
      ],
      headers: ['recipient', 'sender', 'subject', 'blockReason'],
      selectedEmail: null,
    };
  },
  methods: {
    handleRowClick(rowData) {
      this.selectedEmail = rowData;
    },
  },
};
</script>