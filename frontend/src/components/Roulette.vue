<template>
  <div class="roulette-wrapper">
    <div class="pointer text-bento-accent">
      <i class="fa-solid fa-location-arrow"></i>
    </div>

    <div class="wheel-container border-4 border-gray-800">
      
      <div 
        class="wheel-spin-area"
        :style="wheelStyle"
      >
        <div class="wheel-content">
          <div 
            v-for="(item, index) in options" 
            :key="index"
            class="segment-item"
            :style="{ transform: `rotate(${index * segmentDegree}deg)` }"
          >
            <div 
              class="item-text text-gray-800 font-bold"
              :style="{ 
                /* 配合 480px 轉盤，將位移調整至 -150px 讓文字分佈更均勻 */
                transform: `translate(-50%, -50%) rotate(${options.length === 1 ? 0 : segmentDegree / 2}deg) translateY(-150px)`,
                fontSize: '18px'
              }"
            >
              {{ item.name }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// 定義資料型別
interface RouletteOption {
  name: string;
  type?: string;
  rating?: number;
}

// 定義 Props，接收外部傳入的顏色清單
const props = defineProps<{
  colors?: string[];
}>();

const emit = defineEmits<{
  (e: 'spin-end', result: RouletteOption): void
}>();

// 預設配色 (美食模式)
const defaultColors = ['#E9C46A', '#2A9D8F', '#F4F1DE', '#E76F51', '#A8DADC', '#F1FAEE'];

const options = ref<RouletteOption[]>([{ name: '等待設定中...' }]);
const wheelRotation = ref(0);
const isSpinning = ref(false);

// 1. 動態計算每一格的角度
const segmentDegree = computed(() => {
  const count = options.value.length;
  return count > 0 ? 360 / count : 360;
});

// 2. 動態生成轉盤樣式 (連動模式顏色)
const wheelStyle = computed(() => {
  // 優先使用 props 傳進來的顏色，若無則使用預設色
  const activeColors = props.colors && props.colors.length > 0 ? props.colors : defaultColors;
  const count = options.value.length;
  
  let gradientStr = '';
  if (count <= 1) {
    gradientStr = activeColors[0]!;
  } else {
    const steps = options.value.map((_, i) => {
      // 根據索引從色卡中取色
      const color = activeColors[i % activeColors.length]!;
      const start = i * segmentDegree.value;
      const end = (i + 1) * segmentDegree.value;
      return `${color} ${start}deg ${end}deg`;
    });
    gradientStr = `conic-gradient(${steps.join(', ')})`;
  }

  return {
    transform: `rotate(${wheelRotation.value}deg)`,
    transition: isSpinning.value ? 'transform 4s cubic-bezier(0.25, 0.1, 0.15, 1)' : 'none',
    background: gradientStr
  };
});

/**
 * 外部呼叫：設定新的餐廳清單
 */
const setOptions = (newOptions: RouletteOption[]) => {
  if (newOptions && newOptions.length > 0) {
    options.value = newOptions; 
  } else {
    options.value = [{ name: '附近沒找到美食', type: 'N/A', rating: 0 }];
  }
};

/**
 * 執行轉運旋轉
 */
const spin = () => {
  if (isSpinning.value || options.value.length === 0) return;
  isSpinning.value = true;

  const count = options.value.length;
  const prizeIndex = Math.floor(Math.random() * count);
  
  const currentRotation = wheelRotation.value;
  // 確保旋轉角度是累加的，避免轉盤倒轉
  const baseRotation = Math.ceil(currentRotation / 360) * 360;
  
  // 增加一點隨機偏移，讓指針不會每次都指在正中間
  const randomOffset = Math.floor(Math.random() * (segmentDegree.value * 0.6)) - (segmentDegree.value * 0.3);
  
  // 計算目標角度 (轉 5 圈 + 目標格位置)
  const targetDegree = baseRotation + 1800 + (360 - (prizeIndex * segmentDegree.value)) - (segmentDegree.value / 2) + randomOffset;

  wheelRotation.value = targetDegree;

  setTimeout(() => {
    isSpinning.value = false;
    emit('spin-end', options.value[prizeIndex]!);
  }, 4000);
};

defineExpose({ spin, setOptions });
</script>

<style src="../style/Roulette.css" scoped></style>