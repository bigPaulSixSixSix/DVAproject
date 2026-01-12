<template>
  <svg 
    class="connection-line" 
    :class="{ 
      'connection-line--selected': isSelected,
      'connection-line--related': isRelatedToSelectedTask
    }"
    viewBox="0 0 20000 20000" 
    preserveAspectRatio="none"
    :style="{ zIndex: connectionZIndex }"
  >
    <path
      :d="pathData"
      fill="none"
      stroke="transparent"
      stroke-width="12"
      class="connection-line-hit-area"
      @click="handleClick"
      @mousedown.stop
    />
    <path
      :d="pathData"
      :class="[
        isValid ? 'connection-line--valid' : 'connection-line--invalid',
        isSelected ? 'connection-line--selected' : '',
        isRelatedToSelectedTask ? 'connection-line--related' : ''
      ]"
      :stroke-width="isSelected || isRelatedToSelectedTask ? '3' : '2'"
      fill="none"
      :stroke-dasharray="isValid ? 'none' : '5,5'"
      class="connection-line-visual"
    />
    <!-- 删除按钮：位于连接线中间，仅在选中时显示，且结束端点可编辑 -->
    <foreignObject
      v-if="middlePoint && isSelected && shouldShowDeleteButton"
      :x="middlePoint.x - 12"
      :y="middlePoint.y - 12"
      width="24"
      height="24"
      class="connection-delete-button-wrapper"
    >
      <el-button
        circle
        type="danger"
        size="small"
        class="connection-delete-button connection-delete-button--animate"
        @click.stop="handleDelete"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </foreignObject>
  </svg>
</template>

<script setup>
import { computed } from 'vue'
import { ElButton, ElIcon } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { useConnectionLine } from '../../composables/connection/useConnection'

