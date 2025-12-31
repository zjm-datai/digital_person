// frontend/src/stores/app.ts
import { defineStore } from 'pinia'

export type Platform = 'web' | 'app' | 'phone'

export const useAppStore = defineStore('app', {
  state: () => ({
    platform: 'web' as Platform,
  }),
  actions: {
    setPlatform(p?: string) {
      const v = (p || '').toLowerCase()
      this.platform = (v === 'app' || v === 'phone') ? (v as Platform) : 'web'
    },
  },
})
