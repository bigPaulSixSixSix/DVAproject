<template>
  <div class="app-container">
    <!-- 顶部功能区 -->
    <div class="todo-header-wrapper">
      <TodoHeader />
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
            @select-task="handleSelectTask"
          />
        </el-card>

      </el-col>

      <!-- 第二列：任务列表 -->
      <!-- <el-col :span="8" class="task-list-col">
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
      </el-col> -->

      <!-- 第三列：任务详情 -->
      <el-col :span="16" class="task-detail-col">
        <el-card shadow="never" class="task-detail-card">
          <div class="panel-header">明细</div>
          <TaskDetail
            :task-detail="taskDetail"
            :loading="taskDetailLoading"
            @submit="handleSubmit"
            @approve="handleApprove"
            @resubmit="handleResubmit"
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
import { onMounted, watch, ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import TodoHeader from './components/TodoHeader.vue'
import CategoryPanel from './components/CategoryPanel.vue'
import TaskList from './components/TaskList.vue'
import TaskDetail from './components/TaskDetail/index.vue'
import TaskDetailDialog from './components/TaskDetailDialog.vue'
import HistoryApprovalDialog from './components/TaskDetail/HistoryApprovalDialog.vue'
import { useTodoData } from './composables/useTodoData'
import { useTaskOperations } from './composables/useTaskOperations'
import { rejectTask, resubmitTask } from '@/api/todo'

defineOptions({
  name: 'MyTasks'
})

// 使用数据管理
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
const historyApprovalDialogVisible = ref(false)

// 页面初始化
onMounted(async () => {
  // 加载分类统计
  await loadCategories()
  // 加载任务列表
  await loadTaskList()
  // 不自动选中任务，等待用户点击
})

// 选择分类
const handleSelectCategory = (type, value) => {
  selectCategory(type, value)
  // 不自动选中任务，等待用户点击
}

// 选择任务
const handleSelectTask = async (task) => {
  await selectTask(task)
}

// 提交任务
const handleSubmit = async (submitText) => {
  if (!taskDetail.value || !taskDetail.value.taskInfo) return
  
  if (!submitText || !submitText.trim()) {
    ElMessage.warning('请填写完成情况')
    return
  }
  
  const success = await confirmSubmit(
    taskDetail.value.taskInfo.taskId,
    submitText,
    taskDetail.value.taskInfo.taskStatus
  )
  
  if (success) {
    // 刷新数据
    await loadCategories() // 刷新分类统计
    await loadTaskList()
    await loadTaskDetail(taskDetail.value.taskInfo.taskId)
  }
}

// 审批（统一处理通过和驳回）
const handleApprove = async (approvalData) => {
  if (!taskDetail.value || !taskDetail.value.approvalFlow) return
  if (!approvalData) return
  
  const { result, comment, images } = approvalData
  
  if (result === 'approve') {
    // 审批通过
    const success = await confirmApprove(
      taskDetail.value.approvalFlow.applyId,
      comment || '同意'
    )
    
    if (success) {
      // 刷新数据
      await loadCategories() // 刷新分类统计
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  } else if (result === 'reject') {
    // 审批驳回
    const success = await handleReject(
      taskDetail.value.approvalFlow.applyId,
      comment,
      images
    )
    
    if (success) {
      // 刷新数据
      await loadCategories() // 刷新分类统计
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  }
}

// 审批驳回（内部方法，不再使用弹窗）
const handleReject = async (applyId, rejectReason, images = []) => {
  if (!rejectReason || !rejectReason.trim()) {
    ElMessage.warning('驳回时必须填写审批说明')
    return false
  }
  
  try {
    const data = {
      approvalComment: rejectReason,
      approvalImages: images || []
    }
    const res = await rejectTask(applyId, data)
    if (res.code === 200) {
      ElMessage.success('已驳回')
      return true
    }
  } catch (error) {
    console.error('驳回失败:', error)
    return false
  }
  return false
}

// 重新提交（驳回状态专用）
const handleResubmit = async () => {
  if (!taskDetail.value || !taskDetail.value.taskInfo) return
  
  try {
    const res = await resubmitTask(taskDetail.value.taskInfo.taskId, {})
    if (res.code === 200) {
      ElMessage.success('重新提交成功')
      // 刷新数据（后台会返回新的进行中状态，刷新后会自动显示）
      await loadCategories() // 刷新分类统计
      await loadTaskList()
      await loadTaskDetail(taskDetail.value.taskInfo.taskId)
    }
  } catch (error) {
    console.error('重新提交失败:', error)
  }
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
