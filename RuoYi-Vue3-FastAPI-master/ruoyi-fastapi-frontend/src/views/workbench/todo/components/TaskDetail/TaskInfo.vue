<template>
  <div class="task-info-card">
    <div class="section-title">任务明细</div>
    <div v-if="!taskInfo" class="empty-state">
      <el-empty description="暂无任务信息" :image-size="60" />
    </div>
    <div v-else class="info-content">
      <div class="info-item">
        <span class="label">任务名称</span>
        <span class="value">{{ taskInfo.taskName }}</span>
      </div>
      <div v-if="approvalFlow?.applyId" class="info-item">
        <span class="label">申请单号</span>
        <span class="value apply-id-value">
          {{ approvalFlow.applyId }}
          <el-button
            link
            size="small"
            :icon="DocumentCopy"
            class="copy-button"
            @click="handleCopyApplyId"
          >
            复制
          </el-button>
        </span>
      </div>
      <div class="info-item">
        <span class="label">归属阶段</span>
        <span class="value clickable">
          {{ taskInfo.stageName }}
          <el-icon :size="14" class="stage-arrow-icon" style="margin-left: 4px;">
            <ArrowRight />
          </el-icon>
        </span>
      </div>
      <div v-if="taskInfo.taskDescription" class="info-item description-item">
        <span class="label">任务描述</span>
        <span class="value description-text">{{ taskInfo.taskDescription }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowRight, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineOptions({
  name: 'TaskInfo'
})

const props = defineProps({
  taskInfo: {
    type: Object,
    default: null
  },
  approvalFlow: {
    type: Object,
    default: null
  }
})

// 复制申请单号
const handleCopyApplyId = async () => {
  if (!props.approvalFlow?.applyId) {
    ElMessage.warning('申请单号不存在')
    return
  }
  
  try {
    await navigator.clipboard.writeText(props.approvalFlow.applyId)
    ElMessage.success('申请单号已复制到剪贴板')
  } catch (err) {
    // 降级方案：使用传统方法
    const textArea = document.createElement('textarea')
    textArea.value = props.approvalFlow.applyId
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('申请单号已复制到剪贴板')
    } catch (e) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textArea)
  }
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
</script>

<style scoped lang="scss">
.task-info-card {
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

  .info-content {
    .info-item {
      display: flex;
      margin-bottom: 12px;
      font-size: 14px;

      &.description-item {
        flex-direction: column;
        align-items: flex-start;

        .label {
          margin-bottom: 8px;
        }

        .description-text {
          line-height: 1.8;
          white-space: pre-wrap;
          word-break: break-word;
        }
      }

      .label {
        color: var(--el-text-color-secondary);
        width: 100px;
        flex-shrink: 0;
      }

      .value {
        color: var(--el-text-color-primary);
        flex: 1;

        &.clickable {
          cursor: pointer;
          color: var(--el-text-color-primary);
          display: flex;
          align-items: center;

          &:hover {
            text-decoration: underline;
          }
        }

        &.apply-id-value {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }
    }
  }

  // 复制按钮样式（灰色）
  :deep(.copy-button) {
    color: var(--el-text-color-regular) !important;
    
    .el-icon {
      color: var(--el-text-color-regular) !important;
    }
    
    &:hover {
      color: var(--el-text-color-primary) !important;
      
      .el-icon {
        color: var(--el-text-color-primary) !important;
      }
    }
  }

  // 阶段箭头图标样式（灰色）
  .stage-arrow-icon {
    color: var(--el-text-color-regular) !important;
  }
}
</style>
