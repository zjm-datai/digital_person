// frontend/src/stores/summary.ts

import { defineStore } from "pinia";
import type { ChatMessage } from "@/types/web/chat";

export const useSummaryStore = defineStore('summary', {
    state: () => ({
        text: '' as string,
        rawMessage: null as ChatMessage | null,
        lastUpdated: 0 as number,
    }),
    actions: {
        setSummary(payload: { text: string; rawMessage?: ChatMessage | null }) {
            this.text = payload.text
            this.rawMessage = payload.rawMessage ?? null
            this.lastUpdated = Date.now()
        },               
        clear() {
            this.text = ''
            this.rawMessage = null
            this.lastUpdated = 0
        },
    }
})