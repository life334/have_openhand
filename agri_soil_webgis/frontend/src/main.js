import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import VueCesium from 'vue-cesium'
import 'vue-cesium/dist/index.css'

import App from './App.vue'
import './style.css'
import routes from './router'

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create pinia store
const pinia = createPinia()

// Create app instance
const app = createApp(App)

// Use plugins
app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.use(VueCesium, {
  // 使用本地安装的 Cesium 而不是 CDN
  cesiumPath: '',
  accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTIzNTY3ZS01MWJmLTQzYjEtYjE0OS1kODVkMTY2NDRlODIiLCJpZCI6OTYyMCwic2NvcGVzIjpbImFzciIsImdjIl0sImlhdCI6MTU1MzIyODM0OX0.aW0_PLxl0L_UtZXizVSXciJGomjLNpOw8PFXLnXYFYw'
})

// Mount app
app.mount('#app')
