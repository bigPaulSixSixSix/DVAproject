<template>
  <div @click="handleClick" class="function-link">
    <el-card class="function-card" shadow="hover" :body-style="{ padding: '0' }">
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
  </div>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'
import SvgIcon from '@/components/SvgIcon'
import { getNormalPath } from '@/utils/ruoyi'
import { useRouter } from 'vue-router'

const router = useRouter()

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

// 规范化路径，使用完整路径
const normalizedPath = computed(() => {
  return getNormalPath(props.path)
})

// 处理点击事件
const handleClick = () => {
  router.push(normalizedPath.value)
}
</script>

<style scoped lang="scss">
.function-link {
  display: block;
  text-decoration: none;
  color: inherit;
  
  &:hover {
    text-decoration: none;
    color: inherit;
  }
}

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
  align-items: center;
}

.function-arrow {
  display: flex;
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  align-items: center;
}
</style>
