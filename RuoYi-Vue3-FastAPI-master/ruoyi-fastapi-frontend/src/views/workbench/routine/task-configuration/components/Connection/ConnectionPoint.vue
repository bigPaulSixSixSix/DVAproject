<template>
  <div 
    class="connection-point"
    :class="[
      `connection-point--${connectionType}`, 
      { 
        'connection-point--active': isActive || isTargetHighlight,
        'connection-point--related': isRelatedToSelectedTask || isRelatedToSelectedConnection,
        'connection-point--disabled': connectionType === 'predecessor' && isEditable === false,
        'connection-point--uneditable': isEditable === false
      }
    ]"
    @mousedown="handleMouseDown"
    @mouseup="handleMouseUp"
  >
    <div class="connection-dot"></div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  elementId: {
    type: [String, Number],
    required: true
  },
  elementType: {
    type: String,
    required: true,
    validator: (value) => ['stage', 'task'].includes(value)
  },
  connectionType: {
    type: String,
    required: true,
    validator: (value) => ['predecessor', 'successor'].includes(value)
  },
  position: {
    type: String,
    required: true,
    validator: (value) => ['left', 'right'].includes(value)
  },
  zoomLevel: {
    type: [Object, Number],
    default: 1
  },
  isTargetHighlight: {
    type: Boolean,
    default: false
  },
  selectedTaskId: {
    type: [Number, String],
    default: null
  },
  selectedConnectionId: {
    type: [Number, String],
    default: null
  },
  connections: {
    type: Array,
    default: () => []
  },
  isEditable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['connection-start', 'connection-panel-end', 'connection-move', 'connection-cancel'])

// 判断连接点是否属于选中的任务
const isRelatedToSelectedTask = computed(() => {
  if (!props.selectedTaskId || props.elementType !== 'task') {
    return false
  }
  return String(props.elementId) === String(props.selectedTaskId)
})

// 判断连接点是否属于选中的连接线
const isRelatedToSelectedConnection = computed(() => {
  if (!props.selectedConnectionId || !props.connections || props.connections.length === 0) {
    return false
  }
  
  // 找到选中的连接线
  const selectedConnection = props.connections.find(
    conn => String(conn.id) === String(props.selectedConnectionId)
  )
  
  if (!selectedConnection || !selectedConnection.from || !selectedConnection.to) {
    return false
  }
  
  const elementIdStr = String(props.elementId)
  const fromIdStr = String(selectedConnection.from.elementId)
  const toIdStr = String(selectedConnection.to.elementId)
  
  // 判断连接点是否属于连接线的起点或终点
  const isFromElement = selectedConnection.from.elementType === props.elementType && 
                        fromIdStr === elementIdStr
  const isToElement = selectedConnection.to.elementType === props.elementType && 
                      toIdStr === elementIdStr
  
  if (!isFromElement && !isToElement) {
    return false
  }
  
  // 判断连接点的位置是否匹配连接线的方向
  // 如果连接点是起点，应该是右侧（successor）连接点
  // 如果连接点是终点，应该是左侧（predecessor）连接点
  if (isFromElement) {
    // 起点：应该是右侧（successor）连接点
    return props.connectionType === 'successor' && props.position === 'right'
  } else if (isToElement) {
    // 终点：应该是左侧（predecessor）连接点
    return props.connectionType === 'predecessor' && props.position === 'left'
  }
  
  return false
})

const isActive = ref(false)
let globalMouseUpHandler = null
let globalMouseMoveHandler = null

