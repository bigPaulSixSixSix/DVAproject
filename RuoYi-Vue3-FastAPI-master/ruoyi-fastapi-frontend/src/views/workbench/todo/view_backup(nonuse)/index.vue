<template>
  <div class="app-container">
    <!-- 顶部功能区 -->
    <div class="todo-header-wrapper">
      <TodoHeader />
    </div>

    <!-- 三列布局 -->
    <el-row :gutter="0" class="todo-layout">
      <!-- 第一列：分类 -->
      <el-col :span="5" class="category-col">
        <el-card shadow="never" class="category-card">
          <div class="panel-header">分类</div>
          <CategoryPanel
            :categories="categories"
            :filter-state="filterState"
            @select-category="handleSelectCategory"
          />
        </el-card>
      </el-col>

      <!-- 第二列：任务列表 -->
      <el-col :span="8" class="task-list-col">
        <el-card shadow="never" class="task-list-card">
          <div class="panel-header">任务</div>
          <TaskList
            :tasks="taskList"
            :loading="taskListLoading"
            :selected-task-id="selectedTask?.taskId"
            :total="taskListTotal"
            :current-page="taskListQuery.pageNum"
            :page-size="taskListQuery.pageSize"
            @select-task="handleSelectTask"
            @page-change="handlePageChange"
            @size-change="handleSizeChange"
          />
        </el-card>
      </el-col>

      <!-- 第三列：任务详情 -->
      <el-col :span="11" class="task-detail-col">
        <el-card shadow="never" class="task-detail-card">
          <div class="panel-header">明细</div>
          <TaskDetail
            :task-detail="taskDetail"
            :loading="taskDetailLoading"
            @submit="handleSubmit"
            @approve="handleApprove"
            @reject="handleReject"
            @resubmit="handleResubmit"
            @relation-task-click="handleRelationTaskClick"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 其他任务详情弹窗 -->
    <TaskDetailDialog
      v-model="taskDetailDialogVisible"
      :task-id="selectedRelationTaskId"
    />
  </div>
</template>

<script setup>
import { onMounted, watch, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import TodoHeader from './components/TodoHeader.vue'
import CategoryPanel from './components/CategoryPanel.vue'
import TaskList from './components/TaskList.vue'
import TaskDetail from './components/TaskDetail/index.vue'
import TaskDetailDialog from './components/TaskDetailDialog.vue'
import { useTodoData } from './composables/useTodoData'
import { useTaskOperations } from './composables/useTaskOperations'

defineOptions({
  name: 'MyTasks'
})

// 使用数据管理
const {
  categories,
  filterState,
  taskList,
  taskListLoading,
  taskListTotal,
  taskListQuery,
  selectedTask,
  taskDetail,
  taskDetailLoading,
  loadCategories,
  loadTaskList,
  loadTaskDetail,
  selectCategory,
  selectTask,
  resetFilter
} = useTodoData()

// 使用任务操作
const {
  confirmSubmit,
  confirmApprove,
  confirmReject
} = useTaskOperations()

// 其他任务详情弹窗
const taskDetailDialogVisible = ref(false)
const selectedRelationTaskId = ref(null)

// 页面初始化
onMounted(async () => {
  // 加载分类统计
  await loadCategories()
  // 加载任务列表
  await loadTaskList()
  // 默认选中第一个任务
  if (taskList.value.length > 0) {
    await selectTask(taskList.value[0])
  }
})

// 选择分类
const handleSelectCategory = (type, value) => {
  selectCategory(type, value)
  // 如果有任务，选中第一个
  if (taskList.value.length > 0) {
    selectTask(taskList.value[0])
  }
}

// 选择任务
const handleSelectTask = async (task) => {
  await selectTask(task)
}

// 分页变化
const handlePageChange = async (page) => {
  taskListQuery.pageNum = page
  await loadTaskList()
  // 如果有任务，选中第一个
  if (taskList.value.length > 0) {
    await selectTask(taskList.value[0])
  } else {
    selectedTask.value = null
    taskDetail.value = null
  }
}

// 每页数量变化
const handleSizeChange = async (size) => {
  taskListQuery.pageSize = size
  taskListQuery.pageNum = 1
  await loadTaskList()
  // 如果有任务，选中第一个
  if (taskList.value.length > 0) {
    await selectTask(taskList.value[0])
  } else {
    selectedTask.value = null
    taskDetail.value = null
  }
}

// 提交任务
const handleSubmit = async () => {
  if (!taskDetail.value || !taskDetail.value.taskInfo) return
  
  try {
    const { value: submitText } = await ElMessageBox.prompt(
      '请输入提交内容',
      '提交任务',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '请填写任务完成情况...',
        inputValidator: (value) => {
          if (!value || !value.trim()) {
            return '提交内容不能为空'
          }
          return true
        }
      }
    )
    
    const success = await confirmSubmit(
      taskDetail.value.taskInfo.taskId,
      submitText,
      taskDetail.value.taskInfo.taskStatus
    )
    
    if (success) {
      // 刷新数据
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  } catch {
    // 用户取消
  }
}

// 审批通过
const handleApprove = async () => {
  if (!taskDetail.value || !taskDetail.value.approvalFlow) return
  
  try {
    const { value: approvalComment } = await ElMessageBox.prompt(
      '请输入审批意见（可选）',
      '审批通过',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '同意（可选）'
      }
    )
    
    const success = await confirmApprove(
      taskDetail.value.approvalFlow.applyId,
      approvalComment || '同意'
    )
    
    if (success) {
      // 刷新数据
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  } catch {
    // 用户取消
  }
}

// 驳回
const handleReject = async () => {
  if (!taskDetail.value || !taskDetail.value.approvalFlow) return
  
  const success = await confirmReject(taskDetail.value.approvalFlow.applyId)
  
  if (success) {
    // 刷新数据
    await loadTaskList()
    await loadTaskDetail(taskDetail.value.taskInfo.taskId)
  }
}

// 重新提交
const handleResubmit = async () => {
  if (!taskDetail.value || !taskDetail.value.taskInfo) return
  
  try {
    const { value: submitText } = await ElMessageBox.prompt(
      '请输入重新提交内容',
      '重新提交任务',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '请填写任务完成情况...',
        inputValidator: (value) => {
          if (!value || !value.trim()) {
            return '提交内容不能为空'
          }
          return true
        }
      }
    )
    
    const success = await confirmSubmit(
      taskDetail.value.taskInfo.taskId,
      submitText,
      taskDetail.value.taskInfo.taskStatus
    )
    
    if (success) {
      // 刷新数据
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  } catch {
    // 用户取消
  }
}

// 前后置任务点击
const handleRelationTaskClick = (task) => {
  selectedRelationTaskId.value = task.taskId
  taskDetailDialogVisible.value = true
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
  margin-left: -1px !important;
}
</style>
