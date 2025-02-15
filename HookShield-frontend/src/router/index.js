import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import StatView from '../views/StatView.vue'
import ListView from '../views/ListView.vue'
import MailManagerView from '@/views/MailManagerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/stats',
      name: 'stats',
      component: StatView,
    },
    {
      path: '/list',
      name: 'list',
      component: ListView,
    },
    {
      path: '/mailmanager',
      name: 'mailmanager',
      component: MailManagerView,
    }

  ],
})


export default router
