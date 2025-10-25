import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import './assets/styles/main.scss'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 配置Pinia状态管理
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

// 配置路由
app.use(router)

app.mount('#app')
