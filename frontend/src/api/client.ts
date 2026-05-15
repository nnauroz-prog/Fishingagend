import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASIS ?? 'http://localhost:8000',
  timeout: 30_000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (fehler) => {
    if (import.meta.env.DEV) {
      console.error('[api]', fehler?.response?.status, fehler?.config?.url, fehler?.message);
    }
    return Promise.reject(fehler);
  },
);
