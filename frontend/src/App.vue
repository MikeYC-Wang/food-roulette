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

    <div 
      v-if="showResult" 
      class="absolute inset-0 bg-black/40 flex items-center justify-center z-50 backdrop-blur-sm"
    >
      <div class="bg-bento-bg border-4 border-gray-800 p-8 rounded-2xl text-center shadow-[8px_8px_0px_0px_rgba(31,41,55,1)] max-w-sm w-[90%] transform transition-all">
        <h2 class="text-2xl text-gray-600 font-bold mb-2">上天決定讓你吃</h2>
        <p class="text-5xl font-bold text-bento-accent tracking-widest mb-8 mt-4">{{ selectedFood?.name }}</p>
        <button 
          @click="closeResult"
          class="spin-btn w-full bg-bento-secondary text-white text-2xl font-bold py-3 rounded-xl"
        >
          太棒了！
        </button>
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

// 定位功能
const { location, getLocation } = useLocation(); //

// 取得 Roulette 元件的參考，用於呼叫其內部方法
const rouletteRef = ref<InstanceType<typeof Roulette> | null>(null);

// 狀態管理
const isSpinning = ref(false);
const showResult = ref(false);
const selectedFood = ref<{ name: string } | null>(null);
const isFilterOpen = ref(false);

// 儲存目前套用的篩選條件 (預設值)
const currentFilters = ref({
  distance: 500,
  types: [] as string[],
  avoids: [] as string[]
});

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
    // 使用先前修正過的 8001 埠號
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
const handleSpinEnd = (result: { name: string }) => {
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