<template>
  <el-card class="function-card" shadow="hover" @click="handleClick">
    <div class="function-content">
      <div class="function-icon">
        <el-icon :size="32" :color="iconColor">
          <component :is="iconName" />
        </el-icon>
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
  height: 100px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.function-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
}

.function-icon {
  margin-bottom: 12px;
}

.function-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  text-align: center;
}

.function-arrow {
  position: absolute;
  top: 12px;
  right: 12px;
}
</style>
