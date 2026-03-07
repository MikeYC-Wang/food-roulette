<template>
  <div class="roulette-wrapper">
    <div class="pointer text-bento-accent">
      <i class="fa-solid fa-location-arrow"></i>
    </div>

    <div class="wheel border-4 border-gray-800">
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
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 預設的 6 個選項 (後續會從後端 API 獲取)
const options = ref([
  { name: '控肉飯' },
  { name: '排骨飯' },
  { name: '健康餐' },
  { name: '麵食' },
  { name: '素食' },
  { name: '隨便' }
]);
</script>

<style src="../style/Roulette.css" scoped></style>