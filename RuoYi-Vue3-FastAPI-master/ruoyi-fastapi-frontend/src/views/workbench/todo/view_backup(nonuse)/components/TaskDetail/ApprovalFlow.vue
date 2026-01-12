<template>
  <div class="approval-flow">
    <div class="section-title">审批流程</div>
    <div v-if="!approvalFlow" class="empty-state">
      <el-empty description="该任务无审批流程" :image-size="60" />
    </div>
    <div v-else class="approval-nodes">
      <div
        v-for="node in approvalFlow.approvalNodes"
        :key="node.nodeIndex"
        class="approval-node"
        :class="getNodeStatusClass(node.status)"
      >
        <div class="node-header">
          <div class="node-index">{{ node.nodeIndex }}</div>
          <div class="node-info">
            <div class="node-post">{{ node.postName }}</div>
            <div v-if="node.approverName" class="node-approver">
              审批人：{{ node.approverName }}
            </div>
          </div>
          <div class="node-status">
            <el-tag :type="getStatusTagType(node.status)" size="small">
              {{ getStatusText(node.status) }}
            </el-tag>
          </div>
        </div>
        <div v-if="node.approvalTime" class="node-detail">
          <div class="node-time">审批时间：{{ node.approvalTime }}</div>
          <div v-if="node.approvalComment" class="node-comment">
            审批意见：{{ node.approvalComment }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'ApprovalFlow'
})

const props = defineProps({
  approvalFlow: {
    type: Object,
    default: null
  }
})

// 获取节点状态样式类
const getNodeStatusClass = (status) => {
  const classMap = {
    approved: 'status-approved',
    approving: 'status-approving',
    pending: 'status-pending'
  }
  return classMap[status] || ''
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    approved: 'success',
    approving: 'warning',
    pending: 'info'
  }
  return typeMap[status] || 'info'
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
.approval-flow {
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

  .approval-nodes {
    .approval-node {
      padding: 16px;
      margin-bottom: 12px;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 4px;
      background-color: var(--el-bg-color);

      &.status-approved {
        border-left: 4px solid var(--el-color-success);
      }

      &.status-approving {
        border-left: 4px solid var(--el-color-warning);
      }

      &.status-pending {
        border-left: 4px solid var(--el-color-info);
      }

      .node-header {
        display: flex;
        align-items: center;
        gap: 12px;

        .node-index {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background-color: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
          font-weight: 600;
          flex-shrink: 0;
        }

        .node-info {
          flex: 1;

          .node-post {
            font-size: 15px;
            font-weight: 500;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }

          .node-approver {
            font-size: 13px;
            color: var(--el-text-color-regular);
          }
        }
      }

      .node-detail {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--el-border-color-lighter);

        .node-time {
          font-size: 13px;
          color: var(--el-text-color-regular);
          margin-bottom: 8px;
        }

        .node-comment {
          font-size: 13px;
          color: var(--el-text-color-primary);
          line-height: 1.6;
        }
      }
    }
  }
}
</style>
