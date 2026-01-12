<template>
  <el-card class="summary-card" shadow="hover" @click="handleClick">
    <div class="summary-content">
      <div class="summary-icon">
        <el-icon :size="24" :style="{ color: computedIconColor }">
          <component :is="iconName" />
        </el-icon>
      </div>
      <div class="summary-info">
        <div class="summary-title">
          <span>{{ title }}</span>
          <el-tag :type="badgeType" size="small" class="summary-badge">
            {{ badgeText }}
          </el-tag>
        </div>
        <div class="summary-desc">{{ description }}</div>
      </div>
      <div class="summary-arrow">
        <el-icon :size="16" :style="{ color: 'var(--el-text-color-placeholder)' }">
          <ArrowRight />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  badgeText: {
    type: String,
    required: true
  },
  badgeType: {
    type: String,
    default: 'primary'
  },
  iconName: {
    type: String,
    required: true
  },
  iconColor: {
    type: String,
    default: 'primary'
  },
  onClick: {
    type: Function,
    default: null
  }
})

// 颜色类型映射到 Element Plus CSS 变量
const colorMap = {
  primary: 'var(--el-color-primary)',
  success: 'var(--el-color-success)',
  warning: 'var(--el-color-warning)',
  danger: 'var(--el-color-danger)',
  info: 'var(--el-color-info)'
}

// 计算图标颜色：如果是颜色类型则使用 CSS 变量，否则使用传入的值
const computedIconColor = computed(() => {
  if (colorMap[props.iconColor]) {
    return colorMap[props.iconColor]
  }
  // 如果传入的是具体的色值（以 # 开头），则直接使用
  return props.iconColor
})

const handleClick = () => {
  if (props.onClick) {
    props.onClick()
  }
}
</script>

<style scoped lang="scss">
.summary-card {
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.summary-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.summary-icon {
  margin-right: 16px;
  flex-shrink: 0;
}

.summary-info {
  flex: 1;
  min-width: 0;
}

.summary-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  
  span {
    font-size: 16px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-right: 8px;
  }
}

.summary-badge {
  flex-shrink: 0;
  font-size: 14px !important;
  
  // 确保在深色模式下使用正确的颜色，使用 Element Plus 色板
  &.el-tag--primary {
    background-color: var(--el-color-primary) !important;
    border-color: var(--el-color-primary) !important;
    color: #ffffff !important;
  }
  
  &.el-tag--success {
    background-color: var(--el-color-success) !important;
    border-color: var(--el-color-success) !important;
    color: #ffffff !important;
  }
  
  &.el-tag--warning {
    background-color: var(--el-color-warning) !important;
    border-color: var(--el-color-warning) !important;
    color: #ffffff !important;
  }
  
  &.el-tag--danger {
    background-color: var(--el-color-danger) !important;
    border-color: var(--el-color-danger) !important;
    color: #ffffff !important;
  }
  
  &.el-tag--info {
    background-color: var(--el-color-info) !important;
    border-color: var(--el-color-info) !important;
    color: #ffffff !important;
  }
}

.summary-desc {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-arrow {
  margin-left: 12px;
  flex-shrink: 0;
}
</style>
