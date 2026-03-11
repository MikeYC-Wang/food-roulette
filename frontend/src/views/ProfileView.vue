<template>
  <div class="min-h-screen bg-bento-bg flex flex-col items-center justify-center p-4 relative overflow-hidden">
    
    <button @click="$router.push('/')" class="absolute top-8 left-6 text-2xl text-gray-700 hover:text-bento-primary transition-colors z-20">
      <i class="fa-solid fa-arrow-left"></i>
    </button>

    <div class="w-full max-w-md bg-white rounded-3xl p-8 border-4 border-gray-800 relative z-10 flex flex-col max-h-[90vh]" style="box-shadow: 8px 8px 0px 0px rgba(31, 41, 55, 1);">
      
      <div class="text-center mb-6 flex-shrink-0">
        <div class="w-20 h-20 mx-auto bg-bento-primary rounded-full flex items-center justify-center border-4 border-gray-800 mb-2" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-solid fa-user text-3xl text-white"></i>
        </div>
        <h2 class="text-3xl font-black text-gray-800 tracking-wider">個人資料</h2>
      </div>

      <div v-if="isLoading" class="text-center text-gray-500 font-bold py-8 flex-1">
        <i class="fa-solid fa-circle-notch fa-spin text-2xl mb-2"></i><br>
        載入中...
      </div>

      <div v-else class="flex flex-col gap-6 overflow-hidden flex-1">
        <div class="bg-gray-50 p-4 rounded-xl border-2 border-gray-200 flex-shrink-0">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-bold text-gray-400">帳號</span>
            <div class="text-base font-bold text-gray-800">{{ userInfo.username }}</div>
          </div>
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-bold text-gray-400">電子郵件</span>
            <div class="text-base font-bold text-gray-800">{{ userInfo.email }}</div>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-bold text-gray-400">加入時間</span>
            <div class="text-base font-bold text-gray-800">{{ userInfo.created_at }}</div>
          </div>
        </div>

        <div class="flex flex-col flex-1 overflow-hidden">
          <h3 class="text-lg font-black text-gray-800 mb-3 flex items-center flex-shrink-0">
            <i class="fa-solid fa-clock-rotate-left mr-2"></i> 最近轉盤紀錄
          </h3>
          
          <div v-if="spinHistory.length === 0" class="bg-gray-50 text-center py-6 rounded-xl border-2 border-gray-200 text-gray-500 font-bold">
            還沒有轉過任何餐廳喔！趕快去首頁試試手氣吧！
          </div>
          
          <div v-else class="flex flex-col gap-3 overflow-y-auto pr-2 pt-2 -mt-2 custom-scrollbar relative">
            <div v-for="item in spinHistory" :key="item.id" class="bg-white p-3 rounded-xl border-2 border-gray-800 flex justify-between items-center transition-transform hover:-translate-y-1 hover:shadow-sm" style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);">
              <div class="flex-1 min-w-0 pr-3">
                <div class="font-bold text-gray-800 text-base truncate">{{ item.restaurant_name }}</div>
                <div class="text-xs text-gray-500 font-bold mt-1">{{ item.spin_time }}</div>
              </div>
              <a v-if="item.google_place_id" :href="`http://googleusercontent.com/maps.google.com/search/?api=1&query=${encodeURIComponent(item.restaurant_name)}&query_place_id=${item.google_place_id}`" target="_blank" class="bg-bento-primary text-white w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 hover:brightness-110 border-2 border-gray-800 transition-colors">
                <i class="fa-solid fa-map-location-dot"></i>
              </a>
            </div>
          </div>
        </div>

        <button @click="handleLogout" class="w-full bg-red-500 text-white font-bold text-lg py-3 rounded-xl border-2 border-gray-800 mt-2 flex-shrink-0 transition-transform active:translate-y-1 active:translate-x-1 hover:brightness-110" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
          <i class="fa-solid fa-right-from-bracket mr-2"></i> 登出帳號
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
const spinHistory = ref<any[]>([]);

onMounted(async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }

  try {
    const [userRes, historyRes] = await Promise.all([
      axios.get('http://127.0.0.1:8001/api/me', { headers: { Authorization: `Bearer ${token}` } }),
      axios.get('http://127.0.0.1:8001/api/history', { headers: { Authorization: `Bearer ${token}` } })
    ]);
    
    userInfo.value = userRes.data;
    spinHistory.value = historyRes.data.history;
  } catch (error) {
    console.error('取得資料失敗', error);
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    router.push('/login');
  } finally {
    isLoading.value = false;
  }
});

const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  alert('已成功登出！');
  router.push('/');
};
</script>

<style src="../style/ProfileView.css" scoped></style>