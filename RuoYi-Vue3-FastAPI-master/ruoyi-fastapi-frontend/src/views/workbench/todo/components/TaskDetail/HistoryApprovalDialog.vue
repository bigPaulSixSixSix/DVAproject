<template>
  <el-dialog
    v-model="visible"
    title="提交/审批记录"
    width="1200px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading" class="history-approval-dialog">
      <div v-if="!historyApproval || historyApproval.length === 0" class="empty-state">
        <el-empty description="暂无历史记录" :image-size="100" />
      </div>
      <div v-else class="history-content">
        <!-- 左侧：历史记录列表 -->
        <div class="history-list">
          <div
            v-for="(item, index) in historyApproval"
            :key="item.applyId"
            class="history-item"
            :class="{ active: selectedIndex === index }"
            @click="handleSelectHistory(index)"
          >
            <div class="history-item-content">
              第{{ historyApproval.length - index }}次申请/审批
            </div>
          </div>
        </div>

        <!-- 右侧：详情内容 -->
        <div class="history-detail">
          <div v-if="selectedHistoryItem" class="detail-sections">
            <!-- 提交内容 -->
            <div class="detail-section">
              <div class="section-title">提交内容</div>
              <div v-if="selectedHistoryItem.submitContent" class="section-content">
                <div v-if="selectedHistoryItem.submitContent.submitText" class="content-item">
                  <span class="label">完成情况</span>
                  <div class="value text-content">{{ selectedHistoryItem.submitContent.submitText }}</div>
                </div>
                <div v-if="selectedHistoryItem.submitContent.submitImages && selectedHistoryItem.submitContent.submitImages.length > 0" class="content-item">
                  <span class="label">图片</span>
                  <div class="value">
                    <div class="images-list">
                      <el-image
                        v-for="(image, imgIndex) in selectedHistoryItem.submitContent.submitImages"
                        :key="imgIndex"
                        :src="image"
                        :preview-src-list="selectedHistoryItem.submitContent.submitImages"
                        fit="cover"
                        class="submit-image"
                      />
                    </div>
                  </div>
                </div>
                <div v-if="selectedHistoryItem.submitContent.submitTime" class="content-item">
                  <span class="label">提交时间</span>
                  <div class="value">{{ selectedHistoryItem.submitContent.submitTime }}</div>
                </div>
                <div v-if="selectedHistoryItem.submitContent.submitterName" class="content-item">
                  <span class="label">提交人</span>
                  <div class="value">{{ selectedHistoryItem.submitContent.submitterName }}</div>
                </div>
              </div>
              <div v-else class="empty-content">
                <el-empty description="暂无提交内容" :image-size="60" />
              </div>
            </div>

            <!-- 审批详情 -->
            <div class="detail-section">
              <div class="section-title">审批详情</div>
              <div v-if="selectedHistoryItem.approvalNodes && selectedHistoryItem.approvalNodes.length > 0" class="approval-detail-content">
                <div
                  v-for="(node, nodeIndex) in filteredApprovalNodes"
                  :key="node.nodeIndex"
                  class="approval-detail-item"
                  :class="{ 'has-divider': nodeIndex < filteredApprovalNodes.length - 1 }"
                >
                  <div class="approval-item-header">
                    <div class="approval-node-info">
                      <div class="node-index" :class="getNodeStatusClass(node.status)">
                        {{ node.nodeIndex }}
                      </div>
                      <div class="node-content">
                        <div class="node-title">{{ getNodeTitle(node) }}</div>
                      </div>
                    </div>
                    <div class="approval-status">
                      <el-tag :type="getStatusTagType(node.status)" size="small">
                        {{ getStatusText(node.status) }}
                      </el-tag>
                    </div>
                  </div>
                  
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
              <div v-else class="empty-content">
                <el-empty description="暂无审批详情" :image-size="60" />
              </div>
            </div>
          </div>
          <div v-else class="empty-detail">
            <el-empty description="请选择一条记录查看详情" :image-size="100" />
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

