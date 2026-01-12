<template>
  <div class="approval-content-card">
    <div class="section-title">审批结果</div>
    
    <div v-if="!canApprove && !approvalInfo" class="empty-state">
      <el-empty description="暂无审批结果" :image-size="60" />
    </div>
    <div v-else class="content-wrapper">
      <!-- 可编辑区域（如果允许审批） -->
      <template v-if="canApprove">
        <div class="content-item">
          <span class="label">审批结果 <span class="required">*</span></span>
          <div class="value">
            <el-radio-group v-model="approvalResult" class="approval-radio-group">
              <el-radio label="approve">通过</el-radio>
              <el-radio label="reject">驳回</el-radio>
            </el-radio-group>
          </div>
        </div>
        
        <!-- 驳回时显示审批说明 -->
        <template v-if="approvalResult === 'reject'">
          <div class="content-item">
            <span class="label">审批说明</span>
            <div class="value">
              <el-input
                v-model="approvalComment"
                type="textarea"
                :rows="6"
                placeholder="请填写驳回原因"
                class="approval-textarea"
              />
            </div>
          </div>
          
          <div class="content-item">
            <span class="label">图片</span>
            <div class="value">
              <div class="upload-area">
                <el-upload
                  v-model:file-list="fileList"
                  action="#"
                  list-type="picture-card"
                  :auto-upload="false"
                  :limit="9"
                  :on-preview="handlePreview"
                  :on-remove="handleRemove"
                  :on-exceed="handleExceed"
                >
                  <el-icon><Plus /></el-icon>
                </el-upload>
              </div>
            </div>
          </div>
        </template>
      </template>
      
      <!-- 已审批内容显示 -->
      <template v-else-if="approvalInfo">
        <div class="content-item">
          <span class="label">审批结果</span>
          <div class="value">
            <el-tag :type="approvalInfo.result === 'approve' ? 'success' : 'danger'" size="small">
              {{ approvalInfo.result === 'approve' ? '通过' : '驳回' }}
            </el-tag>
          </div>
        </div>
        
        <div v-if="approvalInfo.comment" class="content-item">
          <span class="label">审批说明</span>
          <div class="value comment-content">{{ approvalInfo.comment }}</div>
        </div>
        
        <div v-if="approvalInfo.images && approvalInfo.images.length > 0" class="content-item">
          <span class="label">图片</span>
          <div class="value">
            <div class="images-list">
              <el-image
                v-for="(image, index) in approvalInfo.images"
                :key="index"
                :src="image"
                :preview-src-list="approvalInfo.images"
                fit="cover"
                class="approval-image"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'

defineOptions({
  name: 'ApprovalContent'
})

const props = defineProps({
  canApprove: {
    type: Boolean,
    default: false
  },
  approvalInfo: {
    type: Object,
    default: null
  }
})

const approvalResult = ref('')
const approvalComment = ref('')
const fileList = ref([])

// 预览图片
const handlePreview = (file) => {
  // Element Plus 会自动处理预览
}

// 移除图片
const handleRemove = (file) => {
  // Element Plus 会自动处理移除
}

// 超出限制
const handleExceed = () => {
  // Element Plus 会自动处理
}

// 验证审批数据
const validate = () => {
  if (!approvalResult.value) {
    return { valid: false, message: '请选择审批结果' }
  }
  
  if (approvalResult.value === 'reject') {
    if (!approvalComment.value || !approvalComment.value.trim()) {
      return { valid: false, message: '驳回时必须填写审批说明' }
    }
  }
  
  return { valid: true }
}

// 获取审批数据
const getApprovalData = () => {
  return {
    result: approvalResult.value,
    comment: approvalResult.value === 'reject' ? approvalComment.value : (approvalResult.value === 'approve' ? '同意' : ''),
    images: fileList.value.map(file => file.url || file.response?.url || '').filter(url => url)
  }
}

// 暴露方法供父组件调用
defineExpose({
  validate,
  getApprovalData
})
</script>

<style scoped lang="scss">
.approval-content-card {
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

  .content-wrapper {
      .content-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 12px;
      font-size: 14px;

      .label {
        color: var(--el-text-color-secondary);
        width: 100px;
        flex-shrink: 0;
        line-height: 1.5;
        
        .required {
          color: var(--el-color-danger);
        }
      }

      .value {
        color: var(--el-text-color-primary);
        flex: 1;
        line-height: 1.5;

        .approval-radio-group {
          line-height: 1.5;
          height: auto;
          
          :deep(.el-radio) {
            margin-right: 24px;
            height: auto;
            line-height: 1.5;
            
            .el-radio__label {
              line-height: 1.5;
              padding-left: 8px;
            }
          }
        }

        .comment-content {
          line-height: 1.8;
          white-space: pre-wrap;
          word-break: break-word;
        }

        .images-list {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;

          .approval-image {
            width: 120px;
            height: 120px;
            border-radius: 4px;
            cursor: pointer;
          }
        }

        .approval-textarea {
          :deep(.el-textarea__inner) {
            resize: none;
          }
        }

        .upload-area {
          :deep(.el-upload) {
            width: 120px;
            height: 120px;
            border: 1px dashed var(--el-border-color);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;

            &:hover {
              border-color: var(--el-color-primary);
            }

            .el-icon {
              font-size: 28px;
              color: var(--el-text-color-placeholder);
            }
          }

          :deep(.el-upload-list) {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
          }

          :deep(.el-upload-list__item) {
            width: 120px;
            height: 120px;
            margin: 0;
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

