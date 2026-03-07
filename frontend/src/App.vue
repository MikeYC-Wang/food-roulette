<template>
  <div class="app-container bg-bento-bg">
    
    <header class="pt-16 pb-8 text-center">
      <h1 class="text-5xl font-bold text-gray-800 tracking-widest">食來運轉</h1>
    </header>

    <main class="flex-1 flex flex-col items-center justify-center w-full px-4">
      
      <div class="roulette-placeholder border-4 border-gray-800 bg-white">
        <span class="text-gray-400 font-bold text-xl">輪盤預留區</span>
      </div>

      <button class="spin-btn bg-bento-accent text-white text-3xl font-bold mt-16 py-4 px-12 rounded-xl">
        轉運！
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

  </div>
</template>

<script setup lang="ts">

</script>

<style src="./style/App.css" scoped></style>