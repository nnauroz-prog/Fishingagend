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
      path: '/agenten/:id',
      name: 'agent-detail',
      component: () => import('@/views/AgentDetailView.vue'),
      meta: { titel: 'Agent' },
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
      path: '/simulation/:id',
      name: 'simulation-detail',
      component: () => import('@/views/SimulationDetailView.vue'),
      meta: { titel: 'Simulation' },
    },
    {
      path: '/graphrag',
      name: 'graphrag',
      component: () => import('@/views/GraphRAGView.vue'),
      meta: { titel: 'GraphRAG' },
    },
    {
      path: '/berichte',
      name: 'berichte',
      component: () => import('@/views/BerichteView.vue'),
      meta: { titel: 'Berichte' },
    },
    {
      path: '/pipeline',
      name: 'pipeline',
      component: () => import('@/views/PipelineView.vue'),
      meta: { titel: 'Pipeline' },
    },
    {
      path: '/einstellungen',
      name: 'einstellungen',
      component: () => import('@/views/EinstellungenView.vue'),
      meta: { titel: 'Einstellungen' },
    },
    {
      path: '/:pfad(.*)*',
      name: 'nicht-gefunden',
      component: () => import('@/views/NichtGefundenView.vue'),
      meta: { titel: 'Nicht gefunden' },
    },
  ],
});

router.afterEach((to) => {
  document.title = `Fishingagend · ${to.meta.titel ?? ''}`;
});
