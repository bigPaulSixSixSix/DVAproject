<template>
  <div 
    class="stage-card"
    :class="{
      'stage-card--selected': isSelected,
      'stage-card--connecting-source': isConnectingSource,
      'stage-card--connecting-target': isConnectingTarget,
      'stage-card--overlapping': isOverlappingStage,
      'stage-card--dragging': stage._isResizing || stage._isDragging,
      'stage-card--time-issue': hasTimeIssue,
      'stage-card--disabled': !stage.isEditable
    }"
    :data-stage-id="stage.id"
    :data-element-type="'stage'"
    :style="stageCardStyle"
    @click="handleClick"
  >
    <!-- 时间异常感叹号图标 -->
    <div v-if="hasTimeIssue" class="stage-time-issue-icon">
      <el-icon :size="12" color="#ffffff">
        <Warning />
      </el-icon>
    </div>
    
    <!-- 阶段标题 -->
    <div class="stage-header" @mousedown="handleDragStart" @click.stop="handleHeaderClick">
      <div class="stage-title">
        <span class="stage-id">{{ stage?.id }}</span> {{ stage?.name || '未命名' }} {{ stageTimeDisplay }}
        <el-tag 
          v-if="!stage.isEditable" 
          type="info" 
          size="small"
          class="stage-generated-tag"
        >
          已生成
        </el-tag>
      </div>
      <div class="stage-actions" v-if="isSelected">
        <!-- 已生成阶段：显示查看图标（三个点） -->
        <el-button 
          v-if="!stage.isEditable"
          size="small" 
          class="stage-action-btn stage-action-btn--view"
          @click.stop="handleEdit"
        >
          <el-icon><MoreFilled /></el-icon>
        </el-button>
        <!-- 未生成阶段：显示编辑和删除图标 -->
        <template v-else>
          <el-button 
            size="small" 
            class="stage-action-btn stage-action-btn--edit"
            @click.stop="handleEdit"
          >
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button 
            size="small" 
            class="stage-action-btn stage-action-btn--delete"
            @click.stop="handleDelete"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </div>
    </div>
    
    <!-- 阶段内容区域 -->
    <div class="stage-content">
        <TaskCard
          v-for="task in getVisibleTasks"
          :key="task.id"
          :task="getTaskWithRelativePosition(task)"
          :is-selected="selectedTaskId === task.id"
          :selected-task-id="selectedTaskId"
          :selected-connection-id="selectedConnectionId"
          :connections="connections"
          :is-valid-position="isTaskValidPosition(task)"
          :stages="allStages"
          :zoom-level="zoomLevel"
      :stage-position="stage.position"
          :is-connecting-source="connectingSourceId === task.id && connectingSourceType === 'task'"
          :is-connecting-target="connectingTargetId === task.id && connectingTargetType === 'task'"
          :connecting-source-position="connectingSourcePosition"
          :get-user-display-name="getUserDisplayName"
          @select="handleTaskSelect"
          @edit="handleTaskEdit"
          @delete="handleTaskDelete"
          :on-drag-end-direct="onDragEndDirect"
          @connection-start="handleConnectionStart"
          @connection-panel-end="handleConnectionPanelEnd"
          @connection-move="handleConnectionMove"
          @connection-cancel="handleConnectionCancel"
        />
    </div>
    
    <!-- 调整大小手柄 - 8个方向 -->
    <div 
      class="resize-handle resize-handle--n"
      @mousedown="(e) => handleResizeStart(e, 'n')"
    ></div>
    <div 
      class="resize-handle resize-handle--s"
      @mousedown="(e) => handleResizeStart(e, 's')"
    ></div>
    <div 
      class="resize-handle resize-handle--e"
      @mousedown="(e) => handleResizeStart(e, 'e')"
    ></div>
    <div 
      class="resize-handle resize-handle--w"
      @mousedown="(e) => handleResizeStart(e, 'w')"
    ></div>
    <div 
      class="resize-handle resize-handle--ne"
      @mousedown="(e) => handleResizeStart(e, 'ne')"
    ></div>
    <div 
      class="resize-handle resize-handle--nw"
      @mousedown="(e) => handleResizeStart(e, 'nw')"
    ></div>
    <div 
      class="resize-handle resize-handle--se"
      @mousedown="(e) => handleResizeStart(e, 'se')"
    ></div>
    <div 
      class="resize-handle resize-handle--sw"
      @mousedown="(e) => handleResizeStart(e, 'sw')"
    ></div>
    
    <!-- 连接点（放在调整大小手柄之后，确保事件优先响应） -->
    <ConnectionPoint 
      :element-id="stage.id"
      element-type="stage"
      connection-type="predecessor"
      position="left"
      :zoom-level="zoomLevel"
      :is-target-highlight="isConnectingTarget && connectingSourcePosition === 'right'"
      :selected-connection-id="selectedConnectionId"
      :connections="connections"
      :is-editable="stage.isEditable"
      @connection-start="handleConnectionStart"
      @connection-panel-end="handleConnectionPanelEnd"
      @connection-move="handleConnectionMove"
      @connection-cancel="handleConnectionCancel"
    />
    <ConnectionPoint 
      :element-id="stage.id"
      element-type="stage"
      connection-type="successor"
      position="right"
      :zoom-level="zoomLevel"
      :is-target-highlight="isConnectingTarget && connectingSourcePosition === 'left'"
      :selected-connection-id="selectedConnectionId"
      :connections="connections"
      :is-editable="stage.isEditable"
      @connection-start="handleConnectionStart"
      @connection-panel-end="handleConnectionPanelEnd"
      @connection-move="handleConnectionMove"
      @connection-cancel="handleConnectionCancel"
    />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElButton, ElIcon } from 'element-plus'