const props = defineProps({
  connection: {
    type: Object,
    required: true
  },
  stages: {
    type: Array,
    default: () => []
  },
  unassignedTasks: {
    type: Array,
    default: () => []
  },
  isValid: {
    type: Boolean,
    default: true
  },
  selectedStageId: {
    type: [Number, String],
    default: null
  },
  selectedTaskId: {
    type: [Number, String],
    default: null
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  findTaskById: {
    type: Function,
    default: null
  },
  findStageById: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['select', 'delete'])

const { calculateBezierPath, getConnectionPoints } = useConnectionLine()

const pathData = computed(() => {
  if (!props.stages || props.stages.length === 0) {
    return ''
  }
  
  if (!props.connection || !props.connection.from || !props.connection.to) {
    return ''
  }
  
  const { fromPoint, toPoint } = getConnectionPoints(
    props.connection.from,
    props.connection.to,
    props.stages,
    props.unassignedTasks
  )
  
  // 如果连接点无效，返回空路径
  if (!fromPoint || !toPoint || (fromPoint.x === 0 && fromPoint.y === 0 && toPoint.x === 0 && toPoint.y === 0)) {
    return ''
  }
  
  const path = calculateBezierPath(fromPoint, toPoint)
  return path
})

// 判断连接线是否与选中的任务相关
const isRelatedToSelectedTask = computed(() => {
  if (!props.selectedTaskId || !props.connection || !props.connection.from || !props.connection.to) {
    return false
  }
  
  const selectedTaskIdStr = String(props.selectedTaskId)
  
  // 检查连接线的 from 或 to 是否是选中的任务
  const fromIsTask = props.connection.from.elementType === 'task'
  const toIsTask = props.connection.to.elementType === 'task'
  
  if (fromIsTask && String(props.connection.from.elementId) === selectedTaskIdStr) {
    return true
  }
  
  if (toIsTask && String(props.connection.to.elementId) === selectedTaskIdStr) {
    return true
  }
  
  return false
})

// 计算连接线的 z-index
// 连接线需要能够接收点击事件，所以 z-index 应该高于任务卡片（阶段外任务基础 z-index 为 300）
// 当连接线或关联阶段被选中时，z-index 需要进一步提升，确保展示和可点击性
const connectionZIndex = computed(() => {
  const anyStageInFront = props.stages?.some(stage => stage?._isResizing || stage?._isDragging)
  const activeBaseZ = props.isSelected ? 1500 : 1300
  
  if (!props.connection || !props.connection.from || !props.connection.to) {
    return anyStageInFront ? activeBaseZ : 600 // 默认值，高于任务卡片（300）
  }
  
  const fromType = props.connection.from.elementType
  const toType = props.connection.to.elementType
  
  // 如果连接线被选中，使用最高 z-index
  if (props.isSelected) {
    return activeBaseZ
  }

  if (anyStageInFront) {
    return activeBaseZ
  }
  
  // 辅助函数：检查阶段是否被选中
  const isStageSelected = (stageId) => {
    if (!props.selectedStageId || !stageId) return false
    return String(props.selectedStageId) === String(stageId)
  }
  
  // 阶段到阶段的连接
  if (fromType === 'stage' && toType === 'stage') {
    const fromStageIndex = props.stages.findIndex(s => String(s.id) === String(props.connection.from.elementId))
    const toStageIndex = props.stages.findIndex(s => String(s.id) === String(props.connection.to.elementId))
    
    const fromStage = props.stages[fromStageIndex]
    const toStage = props.stages[toStageIndex]
    
    // 如果连接的任一阶段被选中，提升 z-index 到 1001（高于阶段卡片的 1000）
    if ((fromStage && isStageSelected(fromStage.id)) || (toStage && isStageSelected(toStage.id))) {
      return 1100
    }
    
    // 否则使用较高的 z-index，确保能够接收点击事件（高于任务卡片 5）
    const maxIndex = Math.max(fromStageIndex, toStageIndex)
    return Math.max(600, 3 + maxIndex + 300) // 保证高于阶段外任务
  }
  
  // 任务到任务的连接
  if (fromType === 'task' && toType === 'task') {
    // 查找任务所在的阶段
    let stageIndex = -1
    let stage = null
    
    for (let i = 0; i < props.stages.length; i++) {
      const currentStage = props.stages[i]
      if (currentStage.tasks && Array.isArray(currentStage.tasks)) {
        const fromTask = currentStage.tasks.find(t => String(t.id) === String(props.connection.from.elementId))
        const toTask = currentStage.tasks.find(t => String(t.id) === String(props.connection.to.elementId))
        
        if (fromTask && toTask) {
          stageIndex = i
          stage = currentStage
          break
        }
      }
    }
    
    if (stageIndex >= 0) {
      // 如果阶段被选中，提升 z-index 到 1001（高于阶段卡片的 1000）
      if (stage && isStageSelected(stage.id)) {
        return 1100
      }
      
      // 否则使用较高的 z-index，确保能够接收点击事件（高于任务卡片 5）
      return Math.max(600, 3 + stageIndex + 300)
    }
  }
  
  // 默认值：高于任务卡片
  return 600
})

// 计算贝塞尔曲线的中点（t=0.5）
// 对于三次贝塞尔曲线 B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
// 当 t=0.5 时：B(0.5) = 0.125P₀ + 0.375P₁ + 0.375P₂ + 0.125P₃
const middlePoint = computed(() => {
  if (!props.stages || props.stages.length === 0) {
    return null
  }
  
  if (!props.connection || !props.connection.from || !props.connection.to) {
    return null
  }
  
  const { fromPoint, toPoint } = getConnectionPoints(
    props.connection.from,
    props.connection.to,
    props.stages,
    props.unassignedTasks
  )
  
  // 如果连接点无效，返回 null
  if (!fromPoint || !toPoint || (fromPoint.x === 0 && fromPoint.y === 0 && toPoint.x === 0 && toPoint.y === 0)) {
    return null
  }
  
  // 计算控制点（与 calculateBezierPath 中的逻辑保持一致）
  const HORIZONTAL_OFFSET = 0
  const curveDistance = Math.abs(toPoint.x - fromPoint.x)
  const verticalDistance = Math.abs(toPoint.y - fromPoint.y)
  const controlOffset = Math.min(curveDistance / 2, verticalDistance / 2, 100)
  
  const cp1 = {
    x: fromPoint.x + HORIZONTAL_OFFSET + controlOffset,
    y: fromPoint.y
  }
  
  const cp2 = {
    x: toPoint.x - HORIZONTAL_OFFSET - controlOffset,
    y: toPoint.y
  }
  
  // 如果起点和终点太近，使用简单的直线中点
  if (Math.abs(toPoint.x - fromPoint.x) < HORIZONTAL_OFFSET * 2) {
    return {
      x: (fromPoint.x + toPoint.x) / 2,
      y: (fromPoint.y + toPoint.y) / 2
    }
  }
  
  // 计算贝塞尔曲线中点（t=0.5）
  const t = 0.5
  const mt = 1 - t
  const x = mt * mt * mt * fromPoint.x + 
            3 * mt * mt * t * cp1.x + 
            3 * mt * t * t * cp2.x + 
            t * t * t * toPoint.x
  const y = mt * mt * mt * fromPoint.y + 
            3 * mt * mt * t * cp1.y + 
            3 * mt * t * t * cp2.y + 
            t * t * t * toPoint.y
  
  return { x, y }
})

// 判断是否应该显示删除按钮
// 如果连接线结束端点（后置任务/阶段）是已生成的，则不显示删除按钮
const shouldShowDeleteButton = computed(() => {
  if (!props.connection || !props.connection.to) {
    return false
  }
  
  const toElement = props.connection.to
  let toElementData = null
  
  if (toElement.elementType === 'task' && props.findTaskById) {
    const taskInfo = props.findTaskById(toElement.elementId)
    toElementData = taskInfo?.task
  } else if (toElement.elementType === 'stage' && props.findStageById) {
    toElementData = props.findStageById(toElement.elementId)
  }
  
  // 如果结束端点不可编辑（已生成），则不显示删除按钮
  if (toElementData && toElementData.isEditable === false) {
    return false
  }
  
  return true
})

const handleClick = (event) => {
  event.stopPropagation()
  event.preventDefault()
  emit('select', props.connection.id)
}

const handleDelete = (event) => {
  event.stopPropagation()
  event.preventDefault()
  emit('delete', props.connection.id)
}
</script>

<style scoped>
.connection-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 20000px;
  height: 20000px;
  pointer-events: none; /* 由 hit-area 处理点击 */
  overflow: visible;
  /* 优化 z-index 变化时的渲染性能，减少闪烁 */
  will-change: z-index;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.connection-line--valid {
  stroke: var(--el-text-color-placeholder);
}

.connection-line--invalid {
  stroke: var(--el-color-danger);
}

.connection-line--selected {
  stroke-width: 3;
}

.connection-line--selected.connection-line--valid {
  stroke: var(--el-color-primary);
}

.connection-line--selected.connection-line--invalid {
  stroke: var(--el-color-danger);
}

.connection-line--related.connection-line--valid {
  stroke: var(--el-color-primary);
}

.connection-line--related.connection-line--invalid {
  stroke: var(--el-color-danger);
}

.connection-line-hit-area {
  pointer-events: stroke;
  /* 确保 hit-area 能够接收点击事件 */
  stroke-width: 12 !important; /* 增加点击区域 */
}

.connection-line-visual {
  pointer-events: none;
}

.connection-delete-button-wrapper {
  pointer-events: all;
  overflow: visible;
}

.connection-delete-button {
  width: 24px;
  height: 24px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s, box-shadow 0.2s;
}

.connection-delete-button--animate {
  animation: buttonScaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.connection-delete-button:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.connection-delete-button :deep(.el-icon) {
  font-size: 14px;
}

@keyframes buttonScaleIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  60% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
