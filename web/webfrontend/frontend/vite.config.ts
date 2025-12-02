import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
//import vueDevTools from 'vite-plugin-vue-devtools'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
   // vueDevTools(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': '/src'
    },
  },
  server: {
    fs: {
      allow: [
       '..'
      ],
    },
    proxy: {
      '/api': {
        target: 'http://192.168.0.17:8899',
        changeOrigin: true,
        // 如果你的后端接口URL本身有/api前缀，这行可以注释掉
       // rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
