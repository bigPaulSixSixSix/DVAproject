<template>
  <div class="submit-content-card">
    <div class="section-header">
      <div class="section-title">提交内容</div>
      <div 
        v-if="historyApproval && historyApproval.length > 0" 
        class="history-link"
        @click="handleShowHistory"
      >
        提交/审批记录（{{ historyApproval.length }}）
        <el-icon :size="14" style="margin-left: 4px;">
          <ArrowRight />
        </el-icon>
      </div>
    </div>
    
    <div v-if="!submitContent && !canEdit" class="empty-state">
      <el-empty description="暂无提交内容" :image-size="60" />
    </div>
    <div v-else class="content-wrapper">
      <!-- 已提交内容显示（所有状态都显示） -->
      <template v-if="submitContent">
        <div v-if="submitContent.submitText" class="content-item">
          <span class="label">完成情况</span>
          <div class="value text-content">{{ submitContent.submitText }}</div>
        </div>
        <div v-if="submitContent.submitImages && submitContent.submitImages.length > 0" class="content-item">
          <span class="label">图片</span>
          <div class="value">
            <div class="images-list">
              <el-image
                v-for="(image, index) in submitContent.submitImages"
                :key="index"
                :src="image"
                :preview-src-list="submitContent.submitImages"
                fit="cover"
                class="submit-image"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- 可编辑区域（如果允许提交或重新提交，且非驳回状态） -->
      <template v-if="canEdit && !isRejected">
        <div class="content-item">
          <span class="label">
            完成情况
            <span class="required">*</span>
          </span>
          <div class="value">
            <el-input
              v-model="submitText"
              type="textarea"
              :rows="6"
              placeholder="请填写完成情况"
              class="submit-textarea"
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
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, ArrowRight } from '@element-plus/icons-vue'

defineOptions({
  name: 'SubmitContent'
})

const props = defineProps({
  submitContent: {
    type: Object,
    default: null
  },
  canSubmit: {
    type: Boolean,
    default: false
  },
  canResubmit: {
    type: Boolean,
    default: false
  },
  taskStatus: {
    type: Number,
    default: null
  },
  historyApproval: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-history'])

const submitText = ref('')
const fileList = ref([])

const canEdit = computed(() => {
  return props.canSubmit || props.canResubmit
})

// 判断是否为驳回状态
const isRejected = computed(() => {
  return props.taskStatus === 4
})

// 监听 submitContent 变化，当任务切换时重置输入内容
watch(() => props.submitContent, (newVal, oldVal) => {
  // 如果任务切换了（submitContent 变化），重置输入内容
  if (newVal !== oldVal) {
    submitText.value = ''
    fileList.value = []
  }
}, { deep: true })

// 监听 canSubmit 和 canResubmit 变化，当任务切换时重置输入内容
watch([() => props.canSubmit, () => props.canResubmit], () => {
  // 当任务切换导致权限变化时，重置输入内容
  submitText.value = ''
  fileList.value = []
})

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

// 显示历史记录
const handleShowHistory = () => {
  emit('show-history')
}

// 暴露方法供父组件调用，获取提交文本
defineExpose({
  getSubmitText: () => submitText.value
})
</script>

<style scoped lang="scss">
.submit-content-card {
  border-radius: 4px;
  padding: 16px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .history-link {
      font-size: 14px;
      color: var(--el-text-color-regular);
      cursor: pointer;
      user-select: none;
      display: flex;
      align-items: center;

      &:hover {
        color: var(--el-text-color-primary);
      }
    }
  }

  .empty-state {
    padding: 20px 0;
  }

  .content-wrapper {
    .content-item {
      display: flex;
      margin-bottom: 12px;
      font-size: 14px;

      .label {
        color: var(--el-text-color-secondary);
        width: 100px;
        flex-shrink: 0;

        .required {
          color: var(--el-color-danger);
          margin-left: 2px;
        }
      }

      .value {
        color: var(--el-text-color-primary);
        flex: 1;

        .text-content {
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

        .submit-textarea {
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
}
</style>
