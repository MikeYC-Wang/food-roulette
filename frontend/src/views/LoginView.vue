<template>
  <div class="min-h-screen bg-bento-bg flex flex-col items-center justify-center p-4 relative overflow-hidden">
    
    <button @click="$router.push('/')" class="absolute top-8 left-6 text-2xl text-gray-700 hover:text-bento-primary transition-colors z-20">
      <i class="fa-solid fa-arrow-left"></i>
    </button>

    <div class="w-full max-w-md bg-white rounded-3xl p-8 border-4 border-gray-800 relative z-10" style="box-shadow: 8px 8px 0px 0px rgba(31, 41, 55, 1);">
      
      <div class="text-center mb-8">
        <h2 class="text-3xl font-black text-gray-800 tracking-wider">
          {{ viewMode === 'login' ? '歡迎回來' : (viewMode === 'register' ? '建立新帳號' : '重設密碼') }}
        </h2>
        <p class="text-gray-500 mt-2 font-bold">
          {{ viewMode === 'login' ? '登入以儲存你的轉運紀錄' : (viewMode === 'register' ? '加入我們，紀錄每一次的美食邂逅' : '請輸入信箱來獲取重設驗證碼') }}
        </p>
      </div>

      <div v-if="message" :class="messageType === 'error' ? 'bg-red-100 text-red-700 border-red-300' : 'bg-green-100 text-green-700 border-green-300'" class="mb-4 p-3 rounded-xl border-2 font-bold text-center text-sm">
        {{ message }}
      </div>

      <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
        
        <div v-if="viewMode !== 'forgot'">
          <label class="block text-gray-700 font-bold mb-2 ml-1">帳號</label>
          <input v-model="username" type="text" required placeholder="請輸入帳號" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
        </div>

        <div v-if="viewMode !== 'login'">
          <label class="block text-gray-700 font-bold mb-2 ml-1">電子郵件</label>
          <input v-model="email" type="email" required placeholder="example@email.com" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
        </div>
        
        <div v-if="viewMode !== 'login'">
          <label class="block text-gray-700 font-bold mb-2 ml-1">驗證碼</label>
          <div class="flex gap-2">
            <input v-model="verificationCode" type="text" required placeholder="請輸入 6 位數驗證碼" class="flex-1 w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="sendCode" :disabled="countdown > 0 || isSendingCode" class="bg-bento-primary text-white font-bold px-4 rounded-xl border-2 border-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap" style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);">
              {{ countdown > 0 ? `${countdown} 秒後重試` : (isSendingCode ? '發送中...' : '獲取驗證碼') }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-gray-700 font-bold mb-2 ml-1">{{ viewMode === 'forgot' ? '新密碼' : '密碼' }}</label>
          <div class="relative">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required :placeholder="viewMode === 'forgot' ? '請輸入新密碼' : '請輸入密碼'" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 pr-12 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
              <i class="fa-solid" :class="showPassword ? 'fa-eye' : 'fa-eye-slash'"></i>
            </button>
          </div>
        </div>

        <div v-if="viewMode !== 'login'">
          <label class="block text-gray-700 font-bold mb-2 ml-1">確認密碼</label>
          <div class="relative">
            <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required placeholder="請再次輸入密碼" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 pr-12 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
              <i class="fa-solid" :class="showConfirmPassword ? 'fa-eye' : 'fa-eye-slash'"></i>
            </button>
          </div>
        </div>

        <div v-if="viewMode === 'login'" class="text-right mt-[-8px]">
          <button type="button" @click="changeMode('forgot')" class="text-sm font-bold text-gray-500 hover:text-bento-primary transition-colors">忘記密碼？</button>
        </div>

        <button type="submit" :disabled="isLoading" class="w-full bg-bento-accent text-white font-bold text-xl py-3 rounded-xl border-2 border-gray-800 mt-2 transition-transform active:translate-y-1 active:translate-x-1 hover:brightness-110" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          {{ isLoading ? '處理中...' : (viewMode === 'login' ? '登入' : (viewMode === 'register' ? '註冊' : '確認重設')) }}
        </button>
      </form>

      <div v-if="viewMode !== 'forgot'">
        <div class="flex items-center justify-between mt-6 mb-6">
          <hr class="w-full border-gray-300">
          <span class="px-3 text-gray-400 font-bold text-sm whitespace-nowrap">或使用快速登入</span>
          <hr class="w-full border-gray-300">
        </div>

        <div class="flex flex-col gap-3">
          <a href="http://127.0.0.1:8001/api/auth/google" class="w-full bg-white text-gray-700 font-bold py-3 rounded-xl border-2 border-gray-800 flex items-center justify-center gap-3 transition-transform active:translate-y-1 active:translate-x-1" style="box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);">
              <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-6 h-6">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                <path fill="none" d="M0 0h48v48H0z"></path>
              </svg>
              Google 登入
          </a>

          <a href="http://127.0.0.1:8001/api/auth/line" class="w-full bg-[#06C755] text-white font-bold py-3 rounded-xl border-2 border-gray-800 flex items-center justify-center gap-3 transition-transform active:translate-y-1 active:translate-x-1" style="box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);">
              <i class="fa-brands fa-line text-2xl"></i> LINE 登入
          </a>
        </div>
      </div>

      <div class="mt-8 text-center">
        <button v-if="viewMode === 'login'" @click="changeMode('register')" type="button" class="text-bento-primary font-bold hover:underline">
          還沒有帳號？點此註冊
        </button>
        <button v-else @click="changeMode('login')" type="button" class="text-bento-primary font-bold hover:underline">
          想起密碼了？返回登入
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();

// 取代原本的 isLoginMode，使用 viewMode 控制三種狀態
const viewMode = ref<'login' | 'register' | 'forgot'>('login');

const username = ref('');
const email = ref('');
const verificationCode = ref('');
const password = ref('');
const confirmPassword = ref('');

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const isLoading = ref(false);
const isSendingCode = ref(false);
const countdown = ref(0);
let timer: any = null;

const message = ref('');
const messageType = ref<'success' | 'error'>('success');

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// OAuth 跳轉回來處理
onMounted(() => {
  const token = route.query.token as string;
  if (token) {
    localStorage.setItem('token', token);
    messageType.value = 'success';
    message.value = '社群登入成功！跳轉中...';
    setTimeout(() => {
      router.push('/');
    }, 1500);
  }
});

// 切換模式並清空所有輸入框
const changeMode = (targetMode: 'login' | 'register' | 'forgot') => {
  viewMode.value = targetMode;
  message.value = '';
  username.value = '';
  email.value = '';
  verificationCode.value = '';
  password.value = '';
  confirmPassword.value = '';
  showPassword.value = false;
  showConfirmPassword.value = false;
  if (timer) clearInterval(timer);
  countdown.value = 0;
};

// 共用的發送驗證碼函式 (根據 mode 決定打哪一支 API)
const sendCode = async () => {
  if (!emailRegex.test(email.value)) {
    messageType.value = 'error';
    message.value = '請先輸入正確的電子郵件信箱';
    return;
  }

  isSendingCode.value = true;
  message.value = '';

  try {
    const endpoint = viewMode.value === 'register' ? '/api/send-code' : '/api/password-reset/request';
    const res = await axios.post(`http://127.0.0.1:8001${endpoint}`, { email: email.value });
    
    messageType.value = 'success';
    message.value = res.data.message;
    
    countdown.value = 60;
    timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  } catch (error: any) {
    messageType.value = 'error';
    message.value = error.response?.data?.detail || '發送驗證碼失敗，請稍後再試';
  } finally {
    isSendingCode.value = false;
  }
};

// 處理表單提交
const handleSubmit = async () => {
  isLoading.value = true;
  message.value = '';

  try {
    if (viewMode.value === 'login') {
      const params = new URLSearchParams();
      params.append('username', username.value);
      params.append('password', password.value);

      const response = await axios.post('http://127.0.0.1:8001/api/login', params);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('username', response.data.username);
      
      messageType.value = 'success';
      message.value = '登入成功！跳轉中...';
      
      setTimeout(() => {
        router.push('/');
      }, 1000);

    } else {
      // 註冊與忘記密碼的共用防呆
      if (!emailRegex.test(email.value)) {
        messageType.value = 'error';
        message.value = '請輸入正確的電子郵件格式';
        isLoading.value = false;
        return;
      }
      if (password.value !== confirmPassword.value) {
        messageType.value = 'error';
        message.value = '兩次輸入的密碼不一致！';
        isLoading.value = false;
        return;
      }
      if (!verificationCode.value) {
        messageType.value = 'error';
        message.value = '請輸入驗證碼！';
        isLoading.value = false;
        return;
      }

      if (viewMode.value === 'register') {
        await axios.post('http://127.0.0.1:8001/api/register', {
          username: username.value,
          password: password.value,
          email: email.value,
          code: verificationCode.value
        });
        messageType.value = 'success';
        message.value = '註冊成功！請直接登入';
        changeMode('login');

      } else if (viewMode.value === 'forgot') {
        await axios.post('http://127.0.0.1:8001/api/password-reset/confirm', {
          email: email.value,
          code: verificationCode.value,
          new_password: password.value
        });
        messageType.value = 'success';
        message.value = '密碼重設成功！請使用新密碼登入';
        changeMode('login');
      }
    }
  } catch (error: any) {
    messageType.value = 'error';
    if (error.response && error.response.data && error.response.data.detail) {
      message.value = error.response.data.detail;
    } else {
      message.value = '系統發生錯誤，請稍後再試';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>