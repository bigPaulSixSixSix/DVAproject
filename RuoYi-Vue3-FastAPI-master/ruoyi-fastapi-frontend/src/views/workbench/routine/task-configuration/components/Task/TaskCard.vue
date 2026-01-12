<template>
  <div 
    class="task-card"
    :class="{
      'task-card--invalid': hasMissingRequiredFields,
      'task-card--time-issue': hasTimeIssue && !hasMissingRequiredFields,
      'task-card--selected': isSelected,
      'task-card--connecting-source': isConnectingSource,
      'task-card--connecting-target': isConnectingTarget,
      'task-card--dragging': task._isPreview || task._isDragging || task._stageResizing,
      'task-card--disabled': !task.isEditable
    }"
    :data-task-id="task.id"
    :data-element-type="'task'"
    :style="taskCardStyle"
    @click="handleClick"
    @mousedown="handleMouseDown"
  >
    <!-- 已生成标识 -->
    <el-tag 
      v-if="!task.isEditable" 
      type="info" 
      size="small"
      class="task-generated-tag"
    >
      已生成
    </el-tag>
    
    <!-- 时间异常感叹号图标 -->
    <div v-if="hasTimeIssue && !hasMissingRequiredFields" class="task-time-issue-icon">
      <el-icon :size="12" color="#ffffff">
        <Warning />
      </el-icon>
    </div>
    
    <!-- 任务内容 -->
    <div class="task-content">
      <div class="task-title">
        <span class="task-id">{{ task.id }}</span> {{ task.name }}
      </div>
      <div class="task-info">
        <div class="task-time">{{ formatTime(task.startTime) }} - {{ formatTime(task.endTime) }}</div>
        <div class="task-duration">共{{ task.duration }}天</div>
        <div class="task-assignee">{{ getAssigneeDisplayName(task.jobNumber || task.assignee) }}</div>
      </div>
    </div>
    
    <!-- 连接点（只在阶段内任务显示） -->
    <ConnectionPoint 
      v-if="isValidPosition"
      :element-id="task.id"
      element-type="task"
      connection-type="predecessor"
      position="left"
      :zoom-level="zoomLevel"
      :is-target-highlight="isConnectingTarget && connectingSourcePosition === 'right'"
      :selected-task-id="selectedTaskId"
      :selected-connection-id="selectedConnectionId"
      :connections="connections"
      :is-editable="task.isEditable"
      @connection-start="handleConnectionStart"
      @connection-panel-end="handleConnectionPanelEnd"
      @connection-move="handleConnectionMove"
      @connection-cancel="handleConnectionCancel"
    />
    <ConnectionPoint 
      v-if="isValidPosition"
      :element-id="task.id"
      element-type="task"
      connection-type="successor"
      position="right"
      :zoom-level="zoomLevel"
      :is-target-highlight="isConnectingTarget && connectingSourcePosition === 'left'"
      :selected-task-id="selectedTaskId"
      :selected-connection-id="selectedConnectionId"
      :connections="connections"
      :is-editable="task.isEditable"
      @connection-start="handleConnectionStart"
      @connection-panel-end="handleConnectionPanelEnd"
      @connection-move="handleConnectionMove"
      @connection-cancel="handleConnectionCancel"
    />
    
    <!-- 操作按钮 teleport 到独立图层 -->
    <Teleport v-if="isSelected" to="#task-action-layer">
      <div class="task-actions" :style="taskActionStyle">
        <!-- 已生成任务：显示查看图标（三个点） -->
        <el-button 
          v-if="!task.isEditable"
          size="small" 
          class="task-action-btn task-action-btn--view"
          @click.stop="handleEdit"
        >
          <el-icon><MoreFilled /></el-icon>
        </el-button>
        <!-- 未生成任务：显示编辑和删除图标 -->
        <template v-else>
          <el-button 
            size="small" 
            class="task-action-btn task-action-btn--edit"
            @click.stop="handleEdit"
          >
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button 
            size="small" 
            class="task-action-btn task-action-btn--delete"
            @click.stop="handleDelete"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElButton, ElIcon, ElMessage } from 'element-plus'
import { Edit, Delete, Warning, MoreFilled } from '@element-plus/icons-vue'
import ConnectionPoint from '../Connection/ConnectionPoint.vue'
import { useDragDrop } from '../../composables/canvas/useDragDrop'

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  stagePosition: {
    type: Object,
    default: null
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  selectedTaskId: {
    type: [String, Number],
    default: null
  },
  selectedConnectionId: {
    type: [String, Number],
    default: null
  },
  connections: {
    type: Array,
    default: () => []
  },
  isValidPosition: {
    type: Boolean,
    default: true
  },
  stages: {
    type: Array,
    default: () => []
  },
  zoomLevel: {
    type: [Object, Number], // 接受 ref 对象或直接的数字值
    required: true
  },
  isConnectingSource: {
    type: Boolean,
    default: false
  },
  isConnectingTarget: {
    type: Boolean,
    default: false
  },
  connectingSourcePosition: {
    type: String,
    default: null
  },
  onDragEndDirect: {
    type: Function,
    default: null
  },
  getUserDisplayName: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['select', 'edit', 'delete', 'drag-end', 'connection-start', 'connection-panel-end', 'connection-move', 'connection-cancel'])

