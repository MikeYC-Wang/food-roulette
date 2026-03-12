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
        <h3 class="text-lg font-black text-gray-800 mb-2 px-2 flex justify-between items-center">
          <span><i class="fa-solid fa-fire text-red-500 mr-2"></i>手搖飲狂熱度</span>
          <span class="text-xs text-gray-400 font-bold bg-gray-100 px-2 py-1 rounded-md">本月打卡</span>
        </h3>
        <div ref="heatmapChartRef" class="w-full h-56"></div>
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

    <button @click="openRecordModal" class="fixed bottom-6 right-6 z-50 w-14 h-14 bg-bento-accent text-white rounded-full flex items-center justify-center text-2xl border-2 border-gray-800 transition-transform active:scale-90 hover:scale-110" style="box-shadow: 4px 4px 0px 0px rgba(31,41,55,1);">
      <i class="fa-solid fa-plus"></i>
    </button>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm px-4">
      <div class="bg-white w-full max-w-sm rounded-3xl p-6 border-4 border-gray-800 relative shadow-2xl">
        <button @click="showModal = false" class="absolute top-4 right-4 text-gray-400 hover:text-gray-800 text-2xl">
          <i class="fa-solid fa-xmark"></i>
        </button>
        
        <h2 class="text-2xl font-black text-gray-800 mb-6"><i class="fa-solid fa-pen-to-square text-bento-primary mr-2"></i>新增紀錄</h2>
        
        <form @submit.prevent="submitRecord" class="flex flex-col gap-4">
          <div>
            <label class="block text-sm font-bold text-gray-600 mb-1">日期</label>
            <input type="date" v-model="formData.record_date" required class="w-full bg-gray-50 border-2 border-gray-300 rounded-xl px-4 py-2 font-bold text-gray-800 focus:border-bento-primary focus:outline-none" />
          </div>

          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-bold text-gray-600 mb-1">餐別</label>
              <select v-model="formData.meal_type" required class="w-full bg-gray-50 border-2 border-gray-300 rounded-xl px-4 py-2 font-bold text-gray-800 focus:border-bento-primary focus:outline-none appearance-none">
                <option value="早餐">早餐</option>
                <option value="午餐">午餐</option>
                <option value="晚餐">晚餐</option>
                <option value="宵夜">宵夜</option>
                <option value="手搖飲">手搖飲</option>
                <option value="點心">點心</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-bold text-gray-600 mb-1">花費金額</label>
              <div class="relative">
                <span class="absolute left-3 top-2 text-gray-500 font-bold">$</span>
                <input type="number" v-model="formData.price" min="0" required class="w-full bg-gray-50 border-2 border-gray-300 rounded-xl pl-8 pr-4 py-2 font-bold text-gray-800 focus:border-bento-primary focus:outline-none" placeholder="0" />
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-600 mb-1">品項名稱 (如: 珍珠奶茶、排骨飯)</label>
            <input type="text" v-model="formData.food_name" required class="w-full bg-gray-50 border-2 border-gray-300 rounded-xl px-4 py-2 font-bold text-gray-800 focus:border-bento-primary focus:outline-none" placeholder="輸入美食名稱..." />
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-600 mb-1">食物分類</label>
            <div class="relative">
              <select v-model="formData.food_category" required class="w-full bg-gray-50 border-2 border-gray-300 rounded-xl px-4 py-2 pr-10 font-bold text-gray-800 focus:border-bento-primary focus:outline-none appearance-none">
                <option value="便當/米飯">便當/米飯</option>
                <option value="麵食">麵食</option>
                <option value="火鍋/壽喜燒">火鍋/壽喜燒</option>
                <option value="速食/炸物">速食/炸物</option>
                <option value="小吃/滷味">小吃/滷味</option>
                <option value="異國料理">異國料理 (日/韓/泰/義)</option>
                <option value="飲料">飲料 (手搖飲/果汁)</option>
                <option value="咖啡/輕食">咖啡/輕食</option>
                <option value="甜點/冰品">甜點/冰品</option>
                <option value="健康/素食">健康/素食</option>
                <option value="其他">其他</option>
              </select>
              <i class="fa-solid fa-chevron-down absolute right-4 top-3.5 text-gray-400 pointer-events-none"></i>
            </div>
          </div>

          <button type="submit" class="w-full bg-bento-primary text-white font-bold text-lg py-3 rounded-xl border-2 border-gray-800 mt-2 hover:brightness-110 active:translate-y-1 transition-transform" style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);" :disabled="isSubmitting">
            {{ isSubmitting ? '儲存中...' : '儲存紀錄' }}
          </button>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
// 👉 移除了沒用到的 useRouter
import * as echarts from 'echarts';
import api from '../api/axios';
import { toast } from 'vue3-toastify';

// DOM 參考
const pieChartRef = ref<HTMLElement | null>(null);
const barChartRef = ref<HTMLElement | null>(null);
const heatmapChartRef = ref<HTMLElement | null>(null);

// 狀態
const totalSpent = ref(0);
const records = ref<any[]>([]);
const currentMonthStr = ref('');

// 表單狀態
const showModal = ref(false);
const isSubmitting = ref(false);
const formData = ref({
  record_date: '',
  meal_type: '午餐',
  food_name: '',
  food_category: '便當/米飯',
  price: 0
});

