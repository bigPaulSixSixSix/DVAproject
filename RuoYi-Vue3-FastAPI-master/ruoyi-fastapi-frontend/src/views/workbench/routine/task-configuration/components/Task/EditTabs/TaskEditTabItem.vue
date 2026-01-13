<template>
  <div
    class="task-edit-tab-item"
    :class="{ 
      active,
      'task-edit-tab-item--invalid': hasMissingRequiredFields,
      'task-edit-tab-item--time-issue': hasTimeIssue && !hasMissingRequiredFields
    }"
    @click="$emit('select', tab.taskId)"
  >
    <div class="tab-id">ID: {{ tab.taskId }}</div>
    <div class="tab-name" :title="taskName">
      {{ taskName }}
    </div>
    <div class="tab-meta" :title="metaText">
      <span class="tab-range">{{ dateRange }}</span>
      <span class="tab-assignee">{{ assigneeName }}</span>
    </div>
    <button class="tab-close" type="button" @click.stop="$emit('close', tab.taskId)">
      <el-icon>
        <Close />
      </el-icon>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Close } from '@element-plus/icons-vue'

const props = defineProps({
  tab: {
    type: Object,
    required: true
  },
  active: {
    type: Boolean,
    default: false
  },
  getUserNickName: {
    type: Function,
    required: true
  },
  findTaskById: {
    type: Function,
    default: null
  }
})

defineEmits(['select', 'close'])

const fallbackText = '未命名任务'

const taskName = computed(() => props.tab?.formState?.name || fallbackText)

const assigneeName = computed(() => {
  const jobNumber = props.tab?.formState?.jobNumber || props.tab?.formState?.assignee
  if (!jobNumber) return '未分配'
  return props.getUserNickName(jobNumber)
})

const dateRange = computed(() => {
  const start = props.tab?.formState?.startTime || '--'
  const end = props.tab?.formState?.endTime || '--'
  const duration = props.tab?.formState?.duration
  const durationText = duration ? `共${duration}天` : '共--天'
  return `${start} - ${end} ${durationText}`
})

const metaText = computed(() => `${dateRange.value} ${assigneeName.value}`)

// 检查任务是否缺少必要字段（用于红色标注）
const hasMissingRequiredFields = computed(() => {
  const formState = props.tab?.formState
  if (!formState) return true
  // 检查关键字段是否为null或空
  // 检查审批层级是否配置：approvalLevel 如果为 undefined 或 null，则认为未配置
  // 但如果审批类型为"none"（无需审批），则不需要检查审批层级
  const approvalType = formState.approvalType || 'sequential'
  const hasApprovalLevel = approvalType === 'none' 
    ? true // 无需审批时，认为审批层级已配置
    : (formState.approvalLevel !== undefined && formState.approvalLevel !== null)
  return !formState.startTime || !formState.endTime || (!formState.jobNumber && !formState.assignee) || !hasApprovalLevel // 兼容旧数据
})

// 检查任务是否有时间问题（用于黄色标注）
const hasTimeIssue = computed(() => {
  // 如果信息不完全（红色），不显示黄色标注
  if (hasMissingRequiredFields.value) {
    return false
  }
  if (!props.findTaskById || !props.tab?.taskId) return false
  const taskInfo = props.findTaskById(props.tab.taskId)
  if (!taskInfo || !taskInfo.task) return false
  return Boolean(taskInfo.task.hasTimeIssue)
})
</script>

<style scoped>
.task-edit-tab-item {
  position: relative;
  min-width: 220px;
  max-width: 260px;
  padding: 10px 32px 10px 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

/* 有信息未填写 - 红色 */
.task-edit-tab-item--invalid {
  border: 1px solid var(--el-color-danger);
  background-color: var(--el-color-danger-light-9);
}

/* 时间异常 - 黄色（前提是没有缺失必填字段） */
.task-edit-tab-item--time-issue {
  border: 1px solid var(--el-color-warning);
  background-color: var(--el-color-warning-light-9);
}

/* 选中状态 - 2px 蓝色描边，保持原有底色 */
.task-edit-tab-item.active {
  border: 2px solid var(--el-color-primary) !important;
}

.task-edit-tab-item--invalid.active {
  background-color: var(--el-color-danger-light-9);
}

.task-edit-tab-item--time-issue.active {
  background-color: var(--el-color-warning-light-9);
}

.tab-id {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.2;
}

.tab-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tab-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: flex;
  gap: 6px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.tab-range,
.tab-assignee {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tab-close {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 50%;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--el-text-color-secondary);
}

.task-edit-tab-item.active .tab-close {
  color: var(--el-color-primary);
}

.tab-close:hover {
  background: rgba(0, 0, 0, 0.08);
}

.tab-close :deep(svg) {
  width: 12px;
  height: 12px;
}
</style>

