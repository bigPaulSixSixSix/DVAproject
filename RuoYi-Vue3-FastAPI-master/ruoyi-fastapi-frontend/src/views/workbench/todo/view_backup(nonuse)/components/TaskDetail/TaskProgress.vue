<template>
  <div class="task-progress">
    <div class="section-title">任务进度</div>
    <div v-if="!taskProgress" class="empty-state">
      <el-empty description="暂无进度信息" :image-size="60" />
    </div>
    <div v-else class="progress-content">
      <div class="progress-item">
        <span class="label">计划开始时间：</span>
        <span class="value">{{ taskProgress.startTime }}</span>
      </div>
      <div class="progress-item">
        <span class="label">计划结束时间：</span>
        <span class="value">{{ taskProgress.endTime }}</span>
      </div>
      <div class="progress-item">
        <span class="label">总工期：</span>
        <span class="value">{{ taskProgress.totalDuration }}天</span>
      </div>
      <div v-if="taskProgress.actualStartTime" class="progress-item">
        <span class="label">实际开始时间：</span>
        <span class="value">{{ taskProgress.actualStartTime }}</span>
      </div>
      <div v-if="taskProgress.actualEndTime" class="progress-item">
        <span class="label">实际完成时间：</span>
        <span class="value">{{ taskProgress.actualEndTime }}</span>
      </div>
      <div class="progress-item">
        <span class="label">当前状态：</span>
        <el-tag :type="taskProgress.isOverdue ? 'danger' : 'success'" size="small">
          {{ taskProgress.currentStatus }}
        </el-tag>
      </div>
      <div v-if="taskProgress.isOverdue" class="progress-item">
        <span class="label">逾期天数：</span>
        <span class="value overdue">{{ taskProgress.overdueDays }}天</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'TaskProgress'
})

const props = defineProps({
  taskProgress: {
    type: Object,
    default: null
  }
})
</script>

<style scoped lang="scss">
.task-progress {
  margin-bottom: 24px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--el-border-color-lighter);
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
        width: 120px;
        flex-shrink: 0;
      }

      .value {
        color: var(--el-text-color-primary);
        flex: 1;

        &.overdue {
          color: var(--el-color-danger);
        }
      }
    }
  }
}
</style>
