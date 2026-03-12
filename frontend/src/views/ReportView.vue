<template>
  <div class="app-container bg-bento-bg min-h-screen p-6 pb-24 relative">
    
    <button @click="$router.push('/')" class="absolute top-6 left-6 z-50 w-10 h-10 bg-white border-2 border-gray-800 rounded-xl flex items-center justify-center text-gray-800 transition-transform active:translate-y-1 hover:scale-105" style="box-shadow: 2px 2px 0px 0px rgba(31,41,55,1);">
      <i class="fa-solid fa-chevron-left"></i>
    </button>

    <header class="w-full max-w-2xl mx-auto flex items-center justify-center mb-8 mt-2">
      <h1 class="text-2xl font-black text-gray-800 tracking-widest flex items-center gap-3">
        <i class="fa-solid fa-chart-column text-blue-500"></i> 飲食手札
      </h1>
    </header>

    <main class="w-full max-w-2xl mx-auto flex flex-col gap-8">
      <section class="bg-bento-primary text-white p-6 rounded-3xl border-4 border-gray-800 relative" style="box-shadow: 4px 4px 0px 0px rgba(31,41,55,1);">
        <h2 class="text-lg font-bold mb-1">本月累計花費</h2>
        <div class="text-4xl font-black flex items-baseline gap-2">
          <span class="text-xl">$</span>{{ totalSpent }}
        </div>
        <i class="fa-solid fa-wallet absolute right-6 top-8 text-5xl opacity-20"></i>
      </section>

      <section class="bg-white p-4 rounded-3xl border-[3px] border-gray-800" style="box-shadow: 4px 4px 0px 0px rgba(31,41,55,1);">
        <h3 class="text-lg font-black text-gray-800 mb-2 px-2"><i class="fa-solid fa-chart-pie text-bento-secondary mr-2"></i>吃貨雷達</h3>
        <div ref="pieChartRef" class="w-full h-64"></div>
      </section>

      <section class="bg-white p-4 rounded-3xl border-[3px] border-gray-800" style="box-shadow: 4px 4px 0px 0px rgba(31,41,55,1);">
        <h3 class="text-lg font-black text-gray-800 mb-2 px-2"><i class="fa-solid fa-chart-column text-blue-500 mr-2"></i>每日花費</h3>
        <div ref="barChartRef" class="w-full h-64"></div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import api from '../api/axios';

// DOM 參考
const pieChartRef = ref<HTMLElement | null>(null);
const barChartRef = ref<HTMLElement | null>(null);

// 狀態
const totalSpent = ref(0);
const records = ref<any[]>([]);

// 初始化圖表
const initCharts = () => {
  if (!pieChartRef.value || !barChartRef.value) return;

  const pieChart = echarts.init(pieChartRef.value);
  const barChart = echarts.init(barChartRef.value);

  // 1. 處理圓餅圖資料 (依類別統計花費)
  const categoryData: Record<string, number> = {};
  records.value.forEach(r => {
    categoryData[r.category] = (categoryData[r.category] || 0) + r.price;
  });
  const pieData = Object.keys(categoryData).map(key => ({ name: key, value: categoryData[key] }));

  // 2. 處理柱狀圖資料 (依日期統計花費)
  const dateData: Record<string, number> = {};
  records.value.forEach(r => {
    // 只取 DD 號碼
    const day = r.date.split('-')[2];
    dateData[day] = (dateData[day] || 0) + r.price;
  });
  const xAxisData = Object.keys(dateData).sort();
  const barData = xAxisData.map(day => dateData[day]);

  // 設定圓餅圖 (Bento 風格配色)
  pieChart.setOption({
    color: ['#F4A261', '#2A9D8F', '#E9C46A', '#E76F51', '#3A86FF'],
    tooltip: { trigger: 'item', formatter: '{b}: ${c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      data: pieData.length > 0 ? pieData : [{ name: '尚無資料', value: 0 }]
    }]
  });

  // 設定柱狀圖
  barChart.setOption({
    color: ['#3A86FF'],
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '5%', bottom: '10%', top: '10%' },
    xAxis: { type: 'category', data: xAxisData.length > 0 ? xAxisData : ['無'], axisLine: { lineStyle: { color: '#1f2937' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [{
      data: barData.length > 0 ? barData : [0],
      type: 'bar',
      barWidth: '50%',
      itemStyle: { borderRadius: [5, 5, 0, 0] }
    }]
  });

  // RWD 縮放
  window.addEventListener('resize', () => {
    pieChart.resize();
    barChart.resize();
  });
};

// 抓取後端資料
const fetchStats = async () => {
  try {
    const today = new Date();
    const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    
    // 呼叫後端 API
    const res = await api.get(`/api/diet/stats?month=${month}`);
    if (res.data.status === 'success') {
      totalSpent.value = res.data.total_spent;
      records.value = res.data.records;
      
      // 資料拿回來後畫圖
      initCharts();
    }
  } catch (error) {
    console.error('取得統計資料失敗', error);
  }
};

onMounted(() => {
  fetchStats();
});
</script>