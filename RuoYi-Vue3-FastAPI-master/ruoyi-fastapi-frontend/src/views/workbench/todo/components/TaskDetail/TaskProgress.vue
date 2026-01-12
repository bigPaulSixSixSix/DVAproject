<template>
  <div class="task-progress-card">
    <div class="section-title">任务进度</div>
    <div v-if="!taskProgress" class="empty-state">
      <el-empty description="暂无进度信息" :image-size="60" />
    </div>
    <div v-else class="progress-content">
      <div class="progress-item">
        <span class="label">总工期</span>
        <span class="value">{{ taskProgress.totalDuration }}天</span>
      </div>
      <div class="progress-item">
        <span class="label">开始时间</span>
        <span class="value">{{ formatDate(taskProgress.startTime) }}</span>
      </div>
      <div class="progress-item">
        <span class="label">结束时间</span>
        <span class="value">{{ formatDate(taskProgress.endTime) }}</span>
      </div>
      <div class="progress-item">
        <span class="label">当前进度</span>
        <div class="value tags">
          <el-tag :type="getStatusTagType(taskProgress.currentStatus)" size="small">
            {{ taskProgress.currentStatus }}
          </el-tag>
          <el-tag v-if="taskProgress.isOverdue" type="danger" size="small">
            逾期{{ taskProgress.overdueDays }}天
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'TaskProgress'
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/')
}

const props = defineProps({
  taskProgress: {
    type: Object,
    default: null
  }
})

// 根据当前状态获取标签类型
const getStatusTagType = (currentStatus) => {
  if (!currentStatus) return 'info'
  
  // 待提交：蓝色
  if (currentStatus === '进行中' || currentStatus === '待提交') {
    return 'primary'
  }
  
  // 审批中：黄色
  if (currentStatus === '已提交' || currentStatus === '审批中') {
    return 'warning'
  }
  
  // 驳回：红色
  if (currentStatus === '驳回') {
    return 'danger'
  }
  
  // 默认蓝色
  return 'primary'
}
</script>

<style scoped lang="scss">
.task-progress-card {
  border-radius: 4px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
  }

  .empty-state {
    padding: 20px 0;
  }

  .progress-content {
    .progress-item {
      display: flex;
      margin-bottom: 12px;
      font-size: 14px;

      .label {
        color: var(--el-text-color-secondary);
        width: 100px;
        flex-shrink: 0;
      }

      .value {
        color: var(--el-text-color-primary);
        flex: 1;

        &.tags {
          display: flex;
          gap: 8px;
        }

        &.overdue {
          color: var(--el-color-danger);
        }
      }
    }
  }

  // 禁用标签动画
  :deep(.el-tag) {
    transition: none !important;
    animation: none !important;
  }
}
</style>
