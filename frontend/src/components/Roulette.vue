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
                transform: `translate(-50%, -50%) rotate(${segmentDegree / 2}deg) translateY(-120px)` 
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

const options = ref<RouletteOption[]>([{ name: '載入中...' }]);
const wheelRotation = ref(0);
const isSpinning = ref(false);
const emit = defineEmits<{
  (e: 'spin-end', result: RouletteOption): void
}>();

// 1. 動態計算每一格的角度 (例如：3筆=120度, 6筆=60度)
const segmentDegree = computed(() => {
  const count = options.value.length;
  return count > 0 ? 360 / count : 360;
});

// 2. 動態生成轉盤樣式 (背景顏色與旋轉動畫)
const wheelStyle = computed(() => {
  const colors = ['#E9C46A', '#2A9D8F', '#F4F1DE', '#E76F51', '#A8DADC', '#F1FAEE'];
  const count = options.value.length;
  
  // 使用 CSS conic-gradient 生成動態圓餅圖背景
  let gradientStr = '';
  if (count <= 1) {
    gradientStr = colors[0]!;
  } else {
    const steps = options.value.map((_, i) => {
      const color = colors[i % colors.length];
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
  // 限制最多 6 筆，若無資料則顯示預設
  if (newOptions && newOptions.length > 0) {
    options.value = newOptions.slice(0, 6);
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
  // 隨機決定落點索引
  const prizeIndex = Math.floor(Math.random() * count);
  
  // 3. 解決累積誤差：計算目前旋轉量，並歸零基準點到下一個 360 度
  const currentRotation = wheelRotation.value;
  const baseRotation = Math.ceil(currentRotation / 360) * 360;
  
  // 4. 計算隨機偏移 (讓指針停在扇形中心附近的隨機位置)
  const randomOffset = Math.floor(Math.random() * (segmentDegree.value * 0.6)) - (segmentDegree.value * 0.3);
  
  // 5. 計算總旋轉角度：歸零起點 + 旋轉 5 圈 + 目標格偏移量 + 置中修正 + 隨機偏移
  const targetDegree = baseRotation + 1800 + (360 - (prizeIndex * segmentDegree.value)) - (segmentDegree.value / 2) + randomOffset;

  wheelRotation.value = targetDegree;

  // 4秒動畫結束後發送結果
  setTimeout(() => {
    isSpinning.value = false;
    // 使用 ! 斷言確保 TS 忽略 prizeIndex 可能越界的警告 (邏輯上已保證在範圍內)
    emit('spin-end', options.value[prizeIndex]!);
  }, 4000);
};

// 暴露 API 給父元件 (App.vue)
defineExpose({ spin, setOptions });
</script>

<style src="../style/Roulette.css" scoped></style>