<template>
  <div class="app-container bg-bento-bg relative">
    
    <header class="pt-16 pb-8 text-center">
      <h1 class="text-5xl font-bold text-gray-800 tracking-widest">食來運轉</h1>
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
      <button class="bottom-icon-btn text-bento-secondary">
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

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Roulette from './components/Roulette.vue';

// 取得 Roulette 元件的參考
const rouletteRef = ref<InstanceType<typeof Roulette> | null>(null);

// 狀態管理
const isSpinning = ref(false);
const showResult = ref(false);
const selectedFood = ref<{ name: string } | null>(null);

// 觸發旋轉
const triggerSpin = () => {
  if (isSpinning.value || !rouletteRef.value) return;
  
  isSpinning.value = true;
  showResult.value = false;
  rouletteRef.value.spin(); // 呼叫子元件暴露出來的方法
};

// 旋轉結束後的處理
const handleSpinEnd = (result: { name: string }) => {
  isSpinning.value = false;
  selectedFood.value = result;
  showResult.value = true; // 顯示結果卡片
};

// 關閉結果卡片
const closeResult = () => {
  showResult.value = false;
};
</script>

<style src="./style/App.css" scoped></style>