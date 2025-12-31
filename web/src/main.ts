import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './index.css'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// @ts-ignore
import './pollyfills.js';

const pinia = createPinia()
const app = createApp(App);

app.use(pinia)
app.use(ElementPlus);
app.use(router);
app.mount('#app');
