import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
const backendPort = Number(process.env.VPS_PORT || 3100)
export default defineConfig({
  plugins: [react()],
  server: { host: '127.0.0.1', port: Number(process.env.VPS_DEV_PORT || 5173), strictPort: true,
    proxy: { '/api': { target: `http://127.0.0.1:${backendPort}` }, '/socket.io': { target: `http://127.0.0.1:${backendPort}`, ws: true } }
  }
})
