<template>
  <div class="category-panel">
    <!-- 项目行 -->
    <div 
      class="category-row"
      :style="{ gridTemplateColumns: getRowGridTemplate('project') }"
    >
      <!-- 全部项目 -->
      <div
        class="category-item category-item--all"
        :class="{ active: isActive('project', null) }"
        @click="handleSelectCategory('project', null)"
      >
        <span class="category-name">全部项目</span>
        <span class="category-count">{{ getTotal('project') }}</span>
      </div>
      <!-- 具体项目 -->
      <div
        v-for="item in getItems('project')"
        :key="getItemId(item, 'project')"
        class="category-item category-item--specific"
        :class="{ active: isActive('project', getItemId(item, 'project')) }"
        @click="handleSelectCategory('project', getItemId(item, 'project'))"
      >
        <span class="category-name">{{ getItemName(item, 'project') }}</span>
        <span class="category-count">{{ item.count }}</span>
      </div>
    </div>

    <!-- 部门行 -->
    <div 
      class="category-row"
      :style="{ gridTemplateColumns: getRowGridTemplate('department') }"
    >
      <!-- 全部部门 -->
      <div
        class="category-item category-item--all"
        :class="{ active: isActive('department', null) }"
        @click="handleSelectCategory('department', null)"
      >
        <span class="category-name">全部部门</span>
        <span class="category-count">{{ getTotal('department') }}</span>
      </div>
      <!-- 具体部门 -->
      <div
        v-for="item in getItems('department')"
        :key="getItemId(item, 'department')"
        class="category-item category-item--specific"
        :class="{ active: isActive('department', getItemId(item, 'department')) }"
        @click="handleSelectCategory('department', getItemId(item, 'department'))"
      >
        <span class="category-name">{{ getItemName(item, 'department') }}</span>
        <span class="category-count">{{ item.count }}</span>
      </div>
    </div>

    <!-- 状态行 -->
    <div 
      class="category-row"
      :style="{ gridTemplateColumns: getRowGridTemplate('status') }"
    >
      <!-- 全部状态 -->
      <div
        class="category-item category-item--all"
        :class="{ active: isActive('status', null) }"
        @click="handleSelectCategory('status', null)"
      >
        <span class="category-name">全部状态</span>
        <span class="category-count">{{ getTotal('status') }}</span>
      </div>
      <!-- 具体状态 -->
      <div
        v-for="item in getItems('status')"
        :key="getItemId(item, 'status')"
        class="category-item category-item--specific"
        :class="{ active: isActive('status', getItemId(item, 'status')) }"
        @click="handleSelectCategory('status', getItemId(item, 'status'))"
      >
        <span class="category-name">{{ getItemName(item, 'status') }}</span>
        <span class="category-count">{{ item.count }}</span>
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

// 获取每行的总标签数（1个"全部" + 具体分类数量）
const getRowItemCount = (type) => {
  const itemsCount = getItems(type).length
  return 1 + itemsCount // 1个"全部" + 具体分类数量
}

// 获取所有行中元素最多的数量（包括"全部"）
const getMaxRowItemCount = () => {
  const projectCount = getRowItemCount('project')
  const departmentCount = getRowItemCount('department')
  const statusCount = getRowItemCount('status')
  return Math.max(projectCount, departmentCount, statusCount)
}

// 获取每行的 Grid 模板列定义
const getRowGridTemplate = (type) => {
  const maxCount = getMaxRowItemCount()
  const currentRowCount = getRowItemCount(type)
  const specificItemsCount = getItems(type).length
  
  // 计算基准宽度（基于最多元素的数量）
  const baseWidthPercent = 100 / maxCount
  
  // "全部"按钮固定为基准宽度
  const allWidth = `${baseWidthPercent}%`
  
  // 剩余空间（100% - "全部"的宽度）
  const remainingWidth = 100 - baseWidthPercent
  
  // 具体分类项平分剩余空间
  const specificWidth = specificItemsCount > 0 
    ? `${remainingWidth / specificItemsCount}%` 
    : '0'
  
  // 构建 grid-template-columns
  // 格式: "20% 40% 40%" 或 "20% 20% 20% 20% 20%" 等
  const columns = [allWidth]
  for (let i = 0; i < specificItemsCount; i++) {
    columns.push(specificWidth)
  }
  
  return columns.join(' ')
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
  display: flex;
  flex-direction: column;
  margin-top: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  height: fit-content;
  margin-left: 16px;
  margin-right: 16px;
  gap: 8px;

  // 每一行使用 Grid 布局，让所有标签平均分布
  .category-row {
    display: grid;
    gap: 4px;
    width: 100%;
  }

  // 统一的分类项样式
  .category-item {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    cursor: pointer;
    transition: all 0.2s;
    border-radius: 4px;
    border: 1px solid var(--el-border-color-lighter);
    height: fit-content;

    &:hover {
      background-color: var(--el-fill-color-light);
    }

    &.active {
      background-color: var(--el-color-primary);
      font-weight: 500;
    }

    .category-name {
      font-size: 14px;
      color: var(--el-text-color-primary);
    }

    .category-count {
      font-size: 12px;
      color: var(--el-text-color-primary);
      margin-left: 4px;
    }

    &.active {
      .category-name,
      .category-count {
        color: var(--el-fill-color) !important;
      }
    }
  }
}
</style>
