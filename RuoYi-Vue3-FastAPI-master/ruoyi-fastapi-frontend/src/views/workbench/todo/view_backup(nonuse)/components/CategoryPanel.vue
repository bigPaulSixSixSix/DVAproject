<template>
  <div class="category-panel">
    <!-- 顶部全部选项 -->
    <div class="category-all-row">
      <div
        class="category-item"
        :class="{ active: isActive('project', null) }"
        @click="handleSelectCategory('project', null)"
      >
        <span class="category-name">全部项目</span>
        <span class="category-count">{{ getTotal('project') }}</span>
      </div>
      <div
        class="category-item"
        :class="{ active: isActive('department', null) }"
        @click="handleSelectCategory('department', null)"
      >
        <span class="category-name">全部部门</span>
        <span class="category-count">{{ getTotal('department') }}</span>
      </div>
      <div
        class="category-item"
        :class="{ active: isActive('status', null) }"
        @click="handleSelectCategory('status', null)"
      >
        <span class="category-name">全部状态</span>
        <span class="category-count">{{ getTotal('status') }}</span>
      </div>
    </div>

    <!-- 三列布局 -->
    <div class="category-columns">
      <!-- 项目列 -->
      <div class="category-column">
        <div class="category-list">
          <div
            v-for="item in getItems('project')"
            :key="getItemId(item, 'project')"
            class="category-item"
            :class="{ active: isActive('project', getItemId(item, 'project')) }"
            @click="handleSelectCategory('project', getItemId(item, 'project'))"
          >
            <span class="category-name">{{ getItemName(item, 'project') }}</span>
            <span class="category-count">{{ item.count }}</span>
          </div>
        </div>
      </div>

      <!-- 部门列 -->
      <div class="category-column">
        <div class="category-list">
          <div
            v-for="item in getItems('department')"
            :key="getItemId(item, 'department')"
            class="category-item"
            :class="{ active: isActive('department', getItemId(item, 'department')) }"
            @click="handleSelectCategory('department', getItemId(item, 'department'))"
          >
            <span class="category-name">{{ getItemName(item, 'department') }}</span>
            <span class="category-count">{{ item.count }}</span>
          </div>
        </div>
      </div>

      <!-- 状态列 -->
      <div class="category-column">
        <div class="category-list">
          <div
            v-for="item in getItems('status')"
            :key="getItemId(item, 'status')"
            class="category-item"
            :class="{ active: isActive('status', getItemId(item, 'status')) }"
            @click="handleSelectCategory('status', getItemId(item, 'status'))"
          >
            <span class="category-name">{{ getItemName(item, 'status') }}</span>
            <span class="category-count">{{ item.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'CategoryPanel'
})

const props = defineProps({
  categories: {
    type: Object,
    required: true
  },
  filterState: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['select-category'])

// 获取分类项列表
const getItems = (type) => {
  return props.categories[type]?.items || []
}

// 获取总数
const getTotal = (type) => {
  return props.categories[type]?.total || 0
}

// 获取项目ID
const getItemId = (item, type) => {
  if (type === 'project') return item.projectId
  if (type === 'department') return item.deptId
  if (type === 'status') return item.status
  return null
}

// 获取项目名称
const getItemName = (item, type) => {
  if (type === 'project') return item.projectName
  if (type === 'department') return item.deptName
  if (type === 'status') return item.statusName
  return ''
}

// 判断是否激活
const isActive = (type, value) => {
  if (type === 'project') return props.filterState.projectId === value
  if (type === 'department') return props.filterState.deptId === value
  if (type === 'status') return props.filterState.taskStatus === value
  return false
}

// 选择分类
const handleSelectCategory = (type, value) => {
  emit('select-category', type, value)
}
</script>

<style scoped lang="scss">
.category-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden; // 禁止面板整体滚动

  // 统一的分类项样式
  .category-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 12px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background-color: var(--el-fill-color-light);
    }

    &.active {
      background-color: var(--el-fill-color-light);
      color: var(--el-color-primary);
      font-weight: 500;
    }

    .category-name {
      flex: 1;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }

    .category-count {
      font-size: 12px;
      color: var(--el-text-color-primary);
      margin-left: 8px;
    }

    &.active {
      .category-name,
      .category-count {
        color: var(--el-color-primary);
      }
    }
  }

  .category-all-row {
    display: flex;
    flex-direction: row;
    gap: 0;

    .category-item {
      flex: 1;
      border-right: 1px solid var(--el-border-color-lighter);
      flex-direction: row;

      &:last-child {
        margin-right: 0;
        border-right: 0;
      }
    }
  }

  .category-columns {
    flex: 1;
    display: flex;
    gap: 0;
    overflow: hidden;

    .category-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--el-border-color-lighter);
      overflow-y: auto;

      &:last-child {
        border-right: none;
      }

      .category-list {
        flex: 1;
        overflow-y: auto;
      }
    }
  }
}
</style>
