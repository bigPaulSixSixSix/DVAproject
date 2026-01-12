<template>
  <div class="task-detail">
    <div v-loading="loading" class="task-detail-content">
      <div v-if="!taskDetail" class="empty-state">
        <el-empty description="请选择一个任务查看详情" :image-size="120" />
      </div>
      <div v-else class="detail-sections">
        <!-- 审批流程 -->
        <ApprovalFlow 
          :approval-flow="taskDetail.approvalFlow" 
          :task-info="taskDetail.taskInfo"
        />

        <!-- 前后置任务关系 -->
        <TaskRelations
          :task-relations="taskDetail.taskRelations"
          @task-click="handleRelationTaskClick"
        />

        <!-- 任务明细 -->
        <TaskInfo 
          :task-info="taskDetail.taskInfo" 
          :approval-flow="taskDetail.approvalFlow"
        />

        <!-- 任务进度 -->
        <TaskProgress :task-progress="taskDetail.taskProgress" />

        <!-- 提交内容（所有状态都显示，驳回状态为只读） -->
        <SubmitContent 
          :key="taskDetail.taskInfo?.taskId"
          ref="submitContentRef"
          :submit-content="taskDetail.submitContent"
          :can-submit="taskDetail.canSubmit"
          :can-resubmit="taskDetail.canResubmit"
          :task-status="taskDetail.taskInfo?.taskStatus"
          :history-approval="taskDetail.historyApproval"
          @show-history="handleShowHistory"
        />

        <!-- 审批详情（驳回状态显示） -->
        <ApprovalDetail
          v-if="taskDetail.taskInfo?.taskStatus === 4"
          :approval-flow="taskDetail.approvalFlow"
        />

        <!-- 审批结果（仅审批时显示） -->
        <ApprovalContent
          v-if="taskDetail.canApprove"
          ref="approvalContentRef"
          :can-approve="taskDetail.canApprove"
          :approval-info="null"
        />
      </div>
      <div v-if="taskDetail" class="no-more">没有更多啦</div>
    </div>

    <!-- 操作按钮（吸底固定） -->
    <div v-if="taskDetail && canShowSubmitButton" class="submit-footer">
      <!-- 驳回状态：显示重新提交按钮 -->
      <el-button
        v-if="taskDetail.taskInfo?.taskStatus === 4 && taskDetail.canResubmit"
        type="primary"
        size="large"
        @click="handleResubmitClick"
      >
        重新提交
      </el-button>
      <!-- 其他状态：显示提交按钮 -->
      <el-button
        v-else-if="taskDetail.canSubmit || taskDetail.canApprove"
        type="primary"
        size="large"
        @click="handleSubmitClick"
      >
        提交
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import ApprovalFlow from './ApprovalFlow.vue'
import TaskRelations from './TaskRelations.vue'
import TaskInfo from './TaskInfo.vue'
import TaskProgress from './TaskProgress.vue'
import SubmitContent from './SubmitContent.vue'
import ApprovalContent from './ApprovalContent.vue'
import ApprovalDetail from './ApprovalDetail.vue'

defineOptions({
  name: 'TaskDetail'
})

const props = defineProps({
  taskDetail: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'approve', 'resubmit', 'relation-task-click', 'show-history'])

const submitContentRef = ref(null)
const approvalContentRef = ref(null)

// 是否显示提交按钮
const canShowSubmitButton = computed(() => {
  if (!props.taskDetail) return false
  return props.taskDetail.canSubmit ||
         props.taskDetail.canApprove ||
         props.taskDetail.canResubmit
})

// 提交按钮点击（统一处理提交、审批）
const handleSubmitClick = () => {
  // 如果是审批，从审批组件获取数据
  if (props.taskDetail?.canApprove) {
    if (!approvalContentRef.value) {
      ElMessage.warning('审批组件未加载')
      return
    }
    
    // 验证审批数据
    const validation = approvalContentRef.value.validate()
    if (!validation.valid) {
      ElMessage.warning(validation.message)
      return
    }
    
    // 获取审批数据
    const approvalData = approvalContentRef.value.getApprovalData()
    emit('approve', approvalData)
    return
  }
  
  // 如果是提交，从提交内容组件获取数据
  if (props.taskDetail?.canSubmit) {
    if (!submitContentRef.value) {
      emit('submit', '')
      return
    }
    const submitText = submitContentRef.value.getSubmitText()
    if (!submitText || !submitText.trim()) {
      ElMessage.warning('请填写完成情况')
      return
    }
    
    emit('submit', submitText)
  }
}

// 重新提交按钮点击（驳回状态专用）
const handleResubmitClick = () => {
  if (!props.taskDetail || !props.taskDetail.taskInfo) {
    ElMessage.warning('任务信息不存在')
    return
  }
  
  // 直接触发重新提交事件，不需要提交内容
  emit('resubmit', '')
}

// 前后置任务点击
const handleRelationTaskClick = (task) => {
  emit('relation-task-click', task)
}

// 显示历史记录
const handleShowHistory = () => {
  emit('show-history')
}
</script>

<style scoped lang="scss">
.task-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: var(--el-bg-color-page); // 浅灰色背景

  .task-detail-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    padding-bottom: 80px; // 为吸底按钮留出空间
    min-height: 0;

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .detail-sections {
      display: flex;
      flex-direction: column;
      gap: 16px;
      // 子元素设置背景颜色

      :deep(.approval-flow-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.task-relations-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.task-info-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.task-progress-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.submit-content-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.approval-content-card) {
        background-color: var(--el-bg-color);
      }
      :deep(.approval-detail-card) {
        background-color: var(--el-bg-color);
      }
    }
  }

  .submit-footer {
    position: sticky;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px;
    background-color: var(--el-bg-color);
    border-top: 1px solid var(--el-border-color-lighter);
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
    z-index: 10;
  }
}

.no-more {
    text-align: center;
    color: var(--el-text-color-placeholder);
    font-size: 12px;
    margin-top: 16px;
    padding-top: 16px;
  }
</style>
