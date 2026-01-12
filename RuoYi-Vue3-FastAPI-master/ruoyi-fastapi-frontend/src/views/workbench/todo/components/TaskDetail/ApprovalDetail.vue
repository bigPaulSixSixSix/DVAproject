<template>
  <div class="approval-detail-card">
    <div class="section-title">审批详情</div>
    <div v-if="!approvalFlow || !approvalFlow.approvalNodes || approvalFlow.approvalNodes.length === 0" class="empty-state">
      <el-empty description="暂无审批详情" :image-size="60" />
    </div>
    <div v-else class="approval-detail-content">
      <div
        v-for="(node, index) in filteredApprovalNodes"
        :key="node.nodeIndex"
        class="approval-detail-item"
        :class="{ 'has-divider': index < filteredApprovalNodes.length - 1 }"
      >
        <div class="approval-item-header">
          <div class="approval-node-info">
            <div class="node-index" :class="getNodeStatusClass(node.status)">
              {{ node.nodeIndex }}
            </div>
            <div class="node-content">
              <div class="node-title">{{ getNodeTitle(node) }}</div>
              <div v-if="node.approvalTime || node.approvalComment" class="approval-item-content">
              <div v-if="node.approvalTime" class="approval-info-item">
                <span class="label">审批时间</span>
                <span class="value">{{ node.approvalTime }}</span>
              </div>
          <div v-if="node.approvalComment" class="approval-info-item">
            <span class="label">审批说明</span>
            <span class="value">{{ node.approvalComment }}</span>
          </div>
        </div>
            </div>
          </div>
          <div class="approval-status">
            <el-tag :type="getStatusTagType(node.status)" size="small">
              {{ getStatusText(node.status) }}
            </el-tag>
          </div>
        </div>
        

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineOptions({
  name: 'ApprovalDetail'
})

const props = defineProps({
  approvalFlow: {
    type: Object,
    default: null
  }
})

// 过滤审批节点：一旦有驳回，就只显示到驳回节点为止，不显示后续的待审批节点
const filteredApprovalNodes = computed(() => {
  if (!props.approvalFlow || !props.approvalFlow.approvalNodes) {
    return []
  }
  
  const nodes = props.approvalFlow.approvalNodes
  // 找到第一个驳回的节点
  const rejectedIndex = nodes.findIndex(node => node.status === 'rejected')
  
  // 如果有驳回节点，只返回到驳回节点为止的所有节点（包括驳回节点）
  if (rejectedIndex !== -1) {
    return nodes.slice(0, rejectedIndex + 1)
  }
  
  // 如果没有驳回，返回所有节点
  return nodes
})

// 获取节点标题
const getNodeTitle = (node) => {
  const postName = node.postName || '未知岗位'
  
  // 审批驳回状态
  if (node.status === 'rejected') {
    const approverName = node.approverName || '未知'
    return `${postName} ${approverName} 审批驳回`
  }
  
  // 已审批通过状态
  if (node.status === 'approved') {
    const approverName = node.approverName || '未知'
    // 判断是否为空岗自动审批
    if (node.approverId === 'system' || approverName === 'system') {
      return `${postName} 空岗 自动审批通过`
    } else {
      return `${postName} ${approverName} 审批通过`
    }
  }
  
  // 审批中状态
  if (node.status === 'approving') {
    if (node.approverId && node.approverName) {
      return `${postName} ${node.approverName} 审批中`
    } else {
      return `${postName} 空岗 跳过`
    }
  }
  
  // 待审批状态
  if (node.status === 'pending') {
    if (node.approverId && node.approverName) {
      return `${postName} ${node.approverName} 待审批`
    } else {
      return `${postName} 空岗 跳过`
    }
  }
  
  return `${postName} 审批`
}

// 获取节点状态样式类
const getNodeStatusClass = (status) => {
  const classMap = {
    approved: 'status-approved',
    rejected: 'status-rejected',
    approving: 'status-approving',
    pending: 'status-pending'
  }
  return classMap[status] || ''
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    approved: 'success',
    rejected: 'danger',
    approving: 'warning',
    pending: 'info'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    approved: '已通过',
    rejected: '已驳回',
    approving: '审批中',
    pending: '待审批'
  }
  return textMap[status] || '未知'
}
</script>

<style scoped lang="scss">
.approval-detail-card {
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

  .approval-detail-content {
    .approval-detail-item {
      margin-bottom: 16px;

      &.has-divider {
        border-bottom: 1px solid var(--el-border-color-lighter);
      }

      .approval-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;

        .approval-node-info {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          flex: 1;

          .node-index {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background-color: var(--el-fill-color-light);
            color: var(--el-text-color-primary);
            font-weight: 600;
            flex-shrink: 0;

            &.status-approved {
              background-color: var(--el-color-success-light-9);
              color: var(--el-color-success);
            }

            &.status-rejected {
              background-color: var(--el-color-danger-light-9);
              color: var(--el-color-danger);
            }

            &.status-approving {
              background-color: var(--el-color-warning-light-9);
              color: var(--el-color-warning);
            }

            &.status-pending {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-regular);
            }
          }

          .node-content {
            flex: 1;

            .node-title {
              font-size: 15px;
              font-weight: 500;
              color: var(--el-text-color-primary);
              margin-bottom: 12px;
            }

            .node-approver {
              font-size: 13px;
              color: var(--el-text-color-regular);
            }
          }
        }

        .approval-status {
          flex-shrink: 0;
        }
      }

      .approval-item-content {

        .approval-info-item {
          display: flex;
          margin-bottom: 8px;
          font-size: 14px;

          &:last-child {
            margin-bottom: 0;
          }

          .label {
            color: var(--el-text-color-secondary);
            width: 80px;
            flex-shrink: 0;
          }

          .value {
            color: var(--el-text-color-primary);
            flex: 1;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
          }
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
