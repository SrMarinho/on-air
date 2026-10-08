import { fileURLToPath, URL } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

const repoRoot = fileURLToPath(new URL('../..', import.meta.url))

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  // Game art lives once at <repo>/assets and is shared with the Godot client.
  publicDir: fileURLToPath(new URL('../../assets', import.meta.url)),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@design': fileURLToPath(new URL('../../shared/design', import.meta.url)),
      '@levels': fileURLToPath(
        new URL('../../backend/src/onair/modules/levels/infrastructure/data', import.meta.url),
      ),
    },
  },
  server: { fs: { allow: [repoRoot] } },
  test: { environment: 'jsdom' },
})
