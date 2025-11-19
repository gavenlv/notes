// Vue 3 + TypeScript 应用入口文件

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

// 创建Vue应用实例
const app = createApp(App);

// 创建Pinia状态管理实例
const pinia = createPinia();

// 使用Pinia
app.use(pinia);

// 挂载应用
app.mount('#app');