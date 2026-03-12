<template>
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-40 flex flex-col justify-end backdrop-blur-sm" @click.self="closeDrawer">
      <Transition name="slide-up" appear>
        <div v-if="isOpen" class="bg-bento-bg w-full rounded-t-3xl border-t-4 border-l-4 border-r-4 border-gray-800 p-6 pb-12 shadow-[0px_-4px_0px_0px_rgba(31,41,55,1)] flex flex-col gap-6 max-h-[85vh] overflow-y-auto custom-scrollbar">
          
          <div class="flex justify-between items-center mb-2">
            <h2 class="text-2xl font-bold text-gray-800 tracking-wider">篩選條件</h2>
            <button @click="closeDrawer" class="text-gray-800 text-3xl hover:text-bento-accent transition-colors">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="flex gap-4">
            <button @click="selectedOpenNow = !selectedOpenNow" 
                    class="flex-1 py-3 font-bold rounded-xl border-2 border-gray-800 transition-all flex justify-center items-center gap-2"
                    :style="selectedOpenNow ? '' : 'box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);'"
                    :class="selectedOpenNow ? 'bg-green-600 text-white translate-y-1 translate-x-1' : 'bg-white text-gray-700'">
              <i class="fa-solid fa-door-open"></i> 目前營業中
            </button>
            <button @click="selectedHighRating = !selectedHighRating" 
                    class="flex-1 py-3 font-bold rounded-xl border-2 border-gray-800 transition-all flex justify-center items-center gap-2"
                    :style="selectedHighRating ? '' : 'box-shadow: 3px 3px 0px 0px rgba(31, 41, 55, 1);'"
                    :class="selectedHighRating ? 'bg-bento-primary text-gray-900 translate-y-1 translate-x-1' : 'bg-white text-gray-700'">
              <i class="fa-solid fa-star"></i> 4星以上
            </button>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3">
              <i class="fa-solid fa-list-ol mr-2 text-blue-500"></i>要轉幾家餐廳？ (目前: {{ selectedSpinCount }} 家)
            </h3>
            <input 
              type="range" min="2" max="9" step="1" 
              v-model.number="selectedSpinCount" 
              class="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer accent-bento-primary"
            >
            <div class="flex justify-between text-xs font-bold text-gray-500 mt-2">
              <span>2 家</span><span>9 家</span>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-person-walking mr-2"></i>距離範圍</h3>
            <div class="flex gap-4">
              <button v-for="dist in distances" :key="dist.value" @click="selectedDistance = dist.value" class="filter-chip flex-1 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all" :class="selectedDistance === dist.value ? 'bg-bento-primary text-gray-800 chip-active' : 'bg-white text-gray-600 chip-inactive'">
                {{ dist.label }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-sack-dollar mr-2 text-green-600"></i>價位區間</h3>
            <div class="flex flex-wrap gap-2">
              <button v-for="price in priceLevels" :key="price.value" @click="toggleSelection(selectedPrices, price.value)" class="filter-chip px-3 py-2 text-sm font-bold rounded-lg border-2 border-gray-800 transition-all" :class="selectedPrices.includes(price.value) ? 'bg-green-600 text-white chip-active border-green-700' : 'bg-white text-gray-600 chip-inactive'">
                {{ price.label }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-utensils mr-2"></i>想吃什麼</h3>
            <div class="flex flex-wrap gap-3">
              <button v-for="type in foodTypes" :key="type" @click="toggleSelection(selectedTypes, type)" class="filter-chip px-4 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all" :class="selectedTypes.includes(type) ? 'bg-bento-secondary text-white chip-active' : 'bg-white text-gray-600 chip-inactive'">
                {{ type }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-heart mr-2 text-bento-accent"></i>加分條件</h3>
            <div class="flex flex-wrap gap-3">
              <button v-for="feature in featureList" :key="feature" @click="toggleSelection(selectedFeatures, feature)" class="filter-chip px-4 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all" :class="selectedFeatures.includes(feature) ? 'bg-bento-accent text-white chip-active border-bento-accent' : 'bg-white text-gray-600 chip-inactive'">
                {{ feature }}
              </button>
            </div>
          </div>

          <button @click="applyFilters" class="mt-4 bg-bento-accent text-white text-2xl font-bold py-3 px-8 rounded-xl border-2 border-gray-800 btn-shadow active:translate-y-1 active:translate-x-1 transition-all">
            確定套用
          </button>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{ isOpen: boolean; }>();
const emit = defineEmits(['update:isOpen', 'apply']);

const distances = [{ label: '500m', value: 500 }, { label: '1km', value: 1000 }, { label: '2km', value: 2000 }];
const priceLevels = [
  { label: '💰 平價', value: 'PRICE_LEVEL_INEXPENSIVE' },
  { label: '💰💰 中等', value: 'PRICE_LEVEL_MODERATE' },
  { label: '💰💰💰 稍貴', value: 'PRICE_LEVEL_EXPENSIVE' },
  { label: '💰💰💰💰 高級', value: 'PRICE_LEVEL_VERY_EXPENSIVE' }
];

// 擴充了實用選項
const foodTypes = ['麵食', '便當', '健康餐', '小吃', '異國料理', '速食', '素食/蔬食', '吃到飽', '甜點/咖啡廳'];
const featureList = ['有冷氣', '好停車', '寵物友善', '深夜食堂', '網美打卡', '適合聚餐'];

const selectedDistance = ref(500);
const selectedTypes = ref<string[]>([]);
const selectedFeatures = ref<string[]>([]);
const selectedPrices = ref<string[]>([]);
const selectedSpinCount = ref(6);

// 新增狀態綁定
const selectedOpenNow = ref(true);
const selectedHighRating = ref(false);

const toggleSelection = (list: string[], item: string) => {
  const index = list.indexOf(item);
  if (index === -1) list.push(item);
  else list.splice(index, 1);
};

const closeDrawer = () => emit('update:isOpen', false);

const applyFilters = () => {
  emit('apply', {
    distance: selectedDistance.value,
    types: selectedTypes.value,
    features: selectedFeatures.value,
    priceLevels: selectedPrices.value,
    spinCount: selectedSpinCount.value,
    openNow: selectedOpenNow.value, 
    highRating: selectedHighRating.value
  });
  closeDrawer();
};
</script>

<style src="../style/FilterDrawer.css" scoped></style>