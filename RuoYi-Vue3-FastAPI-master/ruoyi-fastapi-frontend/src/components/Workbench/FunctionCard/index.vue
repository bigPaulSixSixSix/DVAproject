<template>
  <el-card class="function-card" shadow="hover" @click="handleClick" :body-style="{ padding: '0' }">
    <div class="function-content">
      <div class="function-icon">
        <svg-icon :icon-class="iconName" :style="{ color: iconColor, fontSize: '24px' }" />
      </div>
      <div class="function-title">{{ title }}</div>
      <div class="function-arrow">
        <el-icon :size="16" color="#999">
          <ArrowRight />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import SvgIcon from '@/components/SvgIcon'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  iconName: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: '#409EFF'
  },
  path: {
    type: String,
    required: true
  }
})

const router = useRouter()

const handleClick = () => {
  router.push(props.path)
}
</script>

<style scoped lang="scss">
.function-card {
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  // 强制覆盖Element Plus的默认padding
  :deep(.el-card__body) {
    padding: 0 !important;
  }
}

.function-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
  position: relative;
  padding: 16px;
}

.function-icon {
  margin-right: 12px;
  flex-shrink: 0;
}

.function-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  flex: 1;
  text-align: left;
}

.function-arrow {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
}
</style>
