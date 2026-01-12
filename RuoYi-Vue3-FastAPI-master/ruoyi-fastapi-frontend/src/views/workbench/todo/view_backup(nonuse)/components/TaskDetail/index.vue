<template>
  <div class="task-detail">
    <div v-loading="loading" class="task-detail-content" style="padding: 16px;">
      <div v-if="!taskDetail" class="empty-state">
        <el-empty description="请选择一个任务查看详情" :image-size="120" />
      </div>
      <div v-else class="detail-sections">
        <!-- 审批流程 -->
        <ApprovalFlow :approval-flow="taskDetail.approvalFlow" />

        <!-- 前后置任务关系 -->
        <TaskRelations
          :task-relations="taskDetail.taskRelations"
          @task-click="handleRelationTaskClick"
        />

        <!-- 任务明细 -->
        <TaskInfo :task-info="taskDetail.taskInfo" />

        <!-- 任务进度 -->
        <TaskProgress :task-progress="taskDetail.taskProgress" />

        <!-- 提交内容 -->
        <SubmitContent :submit-content="taskDetail.submitContent" />
      </div>
    </div>

    <!-- 提交按钮（吸底固定） -->
    <div v-if="taskDetail && canShowSubmitButton" class="submit-footer">
      <el-button
        v-if="taskDetail.canSubmit"
        type="primary"
        size="large"
        @click="handleSubmitClick"
      >
        提交
      </el-button>
      <el-button
        v-if="taskDetail.canApprove"
        type="success"
        size="large"
        @click="handleApproveClick"
      >
        审批通过
      </el-button>
      <el-button
        v-if="taskDetail.canApprove"
        type="danger"
        size="large"
        @click="handleRejectClick"
      >
        驳回
      </el-button>
      <el-button
        v-if="taskDetail.canResubmit"
        type="primary"
        size="large"
        @click="handleResubmitClick"
      >
        重新提交
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import ApprovalFlow from './ApprovalFlow.vue'
import TaskRelations from './TaskRelations.vue'
import TaskInfo from './TaskInfo.vue'
import TaskProgress from './TaskProgress.vue'
import SubmitContent from './SubmitContent.vue'

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

const emit = defineEmits(['submit', 'approve', 'reject', 'resubmit', 'relation-task-click'])

// 是否显示提交按钮
const canShowSubmitButton = computed(() => {
  if (!props.taskDetail) return false
  return props.taskDetail.canSubmit ||
         props.taskDetail.canApprove ||
         props.taskDetail.canResubmit
})

// 提交按钮点击
const handleSubmitClick = () => {
  emit('submit')
}

// 审批通过按钮点击
const handleApproveClick = () => {
  emit('approve')
}

// 驳回按钮点击
const handleRejectClick = () => {
  emit('reject')
}

// 重新提交按钮点击
const handleResubmitClick = () => {
  emit('resubmit')
}

// 前后置任务点击
const handleRelationTaskClick = (task) => {
  emit('relation-task-click', task)
}
</script>

<style scoped lang="scss">
.task-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;

  .task-detail-content {
    flex: 1;
    overflow-y: auto;
    padding-right: 8px;
    padding-bottom: 80px; // 为吸底按钮留出空间

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .detail-sections {
      padding-bottom: 20px;
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
</style>
