import { defineStore } from 'pinia'; // Import de defineStore depuis Pinia
import axiosInstance from '@/AxiosInstance'; // Import d'axiosInstance
import axios from 'axios'; // Import d'axios
import router from '@/router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    email: "",
    role: "",
  }),

  actions: {

    async login(email, password) {
      try {
        const data = { email, password };

        const response = await axios.post('http://localhost:8000/login', data, {
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
        await axiosInstance.get('http://localhost:8000/me', {
          withCredentials: true, timeout: 1000,
        }).then((response) => {
          if (response.status === 200) {
            this.email = response.data.email;
            if (response.data.role === 1) {
              this.role = "Admin";
            }
            else if (response.data.role === 2) {
              this.role = "User";
            }
            else {
              this.role = "Unknown";
            }
            this.isAuthenticated = true;
          }
          else {
            this.isAuthenticated = false;
        }});
        
        
      } catch (error) {
        this.isAuthenticated = false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.username = "";
      this.role = "";
      axiosInstance.post('http://localhost:8000/logout', {}, {
        withCredentials: true,
      });
      router.push('/login');
    },

    async checkAuth() {
      try {
        await this.loadUser();
      } catch (error) {
        this.isAuthenticated = false;
      }
    }
  }
});