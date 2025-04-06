<template>
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
    <!-- Boîte de détails du mail -->
  <div
    v-if="selectedTicket"
    style="
      background-color: white;
      border-radius: 16px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      padding: 24px;
      width: 100%;
      max-width: 480px;
      transform: translateY(0);
      transition: all 0.3s ease;
      border: 1px solid #e5e7eb;
      /* Ajout de hauteur maximale et défilement */
      max-height: 90vh;
      overflow-y: auto;
    "
    :class="{ 'dark-mode': isDarkMode, 'custom-scrollbar': true }"
  >
    <!-- En-tête avec bouton de fermeture -->
    <div style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 2px solid #f3f4f6;
      position: sticky;
      top: 0;
      background-color: white;
      z-index: 10;
    " :class="{ 'dark-mode-header': isDarkMode }">
      <h2 style="
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
        display: flex;
        align-items: center;
      ">
        <i class="fas fa-envelope" style="margin-right: 10px;"></i>
        Détails du Mail
      </h2>
      <button
        @click="closeModal"
        @mouseover="handleMouseOver"
        @mouseout="handleMouseOut"
        style="
          background: transparent;
          border: none;
          cursor: pointer;
          font-size: 1.5rem;
          color: #ef4444;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        "
        title="Fermer"
      >
        <i class="fas fa-times">x</i>
      </button>
    </div>

    <!-- Contenu détaillé du mail -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <span style="font-weight: 600; color: #1f2937; min-width: 70px;">De :</span>
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedTicket.source }}</span>
      </div>
      
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <span style="font-weight: 600; color: #1f2937; min-width: 70px;">À :</span>
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedTicket.recipient }}</span>
      </div>
      
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <span style="font-weight: 600; color: #1f2937; min-width: 70px;">Objet :</span>
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedTicket.subject }}</span>
      </div>
      
      <div style="margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 16px;">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
          <span style="font-weight: 600; color: #1f2937; min-width: 70px;">Contenu :</span>
        </div>
        <div style="
          background-color: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          max-height: 200px;
          overflow-y: auto;
          font-size: 0.95rem;
          line-height: 1.6;
          margin-top: 8px;
          color: #1f2937;
        " class="custom-scrollbar">
          {{ selectedTicket.email_body }}
        </div>
      </div>

      <div style="margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 16px;">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
          <span style="font-weight: 600; color: #1f2937; min-width: 70px;">Explication du blocage :</span>
        </div>
        <div style="
          background-color: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          max-height: 200px;
          overflow-y: auto;
          font-size: 0.95rem;
          line-height: 1.6;
          margin-top: 8px;
          color: #1f2937;
        " class="custom-scrollbar">
          {{ selectedTicket.explanation }}
        </div>
      </div>

      <div style="margin-top: 16px; border-top: 1px solid #e5e7eb; padding-top: 16px;">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
          <span style="font-weight: 600; color: #1f2937; min-width: 70px;">Explication de l'utilisateur :</span>
        </div>
        <div style="
          background-color: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 16px;
          max-height: 200px;
          overflow-y: auto;
          font-size: 0.95rem;
          line-height: 1.6;
          margin-top: 8px;
          color: #1f2937;
        " class="custom-scrollbar">
          {{ selectedTicket.user_explanation }}
      </div>
    </div>

    <div style="
      margin-top: 24px; 
      display: flex; 
      flex-direction: column; 
      gap: 12px;
      position: sticky;
      bottom: 0;
      background-color: white;
      padding-top: 16px;
      z-index: 10;
    " :class="{ 'dark-mode-footer': isDarkMode }">
      <button 
        v-if="state==1"
        @click="accept"
        @mouseover="handlePrimaryBtnHover"
        @mouseout="handlePrimaryBtnOut"
        style="
          font-weight: 600;
          padding: 12px;
          border-radius: 8px;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          background-color: #4f46e5;
          color: white;
        "
      >
        <i class="fas fa-shield-alt"></i>
        Accepter la demande
      </button>
      
      <button
        v-if="state==1"
        @click="refuse"
        @mouseover="handleDangerBtnHover"
        @mouseout="handleDangerBtnOut"
        style="
          font-weight: 600;
          padding: 12px;
          border-radius: 8px;
          border: none;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          background-color: #ef4444;
          color: white;
        "
      >
        <i class="fas fa-times"></i>
        Rejeter la demande
      </button>

    </div>
  </div>
  </div>
  </div>
</template>

<script>
import axiosInstance from "@/AxiosInstance";

export default {
  props: {
    selectedTicket: Object,
    email_body: String,
    state: Number,
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  mounted() {
    console.log("Selected ticket in modal:", this.selectedTicket);
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },
    async accept() {
      try {
        const uid = await axiosInstance.get('/email_uid', {
          params: {
            source: this.selectedTicket.source,
            recipient: this.selectedTicket.recipient,
            subject: this.selectedTicket.subject,
            explanation: this.selectedTicket.explanation,
          },
        });

        const response = await axiosInstance.post('/admin/ticket_state', {
          mail_uid: uid.data.email_uid,
          state: 2,
          last_modification_at: new Date().toISOString(),
        });
        this.$emit('close');
      } catch (error) {
        console.error(error.message);
      }
      this.$emit('close');
    },
    async refuse() {
      try {
        const uid = await axiosInstance.get('/email_uid', {
          params: {
            source: this.selectedTicket.source,
            recipient: this.selectedTicket.recipient,
            subject: this.selectedTicket.subject,
            explanation: this.selectedTicket.explanation,
          },
        });

        const response = await axiosInstance.post('/admin/ticket_state', {
          mail_uid: uid.data.email_uid,
          state: 3,
          last_modification_at: new Date().toISOString(),
        })
      } catch (error) {
        console.error(error.message);
      }
      this.$emit('close');
    },
    handleMouseOver(e) {
      e.target.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
      e.target.style.color = '#ef4444';
    },
    handleMouseOut(e) {
      e.target.style.backgroundColor = 'transparent';
      e.target.style.color = '#6b7280';
    },
    handlePrimaryBtnHover(e) {
      e.target.style.backgroundColor = '#4338ca';
    },
    handlePrimaryBtnOut(e) {
      e.target.style.backgroundColor = '#4f46e5';
    },
    handleDangerBtnHover(e) {
      e.target.style.backgroundColor = '#dc2626';
    },
    handleDangerBtnOut(e) {
      e.target.style.backgroundColor = '#ef4444';
    }
  }
}
</script>


<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dark-mode {
  background-color: #1e293b !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
}

.dark-mode-header, .dark-mode-footer {
  background-color: #1e293b !important;
}

.dark-mode h2 {
  color: #f9fafb !important;
}

.dark-mode span[style*="font-weight: 600"] {
  color: #e5e7eb !important;
}

.dark-mode span[style*="color: #4b5563"] {
  color: #d1d5db !important;
}

.dark-mode div[style*="background-color: #f3f4f6"] {
  background-color: #374151 !important;
  border-color: #4b5563 !important;
  color: #e5e7eb !important;
}

.dark-mode div[style*="border-bottom: 2px solid #f3f4f6"] {
  border-bottom-color: #4b5563 !important;
}

.dark-mode div[style*="border-top: 1px solid #e5e7eb"] {
  border-top-color: #4b5563 !important;
}

.dark-mode .custom-scrollbar::-webkit-scrollbar-track {
  background: #374151;
}

.dark-mode .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.dark-mode .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>