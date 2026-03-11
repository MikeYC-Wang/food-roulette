<template>
  <div class="min-h-screen bg-bento-bg flex flex-col items-center justify-center p-4 relative overflow-hidden">
    
    <button @click="$router.push('/')" class="absolute top-8 left-6 text-2xl text-gray-700 hover:text-bento-primary transition-colors z-20">
      <i class="fa-solid fa-arrow-left"></i>
    </button>

    <div class="w-full max-w-md bg-white rounded-3xl p-8 border-4 border-gray-800 relative z-10" style="box-shadow: 8px 8px 0px 0px rgba(31, 41, 55, 1);">
      
      <div class="text-center mb-8">
        <div class="w-24 h-24 mx-auto bg-bento-primary rounded-full flex items-center justify-center border-4 border-gray-800 mb-4" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-solid fa-user text-4xl text-white"></i>
        </div>
        <h2 class="text-3xl font-black text-gray-800 tracking-wider">個人資料</h2>
      </div>

      <div v-if="isLoading" class="text-center text-gray-500 font-bold py-8">
        <i class="fa-solid fa-circle-notch fa-spin text-2xl mb-2"></i><br>
        載入中...
      </div>

      <div v-else class="flex flex-col gap-6">
        <div class="bg-gray-50 p-4 rounded-xl border-2 border-gray-200">
          <div class="mb-3">
            <span class="text-sm font-bold text-gray-400">帳號</span>
            <div class="text-lg font-bold text-gray-800">{{ userInfo.username }}</div>
          </div>
          <div class="mb-3">
            <span class="text-sm font-bold text-gray-400">電子郵件</span>
            <div class="text-lg font-bold text-gray-800">{{ userInfo.email }}</div>
          </div>
          <div>
            <span class="text-sm font-bold text-gray-400">加入時間</span>
            <div class="text-lg font-bold text-gray-800">{{ userInfo.created_at }}</div>
          </div>
        </div>

        <button class="w-full bg-white text-gray-700 font-bold py-3 rounded-xl border-2 border-gray-800 flex items-center justify-between px-4 transition-transform active:translate-y-1 active:translate-x-1" style="box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);">
          <span><i class="fa-solid fa-key mr-2"></i> 修改密碼</span>
          <i class="fa-solid fa-chevron-right text-gray-400"></i>
        </button>

        <button @click="handleLogout" class="w-full bg-red-500 text-white font-bold text-xl py-3 rounded-xl border-2 border-gray-800 mt-4 transition-transform active:translate-y-1 active:translate-x-1 hover:brightness-110" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-solid fa-right-from-bracket mr-2"></i> 登出
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const isLoading = ref(true);
const userInfo = ref({
  username: '',
  email: '',
  created_at: ''
});

// 元件掛載時，去後端抓個人資料
onMounted(async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    // 沒 Token 代表沒登入，踢回登入頁
    router.push('/login');
    return;
  }

  try {
    const res = await axios.get('http://127.0.0.1:8001/api/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    userInfo.value = res.data;
  } catch (error) {
    console.error('取得使用者資料失敗', error);
    // Token 可能過期了，清除並踢回登入頁
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    router.push('/login');
  } finally {
    isLoading.value = false;
  }
});

const handleLogout = () => {
  // 清除本地暫存的 Token
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  alert('已成功登出！');
  router.push('/');
};
</script>