import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // In development, the page runs on port 5173 and FastAPI on 8000. The browser sends API calls
    // to 5173, and Vite passes them on, so both look like one site to the browser.
    proxy: { '/api': 'http://localhost:8000' },
  },
})