defineOptions({
  name: 'HistoryApprovalDialog'
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  historyApproval: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const loading = ref(false)
const selectedIndex = ref(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.historyApproval && props.historyApproval.length > 0) {
    // 默认选中第一条（最新的）
    selectedIndex.value = 0
  } else {
    selectedIndex.value = null
  }
})

// 当前选中的历史记录项
const selectedHistoryItem = computed(() => {
  if (selectedIndex.value === null || !props.historyApproval || props.historyApproval.length === 0) {
    return null
  }
  return props.historyApproval[selectedIndex.value]
})

// 过滤审批节点：一旦有驳回，就只显示到驳回节点为止
const filteredApprovalNodes = computed(() => {
  if (!selectedHistoryItem.value || !selectedHistoryItem.value.approvalNodes) {
    return []
  }
  
  const nodes = selectedHistoryItem.value.approvalNodes
  const rejectedIndex = nodes.findIndex(node => node.status === 'rejected')
  
  if (rejectedIndex !== -1) {
    return nodes.slice(0, rejectedIndex + 1)
  }
  
  return nodes
})

// 选择历史记录
const handleSelectHistory = (index) => {
  selectedIndex.value = index
}

// 获取节点标题
const getNodeTitle = (node) => {
  const postName = node.postName || '未知岗位'
  
  if (node.status === 'rejected') {
    const approverName = node.approverName || '未知'
    return `${postName} ${approverName} 审批驳回`
  }
  
  if (node.status === 'approved') {
    const approverName = node.approverName || '未知'
    if (node.approverId === 'system' || approverName === 'system') {
      return `${postName} 空岗 自动审批通过`
    } else {
      return `${postName} ${approverName} 审批通过`
    }
  }
  
  if (node.status === 'approving') {
    if (node.approverId && node.approverName) {
      return `${postName} ${node.approverName} 审批中`
    } else {
      return `${postName} 空岗 跳过`
    }
  }
  
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

// 关闭弹窗
const handleClose = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped lang="scss">
.history-approval-dialog {
  min-height: 400px;

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
  }

  .history-content {
    display: flex;
    min-height: 500px;
    max-height: 600px;

    // 左侧：历史记录列表
    .history-list {
      width: 200px;
      flex-shrink: 0;
      border-radius: 4px 0 0 4px;
      border:1px solid var(--el-border-color-light);
      margin-right: -1px;
      overflow-y: auto;
      background-color: var(--el-bg-color);

      .history-item {
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s;
        background-color: var(--el-bg-color);
        border-bottom: 1px solid var(--el-border-color-lighter);

        &:hover {
          background-color: var(--el-fill-color-lighter);
        }

        &.active {
          background-color: var(--el-bg-color-page);
        }

        &:last-child {
          border-bottom: none;
        }

        .history-item-content {
          font-size: 14px;
          color: var(--el-text-color-primary);
        }
      }
    }

    // 右侧：详情内容
    .history-detail {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background-color: var(--el-bg-color-page);
      border-radius: 0 4px 4px 0;
      border:1px solid var(--el-border-color-light);

      .empty-detail {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 400px;
      }

      .detail-sections {
        display: flex;
        flex-direction: column;
        gap: 16px;

        .detail-section {
          border-radius: 4px;
          padding: 16px;
          background-color: var(--el-bg-color);

          .section-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: 16px;
          }

          .empty-content {
            padding: 20px 0;
          }

          .section-content {
            .content-item {
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

                &.text-content {
                  line-height: 1.8;
                  white-space: pre-wrap;
                  word-break: break-word;
                }

                .images-list {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 12px;

                  .submit-image {
                    width: 120px;
                    height: 120px;
                    border-radius: 4px;
                    cursor: pointer;
                  }
                }
              }
            }
          }

          .approval-detail-content {
            .approval-detail-item {
              margin-bottom: 16px;

              &.has-divider {
                border-bottom: 1px solid var(--el-border-color-lighter);
                padding-bottom: 16px;
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
