import { defineStore } from 'pinia';
import axiosInstance from '@/AxiosInstance';
import axios from 'axios';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true', // Chargement depuis localStorage
    email: localStorage.getItem('email') || "",
    role: localStorage.getItem('role') || "",
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
          withCredentials: true,
          timeout: 1000,
        }).then((response) => {
          if (response.status === 200) {
            this.email = response.data.email;
            if (response.data.role === 1) {
              this.role = "Admin";
            } else if (response.data.role === 2) {
              this.role = "User";
            } else {
              this.role = "Unknown";
            }
            this.isAuthenticated = true;

            // Persister dans localStorage
            localStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('email', this.email);
            localStorage.setItem('role', this.role);
          } else {
            this.isAuthenticated = false;
            router.push('/login');
          }
        });
      } catch (error) {
        this.isAuthenticated = false;
      }
    },

    logout() {
      this.isAuthenticated = false;
      this.email = "";
      this.role = "";
      
      // Nettoyer les données dans localStorage
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('email');
      localStorage.removeItem('role');
      
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
