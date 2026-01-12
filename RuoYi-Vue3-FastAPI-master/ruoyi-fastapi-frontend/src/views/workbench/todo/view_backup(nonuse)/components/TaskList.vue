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
        <div class="task-header">
          <div class="task-name">
            <el-icon :size="16" :color="task.iconColor">
              <component :is="getIconComponent(task.iconType)" />
            </el-icon>
            <span>{{ task.taskName }}</span>
          </div>
          <el-tag :type="getStatusTagType(task.taskStatus)" size="small">
            {{ task.taskStatusName }}
          </el-tag>
        </div>
        <div class="task-info">
          <div class="task-info-item">
            <span class="label">项目：</span>
            <span class="value">{{ task.projectName }}</span>
          </div>
          <div class="task-info-item">
            <span class="label">部门：</span>
            <span class="value">{{ task.deptName }}</span>
          </div>
          <div v-if="task.deadline" class="task-info-item">
            <span class="label">截止：</span>
            <span class="value deadline">{{ formatDeadline(task.deadline) }}</span>
          </div>
        </div>
        <div v-if="task.deadline" class="task-deadline">
          <span class="deadline-text" :class="getDeadlineClass(task.deadline)">
            {{ calculateRemainingTime(task.deadline) }}
          </span>
        </div>
      </div>
    </div>
    <div v-if="total > 0" class="task-pagination">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowUp, Document, Close } from '@element-plus/icons-vue'
import { calculateRemainingTime } from '../composables/useTimeUtils'

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
  total: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['select-task', 'page-change', 'size-change'])

// 获取图标组件
const getIconComponent = (iconType) => {
  const iconMap = {
    'arrow-up': ArrowUp,
    'document': Document,
    'close': Close
  }
  return iconMap[iconType] || Document
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'warning', // 进行中
    2: 'primary', // 已提交
    4: 'danger'   // 驳回
  }
  return typeMap[status] || 'info'
}

// 格式化截止时间
const formatDeadline = (deadline) => {
  if (!deadline) return ''
  return deadline
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

// 分页变化
const handlePageChange = (page) => {
  emit('page-change', page)
}

// 每页数量变化
const handleSizeChange = (size) => {
  emit('size-change', size)
}
</script>

<style scoped lang="scss">
.task-list {
  height: 100%;
  display: flex;
  flex-direction: column;

  .task-list-content {
    flex: 1;
    overflow-y: auto;
    padding-right: 8px;

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 300px;
    }

    .task-item {
      padding: 16px;
      margin-bottom: 12px;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      background-color: var(--el-bg-color);

      &:hover {
        border-color: var(--el-color-primary);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      &.active {
        border-color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }

      .task-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .task-name {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 500;
          color: var(--el-text-color-primary);
          flex: 1;
        }
      }

      .task-info {
        margin-bottom: 8px;

        .task-info-item {
          font-size: 13px;
          color: var(--el-text-color-regular);
          margin-bottom: 4px;

          .label {
            color: var(--el-text-color-secondary);
          }

          .value {
            &.deadline {
              color: var(--el-color-warning);
            }
          }
        }
      }

      .task-deadline {
        .deadline-text {
          font-size: 12px;
          color: var(--el-color-primary);

          &.overdue {
            color: var(--el-color-danger);
          }
        }
      }
    }
  }

  .task-pagination {
    padding: 16px 0;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}
</style>
