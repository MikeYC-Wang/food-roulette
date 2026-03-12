<template>
  <div class="app-container bg-bento-bg relative">
    <header class="pt-4 text-center flex flex-col items-center z-10 w-full">
      
      <h1 class="flex justify-center w-full px-4">
        <img :src="logoImg" alt="食來運轉" class="h-[13rem] object-contain drop-shadow-sm" />
      </h1>

      <div v-if="!isCustomMode" class="location-status mt-4 flex items-center justify-center gap-2 relative z-20">
        <i :class="statusIconClass" class="text-lg"></i>
        <span class="text-sm font-bold text-gray-600">{{ location.message }}</span>
      </div>
      <div v-else class="location-status mt-4 flex items-center justify-center gap-2 relative z-20">
        <i class="fa-solid fa-list-check text-bento-secondary text-lg"></i>
        <span class="text-sm font-bold text-gray-600">目前為自訂名單模式</span>
      </div>

      <div v-if="location.status !== 'loading'" class="h-40 relative flex items-center justify-center w-full">
        <Transition name="food-fade">
          <img 
            :key="currentFoodIndex"
            :src="foodImages[currentFoodIndex]" 
            alt="food indicator"
            class="floating-food absolute h-56 w-56 object-contain scale-[1.8] pointer-events-none" 
          />
        </Transition>
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-start pt-6 w-full px-4 z-20">
      <Roulette ref="rouletteRef" @spin-end="handleSpinEnd" />
      
      <div class="bg-gray-200 rounded-full p-1 mt-6 flex relative w-64 border-2 border-gray-800" style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);">
        <div class="absolute inset-y-1 left-1 w-[calc(50%-4px)] bg-white rounded-full transition-transform duration-300 shadow-sm"
             :class="isCustomMode ? 'translate-x-[calc(100%+4px)]' : 'translate-x-0'"></div>
        <button @click="switchMode(false)" class="flex-1 py-1.5 text-sm font-bold z-10 transition-colors" :class="!isCustomMode ? 'text-gray-800' : 'text-gray-500'">附近探索</button>
        <button @click="switchMode(true)" class="flex-1 py-1.5 text-sm font-bold z-10 transition-colors" :class="isCustomMode ? 'text-gray-800' : 'text-gray-500'">自訂名單</button>
      </div>

      <button 
        v-if="hasFetchedData"
        @click="triggerSpin" :disabled="isSpinning"
        class="spin-btn bg-bento-accent text-white text-3xl font-bold mt-12 py-4 px-12 rounded-xl"
        :class="{ 'opacity-70 cursor-not-allowed transform translate-y-1 shadow-none': isSpinning }"
      >
        {{ isSpinning ? '轉運中...' : '轉運！' }}
      </button>

      <button 
        v-else
        @click="openAppropriateDrawer"
        class="spin-btn bg-bento-primary text-white text-3xl font-bold mt-12 py-4 px-12 rounded-xl animate-bounce"
      >
        <i class="fa-solid fa-hand-pointer mr-2"></i>{{ isCustomMode ? '請先建立名單' : '請先設定篩選條件' }}
      </button>
    </main>

    <footer class="pb-12 pt-6 flex justify-center gap-16 w-full relative z-20">
      <button @click="openAppropriateDrawer" class="bottom-icon-btn text-bento-secondary">
        <i :class="isCustomMode ? 'fa-solid fa-pen-to-square' : 'fa-solid fa-filter'"></i>
      </button>

      <button @click="handleUserIconClick" class="bottom-icon-btn text-gray-700 relative">
        <i class="fa-solid fa-user"></i>
        <span v-if="isLoggedIn" class="absolute top-0 right-0 block h-3 w-3 rounded-full bg-green-500 ring-2 ring-white"></span>
      </button>
      
      <button @click="isLocationDrawerOpen = true" class="bottom-icon-btn text-bento-primary">
        <i class="fa-solid fa-map-location-dot"></i>
      </button>
    </footer>

    <div v-if="showResult" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm transition-opacity">
      <div class="bg-white w-11/12 max-w-sm rounded-3xl p-6 shadow-2xl transform transition-all border border-gray-100">
        <div class="w-20 h-20 mx-auto bg-bento-primary rounded-full flex items-center justify-center -mt-16 mb-4 shadow-lg border-4 border-white">
          <i class="fa-solid fa-utensils text-4xl text-white"></i>
        </div>

        <div class="text-center">
          <div class="flex items-center justify-center gap-3 mb-2">
            <h2 class="text-2xl font-black text-gray-800 leading-tight">
              {{ selectedFood?.name }}
            </h2>
            <button 
              v-if="selectedFood?.id && !isCustomMode" 
              @click="toggleFavorite"
              class="text-3xl transition-transform active:scale-75 focus:outline-none drop-shadow-sm"
              :class="favoriteIds.includes(selectedFood.id) ? 'text-red-500' : 'text-gray-300 hover:text-red-400'"
            >
              <i class="fa-solid fa-heart"></i>
            </button>
          </div>
          
          <template v-if="!isCustomMode && selectedFood?.type !== 'N/A'">
            <div class="flex items-center justify-center space-x-3 text-sm mb-3">
              <span class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full font-bold flex items-center shadow-sm">
                <i class="fa-solid fa-star mr-1"></i> {{ selectedFood?.rating || '無評分' }}
              </span>
              <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-full font-medium shadow-sm capitalize">
                {{ formatType(selectedFood?.type) }}
              </span>
            </div>

            <div class="flex items-center justify-center space-x-2 text-sm mb-6">
              <span class="text-green-700 font-bold bg-green-50 px-3 py-1.5 rounded-full shadow-sm border border-green-100">
                {{ formatPrice(selectedFood?.priceLevel) }}
              </span>
              
              <span v-if="selectedFood?.openingHours" 
                    class="font-bold px-3 py-1.5 rounded-full shadow-sm border"
                    :class="selectedFood.openingHours.openNow ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-red-50 text-red-600 border-red-100'">
                <i class="fa-solid fa-clock mr-1"></i> 
                {{ selectedFood.openingHours.openNow ? '營業中' : '休息中' }}
              </span>
            </div>
          </template>

          <template v-else-if="isCustomMode">
            <p class="text-gray-500 font-bold mb-6 text-sm">🎊 自訂口袋名單轉出結果！</p>
          </template>
        </div>

        <div class="flex flex-col space-y-3 mt-2">
          <a v-if="selectedFood?.id && !isCustomMode" :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedFood.name)}&query_place_id=${selectedFood.id}`" target="_blank" rel="noopener noreferrer" class="w-full bg-bento-primary text-white font-bold py-3 px-6 rounded-xl hover:bg-opacity-90 transition-all flex items-center justify-center shadow-md">
            <i class="fa-solid fa-map-location-dot mr-2"></i> 帶我去吃！
          </a>
          
          <div class="flex gap-3 w-full">
            <button @click="shareResult" class="flex-1 bg-blue-50 text-blue-600 font-bold py-3 px-4 rounded-xl hover:bg-blue-100 transition-all flex items-center justify-center shadow-sm border border-blue-100">
              <i class="fa-solid fa-share-nodes mr-2"></i> 分享
            </button>
            <button @click="closeResult" class="flex-1 bg-gray-100 text-gray-700 font-bold py-3 px-4 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center shadow-sm">
              <i class="fa-solid fa-rotate-right mr-2"></i> 再轉一次
            </button>
          </div>
        </div>

      </div>
    </div>

    <FilterDrawer v-model:isOpen="isFilterOpen" @apply="handleApplyFilters" />
    <CustomListDrawer v-model:isOpen="isCustomDrawerOpen" :initialList="customList" @apply="handleApplyCustomList" />
    <LocationDrawer v-model:isOpen="isLocationDrawerOpen" :currentLat="location.lat" :currentLng="location.lng" @apply-location="handleApplyLocation" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'; 
import { useRouter } from 'vue-router';
import axios from 'axios';
import confetti from 'canvas-confetti';
import Roulette from '../components/Roulette.vue';
import FilterDrawer from '../components/FilterDrawer.vue';
import CustomListDrawer from '../components/CustomListDrawer.vue';
import { useLocation } from '../composables/useLocation';
import LocationDrawer from '../components/LocationDrawer.vue';

import logoImg from '../assets/LOGO-去背.png';
import food1 from '../assets/food1.png';
import food2 from '../assets/food2.png';
import food3 from '../assets/food3.png';
import food4 from '../assets/food4.png';
import food5 from '../assets/food5.png';

const isLocationDrawerOpen = ref(false);
// 當使用者在任意門按下「我要吃這附近」時觸發
const handleApplyLocation = async (newLoc: any) => {
  // 修改首頁的定位資料
  location.value.lat = newLoc.lat;
  location.value.lng = newLoc.lng;
  location.value.message = newLoc.name;
  location.value.status = 'success';
  
  // 如果現在是「附近探索」模式，就立刻幫他重新掃描新地點的美食！
  if (!isCustomMode.value) {
    hasFetchedData.value = false;
    showResult.value = false;
    await fetchRestaurants();
  }
};

interface RestaurantInfo {
  id?: string;
  name: string;
  type?: string;
  rating?: number;
  priceLevel?: string;
  openingHours?: { openNow: boolean; weekdayDescriptions: string[] }; 
}

const formatPrice = (level?: string) => {
  const priceMap: Record<string, string> = {
    'PRICE_LEVEL_INEXPENSIVE': '💰 平價', 'PRICE_LEVEL_MODERATE': '💰💰 中等',
    'PRICE_LEVEL_EXPENSIVE': '💰💰💰 稍貴', 'PRICE_LEVEL_VERY_EXPENSIVE': '💰💰💰💰 高級',
  };
  return level ? (priceMap[level] || '未知價位') : '未知價位';
};

const formatType = (t?: string) => {
  const map: Record<string, string> = { restaurant: '餐廳', cafe: '咖啡廳', bakery: '烘焙坊', bar: '酒吧', fast_food: '速食', meal_takeaway: '外帶', meal_delivery: '外送' };
  return t ? (map[t] || t) : '美食';
};

const router = useRouter();
const { location, getLocation } = useLocation();
const rouletteRef = ref<InstanceType<typeof Roulette> | null>(null);

const isSpinning = ref(false);
const showResult = ref(false);
const selectedFood = ref<RestaurantInfo | null>(null);
const hasFetchedData = ref(false);

const isFilterOpen = ref(false);
const isCustomDrawerOpen = ref(false);
const isCustomMode = ref(false);
const customList = ref<string[]>([]);
const favoriteIds = ref<string[]>([]); // 存放使用者已收藏的餐廳 ID

const currentFilters = ref({
  distance: 500, types: [] as string[], features: [] as string[], priceLevels: [] as string[],
  spinCount: 6, openNow: true, highRating: false 
});

const foodImages = [food1, food2, food3, food4, food5];
const currentFoodIndex = ref(0);
let foodInterval: ReturnType<typeof setInterval>;

const statusIconClass = computed(() => {
  switch (location.value.status) {
    case 'loading': return 'fa-solid fa-circle-notch fa-spin text-gray-400';
    case 'success': return 'fa-solid fa-location-dot text-bento-secondary';
    case 'default': return 'fa-solid fa-map-pin text-bento-primary';
    case 'error': return 'fa-solid fa-circle-exclamation text-bento-accent';
    default: return 'fa-solid fa-location-crosshairs';
  }
});

const switchMode = (toCustom: boolean) => {
  isCustomMode.value = toCustom;
  hasFetchedData.value = false;
  if (rouletteRef.value) {
    rouletteRef.value.setOptions([{ name: '等待設定中...', type: 'N/A', rating: 0 }]);
  }
};

const openAppropriateDrawer = () => {
  if (isCustomMode.value) {
    isCustomDrawerOpen.value = true;
  } else {
    isFilterOpen.value = true;
  }
};

const fetchRestaurants = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8001/api/spin', {
      lat: location.value.lat, lng: location.value.lng,
      distance: currentFilters.value.distance,
      types: currentFilters.value.types, 
      features: currentFilters.value.features,
      priceLevels: currentFilters.value.priceLevels,
      spinCount: currentFilters.value.spinCount,
      openNow: currentFilters.value.openNow,
      highRating: currentFilters.value.highRating
    });

    if (response.data.status === 'success' && rouletteRef.value) {
      rouletteRef.value.setOptions(response.data.results);
      hasFetchedData.value = true; 
    }
  } catch (error) {
    console.error('抓取餐廳名單失敗:', error);
  }
};

const fetchCustomList = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const res = await axios.get('http://127.0.0.1:8001/api/custom-list', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.data.custom_list) {
        customList.value = res.data.custom_list;
      }
    } catch (error) {
      console.error('取得自訂名單失敗', error);
    }
  }
};

const fetchFavorites = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const res = await axios.get('http://127.0.0.1:8001/api/favorites', {
        headers: { Authorization: `Bearer ${token}` }
      });
      favoriteIds.value = res.data.favorites.map((f: any) => f.google_place_id);
    } catch (error) {
      console.error('取得收藏名單失敗', error);
    }
  }
};

const toggleFavorite = async () => {
  if (!selectedFood.value || !selectedFood.value.id || isCustomMode.value) return;
  
  const token = localStorage.getItem('token');
  if (!token) {
    alert("請先登入才能收藏餐廳喔！");
    return;
  }
  
  try {
    const res = await axios.post('http://127.0.0.1:8001/api/favorites/toggle', {
      restaurant_name: selectedFood.value.name,
      google_place_id: selectedFood.value.id
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (res.data.status === 'added') {
      favoriteIds.value.push(selectedFood.value.id);
    } else if (res.data.status === 'removed') {
      favoriteIds.value = favoriteIds.value.filter(id => id !== selectedFood.value?.id);
    }
  } catch (error) {
    console.error('收藏切換失敗', error);
  }
};

onMounted(() => {
  getLocation();
  fetchCustomList();
  fetchFavorites(); // 網頁載入時順便抓取使用者的最愛清單

  foodInterval = setInterval(() => {
    currentFoodIndex.value = (currentFoodIndex.value + 1) % foodImages.length;
  }, 3500);
});

onUnmounted(() => {
  if (foodInterval) clearInterval(foodInterval);
});

const handleApplyFilters = async (filters: any) => {
  currentFilters.value = filters;
  showResult.value = false;
  await fetchRestaurants();
};

const handleApplyCustomList = async (newList: string[]) => {
  customList.value = newList;
  
  if (rouletteRef.value && newList.length > 0) {
    const formattedList = newList.map(name => ({
      name: name,
      type: 'custom'
    }));
    rouletteRef.value.setOptions(formattedList);
    hasFetchedData.value = true;
  }

  const token = localStorage.getItem('token');
  if (token) {
    try {
      await axios.post('http://127.0.0.1:8001/api/custom-list', {
        restaurants: newList
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('儲存自訂名單失敗', error);
    }
  }
};

const triggerSpin = async () => {
  if (isSpinning.value || !rouletteRef.value) return;
  isSpinning.value = true;
  showResult.value = false;
  rouletteRef.value.spin();
};

const handleSpinEnd = async (result: RestaurantInfo) => {
  isSpinning.value = false;
  selectedFood.value = result;
  showResult.value = true;

  // 觸發紙碎噴發動畫
  confetti({
    particleCount: 150,           // 紙碎的數量
    spread: 80,                   // 噴發的散開角度
    origin: { y: 0.55 },          // 從畫面哪個高度噴發 (0 是最頂端，1 是最底端。0.55 大約在彈窗位置)
    zIndex: 9999,                 // 確保紙碎會蓋在黑色半透明遮罩 (z-50) 的最上面
    colors: ['#E9C46A', '#2A9D8F', '#E76F51', '#A8DADC', '#4285F4'] // 偷偷加入配合你 App 風格的顏色
  });

  const token = localStorage.getItem('token');
  if (token && result) {
    try {
      await axios.post('http://127.0.0.1:8001/api/history', {
        restaurant_name: result.name,
        google_place_id: result.id || ''
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('儲存歷史紀錄失敗:', error);
    }
  }
};

const closeResult = () => showResult.value = false;

const isLoggedIn = ref(!!localStorage.getItem('token'));

const handleUserIconClick = () => {
  if (localStorage.getItem('token')) {
    router.push('/profile');
  } else {
    router.push('/login');
  }
};

// 處理分享轉盤結果
const shareResult = async () => {
  // 確保有抽獎結果 (將 selectedResult 改為 selectedFood)
  if (!selectedFood.value) return;

  const restaurantName = selectedFood.value.name;
  const placeId = selectedFood.value.id || ''; // 在 RestaurantInfo 介面裡，它是 id，不是 google_place_id
  
  // 組合 Google Maps 連結
  let mapUrl = `https://www.google.com/maps/search/?api=1&query=$${encodeURIComponent(restaurantName)}`; // 修正模板字串的 $ 符號
  if (placeId) {
    mapUrl += `&query_place_id=${placeId}`;
  }

  const shareData = {
    title: '食來運轉 - 今晚吃這個！',
    text: `我剛剛用「食來運轉」抽到了這家餐廳：【${restaurantName}】！\n一起去吃吧 👇\n`,
    url: mapUrl
  };

  // 檢查瀏覽器是否支援 Web Share API
  if (navigator.share) {
    try {
      await navigator.share(shareData);
    } catch (error) {
      console.log('使用者取消分享或分享失敗', error);
    }
  } else {
    // 備用方案：如果是在不支援的桌機瀏覽器，直接複製到剪貼簿
    try {
      await navigator.clipboard.writeText(`${shareData.text}\n${shareData.url}`);
      alert('餐廳資訊已複製到剪貼簿！可以直接貼給朋友囉～'); 
    } catch (error) {
      console.error('複製失敗', error);
      alert('抱歉，分享功能目前無法使用。');
    }
  }
};
</script>

<style src="../style/APP.css" scoped></style>