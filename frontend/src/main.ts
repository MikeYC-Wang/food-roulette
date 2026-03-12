import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.css'

// 匯入 Toast 套件與樣式
import Vue3Toastify, { type ToastContainerOptions } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

const app = createApp(App)

app.use(router)

// 全域註冊並設定 Toast 的預設風格
app.use(Vue3Toastify, {
  autoClose: 2500,          // 2.5 秒後自動消失
  position: 'top-center',   // 從畫面上方中間滑出
  theme: 'colored',         // 使用飽和的顏色 (綠色成功、紅色錯誤等)
  transition: 'bounce',     // Q彈的彈跳動畫
  hideProgressBar: true,    // 隱藏下方的進度條讓畫面更乾淨
  style: {
    borderRadius: '16px',   // 圓角配合 Bento UI
    fontWeight: 'bold',     // 粗體字
  }
} as ToastContainerOptions);

app.mount('#app')