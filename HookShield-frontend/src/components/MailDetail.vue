<template>
  <div class="fixed inset-0 flex items-center justify-center" style="background-color: rgba(0, 0, 0, 0.5);" @click.self="closeModal">
    <!-- Boîte de détails du mail -->
  <div
    v-if="selectedEmail"
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
    "
    :class="{ 'dark-mode': isDarkMode }"
  >
    <!-- En-tête avec bouton de fermeture -->
    <div style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 2px solid #f3f4f6;
    ">
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
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedEmail.sender }}</span>
      </div>
      
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <span style="font-weight: 600; color: #1f2937; min-width: 70px;">À :</span>
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedEmail.recipient }}</span>
      </div>
      
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <span style="font-weight: 600; color: #1f2937; min-width: 70px;">Objet :</span>
        <span style="color: #4b5563; word-break: break-word; flex: 1;">{{ selectedEmail.subject }}</span>
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
        ">
          {{ email_body }}
        </div>
      </div>
    </div>

    <div style="margin-top: 24px; display: flex; flex-direction: column; gap: 12px;">
      <button 
        v-if="selectedEmail.blockReason !== 'No phishing detected'"
        @click="closeModal"
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
        Déclarer comme non phishing
      </button>
      
      <button
        @click="closeModal"
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
        Fermer
      </button>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  props: {
    selectedEmail: Object,
    email_body: String,
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    closeModal() {
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
.dark-mode {
  background-color: #1e293b !important;
  border-color: #4b5563 !important;
  color: #f9fafb !important;
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
</style>