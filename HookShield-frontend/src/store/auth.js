import { defineStore } from 'pinia'; // Import de defineStore depuis Pinia
import axiosInstance from '@/AxiosInstance'; // Import d'axiosInstance
import axios from 'axios'; // Import d'axios

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    username: "",
    role: "",
  }),

  actions: {

    async login(username, password) {
      try {
        const data = { username, password };

        const response = await axios.post('https://localhost:3000/login', data, {
          withCredentials: true, 
        });

        if (response.status === 200) {

          this.isAuthenticated = true;
          this.loadUser();
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          throw new Error('Invalid credentials');
        }
      }
    },


    async loadUser() {
      try {
        const userResponse = await axiosInstance.get('https://localhost:3000/me', {
          withCredentials: true,
        });
        this.username = userResponse.data.username;
        this.role = userResponse.data.role;
      } catch (error) {
        this.isAuthenticated = false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.username = "";
      this.role = "";
      axiosInstance.post('https://localhost:3000/logout', {}, {
        withCredentials: true,
      });
    },

    async checkAuth() {
      try {
        await this.loadUser();
        this.isAuthenticated = true;
      } catch (error) {
        this.isAuthenticated = false;
      }
    }
  }
});