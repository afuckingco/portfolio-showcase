import { defineConfig } from 'vite';

export default defineConfig({
  root: '.',
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    emptyOutDir: true
  },
  server: {
    port: 5173,
    open: true
  }
});
