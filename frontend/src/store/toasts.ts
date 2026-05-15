import { defineStore } from 'pinia';
import { ref } from 'vue';

export type ToastTyp = 'erfolg' | 'fehler' | 'info';

export interface Toast {
  id: number;
  typ: ToastTyp;
  text: string;
}

export const useToastStore = defineStore('toasts', () => {
  const liste = ref<Toast[]>([]);
  let naechsteId = 1;

  function zeige(text: string, typ: ToastTyp = 'info', dauer = 4000) {
    const id = naechsteId++;
    liste.value.push({ id, typ, text });
    if (dauer > 0) {
      setTimeout(() => entferne(id), dauer);
    }
    return id;
  }

  function erfolg(text: string, dauer?: number) {
    return zeige(text, 'erfolg', dauer);
  }

  function fehler(text: string, dauer?: number) {
    return zeige(text, 'fehler', dauer ?? 6000);
  }

  function info(text: string, dauer?: number) {
    return zeige(text, 'info', dauer);
  }

  function entferne(id: number) {
    liste.value = liste.value.filter((t) => t.id !== id);
  }

  return { liste, zeige, erfolg, fehler, info, entferne };
});
