import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './', // Usar caminhos relativos para funcionar no Cloud Storage
  server: { port: 3000 },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.js',
    coverage: {
      provider: 'v8',
      statements: 25,
      branches: 25,
      functions: 25,
      lines: 25,
    },
  },
});

