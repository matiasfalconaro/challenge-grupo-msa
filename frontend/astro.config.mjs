import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import react from '@astrojs/react';

export default defineConfig({
  output: 'hybrid',
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000
  }
});
