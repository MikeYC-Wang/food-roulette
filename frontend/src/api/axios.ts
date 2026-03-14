import axios from 'axios';
import { toast } from 'vue3-toastify';

// 建立 Axios 實體，自動套用環境變數的網址
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001',
});

// 定義防抖鎖，用來防止併發 API 觸發多次 401 錯誤
let isTokenExpiredAlerted = false;

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
      
      // 檢查鎖是否為 false，確認這段期間內是「第一次」發生 401 才執行
      if (!isTokenExpiredAlerted) {
        isTokenExpiredAlerted = true; // 立刻鎖上，擋住後續同時發生的 401 請求
        
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        toast.error('登入已過期，請重新登入 🔒');
        
        // 延遲一下讓使用者看到 Toast，再跳轉回登入頁
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);

        // 3 秒後自動解鎖（雖然畫面已經跳轉，但加上解鎖是更保險的 SPA 寫法）
        setTimeout(() => {
          isTokenExpiredAlerted = false;
        }, 3000);
      }
    }
    return Promise.reject(error);
  }
);

export default api;