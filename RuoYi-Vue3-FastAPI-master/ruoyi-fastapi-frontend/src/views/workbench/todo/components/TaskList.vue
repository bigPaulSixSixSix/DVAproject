<template>
  <div class="task-list">
    <div v-loading="loading" class="task-list-content" style="padding: 16px;">
      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无任务" :image-size="100" />
      </div>
      <div
        v-for="task in tasks"
        :key="task.taskId"
        class="task-item"
        :class="{ active: selectedTaskId === task.taskId }"
        @click="handleSelectTask(task)"
      >
        <!-- 左侧：图标 + 类型文字 -->
        <div class="task-type-section">
          <div class="task-icon" :class="getIconClass(task.taskStatus)">
            <i :class="getIconName(task.taskStatus)"></i>
          </div>
          <span class="task-type-text" :class="getTypeTextClass(task.taskStatus)">
            {{ getTypeText(task.taskStatus) }}
          </span>
        </div>
        
        <!-- 右侧：任务信息 -->
        <div class="task-content-section">
          <!-- 第一行：任务名称 -->
          <div class="task-name-row">
            {{ task.taskName }}
          </div>
          <!-- 第二行：项目 + 负责人 + 剩余时间/完成时间 -->
          <div class="task-info-row">
            <span class="info-item">{{ task.projectName }}</span>
            <span class="info-separator">·</span>
            <span class="info-item">{{ task.assigneeName || '未分配' }}</span>
            <span class="info-separator">·</span>
            <!-- 历史任务：显示完成时间和逾期时间 -->
            <template v-if="isHistory">
              <span class="info-item">{{ formatCompleteTime(task.actualCompleteTime) }}</span>
              <span class="info-separator">·</span>
              <span 
                class="info-item remaining-time" 
                :class="getHistoryOverdueClass(task.actualCompleteTime, task.deadline)"
              >
                {{ getHistoryOverdueTime(task.actualCompleteTime, task.deadline) }}
              </span>
            </template>
            <!-- 我的任务：显示剩余时间 -->
            <template v-else>
              <span 
                class="info-item remaining-time" 
                :class="getDeadlineClass(task.deadline)"
              >
                {{ getRemainingTimeText(task.deadline, task.taskStatus) }}
              </span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { calculateRemainingTime } from '../composables/useTimeUtils'
import '@/assets/icons/todo_icons/style.css'

defineOptions({
  name: 'TaskList'
})

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedTaskId: {
    type: [Number, String],
    default: null
  },
  isHistory: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-task'])

// 根据任务状态获取图标类名
const getIconName = (status) => {
  // 1: 进行中 -> 提交
  // 2: 已提交 -> 审批
  // 3: 完成 -> 完成
  // 4: 驳回 -> 驳回
  const iconMap = {
    1: 'icon-ic_todo_todo',         // 提交
    2: 'icon-ic_todo_approve',       // 审批
    3: 'icon-ic_todo_result_true',   // 完成
    4: 'icon-ic_todo_giveBack'       // 驳回
  }
  return iconMap[status] || 'icon-ic_todo_todo'
}

// 获取图标容器类名（用于设置颜色）
const getIconClass = (status) => {
  const classMap = {
    1: 'icon-submit',      // 提交 - 蓝色
    2: 'icon-approve',     // 审批 - 金色
    3: 'icon-complete',   // 完成 - 蓝色
    4: 'icon-reject'       // 驳回 - 红色
  }
  return classMap[status] || 'icon-submit'
}

// 获取类型文字
const getTypeText = (status) => {
  const textMap = {
    1: '提交',
    2: '审批',
    3: '完成',
    4: '驳回'
  }
  return textMap[status] || '提交'
}

// 获取类型文字样式类
const getTypeTextClass = (status) => {
  const classMap = {
    1: 'type-submit',
    2: 'type-approve',    // 审批 - 金色
    3: 'type-complete',  // 完成 - 蓝色
    4: 'type-reject'
  }
  return classMap[status] || 'type-submit'
}

// 获取剩余时间文本
const getRemainingTimeText = (deadline, status) => {
  if (!deadline) return ''
  const remaining = calculateRemainingTime(deadline)
  
  // 根据任务状态添加后缀
  if (status === 2) {
    // 审批状态，添加"需审批"
    if (remaining.includes('剩余')) {
      return remaining + '需审批'
    } else if (remaining.includes('逾期')) {
      return remaining + '需审批'
    }
  }
  
  return remaining
}

