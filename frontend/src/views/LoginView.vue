<template>
  <div class="min-h-screen bg-bento-bg flex flex-col items-center justify-center p-4 relative overflow-hidden">
    
    <button @click="$router.push('/')" class="absolute top-8 left-6 text-2xl text-gray-700 hover:text-bento-primary transition-colors z-20">
      <i class="fa-solid fa-arrow-left"></i>
    </button>

    <div class="w-full max-w-md bg-white rounded-3xl p-8 border-4 border-gray-800 relative z-10" style="box-shadow: 8px 8px 0px 0px rgba(31, 41, 55, 1);">
      
      <div class="text-center mb-8">
        <h2 class="text-3xl font-black text-gray-800 tracking-wider">
          {{ isLoginMode ? '歡迎回來' : '建立新帳號' }}
        </h2>
        <p class="text-gray-500 mt-2 font-bold">{{ isLoginMode ? '登入以儲存你的轉運紀錄' : '加入我們，紀錄每一次的美食邂逅' }}</p>
      </div>

      <div v-if="message" :class="messageType === 'error' ? 'bg-red-100 text-red-700 border-red-300' : 'bg-green-100 text-green-700 border-green-300'" class="mb-4 p-3 rounded-xl border-2 font-bold text-center text-sm">
        {{ message }}
      </div>

      <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
        <div>
          <label class="block text-gray-700 font-bold mb-2 ml-1">帳號</label>
          <input v-model="username" type="text" required placeholder="請輸入帳號" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
        </div>

        <div v-if="!isLoginMode">
          <label class="block text-gray-700 font-bold mb-2 ml-1">電子郵件</label>
          <input v-model="email" type="email" required placeholder="example@email.com" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
        </div>
        
        <div v-if="!isLoginMode">
          <label class="block text-gray-700 font-bold mb-2 ml-1">驗證碼</label>
          <div class="flex gap-2">
            <input v-model="verificationCode" type="text" required placeholder="請輸入 6 位數驗證碼" class="flex-1 w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="sendCode" :disabled="countdown > 0 || isSendingCode" class="bg-bento-primary text-white font-bold px-4 rounded-xl border-2 border-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap" style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);">
              {{ countdown > 0 ? `${countdown} 秒後重試` : (isSendingCode ? '發送中...' : '獲取驗證碼') }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-gray-700 font-bold mb-2 ml-1">密碼</label>
          <div class="relative">
            <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="請輸入密碼" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 pr-12 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="showPassword = !showPassword" class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
              <i class="fa-solid" :class="showPassword ? 'fa-eye' : 'fa-eye-slash'"></i>
            </button>
          </div>
        </div>

        <div v-if="!isLoginMode">
          <label class="block text-gray-700 font-bold mb-2 ml-1">確認密碼</label>
          <div class="relative">
            <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required placeholder="請再次輸入密碼" class="w-full bg-gray-50 border-2 border-gray-800 rounded-xl px-4 py-3 pr-12 font-bold focus:outline-none focus:border-bento-primary transition-colors" />
            <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
              <i class="fa-solid" :class="showConfirmPassword ? 'fa-eye' : 'fa-eye-slash'"></i>
            </button>
          </div>
        </div>

        <button type="submit" :disabled="isLoading" class="w-full bg-bento-accent text-white font-bold text-xl py-3 rounded-xl border-2 border-gray-800 mt-2 transition-transform active:translate-y-1 active:translate-x-1 hover:brightness-110" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          {{ isLoading ? '處理中...' : (isLoginMode ? '登入' : '註冊') }}
        </button>
      </form>

      <div class="flex items-center justify-between mt-6 mb-6">
        <hr class="w-full border-gray-300">
        <span class="px-3 text-gray-400 font-bold text-sm whitespace-nowrap">或使用快速登入</span>
        <hr class="w-full border-gray-300">
      </div>

      <div class="flex flex-col gap-3">
        <button @click="triggerOAuth('Google')" class="w-full bg-white text-gray-700 font-bold py-3 rounded-xl border-2 border-gray-800 flex items-center justify-center gap-3 transition-transform active:translate-y-1 active:translate-x-1" style="box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-brands fa-google text-red-500 text-xl"></i> Google 登入
        </button>
        <button @click="triggerOAuth('LINE')" class="w-full bg-[#06C755] text-white font-bold py-3 rounded-xl border-2 border-gray-800 flex items-center justify-center gap-3 transition-transform active:translate-y-1 active:translate-x-1" style="box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-brands fa-line text-2xl"></i> LINE 登入
        </button>
      </div>

      <div class="mt-8 text-center">
        <button @click="toggleMode" type="button" class="text-bento-primary font-bold hover:underline">
          {{ isLoginMode ? '還沒有帳號？點此註冊' : '已經有帳號了？點此登入' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const isLoginMode = ref(true);

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

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value;
  message.value = '';
  username.value = '';
  email.value = '';
  verificationCode.value = '';
  password.value = '';
  confirmPassword.value = '';
  showPassword.value = false;
  showConfirmPassword.value = false;
};

const sendCode = async () => {
  if (!emailRegex.test(email.value)) {
    messageType.value = 'error';
    message.value = '請先輸入正確的電子郵件信箱';
    return;
  }

  isSendingCode.value = true;
  message.value = '';

  try {
    const res = await axios.post('http://127.0.0.1:8001/api/send-code', { email: email.value });
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

const handleSubmit = async () => {
  isLoading.value = true;
  message.value = '';

  try {
    if (isLoginMode.value) {
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

      await axios.post('http://127.0.0.1:8001/api/register', {
        username: username.value,
        password: password.value,
        email: email.value,
        code: verificationCode.value
      });
      
      messageType.value = 'success';
      message.value = '註冊成功！請直接登入';
      isLoginMode.value = true; 
      password.value = ''; 
      confirmPassword.value = ''; 
      verificationCode.value = '';
      showPassword.value = false;
      if (timer) clearInterval(timer);
      countdown.value = 0;
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

const triggerOAuth = (provider: string) => {
  alert(`即將實作 ${provider} 快速登入！\n(需要先至開發者後台申請 API Key)`);
};
</script>