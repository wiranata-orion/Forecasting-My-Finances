import { createRouter, createWebHistory } from 'vue-router';
import Home from '../src/components/Home.vue';
import Budget from '../src/components/Budget.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/budget', component: Budget }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;