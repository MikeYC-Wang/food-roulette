<template>
  <div class="min-h-screen bg-bento-bg flex flex-col items-center p-6 relative overflow-hidden">
    
    <button @click="$router.push('/')" class="absolute top-6 left-6 z-50 w-10 h-10 bg-white border-2 border-gray-800 rounded-xl flex items-center justify-center text-gray-800 transition-transform active:translate-y-1 hover:scale-105" style="box-shadow: 2px 2px 0px 0px rgba(31,41,55,1);">
      <i class="fa-solid fa-chevron-left"></i>
    </button>

    <div class="w-full max-w-md flex-1 flex flex-col justify-center pb-4 mt-8">
      <div class="w-full bg-white rounded-3xl p-8 border-4 border-gray-800 relative z-10 flex flex-col max-h-[85vh]" style="box-shadow: 8px 8px 0px 0px rgba(31, 41, 55, 1);">
        
        <div class="text-center mb-6 flex-shrink-0">
          <input type="file" ref="fileInput" @change="handleFileUpload" accept="image/*" class="hidden" />

          <div @click="triggerFileInput" 
               class="w-24 h-24 mx-auto bg-bento-primary rounded-full flex items-center justify-center border-4 border-gray-800 mb-2 relative cursor-pointer overflow-hidden group transition-transform hover:scale-105" >
            
            <img v-if="userInfo.avatar_url" :src="userInfo.avatar_url" class="w-full h-full object-cover" alt="User Avatar" />
            <i v-else class="fa-solid fa-user text-4xl text-white"></i>

            <div v-if="isUploadingAvatar" class="absolute inset-0 bg-black/50 flex items-center justify-center">
              <i class="fa-solid fa-circle-notch fa-spin text-white text-2xl"></i>
            </div>

            <div v-else class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <i class="fa-solid fa-camera text-white text-2xl"></i>
            </div>
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

          <div class="flex gap-3 flex-shrink-0">
            <button @click="activeTab = 'history'" class="flex-1 py-2 rounded-xl font-bold border-2 border-gray-800 transition-all" :class="activeTab === 'history' ? 'bg-bento-primary text-gray-800 translate-y-1' : 'bg-white text-gray-500'" :style="activeTab === 'history' ? '' : 'box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);'">
              <i class="fa-solid fa-clock-rotate-left mr-1"></i>歷史紀錄
            </button>
            <button @click="activeTab = 'favorites'" class="flex-1 py-2 rounded-xl font-bold border-2 border-gray-800 transition-all" :class="activeTab === 'favorites' ? 'bg-red-500 text-white translate-y-1 border-red-700' : 'bg-white text-gray-500'" :style="activeTab === 'favorites' ? '' : 'box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);'">
              <i class="fa-solid fa-heart mr-1"></i>我的最愛
            </button>
          </div>

          <div class="flex flex-col flex-1 min-h-0">
            
            <div v-if="activeTab === 'history'" class="flex flex-col flex-1 min-h-0">
              <div v-if="spinHistory.length === 0" class="bg-gray-50 text-center py-6 rounded-xl border-2 border-gray-200 text-gray-500 font-bold flex-shrink-0">
                還沒有轉過任何餐廳喔！趕快去試試手氣吧！
              </div>
              
              <div v-else class="flex-1 min-h-0 flex flex-col gap-3 overflow-y-auto pr-2 pt-2 -mt-2 custom-scrollbar">
                <div v-for="item in spinHistory" :key="item.id" class="bg-white p-3 rounded-xl border-2 border-gray-800 flex justify-between items-center transition-all duration-200 hover:-translate-y-1 relative z-10 hover:z-50 flex-shrink-0" style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);">
                  <div class="flex-1 min-w-0 pr-3">
                    <div class="font-bold text-gray-800 text-base truncate">{{ item.restaurant_name }}</div>
                    <div class="text-xs text-gray-500 font-bold mt-1">{{ item.spin_time }}</div>
                  </div>
                  <a v-if="item.google_place_id" :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(item.restaurant_name)}&query_place_id=${item.google_place_id}`" target="_blank" class="bg-bento-primary text-white w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 hover:brightness-110 border-2 border-gray-800 transition-colors">
                    <i class="fa-solid fa-map-location-dot"></i>
                  </a>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'favorites'" class="flex flex-col flex-1 min-h-0">
              <div v-if="favoriteList.length === 0" class="bg-gray-50 text-center py-6 rounded-xl border-2 border-gray-200 text-gray-500 font-bold flex-shrink-0">
                還沒有收藏餐廳喔！在轉盤結果按下愛心收藏吧！
              </div>
              
              <div v-else class="flex-1 min-h-0 flex flex-col gap-3 overflow-y-auto pr-2 pt-2 -mt-2 custom-scrollbar">
                <div v-for="item in favoriteList" :key="item.id" class="bg-white p-3 rounded-xl border-2 border-red-500 flex justify-between items-center transition-all duration-200 hover:-translate-y-1 relative z-10 hover:z-50 flex-shrink-0" style="box-shadow: 2px 2px 0px 0px #ef4444;">
                  <div class="flex-1 min-w-0 pr-3">
                    <div class="font-bold text-gray-800 text-base truncate">{{ item.restaurant_name }}</div>
                    <div class="text-xs text-gray-500 font-bold mt-1">收藏於: {{ item.created_at.split(' ')[0] }}</div>
                  </div>
                  <a :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(item.restaurant_name)}&query_place_id=${item.google_place_id}`" target="_blank" class="bg-red-500 text-white w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 hover:bg-red-600 border-2 border-red-700 transition-colors">
                    <i class="fa-solid fa-map-location-dot"></i>
                  </a>
                </div>
              </div>
            </div>

          </div>

          <button @click="handleLogout" class="w-full bg-red-500 text-white font-bold text-lg py-3 rounded-xl border-2 border-gray-800 mt-2 flex-shrink-0 transition-transform active:translate-y-1 active:translate-x-1 hover:brightness-110" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
            <i class="fa-solid fa-right-from-bracket mr-2"></i> 登出帳號
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toast } from 'vue3-toastify';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/axios';

