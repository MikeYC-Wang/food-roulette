<template>
  <div class="app-container bg-bento-bg relative">
    
    <header class="pt-16 pb-2 text-center">
      <h1 class="text-5xl font-bold text-gray-800 tracking-widest">食來運轉</h1>
      
      <div class="location-status mt-4 flex items-center justify-center gap-2">
        <i :class="statusIconClass" class="text-lg"></i>
        <span class="text-sm font-bold text-gray-600">{{ location.message }}</span>
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-center w-full px-4">
      
      <Roulette ref="rouletteRef" @spin-end="handleSpinEnd" />

      <button 
        @click="triggerSpin"
        :disabled="isSpinning"
        class="spin-btn bg-bento-accent text-white text-3xl font-bold mt-16 py-4 px-12 rounded-xl"
        :class="{ 'opacity-70 cursor-not-allowed transform translate-y-1 shadow-none': isSpinning }"
      >
        {{ isSpinning ? '轉運中...' : '轉運！' }}
      </button>

    </main>

    <footer class="pb-12 pt-6 flex justify-center gap-16 w-full">
      <button @click="isFilterOpen = true" class="bottom-icon-btn text-bento-secondary">
        <i class="fa-solid fa-filter"></i>
      </button>
      <button class="bottom-icon-btn text-bento-primary">
        <i class="fa-solid fa-map-location-dot"></i>
      </button>
    </footer>

    <div v-if="showResult" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm transition-opacity">
      <div class="bg-white w-11/12 max-w-sm rounded-3xl p-6 shadow-2xl transform transition-all border border-gray-100">
        
        <div class="w-20 h-20 mx-auto bg-bento-primary rounded-full flex items-center justify-center -mt-16 mb-4 shadow-lg border-4 border-white">
          <i class="fa-solid fa-utensils text-4xl text-white"></i>
        </div>

        <div class="text-center">
          <h2 class="text-2xl font-black text-gray-800 mb-2 leading-tight">
            {{ selectedFood?.name }}
          </h2>
          
          <div class="flex items-center justify-center space-x-3 text-sm mb-6">
            <span class="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full font-bold flex items-center shadow-sm">
              <i class="fa-solid fa-star mr-1"></i> {{ selectedFood?.rating || '無評分' }}
            </span>
            <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-full font-medium shadow-sm capitalize">
              {{ formatType(selectedFood?.type) }}
            </span>
          </div>
        </div>

        <div class="flex flex-col space-y-3 mt-2">
          <a 
            v-if="selectedFood?.id"
            :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedFood.name)}&query_place_id=${selectedFood.id}`"
            target="_blank"
            rel="noopener noreferrer"
            class="w-full bg-bento-primary text-white font-bold py-3 px-6 rounded-xl hover:bg-opacity-90 transition-all flex items-center justify-center shadow-md"
          >
            <i class="fa-solid fa-map-location-dot mr-2"></i> 帶我去吃！
          </a>
          
          <button 
            @click="closeResult"
            class="w-full bg-gray-100 text-gray-700 font-bold py-3 px-6 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center"
          >
            <i class="fa-solid fa-rotate-right mr-2"></i> 再轉一次
          </button>
        </div>

      </div>
    </div>

    <FilterDrawer 
      v-model:isOpen="isFilterOpen" 
      @apply="handleApplyFilters"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import Roulette from './components/Roulette.vue';
import FilterDrawer from './components/FilterDrawer.vue';
import { useLocation } from './composables/useLocation'; // 引入定位邏輯

// 定義完整的餐廳資料型別
interface RestaurantInfo {
  id?: string;
  name: string;
  type?: string;
  rating?: number;
}

// 定位功能
const { location, getLocation } = useLocation();

// 取得 Roulette 元件的參考，用於呼叫其內部方法
const rouletteRef = ref<InstanceType<typeof Roulette> | null>(null);

// 狀態管理
const isSpinning = ref(false);
const showResult = ref(false);
// 更新：使用 RestaurantInfo 型別替換原本的簡單 string
const selectedFood = ref<RestaurantInfo | null>(null);
const isFilterOpen = ref(false);

// 儲存目前套用的篩選條件 (預設值)
const currentFilters = ref({
  distance: 500,
  types: [] as string[],
  avoids: [] as string[]
});

// 新增：將 Google 傳回的英文類型翻譯成中文的輔助函式
const formatType = (type?: string) => {
  const typeMap: Record<string, string> = {
    restaurant: '餐廳',
    cafe: '咖啡廳',
    bakery: '烘焙坊',
    bar: '酒吧',
    fast_food: '速食',
    meal_takeaway: '外帶',
    meal_delivery: '外送'
  };
  // 找不到對應翻譯時，預設顯示原本的字或「美食」
  return type ? (typeMap[type] || type) : '美食';
};

// 根據定位狀態切換 FontAwesome 圖示
const statusIconClass = computed(() => {
  switch (location.value.status) {
    case 'loading': return 'fa-solid fa-circle-notch fa-spin text-gray-400';
    case 'success': return 'fa-solid fa-location-dot text-bento-secondary';
    case 'default': return 'fa-solid fa-map-pin text-bento-primary';
    case 'error': return 'fa-solid fa-circle-exclamation text-bento-accent';
    default: return 'fa-solid fa-location-crosshairs';
  }
});

/**
 * 向後端抓取餐廳名單並更新轉盤選項
 */
const fetchRestaurants = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8001/api/spin', {
      lat: location.value.lat,
      lng: location.value.lng,
      distance: currentFilters.value.distance,
      types: currentFilters.value.types,
      avoids: currentFilters.value.avoids
    });

    if (response.data.status === 'success' && rouletteRef.value) {
      // 更新輪盤內的餐廳選項
      rouletteRef.value.setOptions(response.data.results);
    }
  } catch (error) {
    console.error('抓取餐廳名單失敗:', error);
  }
};

/**
 * 監聽定位狀態：一旦定位成功或進入預設狀態，立刻抓取餐廳資料
 * 這樣使用者一進來就能看到名單，不用等到按下轉運按鈕
 */
watch(() => location.value.status, (newStatus) => {
  if (newStatus === 'success' || newStatus === 'default') {
    fetchRestaurants();
  }
}, { immediate: true });

// 頁面掛載時自動獲取定位
onMounted(() => {
  getLocation();
});

// 接收來自篩選抽屜的條件並更新狀態
const handleApplyFilters = async (filters: any) => {
  currentFilters.value = filters;
  console.log('篩選條件已更新:', currentFilters.value);
  // 條件更新後，立即重新抓取名單讓轉盤同步更新
  await fetchRestaurants();
};

// 觸發旋轉：啟動輪盤動畫
const triggerSpin = async () => {
  if (isSpinning.value || !rouletteRef.value) return;
  
  isSpinning.value = true;
  showResult.value = false;

  // 旋轉前再次確保名單是最新的
  await fetchRestaurants();
  
  // 呼叫輪盤開始旋轉動畫
  rouletteRef.value.spin();
};

// 輪盤旋轉結束後的處理邏輯
// 更新：將 result 型別改為 RestaurantInfo
const handleSpinEnd = (result: RestaurantInfo) => {
  isSpinning.value = false;
  selectedFood.value = result;
  showResult.value = true; // 顯示結果彈窗
};

// 關閉結果卡片
const closeResult = () => {
  showResult.value = false;
};
</script>

<style src="./style/App.css" scoped></style>