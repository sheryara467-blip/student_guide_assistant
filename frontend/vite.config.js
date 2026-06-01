import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy /chat and /topics to the FastAPI backend during development.
      // This avoids CORS issues — the browser talks to Vite, Vite forwards to FastAPI.
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/topics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})