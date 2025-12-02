import ElementPlus from 'element-plus'

import './assets/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'  // 支持 CSS 变量生效
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './styles/global.css'
const app = createApp(App) // ✅ 先创建 app 实例

// ✅ 再注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}


app.use(createPinia())
app.use(router)
app.mount('#app')
