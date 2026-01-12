<template>
  <div class="task-relations">
    <div class="section-title">前后置任务关系</div>
    <div v-if="!hasRelations" class="empty-state">
      <el-empty description="该任务无前后置任务" :image-size="60" />
    </div>
    <div v-else class="relations-content">
      <div v-if="predecessorTasks.length > 0" class="relation-group">
        <div class="group-title">前置任务</div>
        <div class="task-list">
          <div
            v-for="task in predecessorTasks"
            :key="task.taskId"
            class="relation-task"
            @click="handleTaskClick(task)"
          >
            <el-icon :size="16" color="#409EFF">
              <ArrowLeft />
            </el-icon>
            <span class="task-name">{{ task.taskName }}</span>
          </div>
        </div>
      </div>
      <div v-if="successorTasks.length > 0" class="relation-group">
        <div class="group-title">后置任务</div>
        <div class="task-list">
          <div
            v-for="task in successorTasks"
            :key="task.taskId"
            class="relation-task"
            @click="handleTaskClick(task)"
          >
            <el-icon :size="16" color="#67C23A">
              <ArrowRight />
            </el-icon>
            <span class="task-name">{{ task.taskName }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

defineOptions({
  name: 'TaskRelations'
})

const props = defineProps({
  taskRelations: {
    type: Object,
    default: () => ({
      predecessorTasks: [],
      successorTasks: []
    })
  }
})

const emit = defineEmits(['task-click'])

const predecessorTasks = computed(() => {
  return props.taskRelations?.predecessorTasks || []
})

const successorTasks = computed(() => {
  return props.taskRelations?.successorTasks || []
})

const hasRelations = computed(() => {
  return predecessorTasks.value.length > 0 || successorTasks.value.length > 0
})

const handleTaskClick = (task) => {
  emit('task-click', task)
}
</script>

<style scoped lang="scss">
.task-relations {
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

  .relations-content {
    .relation-group {
      margin-bottom: 16px;

      .group-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-bottom: 8px;
      }

      .task-list {
        .relation-task {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 12px;
          margin-bottom: 8px;
          border: 1px solid var(--el-border-color-lighter);
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
          background-color: var(--el-bg-color);

          &:hover {
            border-color: var(--el-color-primary);
            background-color: var(--el-color-primary-light-9);
          }

          .task-name {
            font-size: 14px;
            color: var(--el-text-color-primary);
          }
        }
      }
    }
  }
}
</style>
