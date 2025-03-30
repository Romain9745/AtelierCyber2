<template>
  
      <!-- Modal -->
      <div
        class="fixed top-0 right-0 left-0 flex justify-center items-center w-full h-full" style="background-color: rgba(0, 0, 0, 0.5);" @click="closeModal"
      >
        <div class="relative p-4 w-full max-w-md max-h-full bg-white rounded-lg shadow-sm dark:bg-gray-700" @click="stopPropagation">
          <!-- Modal content -->
          <div  class="flex justify-between items-center p-4 border-b rounded-t dark:border-gray-600">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Connect with Email
            </h3>
            <button
              type="button"
              @click="closeModal"
              class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm h-8 w-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
            >
              <svg
                class="w-3 h-3"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 14 14"
              >
                <path
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                />
              </svg>
            </button>
          </div>
          <!-- Modal body -->
          <div v-if="!showImapForm" class="p-4">
            <p class="text-sm font-normal text-gray-500 dark:text-gray-400">
              Connect with one of our available email providers or enter your
              custom IMAP credentials.
            </p>
            <ul class="my-4 space-y-3">
              <!-- Google Email Option -->
              <li>
                <a
                  href="#"
                  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow dark:bg-gray-600 dark:hover:bg-gray-500 dark:text-white"
                  @click.prevent="connectWithGoogle"
                >
                  <svg
                    aria-hidden="true"
                    class="w-6 h-6 me-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 6h16M4 12h16m-7 6h7"
                    ></path>
                  </svg>
                  <span class="flex-1 ms-3 whitespace-nowrap">Google</span>
                </a>
              </li>
              <!-- Outlook Email Option -->
              <li>
                <a
                  href="#"
                  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow dark:bg-gray-600 dark:hover:bg-gray-500 dark:text-white"
                  @click.prevent="connectWithOutlook"
                >
                  <svg
                    aria-hidden="true"
                    class="w-6 h-6 me-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 3v18l15-9z"
                    ></path>
                  </svg>
                  <span class="flex-1 ms-3 whitespace-nowrap">Outlook</span>
                </a>
              </li>
              <!-- IMAP Email Option -->
              <li>
                <a
                  href="#"
                  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow dark:bg-gray-600 dark:hover:bg-gray-500 dark:text-white"
                  @click.prevent="connectWithImap"
                >
                  <svg
                    aria-hidden="true"
                    class="w-6 h-6 me-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 4h-5l-1-1H9l-1 1H4m15 4H5m15 4H5m15 4H5m15 4H5"
                    ></path>
                  </svg>
                  <span class="flex-1 ms-3 whitespace-nowrap">IMAP (Custom)</span>
                </a>
              </li>
            </ul>
          </div>
          <!-- Form to input IMAP credentials -->
        <div v-if="showImapForm" class="mt-4">
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
            <input
              v-model="imapCredentials.email"
              type="email"
              id="email"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Enter your email"
              required
            />
          </div>
          <div class="mb-4">
            <label for="host" class="block text-sm font-medium text-gray-700 dark:text-gray-300">IMAP Host</label>
            <input
              v-model="imapCredentials.host"
              type="text"
              id="host"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Enter IMAP server host"
              required
            />
          </div>
          <div class="mb-4">
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
            <input
              v-model="imapCredentials.password"
              type="password"
              id="password"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              placeholder="Enter your password"
              required
            />
          </div>
          <p v-if="errorIMAP" class="text-sm text-red-500 dark:text-red-400">{{ errorIMAP }}</p>
          <button
            @click.prevent="submitImapCredentials"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700"
          >
            Connect
          </button>
        </div>
        </div>
      </div>
  </template>
  
  <script>
  import axiosInstance from '@/AxiosInstance';
  export default {
    data() {
      return {
        isModalOpen: false,
        showImapForm: false,
        imapCredentials: {
          email: '',
          host: '',
          password: '',
        },
        errorIMAP: '',
      }; 
    },
    methods: {
      closeModal(email) {
        if(!email) {
          this.$emit("close");
        }
        else {
          this.$emit("close", email);
        }
      },
      async connectWithGoogle() {
        console.log("Connecting with Google...");
        await axiosInstance.get('/login/gmail').then(response => {
          console.log(response.data);
        });

      },
      connectWithOutlook() {
        console.log("Connecting with Outlook...");
      },
      connectWithImap() {
      this.showImapForm = true;
      },
      async submitImapCredentials() {
        this.errorIMAP = '';
        var data = {
          host: this.imapCredentials.host,
          email: this.imapCredentials.email,
          password: this.imapCredentials.password,
        };
        console.log('Submitting IMAP credentials:', data);
        // Send the credentials to the backend (FastAPI)
        try {
          const response = await axiosInstance.post('/login/imap', this.imapCredentials);
          if (response.status === 200) {
            console.log('Successfully connected with IMAP:', response.data);
            this.closeModal(data.email);
          }
        } catch (error) {
          console.error('Error connecting with IMAP:', error);
          this.errorIMAP = 'Error connecting with IMAP. Please check your credentials.';
        }
    },
      stopPropagation(event) {
      event.stopPropagation(); // Empêche la propagation du clic vers les parents
      },
    },
  };
  </script>