const { handleTaskDrag } = useDragDrop()

// 跟踪拖拽状态，防止拖拽后触发选中
const isDragging = ref(false)
const dragStartPosition = ref(null)

const taskZIndex = computed(() => {
  // 拖拽或预览状态下，使用最高层级，确保始终位于阶段卡片之上
  if (props.task?._isPreview || props.task?._isDragging) {
    return 1100
  }
  // 选中状态保持现有最高层级
  if (props.isSelected) {
    return 1000
  }
  // 阶段外任务（isValidPosition === false）需要高于阶段卡片，避免被遮挡
  if (!props.isValidPosition) {
    return 300
  }
  // 阶段内任务保持较低层级，由阶段卡片的 stacking context 管理
  return 10
})

const HEADER_HEIGHT = 60
const TASK_WIDTH = 196
const TASK_HEIGHT = 100
const ACTION_GAP = 4
const ACTION_CONTAINER_HEIGHT = 32
const ACTION_TOTAL_WIDTH = 68 // two buttons (32 each) + 4px gap

const taskAbsolutePosition = computed(() => {
  if (props.stagePosition) {
    return {
      x: props.stagePosition.x + props.task.position.x,
      y: props.stagePosition.y + HEADER_HEIGHT + props.task.position.y
    }
  }
  return {
    x: props.task.position.x,
    y: props.task.position.y
  }
})

const taskCardStyle = computed(() => ({
  left: `${props.task.position.x}px`,
  top: `${props.task.position.y}px`,
  zIndex: taskZIndex.value
}))

const taskActionStyle = computed(() => {
  if (!props.isSelected) return {}
  const absPos = taskAbsolutePosition.value
  // 如果任务不可编辑，只有一个按钮，宽度为32px；否则为68px（两个按钮+间距）
  const actionWidth = props.task.isEditable ? ACTION_TOTAL_WIDTH : 32
  const left = absPos.x + TASK_WIDTH - actionWidth
  const top = absPos.y + TASK_HEIGHT + ACTION_GAP
  return {
    left: `${left}px`,
    top: `${top}px`
  }
})

/**
 * 检查任务是否缺少必要字段（用于阶段内任务的标红）
 */
const hasMissingRequiredFields = computed(() => {
  if (!props.isValidPosition) {
    // 阶段外任务：沿用之前的逻辑
    return true
  }
  const task = props.task
  // 检查关键字段是否为null或空
  // 检查审批节点是否配置：approvalNodes 应该是数组，如果为空数组或不存在，则认为未配置
  const hasApprovalNodes = task.approvalNodes && Array.isArray(task.approvalNodes) && task.approvalNodes.length > 0
  return !task.startTime || !task.endTime || (!task.jobNumber && !task.assignee) || !hasApprovalNodes // 兼容旧数据
})

/**
 * 检查任务是否有时间问题（用于黄色标注）
 */
