import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
// The SIH25033 backend (uvicorn app.main:app --reload) listens on :8000 by
// default and has its own permissive CORSMiddleware, so this proxy is only
// needed if you prefer same-origin requests during local dev.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/seed': 'http://127.0.0.1:8000',
      '/candidates': 'http://127.0.0.1:8000',
      '/internships': 'http://127.0.0.1:8000',
      '/allocate': 'http://127.0.0.1:8000',
      '/allocations': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
    },
  },
})
