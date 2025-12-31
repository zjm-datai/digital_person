// src/stores/session.ts
import { defineStore } from 'pinia';

export interface SessionData {
  session_id: string;
  name: string;
  token: string;
  created_at?: number;
}

const STORAGE_KEY = 'chat_session';

export const useSessionStore = defineStore('session', {
  state: () => ({
    data: null as SessionData | null,
  }),
  actions: {
    setSession(d: SessionData) {
      this.data = { ...d, created_at: Date.now() };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
    },
    loadFromStorage() {
      if (this.data) return this.data;
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      try {
        this.data = JSON.parse(raw);
      } catch { this.data = null; }
      return this.data;
    },
    clear() {
      this.data = null;
      localStorage.removeItem(STORAGE_KEY);
    },
  },
});