// 初始化圖表
const initCharts = () => {
  if (!pieChartRef.value || !barChartRef.value || !heatmapChartRef.value) return;

  const pieChart = echarts.init(pieChartRef.value);
  const barChart = echarts.init(barChartRef.value);
  const heatmapChart = echarts.init(heatmapChartRef.value);

  // 1. 處理圓餅圖資料 👉 (加入 || '未分類' 讓 TypeScript 放心)
  const categoryData: Record<string, number> = {};
  records.value.forEach(r => {
    const cat = r.category || '未分類';
    categoryData[cat] = (categoryData[cat] || 0) + (r.price || 0);
  });
  const pieData = Object.keys(categoryData).map(key => ({ name: key, value: categoryData[key] }));

  // 2. 處理柱狀圖資料 👉 (確保 date 存在才做 split)
  const dateData: Record<string, number> = {};
  records.value.forEach(r => {
    if (r.date) {
      const day = r.date.split('-')[2];
      if (day) {
        dateData[day] = (dateData[day] || 0) + (r.price || 0);
      }
    }
  });
  const xAxisData = Object.keys(dateData).sort();
  const barData = xAxisData.map(day => dateData[day]);

  // 3. 處理熱力圖資料 👉 (加入安全預設值)
  const drinkData: Record<string, number> = {};
  records.value.forEach(r => {
    const cat = r.category || '';
    const name = r.name || '';
    const dateStr = r.date || '';
    
    if (dateStr && (cat.includes('飲料') || r.meal_type === '手搖飲' || name.includes('飲料'))) {
      drinkData[dateStr] = (drinkData[dateStr] || 0) + 1; // 計算當天喝了幾杯
    }
  });
  const heatmapData = Object.entries(drinkData).map(([date, count]) => [date, count]);

  // 設定圓餅圖
  pieChart.setOption({
    color: ['#F4A261', '#2A9D8F', '#E9C46A', '#E76F51', '#3A86FF', '#9C6644'],
    tooltip: { trigger: 'item', formatter: '{b}: ${c} ({d}%)' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      data: pieData.length > 0 ? pieData : [{ name: '尚無資料', value: 0 }]
    }]
  });

  // 設定柱狀圖
  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '12%', right: '5%', bottom: '10%', top: '10%' },
    xAxis: { type: 'category', data: xAxisData.length > 0 ? xAxisData : ['無'], axisLine: { lineStyle: { color: '#1f2937' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [{
      data: barData.length > 0 ? barData : [0], 
      type: 'bar', 
      barWidth: '50%', 
      itemStyle: { 
        borderRadius: [5, 5, 0, 0],
        color: (params: any) => {
          const colorList = ['#F4A261', '#2A9D8F', '#E9C46A', '#E76F51', '#3A86FF', '#9C6644', '#A8DADC', '#457B9D'];
          return colorList[params.dataIndex % colorList.length];
        }
      }
    }]
  });

  // 設定熱力圖 (日曆風格)
  heatmapChart.setOption({
    tooltip: { formatter: (p: any) => `${p.value[0]}: 喝了 ${p.value[1]} 杯` },
    visualMap: {
      show: false, min: 0, max: 3,
      inRange: { color: ['#ebedf0', '#A8DADC', '#457B9D', '#1D3557'] }
    },
    calendar: {
      top: 30, left: 30, right: 30, 
      // 👉 將原本的 ['auto', 20] 改為 ['auto', 28]，讓格子在垂直方向變得更高
      cellSize: ['auto', 28],
      range: currentMonthStr.value,
      itemStyle: { borderWidth: 2, borderColor: '#fff', borderRadius: 4 },
      yearLabel: { show: false },
      dayLabel: { nameMap: 'ZH', color: '#6b7280' },
      monthLabel: { show: false },
      splitLine: { show: false }
    },
    series: { type: 'heatmap', coordinateSystem: 'calendar', data: heatmapData }
  });

  window.addEventListener('resize', () => {
    pieChart.resize(); barChart.resize(); heatmapChart.resize();
  });
};

// 抓取資料
const fetchStats = async () => {
  try {
    const today = new Date();
    currentMonthStr.value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    
    const res = await api.get(`/api/diet/stats?month=${currentMonthStr.value}`);
    if (res.data.status === 'success') {
      totalSpent.value = res.data.total_spent;
      records.value = res.data.records;
      nextTick(() => { initCharts(); });
    }
  } catch (error) {
    console.error('取得統計資料失敗', error);
  }
};

// 打開新增表單 (自動填入今天日期)
const openRecordModal = () => {
  const today = new Date();
  const offset = today.getTimezoneOffset() * 60000;
  const localDate = new Date(today.getTime() - offset).toISOString().split('T')[0];
  
  formData.value.record_date = localDate || '';
  formData.value.food_name = '';
  formData.value.food_category = '便當/米飯';
  formData.value.price = 0;
  showModal.value = true;
};

// 送出新增紀錄
const submitRecord = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  try {
    const res = await api.post('/api/diet/record', formData.value);
    if (res.data.status === 'success') {
      toast.success('紀錄已成功儲存！');
      showModal.value = false;
      fetchStats(); // 重新整理圖表
    }
  } catch (error) {
    toast.error('儲存失敗，請稍後再試');
    console.error('儲存紀錄失敗', error);
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>