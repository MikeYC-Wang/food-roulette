<template>
  <Transition name="fade">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 bg-black/50 z-40 flex flex-col justify-end backdrop-blur-sm"
      @click.self="closeDrawer"
    >
      <Transition name="slide-up" appear>
        <div 
          v-if="isOpen"
          class="bg-bento-bg w-full rounded-t-3xl border-t-4 border-l-4 border-r-4 border-gray-800 p-6 pb-12 shadow-[0px_-4px_0px_0px_rgba(31,41,55,1)] flex flex-col gap-6 max-h-[85vh] overflow-y-auto"
        >
          <div class="flex justify-between items-center mb-2">
            <h2 class="text-2xl font-bold text-gray-800 tracking-wider">篩選條件</h2>
            <button @click="closeDrawer" class="text-gray-800 text-3xl hover:text-bento-accent transition-colors">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-person-walking mr-2"></i>距離範圍</h3>
            <div class="flex gap-4">
              <button 
                v-for="dist in distances" 
                :key="dist.value"
                @click="selectedDistance = dist.value"
                class="filter-chip flex-1 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all"
                :class="selectedDistance === dist.value ? 'bg-bento-primary text-gray-800 chip-active' : 'bg-white text-gray-600 chip-inactive'"
              >
                {{ dist.label }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-utensils mr-2"></i>想吃什麼</h3>
            <div class="flex flex-wrap gap-3">
              <button 
                v-for="type in foodTypes" 
                :key="type"
                @click="toggleSelection(selectedTypes, type)"
                class="filter-chip px-4 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all"
                :class="selectedTypes.includes(type) ? 'bg-bento-secondary text-white chip-active' : 'bg-white text-gray-600 chip-inactive'"
              >
                {{ type }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <h3 class="text-lg font-bold text-gray-700 mb-3"><i class="fa-solid fa-bolt mr-2 text-bento-accent"></i>避雷區</h3>
            <div class="flex flex-wrap gap-3">
              <button 
                v-for="avoid in avoidList" 
                :key="avoid"
                @click="toggleSelection(selectedAvoids, avoid)"
                class="filter-chip px-4 py-2 font-bold rounded-lg border-2 border-gray-800 transition-all"
                :class="selectedAvoids.includes(avoid) ? 'bg-gray-700 text-white chip-active' : 'bg-white text-gray-600 chip-inactive'"
              >
                {{ avoid }}
              </button>
            </div>
          </div>

          <button 
            @click="applyFilters"
            class="mt-4 bg-bento-accent text-white text-2xl font-bold py-3 px-8 rounded-xl border-2 border-gray-800 btn-shadow active:translate-y-1 active:translate-x-1 transition-all"
          >
            確定套用
          </button>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 定義 Props (接收外部控制開啟/關閉的狀態)
defineProps<{
  isOpen: boolean;
}>();

// 定義 Emit (向外傳遞事件)
const emit = defineEmits(['update:isOpen', 'apply']);

// 選項資料預設值
const distances = [
  { label: '500m', value: 500 },
  { label: '1km', value: 1000 },
  { label: '2km', value: 2000 }
];
const foodTypes = ['麵食', '便當', '健康餐', '小吃', '異國料理', '速食'];
const avoidList = ['不吃辣', '不要香菜', '排除連鎖店'];

// 使用者的選擇狀態
const selectedDistance = ref(500);
const selectedTypes = ref<string[]>([]);
const selectedAvoids = ref<string[]>([]);

// 切換複選按鈕的邏輯
const toggleSelection = (list: string[], item: string) => {
  const index = list.indexOf(item);
  if (index === -1) {
    list.push(item);
  } else {
    list.splice(index, 1);
  }
};

// 關閉抽屜
const closeDrawer = () => {
  emit('update:isOpen', false);
};

// 點擊套用
const applyFilters = () => {
  emit('apply', {
    distance: selectedDistance.value,
    types: selectedTypes.value,
    avoids: selectedAvoids.value
  });
  closeDrawer();
};
</script>

<style src="../style/FilterDrawer.css" scoped></style>