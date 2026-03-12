<template>
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-50 flex flex-col justify-end backdrop-blur-sm" @click.self="closeDrawer">
      <Transition name="slide-up" appear>
        <div v-if="isOpen" class="bg-bento-bg w-full rounded-t-3xl border-t-4 border-l-4 border-r-4 border-gray-800 p-6 pb-10 shadow-[0px_-4px_0px_0px_rgba(31,41,55,1)] flex flex-col gap-4" style="height: 85vh;">
          
          <div class="flex justify-between items-center flex-shrink-0">
            <h2 class="text-2xl font-bold text-gray-800 tracking-wider">
              <i class="fa-solid fa-map-location-dot mr-2"></i>美食任意門
            </h2>
            <button @click="closeDrawer" class="text-gray-800 text-3xl hover:text-bento-accent transition-colors">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="relative w-full flex-1 rounded-2xl border-4 border-gray-800 overflow-hidden shadow-sm bg-gray-200" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
             <div id="leaflet-map" class="w-full h-full z-0"></div>
             <div class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center z-10 pb-8">
               <div class="bg-bento-accent text-white px-3 py-1 rounded-full text-xs font-bold mb-1 shadow-md whitespace-nowrap">
                 {{ currentLocName }}
               </div>
               <i class="fa-solid fa-location-dot text-4xl text-bento-accent drop-shadow-[0_4px_2px_rgba(0,0,0,0.5)]"></i>
             </div>
          </div>

          <div class="flex flex-col gap-2 flex-shrink-0 mt-2 relative">
            <div class="flex gap-2 relative z-20">
              <input 
                v-model="searchQuery" 
                @keyup.enter="handleSearch"
                type="text" 
                placeholder="輸入想去的地區 (例如：台北車站)" 
                class="flex-1 bg-white border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors"
              />
              <button 
                @click="handleSearch" 
                :disabled="isSearching || !searchQuery.trim()"
                class="bg-bento-primary text-gray-800 font-bold px-4 rounded-xl border-2 border-gray-800 transition-transform active:translate-y-1 active:translate-x-1 disabled:opacity-50 flex items-center justify-center w-14"
                style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);"
              >
                <i v-if="isSearching" class="fa-solid fa-circle-notch fa-spin"></i>
                <i v-else class="fa-solid fa-magnifying-glass"></i>
              </button>
            </div>
            
            <div v-if="searchResults.length > 0" class="absolute bottom-full mb-2 left-0 right-0 bg-white border-4 border-gray-800 rounded-xl z-30 max-h-48 overflow-y-auto p-2" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);">
              <div class="flex justify-between items-center px-2 pb-2 mb-2 border-b-2 border-gray-100">
                <span class="text-sm font-bold text-gray-500">搜尋結果</span>
                <button @click="searchResults = []" class="text-gray-400 hover:text-gray-800"><i class="fa-solid fa-xmark"></i></button>
              </div>
              <div 
                v-for="(res, idx) in searchResults" :key="idx" 
                @click="selectLocation(res)"
                class="p-2 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
              >
                <div class="font-bold text-gray-800">{{ res.name }}</div>
                <div class="text-xs text-gray-500 truncate">{{ res.address }}</div>
              </div>
            </div>
          </div>

          <button 
            @click="applyNewLocation" 
            class="bg-bento-accent text-white text-xl font-bold py-4 px-8 rounded-xl border-2 border-gray-800 transition-transform active:translate-y-1 active:translate-x-1 flex-shrink-0 mt-2"
            style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);"
          >
            <i class="fa-solid fa-paper-plane mr-2"></i>好，我要吃這附近！
          </button>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps<{ isOpen: boolean; currentLat: number; currentLng: number; }>();
const emit = defineEmits(['update:isOpen', 'apply-location']);

const searchQuery = ref('');
const isSearching = ref(false);
const searchResults = ref<any[]>([]);
const centerLatLng = ref({ lat: 25.0478, lng: 121.5170 });
const currentLocName = ref('目前定位點');

let mapInstance: any = null;

// 👉 動態載入免費的 Leaflet 地圖套件，保持專案乾淨！
const loadLeaflet = async () => {
  if ((window as any).L) return (window as any).L;
  return new Promise((resolve) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(link);

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.onload = () => resolve((window as any).L);
    document.head.appendChild(script);
  });
};

watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    centerLatLng.value = { lat: props.currentLat, lng: props.currentLng };
    const L = await loadLeaflet();
    
    // 稍微等待 Vue 動畫展開完畢，避免地圖尺寸計算錯誤
    setTimeout(() => {
      if (!mapInstance) {
        mapInstance = L.map('leaflet-map', { zoomControl: false }).setView([centerLatLng.value.lat, centerLatLng.value.lng], 16);
        // 使用質感極佳的 Voyager 淺色地圖圖層
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
          attribution: '&copy; OpenStreetMap'
        }).addTo(mapInstance);
        
        // 拖動地圖時，即時更新座標點
        mapInstance.on('moveend', () => {
          const center = mapInstance.getCenter();
          centerLatLng.value = { lat: center.lat, lng: center.lng };
          if (currentLocName.value !== '目前定位點') currentLocName.value = '自訂地圖定位';
        });
      } else {
        mapInstance.invalidateSize();
        mapInstance.setView([centerLatLng.value.lat, centerLatLng.value.lng], 16);
      }
    }, 300);
  } else {
    searchResults.value = [];
    searchQuery.value = '';
  }
});

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;
  isSearching.value = true;
  try {
    const res = await axios.get(`http://127.0.0.1:8001/api/search-location?query=${encodeURIComponent(searchQuery.value)}`);
    if (res.data.status === 'success' && res.data.results.length > 0) {
      searchResults.value = res.data.results;
    } else {
      alert('找不到該地點，請換個關鍵字！');
    }
  } catch (error) {
    console.error('搜尋地點失敗', error);
  } finally {
    isSearching.value = false;
  }
};

const selectLocation = (res: any) => {
  centerLatLng.value = { lat: res.lat, lng: res.lng };
  currentLocName.value = res.name;
  searchQuery.value = res.name;
  searchResults.value = [];
  if (mapInstance) {
    mapInstance.setView([res.lat, res.lng], 16);
  }
};

const closeDrawer = () => emit('update:isOpen', false);

const applyNewLocation = () => {
  emit('apply-location', {
    lat: centerLatLng.value.lat,
    lng: centerLatLng.value.lng,
    name: currentLocName.value
  });
  closeDrawer();
};
</script>