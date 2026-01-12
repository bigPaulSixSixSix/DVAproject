<template>
  <div class="task-info">
    <div class="section-title">任务明细</div>
    <div v-if="!taskInfo" class="empty-state">
      <el-empty description="暂无任务信息" :image-size="60" />
    </div>
    <div v-else class="info-content">
      <div class="info-item">
        <span class="label">任务名称：</span>
        <span class="value">{{ taskInfo.taskName }}</span>
      </div>
      <div v-if="taskInfo.taskDescription" class="info-item">
        <span class="label">任务描述：</span>
        <span class="value">{{ taskInfo.taskDescription }}</span>
      </div>
      <div class="info-item">
        <span class="label">项目：</span>
        <span class="value">{{ taskInfo.projectName }}</span>
      </div>
      <div class="info-item">
        <span class="label">阶段：</span>
        <span class="value">{{ taskInfo.stageName }}</span>
      </div>
      <div class="info-item">
        <span class="label">部门：</span>
        <span class="value">{{ taskInfo.deptName }}</span>
      </div>
      <div class="info-item">
        <span class="label">负责人：</span>
        <span class="value">{{ taskInfo.assigneeName }}</span>
      </div>
      <div class="info-item">
        <span class="label">状态：</span>
        <el-tag :type="getStatusTagType(taskInfo.taskStatus)" size="small">
          {{ taskInfo.taskStatusName }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'TaskInfo'
})

const props = defineProps({
  taskInfo: {
    type: Object,
    default: null
  }
})

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'warning', // 进行中
    2: 'primary', // 已提交
    4: 'danger'   // 驳回
  }
  return typeMap[status] || 'info'
}
</script>

<style scoped lang="scss">
.task-info {
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

  .info-content {
    .info-item {
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
      }
    }
  }
}
</style>
