<template>
  <el-dialog
    v-model="visible"
    title="任务详情"
    width="800px"
    append-to-body
    @close="handleClose"
  >
    <div v-loading="loading" class="dialog-content">
      <div v-if="taskDetail">
        <!-- 任务基本信息 -->
        <div class="detail-section">
          <div class="section-title">任务信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">任务名称：</span>
              <span class="value">{{ taskDetail.taskInfo?.taskName }}</span>
            </div>
            <div class="info-item">
              <span class="label">项目：</span>
              <span class="value">{{ taskDetail.taskInfo?.projectName }}</span>
            </div>
            <div class="info-item">
              <span class="label">负责人：</span>
              <span class="value">{{ taskDetail.taskInfo?.assigneeName }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态：</span>
              <el-tag :type="getStatusTagType(taskDetail.taskInfo?.taskStatus)" size="small">
                {{ getStatusDisplayName(taskDetail.taskInfo?.taskStatus, taskDetail.taskInfo?.taskStatusName) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 提交内容 -->
        <div v-if="taskDetail.submitContent" class="detail-section">
          <div class="section-title">提交内容</div>
          <div v-if="taskDetail.submitContent.submitText" class="submit-text">
            {{ taskDetail.submitContent.submitText }}
          </div>
          <div v-if="taskDetail.submitContent.submitTime" class="submit-time">
            提交时间：{{ taskDetail.submitContent.submitTime }}
          </div>
        </div>

        <!-- 审批流程 -->
        <div v-if="taskDetail.approvalFlow" class="detail-section">
          <div class="section-title">审批流程</div>
          <div class="approval-nodes">
            <div
              v-for="node in taskDetail.approvalFlow.approvalNodes"
              :key="node.nodeIndex"
              class="approval-node"
            >
              <div class="node-info">
                <span class="node-post">{{ node.postName }}</span>
                <el-tag :type="getStatusTagType(node.status)" size="small">
                  {{ getStatusText(node.status) }}
                </el-tag>
              </div>
              <div v-if="node.approverName" class="node-approver">
                审批人：{{ node.approverName }}
              </div>
              <div v-if="node.approvalTime" class="node-time">
                审批时间：{{ node.approvalTime }}
              </div>
              <div v-if="node.approvalComment" class="node-comment">
                审批意见：{{ node.approvalComment }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getTaskDetailSimple } from '@/api/todo'

defineOptions({
  name: 'TaskDetailDialog'
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  taskId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const loading = ref(false)
const taskDetail = ref(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.taskId) {
    loadTaskDetail()
  } else {
    taskDetail.value = null
  }
})

watch(() => props.taskId, (val, oldVal) => {
  // 只有当弹窗已打开且taskId发生变化时才加载（避免重复请求）
  if (visible.value && val && val !== oldVal) {
    loadTaskDetail()
  }
})

// 加载任务详情
const loadTaskDetail = async () => {
  if (!props.taskId) return
  loading.value = true
  try {
    const res = await getTaskDetailSimple(props.taskId)
    if (res.code === 200 && res.data) {
      taskDetail.value = res.data
    }
  } catch (error) {
    console.error('加载任务详情失败:', error)
    taskDetail.value = null
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  emit('update:modelValue', false)
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  if (typeof status === 'number') {
    const typeMap = {
      0: 'info',       // 未开始 - 灰色
      1: 'primary',    // 待提交 - 蓝色
      2: 'warning',    // 审批中 - 黄色
      3: 'info',       // 完成 - 灰色
      4: 'danger'     // 驳回 - 红色
    }
    return typeMap[status] || 'info'
  } else if (typeof status === 'string') {
    const typeMap = {
      approved: 'success',
      approving: 'warning',
      pending: 'info'
    }
    return typeMap[status] || 'info'
  }
  return 'info'
}

// 获取状态显示名称
const getStatusDisplayName = (status, statusName) => {
  if (typeof status === 'number') {
    // 状态0显示为"未开始"
    if (status === 0) {
      return '未开始'
    }
    // 其他状态使用后端返回的状态名称
    return statusName || '未知'
  }
  return statusName || '未知'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    approved: '已审批',
    approving: '审批中',
    pending: '待审批'
  }
  return textMap[status] || '未知'
}
</script>

<style scoped lang="scss">

.dialog-content {
  max-height: 600px;
  overflow-y: auto;

  .detail-section {
    margin-bottom: 24px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--el-border-color-lighter);
    }

    .info-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .info-item {
        display: flex;
        font-size: 14px;

        .label {
          color: var(--el-text-color-secondary);
          width: 100px;
          flex-shrink: 0;
        }

        .value {
          color: var(--el-text-color-primary);
          flex: 1;
        }
      }
    }

    .approval-nodes {
      .approval-node {
        padding: 12px;
        margin-bottom: 8px;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 4px;
        background-color: var(--el-fill-color-light);

        .node-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .node-post {
            font-weight: 500;
            color: var(--el-text-color-primary);
          }
        }

        .node-approver,
        .node-time {
          font-size: 13px;
          color: var(--el-text-color-regular);
          margin-bottom: 4px;
        }

        .node-comment {
          font-size: 13px;
          color: var(--el-text-color-primary);
          line-height: 1.6;
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid var(--el-border-color-lighter);
        }
      }
    }

    .submit-text {
      font-size: 14px;
      color: var(--el-text-color-primary);
      line-height: 1.8;
      padding: 12px;
      background-color: var(--el-fill-color-light);
      border-radius: 4px;
      white-space: pre-wrap;
      word-break: break-word;
      margin-bottom: 8px;
    }

    .submit-time {
      font-size: 13px;
      color: var(--el-text-color-regular);
    }
  }

  // 自定义状态标签样式
  :deep(.el-tag) {
    // 禁用标签动画
    transition: none !important;
    animation: none !important;
    
    // 审批中状态 - 黄色（使用 Element Plus 的颜色变量）
    &.el-tag--warning {
      background-color: var(--el-color-warning-light-9) !important;
      border-color: var(--el-color-warning) !important;
      color: var(--el-color-warning) !important;
    }
  }
}
</style>
