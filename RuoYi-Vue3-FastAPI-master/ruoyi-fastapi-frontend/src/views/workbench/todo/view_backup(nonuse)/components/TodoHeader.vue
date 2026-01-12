<template>
  <div class="todo-header">
    <div class="header-left">
      <h2>我的任务</h2>
    </div>
    <div class="header-right">
      <el-button type="default" :icon="Clock" @click="handleHistoryClick">
        历史任务
      </el-button>
      <el-input
        v-model="searchText"
        placeholder="搜索任务"
        class="search-input"
        :prefix-icon="Search"
        clearable
        @clear="handleSearchClear"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Clock, Search } from '@element-plus/icons-vue'

defineOptions({
  name: 'TodoHeader'
})

const searchText = ref('')

// 历史任务按钮点击（暂时只做样式，功能不实现）
const handleHistoryClick = () => {
  // TODO: 历史任务功能
}

// 搜索框清空
const handleSearchClear = () => {
  // TODO: 搜索功能
}
</script>

<style scoped lang="scss">
.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;

  .header-left {
    h2 {
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;

    .search-input {
      width: 300px;
    }
  }
}
</style>
