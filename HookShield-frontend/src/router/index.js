import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import StatView from '../views/StatView.vue'
import ListView from '../views/ListView.vue'
import MailManagerView from '../views/MailManagerView.vue'
import AdminView from '../views/AdminView.vue'
import { useAuthStore } from '@/store/auth';

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
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  console.log(authStore.isAuthenticated);
  if (!authStore.isAuthenticated && to.path !== '/login' ) {
    next('/login');
  } else {
    if(to.meta.requiresAdmin && authStore.role !== 'admin') {
      next('/');
    }
    next();
  }
});


export default router
