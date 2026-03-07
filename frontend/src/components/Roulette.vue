<template>
  <div class="roulette-wrapper">
    <div class="pointer text-bento-accent">
      <i class="fa-solid fa-location-arrow"></i>
    </div>

    <div class="wheel-container border-4 border-gray-800">
      
      <div 
        class="wheel-spin-area"
        :style="{
          transform: `rotate(${wheelRotation}deg)`,
          transition: isSpinning ? 'transform 4s cubic-bezier(0.25, 0.1, 0.15, 1)' : 'none'
        }"
      >
        <div class="wheel-content">
          <div 
            v-for="(item, index) in options" 
            :key="index"
            class="segment-item"
            :style="{ transform: `rotate(${index * 60}deg)` }"
          >
            <div class="item-text text-gray-800 font-bold">
              {{ item.name }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 預設選項
const options = ref([
  { name: '控肉飯' },
  { name: '排骨飯' },
  { name: '健康餐' },
  { name: '麵食' },
  { name: '素食' },
  { name: '隨便' }
]);

const wheelRotation = ref(0);
const isSpinning = ref(false);
const emit = defineEmits(['spin-end']);

const spin = () => {
  if (isSpinning.value) return;
  isSpinning.value = true;

  const prizeIndex = Math.floor(Math.random() * options.value.length);
  const randomOffset = Math.floor(Math.random() * 30) - 15;
  const targetDegree = wheelRotation.value + 1800 + (360 - (prizeIndex * 60)) - 30 + randomOffset;

  wheelRotation.value = targetDegree;

  setTimeout(() => {
    isSpinning.value = false;
    emit('spin-end', options.value[prizeIndex]);
  }, 4000);
};

const setOptions = (newOptions: { name: string }[]) => {
  options.value = newOptions;
};

defineExpose({ spin, setOptions });

</script>

<style src="../style/Roulette.css" scoped></style>