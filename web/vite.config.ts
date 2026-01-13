import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    proxy: {
      "/console_api": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
        ws: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/console_api/, "console/api"),
      },
      "/dify_api": {
        target: "http://211.90.240.240:30010",
        changeOrigin: true,
        ws: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/dify_api/, ""),
      },
      "/gpustack_api": {
        target: "http://211.90.240.240:30001",
        changeOrigin: true,
        ws: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/gpustack_api/, ""),
      },
    }
  }
})