import axios from 'axios';
import { toast } from 'vue3-toastify';

// 建立 Axios 實體，自動套用環境變數的網址
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
});

// 請求攔截器 (出發前檢查)
api.interceptors.request.use(
  (config) => {
    // 從 localStorage 拿出 Token
    const token = localStorage.getItem('token');
    // 如果有 Token，就自動加進標頭裡！不用再每次手動寫了
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器 (回來後檢查)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 如果後端回傳 401 (未授權/Token過期)
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      toast.error('登入已過期，請重新登入 🔒');
      
      // 延遲一下讓使用者看到 Toast，再跳轉回登入頁
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    }
    return Promise.reject(error);
  }
);

export default api;