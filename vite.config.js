import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    chunkSizeWarningLimit: 1000, // Increase limit to 1000kb
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor'
            }
            if (id.includes('react-router')) {
              return 'router'
            }
            if (id.includes('framer-motion') || id.includes('lucide-react')) {
              return 'ui'
            }
            if (id.includes('axios')) {
              return 'http'
            }
            if (id.includes('react-markdown') || id.includes('react-syntax-highlighter')) {
              return 'markdown'
            }
            if (id.includes('react-hot-toast')) {
              return 'notifications'
            }
            // Other vendor libraries
            return 'vendor'
          }

          // Application chunks
          if (id.includes('src/pages/')) {
            return 'pages'
          }
          if (id.includes('src/components/')) {
            return 'components'
          }
          if (id.includes('src/services/')) {
            return 'services'
          }
        }
      }
    }
  },
  define: {
    'process.env': process.env
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom']
  }
})