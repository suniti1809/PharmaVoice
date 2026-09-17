import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // Relative asset paths so the built bundle works under any sub-path.
  base: './',
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy keeps the frontend origin-agnostic: the browser only ever calls /api.
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