const router = useRouter();
const isLoading = ref(true);
const activeTab = ref('history');

// 新增上傳大頭貼相關 ref
const fileInput = ref<HTMLInputElement | null>(null);
const isUploadingAvatar = ref(false);

const userInfo = ref({
  username: '',
  email: '',
  created_at: '',
  avatar_url: '' // 加上 avatar_url
});
const spinHistory = ref<any[]>([]);
const favoriteList = ref<any[]>([]); 

// 在 ProfileView.vue 中替換：
onMounted(async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }

  try {
    const [userRes, historyRes, favRes] = await Promise.all([
      api.get('/api/me'),
      api.get('/api/history'),
      api.get('/api/favorites')
    ]);
    
    userInfo.value = userRes.data;
    spinHistory.value = historyRes.data.history;
    favoriteList.value = favRes.data.favorites;
  } catch (error) {
    console.error('取得資料失敗', error);
    // 這裡不用再手動導向了，總機會幫我們處理！
  } finally {
    isLoading.value = false;
  }
});

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    toast.warning('請上傳圖片檔案！');
    target.value = ''; 
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  isUploadingAvatar.value = true;

  try {
    const res = await api.post('/api/user/upload-avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    userInfo.value.avatar_url = res.data.avatar_url;
  } catch (error) {
    console.error('上傳大頭貼失敗', error);
    toast.error('大頭貼上傳失敗，請稍後再試');
  } finally {
    isUploadingAvatar.value = false;
    target.value = ''; 
  }
};

// 點擊大頭貼觸發隱藏的 file input
const triggerFileInput = () => {
  if (!isUploadingAvatar.value) {
    fileInput.value?.click();
  }
};

const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  toast.success('已成功登出！');
  router.push('/');
};
</script>

<style src="../style/ProfileView.css" scoped></style>