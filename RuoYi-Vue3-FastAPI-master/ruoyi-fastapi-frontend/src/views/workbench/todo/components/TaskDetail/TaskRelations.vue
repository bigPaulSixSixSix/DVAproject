<template>
  <div class="task-relations-card">
    <div class="section-title">前后置任务关系</div>
    <div v-if="!hasRelations" class="empty-state">
      <el-empty description="该任务无前后置任务" :image-size="60" />
    </div>
    <div v-else class="relations-flow" ref="relationsFlowRef">
      <!-- SVG容器用于绘制连接线 -->
      <svg 
        class="connection-lines-svg" 
        v-if="hasRelations && svgWidth > 0 && svgHeight > 0"
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        preserveAspectRatio="none"
      >
        <!-- 前置任务到当前任务的连接线 -->
        <path
          v-for="(task, index) in predecessorTasks"
          :key="`predecessor-${getTaskId(task)}`"
          :d="getPredecessorPath(index)"
          class="connection-path"
          stroke="var(--el-border-color)"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- 当前任务到后置任务的连接线 -->
        <path
          v-for="(task, index) in successorTasks"
          :key="`successor-${getTaskId(task)}`"
          :d="getSuccessorPath(index)"
          class="connection-path"
          stroke="var(--el-border-color)"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>

      <!-- 左侧：前置任务 -->
      <div v-if="predecessorTasks.length > 0" class="predecessor-column">
        <div
          v-for="(task, index) in predecessorTasks"
          :key="getTaskId(task)"
          class="predecessor-item"
          :ref="el => setPredecessorRef(el, index)"
        >
          <div
            class="relation-task-card"
            :class="getTaskStatusClass(task)"
            @click="handleTaskClick(task)"
          >
            <div class="task-header">
              <div class="task-title" :class="getTaskStatusClass(task)">
                {{ getTaskName(task) }}
              </div>
              <el-icon class="task-arrow" :size="16" :class="getTaskStatusClass(task)">
                <ArrowRight />
              </el-icon>
            </div>
            <div class="task-content">
              <el-tag 
                :type="getStatusTagType(task)"
                :class="['status-tag', getStatusTagClass(task)]"
                size="small"
              >
                {{ getStatusText(task) }}
              </el-tag>
              <span class="task-info" :class="getTaskStatusClass(task)">
                {{ formatTaskDates(task) }} {{ getAssigneeName(task) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中心：当前任务 -->
      <div class="current-column" ref="currentTaskRef">
        <div class="current-task-box">当前任务</div>
      </div>

      <!-- 右侧：后置任务 -->
      <div v-if="successorTasks.length > 0" class="successor-column">
        <div
          v-for="(task, index) in successorTasks"
          :key="getTaskId(task)"
          class="successor-item"
          :ref="el => setSuccessorRef(el, index)"
        >
          <div
            class="relation-task-card"
            :class="getTaskStatusClass(task)"
            @click="handleTaskClick(task)"
          >
            <div class="task-header">
              <div class="task-title" :class="getTaskStatusClass(task)">
                {{ getTaskName(task) }}
              </div>
              <el-icon class="task-arrow" :size="16" :class="getTaskStatusClass(task)">
                <ArrowRight />
              </el-icon>
            </div>
            <div class="task-content">
              <el-tag 
                :type="getStatusTagType(task)"
                :class="['status-tag', getStatusTagClass(task)]"
                size="small"
              >
                {{ getStatusText(task) }}
              </el-tag>
              <span class="task-info" :class="getTaskStatusClass(task)">
                {{ formatTaskDates(task) }} {{ getAssigneeName(task) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

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

// 获取任务ID（从taskInfo中获取）
const getTaskId = (task) => {
  return task?.taskInfo?.taskId || task?.taskId
}

// 获取任务信息
const getTaskInfo = (task) => {
  return task?.taskInfo || task
}

const handleTaskClick = (task) => {
  const taskInfo = getTaskInfo(task)
  emit('task-click', taskInfo)
}

// 获取任务名称
const getTaskName = (task) => {
  const taskInfo = getTaskInfo(task)
  return taskInfo.taskName || '任务'
}

// 获取任务状态文本
const getTaskStatus = (task) => {
  const taskInfo = getTaskInfo(task)
  const status = taskInfo.taskStatus
  const statusName = taskInfo.taskStatusName
  
  // 未生成任务
  if (status === -1 || statusName === '未生成') return '未生成'
  if (status === 1) return '待提交'  // 改为待提交
  if (status === 2) return '审批中'
  if (status === 3 || statusName === '完成' || statusName?.includes('完成')) return '完成'
  return '未开始'
}

// 获取状态文本（用于标签显示）
const getStatusText = (task) => {
  const status = getTaskStatus(task)
  const date = formatStatusDate(task)
  if (status === '完成' && date) {
    return `${status} ${date}`
  }
  return status
}

// 获取任务状态样式类（用于文字和图标颜色）
const getTaskStatusClass = (task) => {
  const taskInfo = getTaskInfo(task)
  const status = taskInfo.taskStatus
  const statusName = taskInfo.taskStatusName
  
  // 未生成任务
  if (status === -1 || statusName === '未生成') return 'status-ungenerated'
  if (status === 1) return 'status-in-progress' // 待提交 - 蓝色
  if (status === 2) return 'status-approving' // 审批中 - 黄色
  if (status === 4) return 'status-rejected' // 驳回 - 红色
  if (status === 3 || statusName === '完成' || statusName?.includes('完成')) return 'status-completed' // 完成 - 灰色
  return 'status-not-started' // 未开始 - 灰色
}

// 获取状态标签样式类
const getStatusTagClass = (task) => {
  return getTaskStatusClass(task)
}

// 获取状态标签类型（用于 Element Plus 的 type 属性）
const getStatusTagType = (task) => {
  const taskInfo = getTaskInfo(task)
  const status = taskInfo.taskStatus
  const statusName = taskInfo.taskStatusName
  
  // 未生成任务
  if (status === -1 || statusName === '未生成') return 'info'
  // 待提交 - 蓝色
  if (status === 1) return 'primary'
  // 审批中 - 黄色
  if (status === 2) return 'warning'
  // 驳回 - 红色
  if (status === 4) return 'danger'
  // 完成 - 灰色
  if (status === 3 || statusName === '完成' || statusName?.includes('完成')) return 'info'
  // 未开始 - 灰色
  return 'info'
}

// 格式化状态日期（从taskInfo中获取，如果没有则从task中获取）
const formatStatusDate = (task) => {
  const taskInfo = getTaskInfo(task)
  // 如果有actualEndTime，使用actualEndTime；否则使用task中的其他日期字段
  if (task.actualEndTime) {
    const date = new Date(task.actualEndTime)
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
  return ''
}

// 格式化任务日期
const formatTaskDates = (task) => {
  const taskInfo = getTaskInfo(task)
  
  // 未生成任务，返回 "-"
  if (taskInfo.taskStatus === -1 || taskInfo.taskStatusName === '未生成') {
    return '-'
  }
  
  // 从taskInfo中获取日期信息，如果没有则从task中获取
  // 需要从任务详情接口返回的数据中获取，这里先尝试多种可能的字段
  let startTime = taskInfo.actualStartTime || taskInfo.startTime || task.startTime || task.planStartTime
  let endTime = taskInfo.actualCompleteTime || taskInfo.endTime || task.endTime || task.planEndTime
  let duration = taskInfo.duration || task.duration || taskInfo.totalDuration || task.totalDuration
  
  // 如果没有duration，尝试从日期计算
  if (!duration && startTime && endTime) {
    const start = new Date(startTime)
    const end = new Date(endTime)
    duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  }
  
  if (startTime && endTime) {
    const start = new Date(startTime).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    const end = new Date(endTime).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
    const days = duration || 1
    return `${start} - ${end} 共${days}天`
  }
  return '-'
}

// 获取负责人名称
const getAssigneeName = (task) => {
  const taskInfo = getTaskInfo(task)
  return taskInfo.assigneeName || '未分配'
}

// DOM引用
const relationsFlowRef = ref(null)
const predecessorRefs = ref([])
const successorRefs = ref([])
const currentTaskRef = ref(null)

// SVG尺寸
const svgWidth = ref(1000)
const svgHeight = ref(200)

// 设置前置任务引用
const setPredecessorRef = (el, index) => {
  if (el) {
    predecessorRefs.value[index] = el
  }
}

// 设置后置任务引用
const setSuccessorRef = (el, index) => {
  if (el) {
    successorRefs.value[index] = el
  }
}

// 更新SVG尺寸
const updateSvgSize = () => {
  if (relationsFlowRef.value) {
    const rect = relationsFlowRef.value.getBoundingClientRect()
    svgWidth.value = rect.width
    svgHeight.value = rect.height
  }
}

// 获取前置任务连接线路径（横平竖直，带圆角）
const getPredecessorPath = (index) => {
  if (!predecessorRefs.value[index] || !currentTaskRef.value || !relationsFlowRef.value) {
    return ''
  }
  
  // 确保SVG尺寸已初始化
  if (svgWidth.value === 0 || svgHeight.value === 0) {
    return ''
  }

  const predecessorEl = predecessorRefs.value[index]
  const currentEl = currentTaskRef.value
  const container = relationsFlowRef.value

  const predecessorRect = predecessorEl.getBoundingClientRect()
  const currentRect = currentEl.getBoundingClientRect()
  const containerRect = container.getBoundingClientRect()

  // 起点：前置任务右侧中心点（相对于容器）
  const startX = predecessorRect.right - containerRect.left
  const startY = predecessorRect.top + predecessorRect.height / 2 - containerRect.top

  // 终点：当前任务左侧中心点（相对于容器）
  const endX = currentRect.left - containerRect.left
  const endY = currentRect.top + currentRect.height / 2 - containerRect.top

  // 圆角半径
  const radius = 8

  // 构建路径：水平 -> 垂直 -> 水平，带圆角
  let path = `M ${startX} ${startY}` // 起点

  // 如果起点和终点在同一水平线，直接画水平线
  if (Math.abs(startY - endY) < 5) {
    path += ` L ${endX} ${endY}`
  } else {
    // 计算中间转折点（X坐标取中点）
    const midX = (startX + endX) / 2

    // 第一段：水平向右到中间点前（留出圆角空间）
    const horizontalEndX = midX - radius
    path += ` L ${horizontalEndX} ${startY}`

    // 圆角转折（如果垂直距离足够）
    if (Math.abs(startY - endY) > radius * 2) {
      if (endY > startY) {
        // 向下转折：第一个圆角（从水平到垂直）
        path += ` A ${radius} ${radius} 0 0 1 ${midX} ${startY + radius}`
        // 垂直段：从第一个圆角后到第二个圆角前
        path += ` L ${midX} ${endY - radius}`
        // 第二个圆角（从垂直到水平）- 改变方向
        path += ` A ${radius} ${radius} 0 0 0 ${midX + radius} ${endY}`
      } else {
        // 向上转折：第一个圆角（从水平到垂直）
        path += ` A ${radius} ${radius} 0 0 0 ${midX} ${startY - radius}`
        // 垂直段：从第一个圆角后到第二个圆角前
        path += ` L ${midX} ${endY + radius}`
        // 第二个圆角（从垂直到水平）- 改变方向
        path += ` A ${radius} ${radius} 0 0 1 ${midX + radius} ${endY}`
      }
    } else {
      // 垂直距离太小，直接连接（不使用圆角）
      path += ` L ${midX} ${endY}`
    }

    // 第二段：水平向右到终点
    path += ` L ${endX} ${endY}`
  }

  return path
}

// 获取后置任务连接线路径（横平竖直，带圆角）
const getSuccessorPath = (index) => {
  if (!successorRefs.value[index] || !currentTaskRef.value || !relationsFlowRef.value) {
    return ''
  }
  
  // 确保SVG尺寸已初始化
  if (svgWidth.value === 0 || svgHeight.value === 0) {
    return ''
  }

  const successorEl = successorRefs.value[index]
  const currentEl = currentTaskRef.value
  const container = relationsFlowRef.value

  const successorRect = successorEl.getBoundingClientRect()
  const currentRect = currentEl.getBoundingClientRect()
  const containerRect = container.getBoundingClientRect()

  // 起点：当前任务右侧中心点（相对于容器）
  const startX = currentRect.right - containerRect.left
  const startY = currentRect.top + currentRect.height / 2 - containerRect.top

  // 终点：后置任务左侧中心点（相对于容器）
  const endX = successorRect.left - containerRect.left
  const endY = successorRect.top + successorRect.height / 2 - containerRect.top

  // 圆角半径
  const radius = 8

  // 构建路径：水平 -> 垂直 -> 水平，带圆角
  let path = `M ${startX} ${startY}` // 起点

  // 如果起点和终点在同一水平线，直接画水平线
  if (Math.abs(startY - endY) < 5) {
    path += ` L ${endX} ${endY}`
  } else {
    // 计算中间转折点（X坐标取中点）
    const midX = (startX + endX) / 2

    // 第一段：水平向右到中间点前（留出圆角空间）
    const horizontalEndX = midX - radius
    path += ` L ${horizontalEndX} ${startY}`

    // 圆角转折（如果垂直距离足够）
    if (Math.abs(startY - endY) > radius * 2) {
      if (endY > startY) {
        // 向下转折：第一个圆角（从水平到垂直）
        path += ` A ${radius} ${radius} 0 0 1 ${midX} ${startY + radius}`
        // 垂直段：从第一个圆角后到第二个圆角前
        path += ` L ${midX} ${endY - radius}`
        // 第二个圆角（从垂直到水平）- 改变方向
        path += ` A ${radius} ${radius} 0 0 0 ${midX + radius} ${endY}`
      } else {
        // 向上转折：第一个圆角（从水平到垂直）
        path += ` A ${radius} ${radius} 0 0 0 ${midX} ${startY - radius}`
        // 垂直段：从第一个圆角后到第二个圆角前
        path += ` L ${midX} ${endY + radius}`
        // 第二个圆角（从垂直到水平）- 改变方向
        path += ` A ${radius} ${radius} 0 0 1 ${midX + radius} ${endY}`
      }
    } else {
      // 垂直距离太小，直接连接（不使用圆角）
      path += ` L ${midX} ${endY}`
    }

    // 第二段：水平向右到终点
    path += ` L ${endX} ${endY}`
  }

  return path
}

// 更新路径（当DOM更新时）
onMounted(() => {
  nextTick(() => {
    updateSvgSize()
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateSvgSize)
})

// 监听任务数据变化，更新SVG尺寸
watch(
  () => [predecessorTasks.value.length, successorTasks.value.length],
  () => {
    nextTick(() => {
      updateSvgSize()
    })
  }
)

// 组件卸载时移除监听器
onUnmounted(() => {
  window.removeEventListener('resize', updateSvgSize)
})

</script>

<style scoped lang="scss">
.task-relations-card {
  border-radius: 4px;
  padding: 16px;

  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
  }

  .empty-state {
    padding: 12px 0;
    
    // 覆盖 el-empty 组件的默认 padding
    :deep(.el-empty) {
      padding: 0 !important;
    }
  }

    .relations-flow {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 20px;
      min-height: 120px;
      position: relative;
      padding: 20px 0;

      // SVG容器用于绘制连接线
      .connection-lines-svg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: visible;
      }

      .connection-path {
        pointer-events: none;
      }

    // 三列布局
    .predecessor-column {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      justify-content: flex-start;
      gap: 12px;
    }

    .current-column {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      gap: 12px;
    }

    .successor-column {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 12px;
    }

    // 前置任务项
    .predecessor-item {
      position: relative;
      display: flex;
      align-items: center;
      
      .relation-task-card {
        position: relative;
        background-color: var(--el-bg-color);
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 4px;
        padding: 12px;
        min-width: 200px;
        cursor: pointer;
        transition: all 0.2s;
        z-index: 1;

        &:hover {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .task-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
          gap: 8px;
        }

        .task-title {
          font-size: 14px;
          font-weight: 600;
          flex: 1;
          
          // 默认灰色（未开始）
          color: var(--el-text-color-primary);
          
          // 进行中 - 蓝色
          &.status-in-progress {
            color: var(--el-color-primary);
          }
          
          // 审批中 - 橙色
          &.status-approving {
            color: var(--el-color-warning);
          }
          
          // 驳回 - 红色
          &.status-rejected {
            color: var(--el-color-danger);
          }
          
          // 完成 - 灰色
          &.status-completed {
            color: var(--el-text-color-primary);
          }
          
          // 未生成 - 灰色虚线
          &.status-ungenerated {
            color: var(--el-text-color-secondary);
          }
        }

        .task-arrow {
          flex-shrink: 0;
          
          // 默认灰色（未开始）
          color: var(--el-text-color-regular);
          
          // 进行中 - 蓝色
          &.status-in-progress {
            color: var(--el-color-primary);
          }
          
          // 审批中 - 橙色
          &.status-approving {
            color: var(--el-color-warning);
          }
          
          // 驳回 - 红色
          &.status-rejected {
            color: var(--el-color-danger);
          }
          
          // 完成 - 灰色
          &.status-completed {
            color: var(--el-text-color-regular);
          }
        }

        .task-content {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;

          .status-tag {
            border-radius: 4px;
            font-size: 12px;
            padding: 2px 8px;
            flex-shrink: 0;
            
            // 默认样式（未开始）
            background-color: var(--el-fill-color-light);
            color: var(--el-text-color-primary);
            
            // 待提交 - 蓝色
            &.status-in-progress {
              background-color: var(--el-color-primary-light-9);
              color: var(--el-color-primary);
            }
            
            // 审批中 - 黄色
            &.status-approving {
              background-color: var(--el-color-warning-light-9);
              color: var(--el-color-warning);
            }
            
            // 驳回 - 红色
            &.status-rejected {
              background-color: var(--el-color-danger-light-9);
              color: var(--el-color-danger);
            }
            
            // 完成 - 灰色
            &.status-completed {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-primary);
            }
            
            // 未生成 - 灰色
            &.status-ungenerated {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-secondary);
            }
          }

          .task-info {
            font-size: 12px;
            line-height: 1.4;
            
            // 默认灰色（未开始）
            color: var(--el-text-color-primary);
            
            // 待提交 - 蓝色
            &.status-in-progress {
              color: var(--el-color-primary);
            }
            
            // 审批中 - 黄色
            &.status-approving {
              color: var(--el-color-warning);
            }
            
            // 驳回 - 红色
            &.status-rejected {
              color: var(--el-color-danger);
            }
            
            // 完成 - 灰色
            &.status-completed {
              color: var(--el-text-color-primary);
            }
            
            // 未生成 - 灰色
            &.status-ungenerated {
              color: var(--el-text-color-secondary);
            }
          }
        }
        
        // 未生成任务样式
        &.status-ungenerated {
          opacity: 0.6;
          border-style: dashed;
          border-color: #909399;
        }
      }

    }

    // 当前任务
    .current-column {
      flex-shrink: 0;
      min-width: 120px;
      position: relative;

      .current-task-box {
        width:100%;
        padding: 16px 24px;
        border: 2px solid var(--el-color-primary);
        border-radius: 4px;
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
        font-weight: 600;
        font-size: 14px;
        white-space: nowrap;
        text-align: center;
        position: relative;
        z-index: 1;
      }
    }

    // 后置任务项
    .successor-item {
      position: relative;
      display: flex;
      align-items: center;


      .relation-task-card {
        position: relative;
        background-color: var(--el-bg-color);
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 4px;
        padding: 12px;
        min-width: 200px;
        cursor: pointer;
        transition: all 0.2s;
        z-index: 1;

        &:hover {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .task-header {
          display: flex;
          align-items: center;
          justify-content: flex-start;
          margin-bottom: 8px;
          gap: 8px;
        }

        .task-arrow {
          flex-shrink: 0;
          
          // 默认灰色（未开始）
          color: var(--el-text-color-regular);
          
          // 进行中 - 蓝色
          &.status-in-progress {
            color: var(--el-color-primary);
          }
          
          // 审批中 - 橙色
          &.status-approving {
            color: var(--el-color-warning);
          }
          
          // 驳回 - 红色
          &.status-rejected {
            color: var(--el-color-danger);
          }
          
          // 完成 - 灰色
          &.status-completed {
            color: var(--el-text-color-regular);
          }
          
          // 未生成 - 灰色
          &.status-ungenerated {
            color: var(--el-text-color-secondary);
          }
        }

        .task-title {
          font-size: 14px;
          font-weight: 600;
          flex: 1;
          
          // 默认灰色（未开始）
          color: var(--el-text-color-primary);
          
          // 进行中 - 蓝色
          &.status-in-progress {
            color: var(--el-color-primary);
          }
          
          // 审批中 - 橙色
          &.status-approving {
            color: var(--el-color-warning);
          }
          
          // 驳回 - 红色
          &.status-rejected {
            color: var(--el-color-danger);
          }
          
          // 完成 - 灰色
          &.status-completed {
            color: var(--el-text-color-primary);
          }
        }

        .task-content {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;

          .status-tag {
            border-radius: 4px;
            font-size: 12px;
            padding: 2px 8px;
            flex-shrink: 0;
            
            // 默认样式（未开始）
            background-color: var(--el-fill-color-light);
            color: var(--el-text-color-primary);
            
            // 待提交 - 蓝色
            &.status-in-progress {
              background-color: var(--el-color-primary-light-9);
              color: var(--el-color-primary);
            }
            
            // 审批中 - 黄色
            &.status-approving {
              background-color: var(--el-color-warning-light-9);
              color: var(--el-color-warning);
            }
            
            // 驳回 - 红色
            &.status-rejected {
              background-color: var(--el-color-danger-light-9);
              color: var(--el-color-danger);
            }
            
            // 完成 - 灰色
            &.status-completed {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-primary);
            }
            
            // 未生成 - 灰色
            &.status-ungenerated {
              background-color: var(--el-fill-color-light);
              color: var(--el-text-color-secondary);
            }
          }

          .task-info {
            font-size: 12px;
            line-height: 1.4;
            
            // 默认灰色（未开始）
            color: var(--el-text-color-primary);
            
            // 待提交 - 蓝色
            &.status-in-progress {
              color: var(--el-color-primary);
            }
            
            // 审批中 - 黄色
            &.status-approving {
              color: var(--el-color-warning);
            }
            
            // 驳回 - 红色
            &.status-rejected {
              color: var(--el-color-danger);
            }
            
            // 完成 - 灰色
            &.status-completed {
              color: var(--el-text-color-primary);
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