const hasTimeIssue = computed(() => {
  // 如果信息不完全（红色），不显示黄色标注
  if (hasMissingRequiredFields.value) {
    return false
  }
  // 从任务对象上读取时间问题标记
  return Boolean(props.task?.hasTimeIssue)
})

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`
}

const getAssigneeDisplayName = (assignee) => {
  if (!assignee) return ''
  // 如果传入了 getUserDisplayName 函数，使用它来获取显示名称
  if (props.getUserDisplayName) {
    return props.getUserDisplayName(assignee)
  }
  // 否则直接返回 assignee（兼容旧数据）
  return String(assignee)
}

const handleClick = (event) => {
  event.stopPropagation()
  // 如果正在拖拽或刚刚完成拖拽，不触发选中
  if (isDragging.value || props.task._isDragging) {
    return
  }
  emit('select', props.task.id)
}

const handleEdit = () => {
  emit('edit', props.task)
}

const handleDelete = () => {
  emit('delete', props.task.id)
}

const handleConnectionStart = (data) => {
  emit('connection-start', data)
}

const handleConnectionPanelEnd = (data) => {
  emit('connection-panel-end', data)
}

const handleConnectionMove = (data) => {
  emit('connection-move', data)
}

const handleConnectionCancel = () => {
  emit('connection-cancel')
}

// 拖拽功能 - 使用闭包捕获最新的props
const createDragHandler = () => {
  // 安全访问 zoomLevel（可能是 ref 对象或直接的数字）
  const zoomLevelValue = props.zoomLevel && typeof props.zoomLevel === 'object' && 'value' in props.zoomLevel
    ? props.zoomLevel
    : { value: props.zoomLevel }
  
  return handleTaskDrag(
    props.task,
    props.stages,
    zoomLevelValue,
    (taskId, newPosition, isValid, isFinal, targetStage) => {
      const dragData = { taskId, newPosition, isValid, isFinal, targetStage }
      // 如果提供了直接回调函数，优先使用它（用于绕过事件传递问题）
      if (props.onDragEndDirect) {
        props.onDragEndDirect(dragData)
      } else {
        // 如果没有直接回调，使用事件传递
        emit('drag-end', dragData)
      }
    }
  )
}

const handleMouseDown = (event) => {
  // 阻止默认行为和冒泡
  event.preventDefault()
  event.stopPropagation()
  
  // 记录拖拽起始位置
  isDragging.value = false
  dragStartPosition.value = { x: event.clientX, y: event.clientY }
  
  // 在开始拖拽前，如果存在未完成的连接操作，主动取消，避免阶段被高亮
  emit('connection-cancel')

  // 每次都创建新的拖拽处理函数（因为props可能会变化）
  const { handleMouseDown: startDrag } = createDragHandler()
  
  // 监听鼠标移动，判断是否发生拖拽
  const handleMouseMove = (moveEvent) => {
    if (dragStartPosition.value) {
      const deltaX = Math.abs(moveEvent.clientX - dragStartPosition.value.x)
      const deltaY = Math.abs(moveEvent.clientY - dragStartPosition.value.y)
      // 如果移动距离超过5px，认为是拖拽
      if (deltaX > 5 || deltaY > 5) {
        isDragging.value = true
      }
    }
  }
  
  const handleMouseUp = () => {
    // 延迟清除拖拽状态，确保点击事件不会触发选中
    setTimeout(() => {
      isDragging.value = false
      dragStartPosition.value = null
    }, 0)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  
  startDrag(event)
}

// 暴露拖拽方法给父组件（兼容性保留）
defineExpose({
  handleMouseDown
})
</script>

<style scoped>
.task-card {
  position: absolute;
  width: 196px; /* 调整为 198px，使得偏置(2px) + 宽度(198px) = 200px = 8的倍数，右边界对齐网格 */
  height: 100px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  transition: all 0.2s ease;
  /* z-index 通过内联样式动态设置（选中时为1000，未选中时为5） */
  user-select: none;
  -webkit-user-select: none;
}

.task-card--dragging {
  transition: none !important;
}

.task-card:hover {
  box-shadow: var(--el-box-shadow-light);
}

.task-card--invalid {
  border: 2px solid var(--el-color-danger) !important;
  background-color: var(--el-color-danger-light-9);
}

.task-card--time-issue {
  border: 2px solid var(--el-color-warning) !important;
  background-color: var(--el-color-warning-light-9);
}

.task-card--selected {
  border: 2px solid var(--el-color-primary) !important;
}

.task-card--connecting-source {
  border: 2px solid var(--el-color-primary) !important;
}

.task-card--connecting-target {
  border: 2px solid var(--el-color-primary) !important;
}

.task-content {
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.task-id {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.task-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  display: flex;
  flex-direction: row;
  gap: 4px;
}

.task-time {
  color: var(--el-text-color-secondary);
}

.task-duration {
  color: var(--el-text-color-secondary);
}

.task-assignee {
  color: var(--el-text-color-secondary);
}

.task-generated-tag {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 10;
}

.task-card--disabled {
  background-color: var(--el-bg-color-page);
  border-color: var(--el-border-color);
  cursor: not-allowed;
  color: var(--el-text-color-secondary);
}

.task-time-issue-icon {
  position: absolute;
  top: -2px;
  left: -2px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  pointer-events: none;
  background-color: var(--el-color-warning);
  border-radius: 4px 0 4px 0;
}

.task-actions {
  position: absolute;
  display: flex;
  gap: 4px;
  pointer-events: none;
}

.task-action-btn {
  width: 32px;
  height: 32px;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color);
  border: none;
  border-radius: 4px;
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.2s ease;
  pointer-events: auto;
}

.task-action-btn:hover {
  box-shadow: var(--el-box-shadow);
}

.task-action-btn--edit {
  color: var(--el-color-primary);
}

.task-action-btn--edit:hover {
  background: var(--el-color-primary-light-9);
}

.task-action-btn--delete {
  color: var(--el-color-danger);
}

.task-action-btn--delete:hover {
  background: var(--el-color-danger-light-9);
}

.task-action-btn--view {
  color: var(--el-text-color-regular);
}

.task-action-btn--view:hover {
  background: var(--el-fill-color-light);
}
</style>
