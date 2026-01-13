<template>
  <div class="approval-flow-card">
    <div class="section-title">审批流程</div>
    <div v-if="!approvalFlow" class="empty-state">
      <el-empty description="该任务无需审批，提交即通过" :image-size="60" />
    </div>
    <el-steps v-else :active="getActiveStepIndex()" finish-status="success" process-status="process" :align-center="false">
      <el-step
        v-for="(node, index) in approvalFlow.approvalNodes"
        :key="node.nodeIndex"
        :title="getStepTitle(node)"
        :description="getStepDescription(node)"
        :status="getStepStatus(node, index)"
      />
    </el-steps>
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
  },
  taskInfo: {
    type: Object,
    default: null
  }
})

// 获取步骤标题
const getStepTitle = (node) => {
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
      return `${postName} ${node.approverName} 审批`
    } else {
      return `${postName} 空岗 跳过`
    }
  }
  
  // 待审批状态
  if (node.status === 'pending') {
    if (node.approverId && node.approverName) {
      return `${postName} ${node.approverName} 审批`
    } else {
      return `${postName} 空岗 跳过`
    }
  }
  
  return `${postName} 审批`
}

// 获取步骤描述（审批时间）
const getStepDescription = (node) => {
  // 如果审批时间为 null，显示"未审批"
  return node.approvalTime || '未审批'
}

// 获取步骤状态
// Element Plus steps 组件状态：
// - wait: 等待状态（灰色，默认）
// - process: 处理中状态（蓝色）
// - success: 成功状态（绿色）
// - error: 错误状态（红色）
const getStepStatus = (node, index) => {
  // 审批驳回：error（错误状态，红色）
  if (node.status === 'rejected') {
    return 'error'
  }
  
  // 审批未开始：wait（等待状态，灰色）
  if (node.status === 'pending') {
    return 'wait'
  }
  
  // 当前审批节点：process（处理中状态，蓝色）
  if (node.status === 'approving') {
    return 'process'
  }
  
  // 已审批节点：success（成功状态，绿色）
  if (node.status === 'approved') {
    return 'success'
  }
  
  // 默认返回 wait
  return 'wait'
}

// 获取当前激活的步骤索引
const getActiveStepIndex = () => {
  if (!props.approvalFlow || !props.approvalFlow.approvalNodes) {
    return -1
  }
  
  const nodes = props.approvalFlow.approvalNodes
  
  // 找到第一个状态为 approving 的节点索引
  const approvingIndex = nodes.findIndex(
    node => node.status === 'approving'
  )
  
  if (approvingIndex !== -1) {
    return approvingIndex
  }
  
  // 找到第一个状态为 rejected 的节点索引（驳回节点）
  const rejectedIndex = nodes.findIndex(
    node => node.status === 'rejected'
  )
  
  if (rejectedIndex !== -1) {
    return rejectedIndex
  }
  
  // 检查是否所有节点都是 approved
  const allApproved = nodes.every(node => node.status === 'approved')
  if (allApproved) {
    // 如果所有节点都已完成，返回节点总数，使所有步骤显示为完成状态
    return nodes.length
  }
  
  // 如果没有审批中的节点，找到最后一个已审批的节点索引
  let lastApprovedIndex = -1
  nodes.forEach((node, index) => {
    if (node.status === 'approved') {
      lastApprovedIndex = index
    }
  })
  
  return lastApprovedIndex
}
</script>

<style scoped lang="scss">
.approval-flow-card {
  border-radius: 4px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
  }

  .empty-state {
    padding: 12px 0;
    
    // 覆盖 el-empty 组件的默认 padding
    :deep(.el-empty) {
      padding: 0 !important;
    }
  }

  // 审批流容器样式（只保留布局相关样式，不覆盖状态颜色）
  :deep(.el-steps) {
    padding: 0;
    display: flex;
    justify-content: center; // 居中对齐
    
    .el-step {
      // 固定宽度为240px
      width: 240px !important;
      flex: 0 0 240px !important;
      
      // 去掉固定高度，使用最小高度
      height: auto !important;
      min-height: auto;
      
      // 去掉所有 line-height
      line-height: normal !important;
      
      // 最后一个step使用最小尺寸
      &:last-child {
        width: auto !important;
        flex: 0 0 auto !important;
      }
      
      .el-step__head {
        line-height: normal !important;
        margin-bottom: 8px; // 图标距下方文字 8px
        
        // 所有描边、线，1px solid
        .el-step__icon {
          border-width: 1px !important;
          border-style: solid !important;
        }
      }
      
      .el-step__main {
        line-height: normal !important;
        
        .el-step__title {
          font-size: 14px !important; // 主标题字号 14px
          line-height: normal !important;
          margin-bottom: 4px; // 主标题距小字 4px
        }
        
        .el-step__description {
          font-size: 12px !important; // 小字字号 12px
          line-height: normal !important;
        }
      }
      
      // step_line 的 border 应为 0，因为已经有高度 1px
      .el-step__line {
        border: 0 !important;
        height: 1px !important;
      }
      
      // 根据节点自身状态设置连接线颜色
      // 如果节点状态是 success（approved），连接线应该是绿色
      // 如果节点状态是 wait/process/error（pending/approving/rejected），连接线应该是灰色
      &.is-success {
        .el-step__line {
          background-color: var(--el-color-success) !important;
        }
      }
      
      &.is-process {
        .el-step__line {
          background-color: var(--el-border-color-lighter) !important;
        }
      }
      
      &.is-wait {
        .el-step__line {
          background-color: var(--el-border-color-lighter) !important;
        }
      }
      
      &.is-error {
        .el-step__line {
          background-color: var(--el-border-color-lighter) !important;
        }
      }
    }
  }
}
</style>
