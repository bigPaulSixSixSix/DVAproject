<template>
  <div class="app-container">
    <!-- 顶部功能区 -->
    <div class="todo-header-wrapper">
      <TodoHeader title="历史任务" :show-history-button="false" />
    </div>

    <!-- 三列布局 -->
    <el-row :gutter="0" class="todo-layout">
      <!-- 第一列：分类 -->
      <el-col :span="8" class="category-col">
        <el-card shadow="never" class="category-card">
          <div class="panel-header">分类/任务列表</div>
          <CategoryPanel
            :categories="categories"
            :filter-state="filterState"
            @select-category="handleSelectCategory"
          />
          <TaskList
            :tasks="taskList"
            :loading="taskListLoading"
            :selected-task-id="selectedTask?.taskId"
            :is-history="true"
            @select-task="handleSelectTask"
          />
        </el-card>
      </el-col>

      <!-- 第三列：任务详情 -->
      <el-col :span="16" class="task-detail-col">
        <el-card shadow="never" class="task-detail-card">
          <div class="panel-header">明细</div>
          <TaskDetail
            :task-detail="taskDetail"
            :loading="taskDetailLoading"
            @relation-task-click="handleRelationTaskClick"
            @show-history="handleShowHistory"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 其他任务详情弹窗 -->
    <TaskDetailDialog
      v-model="taskDetailDialogVisible"
      :task-id="selectedRelationTaskId"
    />

    <!-- 历史审批记录弹窗 -->
    <HistoryApprovalDialog
      v-model="historyApprovalDialogVisible"
      :history-approval="taskDetail?.historyApproval || []"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import TodoHeader from '../todo/components/TodoHeader.vue'
import CategoryPanel from '../todo/components/CategoryPanel.vue'
import TaskList from '../todo/components/TaskList.vue'
import TaskDetail from '../todo/components/TaskDetail/index.vue'
import TaskDetailDialog from '../todo/components/TaskDetailDialog.vue'
import HistoryApprovalDialog from '../todo/components/TaskDetail/HistoryApprovalDialog.vue'
import { useHistoryTodoData } from './composables/useHistoryTodoData'

defineOptions({
  name: 'HistoryTasks'
})

// 使用历史任务数据管理
const {
  categories,
  filterState,
  taskList,
  taskListLoading,
  selectedTask,
  taskDetail,
  taskDetailLoading,
  loadCategories,
  loadTaskList,
  loadTaskDetail,
  selectCategory,
  selectTask,
  resetFilter
} = useHistoryTodoData()

// 其他任务详情弹窗
const taskDetailDialogVisible = ref(false)
const selectedRelationTaskId = ref(null)
const historyApprovalDialogVisible = ref(false)

// 页面初始化
onMounted(async () => {
  // 加载分类统计
  await loadCategories()
  // 加载任务列表
  await loadTaskList()
})

// 选择分类
const handleSelectCategory = (type, value) => {
  selectCategory(type, value)
}

// 选择任务
const handleSelectTask = async (task) => {
  await selectTask(task)
}

// 前后置任务点击
const handleRelationTaskClick = (task) => {
  selectedRelationTaskId.value = task.taskId
  taskDetailDialogVisible.value = true
}

// 显示历史记录
const handleShowHistory = () => {
  historyApprovalDialogVisible.value = true
}
</script>

<style scoped lang="scss">
.app-container {
  padding: 20px;
  height: calc(100vh - 94px); // 减去顶部导航栏(50px)和标签栏(44px)高度
  display: flex;
  flex-direction: column;
  overflow: hidden; // 禁止整体页面滚动
}

.todo-header-wrapper {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.todo-layout {
  flex: 1;
  min-height: 0; // 允许flex子元素缩小
  overflow: hidden; // 禁止布局区域滚动

  .category-col,
  .task-list-col,
  .task-detail-col {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden; // 禁止列区域滚动
  }

  .category-card,
  .task-list-card,
  .task-detail-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden; // 禁止卡片区域滚动
    border-radius: 0 0 0 0; 

    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      padding: 0 !important;
      overflow: hidden; // 禁止卡片内容区域滚动
    }
  }

  .panel-header {
    font-size: 16px;
    font-weight: 600;
    padding: 16px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    color: var(--el-text-color-primary);
    flex-shrink: 0;
  }
}

.category-card {
  border-radius: 4px 0 0 4px !important;
  margin-right: -1px !important;
}

.task-detail-card{
  border-radius: 0 4px 4px 0 !important;
}
</style>
