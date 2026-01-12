<template>
  <div class="submit-content">
    <div class="section-title">提交内容</div>
    <div v-if="!submitContent" class="empty-state">
      <el-empty description="该任务尚未提交" :image-size="60" />
    </div>
    <div v-else class="content-display">
      <div v-if="submitContent.submitText" class="submit-text">
        <div class="text-label">提交文本：</div>
        <div class="text-content">{{ submitContent.submitText }}</div>
      </div>
      <div v-if="submitContent.submitImages && submitContent.submitImages.length > 0" class="submit-images">
        <div class="images-label">提交图片：</div>
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
      <div v-if="submitContent.submitTime" class="submit-time">
        提交时间：{{ submitContent.submitTime }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'SubmitContent'
})

const props = defineProps({
  submitContent: {
    type: Object,
    default: null
  }
})
</script>

<style scoped lang="scss">
.submit-content {
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

  .content-display {
    .submit-text {
      margin-bottom: 16px;

      .text-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }

      .text-content {
        font-size: 14px;
        color: var(--el-text-color-primary);
        line-height: 1.8;
        padding: 12px;
        background-color: var(--el-fill-color-light);
        border-radius: 4px;
        white-space: pre-wrap;
        word-break: break-word;
      }
    }

    .submit-images {
      margin-bottom: 16px;

      .images-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
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

    .submit-time {
      font-size: 13px;
      color: var(--el-text-color-regular);
    }
  }
}
</style>
