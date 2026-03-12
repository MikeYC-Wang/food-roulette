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

    <main class="flex-1 flex flex-col items-center justify-start pt-6 pb-28 w-full px-4 z-20">
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

    <footer class="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-white border-[3px] border-gray-800 rounded-full px-10 py-3 flex justify-center items-center gap-14 z-40" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1); width: max-content;">
      
      <button @click="openAppropriateDrawer" class="text-3xl text-bento-secondary hover:scale-110 transition-transform active:scale-95 drop-shadow-sm">
        <i :class="isCustomMode ? 'fa-solid fa-pen-to-square' : 'fa-solid fa-filter'"></i>
      </button>

      <button @click="handleUserIconClick" class="text-3xl text-gray-700 relative hover:scale-110 transition-transform active:scale-95 drop-shadow-sm">
        <i class="fa-solid fa-user"></i>
        <span v-if="isLoggedIn" class="absolute -top-1 -right-2 block h-4 w-4 rounded-full bg-green-500 border-2 border-white"></span>
      </button>
      
      <button @click="isLocationDrawerOpen = true" class="text-3xl text-bento-primary hover:scale-110 transition-transform active:scale-95 drop-shadow-sm">
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
import { toast } from 'vue3-toastify';
import { ref, onMounted, computed, onUnmounted } from 'vue'; 
import { useRouter } from 'vue-router';
import api from '../api/axios';
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

const handleApplyLocation = async (newLoc: any) => {
  location.value.lat = newLoc.lat;
  location.value.lng = newLoc.lng;
  location.value.message = newLoc.name;
  location.value.status = 'success';
  
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
const favoriteIds = ref<string[]>([]);

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
    const response = await api.post('/api/spin', {
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
  if (localStorage.getItem('token')) {
    try {
      const res = await api.get('/api/custom-list');
      if (res.data.custom_list) {
        customList.value = res.data.custom_list;
      }
    } catch (error) {
      console.error('取得自訂名單失敗', error);
    }
  }
};

const fetchFavorites = async () => {
  if (localStorage.getItem('token')) {
    try {
      const res = await api.get('/api/favorites');
      favoriteIds.value = res.data.favorites.map((f: any) => f.google_place_id);
    } catch (error) {
      console.error('取得收藏名單失敗', error);
    }
  }
};

const toggleFavorite = async () => {
  if (!selectedFood.value || !selectedFood.value.id || isCustomMode.value) return;
  
  if (!localStorage.getItem('token')) {
    toast.info("請先登入才能收藏餐廳喔！");
    return;
  }
  
  try {
    const res = await api.post('/api/favorites/toggle', {
      restaurant_name: selectedFood.value.name,
      google_place_id: selectedFood.value.id
    });
    
    if (res.data.status === 'added') {
      favoriteIds.value.push(selectedFood.value.id);
      toast.success('已加入我的最愛！');
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
  fetchFavorites();

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

  if (localStorage.getItem('token')) {
    try {
      await api.post('/api/custom-list', { restaurants: newList });
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

  confetti({
    particleCount: 150,
    spread: 80,
    origin: { y: 0.55 },
    zIndex: 9999,
    colors: ['#E9C46A', '#2A9D8F', '#E76F51', '#A8DADC', '#4285F4']
  });

  if (localStorage.getItem('token') && result) {
    try {
      await api.post('/api/history', {
        restaurant_name: result.name,
        google_place_id: result.id || ''
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

const shareResult = async () => {
  if (!selectedFood.value) return;

  const restaurantName = selectedFood.value.name;
  const placeId = selectedFood.value.id || ''; 

  let mapUrl = `http://googleusercontent.com/maps.google.com/${encodeURIComponent(restaurantName)}`; 
  if (placeId) {
    mapUrl += `&query_place_id=${placeId}`;
  }

  const shareData = {
    title: '食來運轉 - 今晚吃這個！',
    text: `我剛剛用「食來運轉」抽到了這家餐廳：【${restaurantName}】！\n一起去吃吧 👇\n`,
    url: mapUrl
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
    } catch (error) {
      console.log('使用者取消分享或分享失敗', error);
    }
  } else {
    try {
      await navigator.clipboard.writeText(`${shareData.text}\n${shareData.url}`);
      toast.success('餐廳資訊已複製到剪貼簿！可以直接貼給朋友囉～'); 
    } catch (error) {
      console.error('複製失敗', error);
      toast.error('抱歉，分享功能目前無法使用。');
    }
  }
};
</script>

<style src="../style/APP.css" scoped></style>