import { Edit, Delete, Warning, MoreFilled } from '@element-plus/icons-vue'
import ConnectionPoint from '../Connection/ConnectionPoint.vue'
import TaskCard from '../Task/TaskCard.vue'
import { useDragDrop } from '../../composables/canvas/useDragDrop'
import { useStageTime } from '../../composables/stage/useStageTime'

const props = defineProps({
  stage: {
    type: Object,
    required: true
  },
  allStages: {
    type: Array,
    default: () => []
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
  connectingSourceId: {
    type: [String, Number],
    default: null
  },
  connectingSourceType: {
    type: String,
    default: null
  },
  connectingTargetId: {
    type: [String, Number],
    default: null
  },
  connectingTargetType: {
    type: String,
    default: null
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
  },
  isOverlappingStage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'select', 
  'edit', 
  'delete', 
  'resize-end',
  'position-change',
  'task-select',
  'task-edit', 
  'task-delete',
  'connection-start', 
  'connection-panel-end',
  'connection-move',
  'connection-cancel'
])

const { handleStageResize, handleStageDrag } = useDragDrop()
const { calculateStageTimeRange } = useStageTime()

// 跟踪拖拽状态，防止拖拽后触发选中
const isDragging = ref(false)
const dragStartPosition = ref(null)

// 计算阶段时间显示
const stageTimeDisplay = computed(() => {
  const timeRange = calculateStageTimeRange(props.stage)
  return timeRange.displayText
})

// 判断是否有时间异常（从 stage 对象中读取）
const hasTimeIssue = computed(() => {
  return Boolean(props.stage?.hasTimeIssue)
})

// 过滤掉正在拖拽到阶段外的任务（标记为 _isDraggingOut 的任务不应该在阶段内显示）
const getVisibleTasks = computed(() => {
  if (!props.stage.tasks || !Array.isArray(props.stage.tasks)) {
    return []
  }
  return props.stage.tasks.filter(task => !task._isDraggingOut)
})

const stageCardStyle = computed(() => {
    const pos = props.stage?.position || { x: 0, y: 0, width: 300, height: 200 }
    
  // 仅在拖拽或调整大小时提升阶段层级，平时不设置 z-index，避免子元素被限制在同一 stacking context 中
  let zIndex = null
  if (props.stage._isDragging || props.stage._isResizing) {
    zIndex = 1200
  }
    
  return {
      left: `${pos.x}px`,
      top: `${pos.y}px`,
      width: `${pos.width}px`,
      height: `${pos.height}px`,
    ...(zIndex != null ? { zIndex } : {})
    }
})

const isTaskValidPosition = (task) => {
  // 检查任务是否有效
  if (!task || !task.position || !props.stage.position) {
    return false
  }
  
  // task.position 是绝对坐标（画布坐标），需要先转换为相对坐标
  // 使用与 getTaskWithRelativePosition 和 constrainTaskToStage 相同的逻辑
  const HEADER_HEIGHT = 60 // 阶段头部高度
  const stagePos = props.stage?.position || { x: 0, y: 0 }
  
  // 将绝对坐标转换为相对坐标
  // x 相对于阶段左外边界，y 相对于 stage-content 顶部（需要减去 HEADER_HEIGHT）
  const relativeX = task.position.x - stagePos.x
  const relativeY = task.position.y - stagePos.y - HEADER_HEIGHT
  
  // 使用与 constrainTaskToStage 相同的边界定义
  const TASK_WIDTH = 196 // 任务卡片固定宽度（与 constrainTaskToStage 保持一致）
  const TASK_HEIGHT = 100 // 任务卡片固定高度
  const BORDER_WIDTH = 4 // stage-card 的边框宽度（与 constrainTaskToStage 保持一致）
  
  // 任务边界（相对坐标）
  const taskLeft = relativeX
  const taskTop = relativeY
  const taskRight = relativeX + TASK_WIDTH
  const taskBottom = relativeY + TASK_HEIGHT
  
  // 阶段内容区边界（相对坐标，与 constrainTaskToStage 保持一致）
  // 左边界：0（任务可以紧贴左外边界）
  // 上边界：0（stage-content 顶部）
  // 右边界：stageWidth - BORDER_WIDTH（减去右边框）
  // 下边界：stageHeight - HEADER_HEIGHT - BORDER_WIDTH（总高度 - 头部 - 下边框）
  const stageWidth = props.stage.position.width
  const stageHeight = props.stage.position.height
  const contentLeft = 0
  const contentTop = 0
  const contentRight = stageWidth - BORDER_WIDTH
  const contentBottom = stageHeight - HEADER_HEIGHT - BORDER_WIDTH
  
  // 检查任务是否完全在内容区内
  return taskLeft >= contentLeft &&
         taskTop >= contentTop &&
         taskRight <= contentRight &&
         taskBottom <= contentBottom
}

// 将任务的绝对坐标转换为相对于阶段的坐标
const getTaskWithRelativePosition = (task) => {
  if (!task || !task.position) return task
  
  const stagePos = props.stage?.position || { x: 0, y: 0 }
  
  const HEADER_HEIGHT = 60
  return {
    ...task,
    position: {
      x: task.position.x - stagePos.x,
      y: task.position.y - stagePos.y - HEADER_HEIGHT
    }
  }
}

const handleClick = () => {
  // 如果正在拖拽或刚刚完成拖拽，不触发选中
  if (isDragging.value || props.stage._isDragging || props.stage._isResizing) {
    return
  }
  emit('select', props.stage.id)
}

const handleHeaderClick = () => {
  // 如果正在拖拽或刚刚完成拖拽，不触发选中
  if (isDragging.value || props.stage._isDragging || props.stage._isResizing) {
    return
  }
  emit('select', props.stage.id)
}

const handleDragStart = (event) => {
  event.stopPropagation()
  
  // 如果点击的是按钮，不拖拽
  if (event.target.closest('.stage-actions')) {
    return
  }
  
  // 记录拖拽起始位置
  isDragging.value = false
  dragStartPosition.value = { x: event.clientX, y: event.clientY }
  
  // 安全访问 zoomLevel（可能是 ref 对象或直接的数字）
  const zoomLevelValue = props.zoomLevel && typeof props.zoomLevel === 'object' && 'value' in props.zoomLevel
    ? props.zoomLevel
    : { value: props.zoomLevel }
  
  // 使用封装的阶段拖拽方法（在每次拖拽时创建，避免重复调用）
  const { handleMouseDown } = handleStageDrag(
    props.stage,
    zoomLevelValue,
    (stageId, newPosition) => {
      emit('position-change', { stageId, newPosition })
    }
  )
  
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
  
  handleMouseDown(event)
}

const handleEdit = () => {
  emit('edit', props.stage)
}

const handleDelete = () => {
  emit('delete', props.stage.id)
}

const handleResizeStart = (event, direction) => {
  event.stopPropagation()
  
  // 记录拖拽起始位置
  isDragging.value = false
  dragStartPosition.value = { x: event.clientX, y: event.clientY }
  
  // 安全访问 zoomLevel（可能是 ref 对象或直接的数字）
  const zoomLevelValue = props.zoomLevel && typeof props.zoomLevel === 'object' && 'value' in props.zoomLevel
    ? props.zoomLevel
    : { value: props.zoomLevel }
  
  // 使用封装的阶段调整大小方法（在每次调整时创建）
  const { handleMouseDown } = handleStageResize(
    props.stage,
    zoomLevelValue,
    direction,
    (stageId, newSize, newPosition) => {
      emit('resize-end', { stageId, newSize, newPosition })
    }
  )
  
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
  
  handleMouseDown(event)
}

const handleTaskSelect = (taskId) => {
  emit('task-select', taskId)
}

const handleTaskEdit = (task) => {
  emit('task-edit', task)
}

const handleTaskDelete = (taskId) => {
  emit('task-delete', taskId)
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
</script>

<style scoped>
.stage-card {
  position: absolute;
  background: var(--el-fill-color-lighter);
  border: 2px solid var(--el-border-color-light);
  border-radius: 4px;
  /* 只对 border 和 box-shadow 应用 transition，不包括 z-index */
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  /* z-index 通过内联样式动态设置，不使用 transition */
  user-select: none;
  -webkit-user-select: none;
  /* 优化 z-index 变化时的渲染性能 */
  will-change: z-index;
}

.stage-card--dragging {
  transition: none !important;
}

.stage-card:hover {
  box-shadow: var(--el-box-shadow-light);
}

.stage-card--selected {
  border: 2px solid var(--el-color-primary) !important;
}

.stage-card--connecting-source {
  border: 2px solid var(--el-color-primary) !important;
}

.stage-card--connecting-target {
  border: 2px solid var(--el-color-primary) !important;
}

.stage-card--overlapping {
  border: 2px solid var(--el-color-danger) !important;
  background-color: var(--el-color-danger-light-9) !important;
}

.stage-card--time-issue {
  /* 时间异常只覆盖描边，不覆盖背景色 */
  border: 2px solid var(--el-color-warning) !important;
}

/* 已生成阶段的样式优先级应该高于时间异常的背景色 */
.stage-card--disabled {
  background-color: var(--el-bg-color-page) !important;
  border-color: var(--el-border-color-light);
  color: var(--el-text-color-secondary);
}

/* 已生成阶段 + 时间异常：保留灰色背景，但边框和角标显示时间异常 */
.stage-card--disabled.stage-card--time-issue {
  background-color: var(--el-bg-color-page) !important;
  border-color: var(--el-color-warning) !important;
  color: var(--el-text-color-secondary);
}

/* 已生成阶段的标题栏背景色 */
.stage-card--disabled .stage-header {
  background-color: var(--el-bg-color-page);
}

.stage-generated-tag {
  margin-left: 8px;
}

.stage-time-issue-icon {
  position: absolute;
  top: -2px;
  left: -2px;
  width: 16px;
  height: 16px;
  background-color: var(--el-color-warning);
  border-radius: 4px 0 4px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.stage-header {
  height: 60px;
  padding: 0 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--el-bg-color);
  border-radius: 4px 4px 0 0;
  user-select: none;
  -webkit-user-select: none;
  box-sizing: border-box;
}

.stage-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stage-id {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.stage-actions {
  display: flex;
  gap: 4px;
  /* 按钮的 z-index 应该高于阶段卡片，确保按钮在最上层 */
  position: relative;
  z-index: 1001;
}

.stage-action-btn {
  width: 32px;
  height: 32px;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.stage-action-btn--edit {
  background: var(--el-color-primary);
  color: #ffffff;
}

.stage-action-btn--edit:hover {
  background: var(--el-color-primary-dark-2);
}

.stage-action-btn--delete {
  background: var(--el-color-danger);
  color: #ffffff;
}

.stage-action-btn--delete:hover {
  background: var(--el-color-danger-dark-2);
}

.stage-content {
  position: relative;
  height: calc(100% - 60px);
  overflow: visible;
}

.resize-handle {
  position: absolute;
  background: transparent;
  z-index: 10;
}

.resize-handle:hover {
  background: transparent;
}

/* 边上的手柄 */
.resize-handle--n {
  top: -4px;
  left: 0;
  right: 0;
  height: 8px;
  cursor: n-resize;
}

.resize-handle--s {
  bottom: -4px;
  left: 0;
  right: 0;
  height: 8px;
  cursor: s-resize;
}

.resize-handle--e {
  top: 0;
  bottom: 0;
  right: -4px;
  width: 8px;
  cursor: e-resize;
}

.resize-handle--w {
  top: 0;
  bottom: 0;
  left: -4px;
  width: 8px;
  cursor: w-resize;
}

/* 角落的手柄 */
.resize-handle--ne {
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 0 10px 0 0;
  cursor: ne-resize;
}

.resize-handle--nw {
  top: -4px;
  left: -4px;
  width: 16px;
  height: 16px;
  border-radius: 10px 0 0 0;
  cursor: nw-resize;
}

.resize-handle--se {
  bottom: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 0 0 10px 0;
  cursor: se-resize;
}

.resize-handle--sw {
  bottom: -4px;
  left: -4px;
  width: 16px;
  height: 16px;
  border-radius: 0 0 0 10px;
  cursor: sw-resize;
}
</style>
