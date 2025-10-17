<template>
  <el-card class="summary-card" shadow="hover">
    <div class="summary-content">
      <div class="summary-icon">
        <el-icon :size="24" :color="iconColor">
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
        <el-icon :size="16" color="#999">
          <ArrowRight />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'

defineProps({
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
    default: '#409EFF'
  }
})
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