const handleMouseDown = (event) => {
  event.stopPropagation()
  
  // 如果元素不可编辑且是前置连接点，禁用交互
  if (props.connectionType === 'predecessor' && props.isEditable === false) {
    return
  }
  
  isActive.value = true
  
  // 获取画布元素
  const canvas = event.target.closest('.workflow-canvas')
  if (!canvas) return
  
  // 添加全局 mouseup 监听，确保无论在哪里松开鼠标都能重置状态
  // 使用 capture 阶段确保在事件传播的早期阶段捕获
  globalMouseUpHandler = (event) => {
    // 检查是否在任务/阶段面板上释放
    const target = event.target
    const clickedPanel = target.closest('.task-card, .stage-card')
    const clickedConnectionPoint = target.closest('.connection-point')
    
    // 如果在连接点上释放，找到该连接点所属的任务/阶段，触发连接结束事件
    if (clickedConnectionPoint) {
      // 找到连接点所属的任务/阶段面板
      const parentPanel = clickedConnectionPoint.closest('.task-card, .stage-card')
      if (parentPanel) {
        const elementType = parentPanel.dataset.elementType
        const taskId = parentPanel.dataset.taskId
        const stageId = parentPanel.dataset.stageId
        
        if (elementType && (taskId || stageId)) {
          emit('connection-panel-end', {
            elementId: taskId || stageId,
            elementType: elementType
          })
        }
      } else {
        // 如果找不到所属面板，触发取消事件
        emit('connection-cancel')
      }
    }
    // 如果在面板上释放（且不在连接点上），触发连接结束事件
    else if (clickedPanel) {
      const elementType = clickedPanel.dataset.elementType
      const taskId = clickedPanel.dataset.taskId
      const stageId = clickedPanel.dataset.stageId
      
      if (elementType && (taskId || stageId)) {
        emit('connection-panel-end', {
          elementId: taskId || stageId,
          elementType: elementType
        })
      }
    }
    // 如果不在面板上，也不在连接点上，触发取消事件
    else {
      emit('connection-cancel')
    }
    
    // 立即重置状态
    isActive.value = false
    // 移除监听器
    if (globalMouseUpHandler) {
      document.removeEventListener('mouseup', globalMouseUpHandler, true)
      globalMouseUpHandler = null
    }
    if (globalMouseMoveHandler) {
      document.removeEventListener('mousemove', globalMouseMoveHandler)
      globalMouseMoveHandler = null
    }
  }
  
  // 添加全局 mousemove 监听，用于实时预览连接线
  globalMouseMoveHandler = (moveEvent) => {
    const canvasRect = canvas.getBoundingClientRect()
    const scrollLeft = canvas.scrollLeft || 0
    const scrollTop = canvas.scrollTop || 0
    
    // 获取缩放级别（和 useDragDrop.js 中的处理方式一致）
    const zoomLevelValue = props.zoomLevel && typeof props.zoomLevel === 'object' && 'value' in props.zoomLevel
      ? props.zoomLevel.value
      : props.zoomLevel || 1
    
    // 计算鼠标在画布坐标系中的位置（考虑缩放，和 useDragDrop.js 中的计算方式一致）
    const x = (moveEvent.clientX - canvasRect.left + scrollLeft) / zoomLevelValue
    const y = (moveEvent.clientY - canvasRect.top + scrollTop) / zoomLevelValue
    
    // 检测鼠标下方的元素（任务或阶段面板）
    // 注意：需要排除连接点本身，避免检测到连接点所属的元素
    // 当鼠标在连接点上时，不应该检测到连接点所属的任务卡片或阶段卡片
    
    // 首先检查鼠标是否在连接点上
    const currentConnectionPoint = moveEvent.target.closest('.connection-point')
    
    let targetElement = null
    if (!currentConnectionPoint) {
      // 如果鼠标不在连接点上，正常检测目标元素
      // 优先检测任务卡片，因为任务卡片在阶段卡片内部
      targetElement = moveEvent.target.closest('.task-card')
      if (!targetElement) {
        // 如果没有找到任务卡片，再检测阶段卡片
        targetElement = moveEvent.target.closest('.stage-card')
      }
    } else {
      // 如果鼠标在连接点上，需要排除连接点所属的元素
      // 找到连接点所属的任务卡片或阶段卡片
      const parentTaskCard = currentConnectionPoint.closest('.task-card')
      const parentStageCard = currentConnectionPoint.closest('.stage-card')
      
      // 使用 document.elementFromPoint 来获取鼠标下方的元素（排除连接点本身）
      // 临时隐藏连接点，以便检测到连接点下方的元素
      const originalPointerEvents = currentConnectionPoint.style.pointerEvents
      currentConnectionPoint.style.pointerEvents = 'none'
      
      const elementUnderMouse = document.elementFromPoint(moveEvent.clientX, moveEvent.clientY)
      
      // 恢复连接点的 pointer-events
      currentConnectionPoint.style.pointerEvents = originalPointerEvents
      
      if (elementUnderMouse) {
        // 从鼠标下方的元素开始，向上查找任务卡片或阶段卡片
        let candidate = elementUnderMouse.closest('.task-card')
        if (!candidate) {
          candidate = elementUnderMouse.closest('.stage-card')
        }
        
        // 如果找到的元素不是连接点所属的元素，则使用它
        if (candidate && candidate !== parentTaskCard && candidate !== parentStageCard) {
          targetElement = candidate
        }
      }
    }
    
    let targetInfo = null
    
    if (targetElement) {
      // 通过 data 属性获取元素ID和类型
      const elementType = targetElement.dataset.elementType
      const taskId = targetElement.dataset.taskId
      const stageId = targetElement.dataset.stageId
      
      if (elementType && (taskId || stageId)) {
        targetInfo = {
          elementType: elementType,
          elementId: taskId || stageId
        }
      }
    }
    
    emit('connection-move', { 
      x, 
      y,
      targetElement: targetInfo
    })
  }
  
  // 使用 capture 阶段（true）确保在事件冒泡之前捕获
  document.addEventListener('mouseup', globalMouseUpHandler, true)
  document.addEventListener('mousemove', globalMouseMoveHandler)
  
  emit('connection-start', {
    elementId: props.elementId,
    elementType: props.elementType,
    connectionType: props.connectionType,
    position: props.position
  })
}

const handleMouseUp = (event) => {
  event.stopPropagation()
  // 连接点不再作为结束点，所以这里只阻止事件冒泡
  // 实际的连接结束由 globalMouseUpHandler 处理
}

// 组件卸载时清理监听器
onUnmounted(() => {
  if (globalMouseUpHandler) {
    document.removeEventListener('mouseup', globalMouseUpHandler, true)
    globalMouseUpHandler = null
  }
  if (globalMouseMoveHandler) {
    document.removeEventListener('mousemove', globalMouseMoveHandler)
    globalMouseMoveHandler = null
  }
})
</script>

<style scoped>
.connection-point {
  position: absolute;
  width: 12px;
  height: 12px;
  z-index: 15; /* 高于调整大小手柄的 z-index: 10，确保连接点优先响应 */
  cursor: pointer;
}

.connection-point--disabled {
  cursor: not-allowed;
  pointer-events: none;
}

/* 已生成任务的连接点：灰色描边（与任务面板底色一致） */
.connection-point--uneditable .connection-dot {
  border-color: var(--el-bg-color-page);
}

.connection-point--predecessor {
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
}

.connection-point--successor {
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
}

.connection-dot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: var(--el-text-color-placeholder);
  border: 2px solid var(--el-bg-color);
  box-shadow: var(--el-box-shadow-base);
  transition: all 0.2s ease;
}

.connection-point:hover .connection-dot {
  background-color: var(--el-color-primary);
  transform: scale(1.2);
}

.connection-point--active .connection-dot {
  background-color: var(--el-color-primary);
  transform: scale(1.3);
}

.connection-point--related .connection-dot {
  background-color: var(--el-color-primary);
  transform: scale(1.2);
}
</style>
