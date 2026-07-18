import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so the dev server is reachable from the host
    port: 5173,
    strictPort: true,
    watch: {
      // needed for hot-reload to work reliably inside a Docker bind mount
      usePolling: true,
    },
  },
});
