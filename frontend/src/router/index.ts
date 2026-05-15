import { createRouter, createWebHistory } from 'vue-router';

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'startseite',
      component: () => import('@/views/StartseiteView.vue'),
      meta: { titel: 'Startseite' },
    },
    {
      path: '/agenten',
      name: 'agenten',
      component: () => import('@/views/AgentenView.vue'),
      meta: { titel: 'Agenten' },
    },
    {
      path: '/chat/:agentId?',
      name: 'chat',
      component: () => import('@/views/ChatView.vue'),
      meta: { titel: 'Chat' },
    },
    {
      path: '/simulation',
      name: 'simulation',
      component: () => import('@/views/SimulationView.vue'),
      meta: { titel: 'Simulation' },
    },
    {
      path: '/berichte',
      name: 'berichte',
      component: () => import('@/views/BerichteView.vue'),
      meta: { titel: 'Berichte' },
    },
  ],
});

router.afterEach((to) => {
  document.title = `Fishingagend · ${to.meta.titel ?? ''}`;
});