// 格式化完成时间（历史任务）
const formatCompleteTime = (completeTime) => {
  if (!completeTime) return ''
  // 格式：2025/12/02 23:55:45完成
  const date = new Date(completeTime.replace(/-/g, '/'))
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}完成`
}

// 计算历史任务的逾期时间（使用与 calculateRemainingTime 相同的逻辑）
const getHistoryOverdueTime = (completeTime, deadline) => {
  if (!completeTime || !deadline) return ''
  
  const completeDate = new Date(completeTime.replace(/-/g, '/'))
  const deadlineDate = new Date(deadline.replace(/-/g, '/'))
  const diff = completeDate.getTime() - deadlineDate.getTime()
  
  if (diff <= 0) {
    // 未逾期（完成时间早于或等于截止时间），不显示
    return ''
  }
  
  // 已逾期（完成时间晚于截止时间），使用与 calculateRemainingTime 相同的计算逻辑
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours < 24) {
    return `逾期${hours}小时${minutes}分`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return `逾期${days}天${remainingHours}小时`
  }
}

// 获取历史任务逾期时间的样式类
const getHistoryOverdueClass = (completeTime, deadline) => {
  if (!completeTime || !deadline) return ''
  const completeDate = new Date(completeTime.replace(/-/g, '/'))
  const deadlineDate = new Date(deadline.replace(/-/g, '/'))
  if (completeDate.getTime() > deadlineDate.getTime()) {
    return 'overdue'
  }
  return ''
}

// 获取截止时间样式类
const getDeadlineClass = (deadline) => {
  if (!deadline) return ''
  const now = new Date()
  const deadlineDate = new Date(deadline.replace(/-/g, '/'))
  if (deadlineDate.getTime() < now.getTime()) {
    return 'overdue'
  }
  return ''
}

// 选择任务
const handleSelectTask = (task) => {
  emit('select-task', task)
}
</script>

<style scoped lang="scss">
.task-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;


  .task-list-content {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    margin:0 !important;
    padding: 0 !important;

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 300px;
    }

    .task-item {
      display: flex;
      align-items: center;
      padding: 16px;
      cursor: pointer;
      transition: all 0.2s;
      background-color: var(--el-bg-color);
      border-bottom: 1px solid var(--el-border-color-lighter);
      gap: 16px;

      &:hover {
        background-color: var(--el-fill-color-lighter);
      }

      &.active {
        background-color: var(--el-bg-color-page);
      }

      // 左侧：图标 + 类型文字
      .task-type-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        gap: 8px;

        .task-icon {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;

          &.icon-approve {
            color: var(--el-color-warning); // 金色
          }

          &.icon-submit {
            color: var(--el-color-primary); // 蓝色（提交）
          }

          &.icon-reject {
            color: var(--el-color-danger); // 红色（驳回）
          }

          &.icon-complete {
            color: var(--el-color-primary); // 蓝色（完成）
          }

          i {
            font-size: 24px;
          }
        }

        .task-type-text {
          font-size: 13px;
          white-space: nowrap;

          &.type-approve {
            color: var(--el-color-warning); // 金色
          }

          &.type-submit {
            color: var(--el-color-primary); // 蓝色
          }

          &.type-reject {
            color: var(--el-color-danger); // 红色
          }

          &.type-complete {
            color: var(--el-color-primary); // 蓝色（完成）
          }
        }
      }

      // 右侧：任务信息
      .task-content-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-width: 0; // 允许文本截断

        // 第一行：任务名称
        .task-name-row {
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        // 第二行：项目 + 负责人 + 剩余时间
        .task-info-row {
          display: flex;
          align-items: center;
          font-size: 13px;
          color: var(--el-text-color-regular);
          gap: 6px;
          flex-wrap: wrap;

          .info-item {
            color: var(--el-text-color-regular);

            &.remaining-time {
              color: var(--el-color-primary);

              &.overdue {
                color: var(--el-color-danger);
              }
            }
          }

          .info-separator {
            color: var(--el-text-color-placeholder);
            margin: 0 2px;
          }
        }
      }
    }
  }
}
</style>
