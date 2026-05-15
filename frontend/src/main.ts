import { createPinia } from 'pinia';
import { createApp } from 'vue';

import App from '@/App.vue';
import { i18n } from '@/i18n';
import { router } from '@/router';

import '@/assets/main.css';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(i18n);

// Auth-Token aus localStorage laden, bevor die App startet
import { useAuthStore } from '@/store/auth';
useAuthStore().lade();

app.mount('#app');
