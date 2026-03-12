<template>
  <Transition name="fade">
    <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-40 flex flex-col justify-end backdrop-blur-sm" @click.self="closeDrawer">
      <Transition name="slide-up" appear>
        <div v-if="isOpen" class="bg-bento-bg w-full rounded-t-3xl border-t-4 border-l-4 border-r-4 border-gray-800 p-6 pb-12 shadow-[0px_-4px_0px_0px_rgba(31,41,55,1)] flex flex-col gap-4 max-h-[85vh]">
          
          <div class="flex justify-between items-center mb-2">
            <h2 class="text-2xl font-bold text-gray-800 tracking-wider">自訂口袋名單</h2>
            <button @click="closeDrawer" class="text-gray-800 text-3xl hover:text-bento-accent transition-colors">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <div class="flex gap-2">
            <input 
              v-model="newItemName" 
              @keyup.enter="addItem"
              type="text" 
              placeholder="輸入餐廳名稱..." 
              class="flex-1 bg-white border-2 border-gray-800 rounded-xl px-4 py-3 font-bold focus:outline-none focus:border-bento-primary transition-colors"
              :disabled="customList.length >= 9"
            />
            <button 
              @click="addItem" 
              :disabled="!newItemName.trim() || customList.length >= 9"
              class="bg-bento-primary text-gray-800 font-bold px-4 rounded-xl border-2 border-gray-800 transition-transform active:translate-y-1 active:translate-x-1 disabled:opacity-50"
              style="box-shadow: 2px 2px 0px 0px rgba(31, 41, 55, 1);"
            >
              <i class="fa-solid fa-plus"></i> 新增
            </button>
          </div>

          <p class="text-xs text-gray-500 font-bold text-right -mt-2">最多 9 家，目前：{{ customList.length }} 家</p>

          <div class="flex flex-col gap-3 overflow-y-auto flex-1 custom-scrollbar pr-2 min-h-[200px] pt-2 -mt-2">
            <div v-if="customList.length === 0" class="text-center text-gray-400 font-bold py-8">
              還沒有名單喔，趕快在上面輸入吧！
            </div>
            
            <div 
              v-for="(item, index) in customList" 
              :key="index"
              class="bg-white p-3 rounded-xl border-2 border-gray-800 flex justify-between items-center transition-transform hover:-translate-y-1 hover:shadow-sm relative"
            >
              <span class="font-bold text-gray-800 flex-1 truncate pr-2">{{ index + 1 }}. {{ item }}</span>
              <button @click="removeItem(index)" class="text-red-500 hover:text-red-700 p-1">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          </div>

          <button 
            @click="applyCustomList" 
            :disabled="customList.length < 2"
            class="mt-2 bg-bento-accent text-white text-2xl font-bold py-3 px-8 rounded-xl border-2 border-gray-800 transition-transform active:translate-y-1 active:translate-x-1 disabled:opacity-50 disabled:cursor-not-allowed"
            style="box-shadow: 4px 4px 0px 0px rgba(31, 41, 55, 1);"
          >
            {{ customList.length < 2 ? '請至少輸入 2 家' : '確定並準備轉運' }}
          </button>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{ isOpen: boolean; initialList: string[] }>();
const emit = defineEmits(['update:isOpen', 'apply']);

const newItemName = ref('');
const customList = ref<string[]>([]);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    customList.value = [...props.initialList];
    newItemName.value = '';
  }
});

const addItem = () => {
  if (newItemName.value.trim() && customList.value.length < 9) {
    customList.value.push(newItemName.value.trim());
    newItemName.value = '';
  }
};

const removeItem = (index: number) => {
  customList.value.splice(index, 1);
};

const closeDrawer = () => emit('update:isOpen', false);

const applyCustomList = () => {
  if (customList.value.length >= 2) {
    emit('apply', customList.value);
    closeDrawer();
  }
};
</script>

<style src="../style/CustomListDrawer.css" scoped></style>