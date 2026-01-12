<template>
  <div class="workflow-canvas-container">
    <!-- 工具栏 -->
<div class="workflow-toolbar">
      <div class="toolbar-left">
        <h2 class="toolbar-title">{{ projectName || '项目' }}任务配置</h2>
      </div>
      <div class="toolbar-center">
        <el-tooltip content="新建任务" placement="top">
          <el-button 
            class="toolbar-icon-button drag-to-add-button"
            @mousedown.prevent="handleTaskButtonMouseDown"
          >
            <i class="icon-add_task"></i>
          </el-button>
        </el-tooltip>
        <el-tooltip content="新建阶段" placement="top">
          <el-button 
            class="toolbar-icon-button drag-to-add-button"
            @mousedown.prevent="handleStageButtonMouseDown"
          >
            <i class="icon-add_stage"></i>
          </el-button>
        </el-tooltip>
        <div class="toolbar-divider"></div>
        <el-tooltip content="整理布局" placement="top">
          <el-button 
            class="toolbar-icon-button"
            @click="handleOrganizeLayout"
          >
            <i class="icon-layout"></i>
          </el-button>
        </el-tooltip>
        <div class="toolbar-divider"></div>
        <el-tooltip content="撤销" placement="top">
          <el-button 
            class="toolbar-icon-button"
            @click="handleUndo"
          >
            <i class="icon-back"></i>
          </el-button>
        </el-tooltip>
        <div class="toolbar-divider"></div>
        <el-tooltip content="保存任务" placement="top">
          <el-button 
            class="toolbar-icon-button"
            @click="handleSave"
          >
            <i class="icon-save"></i>
          </el-button>
        </el-tooltip>
        <el-tooltip content="保存任务并生成" placement="top">
          <el-button 
            class="toolbar-icon-button"
            @click="handleSaveAndGenerate"
          >
            <i class="icon-save_generate"></i>
          </el-button>
        </el-tooltip>
      </div>
      <div class="toolbar-right">
        <div class="toolbar-right-group">
          <div class="abnormal-task-button-wrapper">
            <el-button
              :type="totalAbnormalCount === 0 ? 'success' : totalAbnormalType"
              plain
              @click="totalAbnormalCount > 0 ? handleAbnormalButtonClick() : null"
              :class="['abnormal-task-button', { 'abnormal-task-button--no-hover': totalAbnormalCount === 0 }]"
            >
              <span class="abnormal-task-text">{{ totalAbnormalCount === 0 ? '无异常' : totalAbnormalCount }}</span>
            </el-button>
            <el-icon v-if="totalAbnormalCount > 0" class="abnormal-task-badge">
              <WarningFilled />
            </el-icon>
          </div>
          <el-button
            plain
            @click="helpDialogVisible = true"
            class="help-button"
          >
            帮助
          </el-button>
        </div>
        <div class="toolbar-divider"></div>
        <el-dropdown
          trigger="click"
          @command="handleZoomCommand"
          class="zoom-dropdown"
        >
          <el-button plain class="zoom-button">
            {{ zoomPercentage }}%
            <el-icon class="zoom-dropdown-icon"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="reset">重置缩放</el-dropdown-item>
              <el-dropdown-item
                v-for="option in zoomOptions"
                :key="option.label"
                :command="option.command"
                :disabled="option.disabled"
              >
                {{ option.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 画布 -->
    <div 
      ref="canvasRef"
      class="workflow-canvas"
      :class="{ 
        'canvas-dragging': isCanvasDragging,
        'canvas-dragging-to-add': isDraggingToAdd
      }"
      @wheel="handleWheelEvent"
      @click="handleCanvasClick"
      @mousemove="handleCanvasMouseMove"
      @mouseup="handleCanvasMouseUp"
      @mouseleave="handleCanvasMouseLeave"
    >
      <!-- 画布内容容器 -->
      <div 
        class="canvas-wrapper"
        :style="canvasWrapperStyle"
      >
        <!-- 网格背景 -->
        <div class="grid-background"></div>
        
        <!-- 画布内容 -->
        <div class="canvas-content">
        <!-- 阶段卡片 -->
        <StageCard
          v-for="stage in stages"
          :key="stage.id"
          :stage="stage"
          :all-stages="stages"
          :is-selected="selectedStageId === stage.id"
          :selected-task-id="selectedTaskId"
          :selected-connection-id="selectedConnectionId"
          :connections="connections"
          :zoom-level="zoomLevel"
          :is-connecting-source="connectingSourceId === stage.id && connectingSourceType === 'stage'"
          :is-connecting-target="connectingTargetId === stage.id && connectingTargetType === 'stage'"
          :connecting-source-id="connectingSourceId"
          :connecting-target-id="connectingTargetId"
          :connecting-source-type="connectingSourceType"
          :connecting-target-type="connectingTargetType"
          :connecting-source-position="connectingSourcePosition"
          :is-overlapping-stage="isDraggingToAdd && dragType === 'stage' && overlappingStageId === stage.id"
          :get-user-display-name="getUserDisplayName"
          @select="handleStageSelect"
          @edit="handleStageEdit"
          @delete="handleStageDelete"
          @resize-end="handleStageResizeEnd"
          @position-change="handleStagePositionChange"
          @task-select="handleTaskSelect"
          @task-edit="handleTaskEdit"
          @task-delete="handleTaskDelete"
          :on-drag-end-direct="onTaskDragEnd"
          @connection-start="handleConnectionStart"
          @connection-panel-end="handleConnectionPanelEnd"
          @connection-move="handleConnectionMove"
          @connection-cancel="handleConnectionCancel"
        />
        
        <!-- 连接线 -->
        <ConnectionLine
          v-for="connection in connections"
          :key="connection.id"
          :connection="connection"
          :stages="stages"
          :unassigned-tasks="unassignedTasks"
          :is-valid="true"
          :selected-stage-id="selectedStageId"
          :selected-task-id="selectedTaskId"
          :is-selected="selectedConnectionId === connection.id"
          :find-task-by-id="findTaskById"
          :find-stage-by-id="findStageById"
          @select="handleConnectionSelect"
          @delete="handleConnectionDelete"
        />
        
        <!-- 预览连接线 -->
        <ConnectionLinePreview
          v-if="previewConnection"
          :from-point="previewConnection.fromPoint"
          :to-point="previewConnection.toPoint"
        />
        
        <!-- 拖拽添加预览元素 -->
        <div
          v-if="isDraggingToAdd && previewStyle"
          class="drag-to-add-preview"
          :class="{
            'drag-to-add-preview--stage': dragType === 'stage',
            'drag-to-add-preview--task': dragType === 'task',
            'drag-to-add-preview--invalid': !isPreviewValid
          }"
          :style="previewStyle"
        >
          <div class="drag-to-add-preview-icon">
            <div v-if="dragType === 'stage'" class="preview-icon-stage">
              <div class="preview-icon-stage-header"></div>
              <div class="preview-icon-stage-body">
                <div class="preview-icon-stage-dot"></div>
                <div class="preview-icon-stage-dot"></div>
                <div class="preview-icon-stage-dot"></div>
              </div>
            </div>
            <div v-else class="preview-icon-task">
              <div class="preview-icon-task-dot"></div>
            </div>
          </div>
        </div>
        
        <!-- 阶段外任务（过滤掉拖拽中的任务，避免重复显示） -->
        <TaskCard
          v-for="task in getVisibleUnassignedTasks"
          :key="task.id"
          :task="task"
          :is-selected="selectedTaskId === task.id"
          :selected-task-id="selectedTaskId"
          :selected-connection-id="selectedConnectionId"
          :connections="connections"
          :is-valid-position="false"
          :stages="stages"
          :zoom-level="zoomLevel"
          :is-connecting-source="false"
          :is-connecting-target="false"
          :connecting-source-position="null"
          :get-user-display-name="getUserDisplayName"
          @select="handleTaskSelect"
          @edit="handleTaskEdit"
          @delete="handleTaskDelete"
          :on-drag-end-direct="onTaskDragEnd"
        />
        <div id="task-action-layer" class="task-action-layer"></div>
        </div>
      </div>
    </div>
    <el-dialog
      v-model="abnormalDialogVisible"
      title="异常列表"
      width="820px"
      append-to-body
    >
      <!-- 异常任务列表 -->
      <div v-if="abnormalTaskCount > 0" style="margin-bottom: 20px;">
        <div style="font-weight: bold; margin-bottom: 10px;">异常任务</div>
        <el-table
          :data="abnormalTasks"
          border
          size="small"
          style="width: 100%"
        >
          <el-table-column prop="id" label="任务ID" width="60" />
          <el-table-column label="任务名称" min-width="160">
            <template #default="{ row }">
              <div class="abnormal-task-name">
                <span class="abnormal-task-id">{{ row.id }}</span>
                {{ row.name }}
              </div>
              <div class="abnormal-task-stage">阶段：{{ row.stageName }}</div>
            </template>
          </el-table-column>
          <el-table-column label="异常原因" width="309">
            <template #default="{ row }">
              <el-tag
                v-for="(reason, index) in row.reasons"
                :key="`task-${row.id}-reason-${index}`"
                :class="getReasonTagClass(reason)"
                size="small"
                :disable-transitions="true"
                style="white-space: nowrap;"
              >
                {{ reason }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="65" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                @click="handleFocusAbnormalTask(row.id)"
              >
                定位
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 异常阶段列表 -->
      <div v-if="abnormalStageCount > 0">
        <div style="font-weight: bold; margin-bottom: 10px;">异常阶段</div>
        <el-table
          :data="abnormalStages"
          border
          size="small"
          style="width: 100%"
        >
          <el-table-column prop="id" label="阶段ID" width="60" />
          <el-table-column label="阶段名称" min-width="160">
            <template #default="{ row }">
              <div class="abnormal-task-name">
                <span class="abnormal-task-id">{{ row.id }}</span>
                {{ row.name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="异常原因" width="249">
            <template #default="{ row }">
              <el-tag
                v-for="(reason, index) in row.reasons"
                :key="`stage-${row.id}-reason-${index}`"
                :class="getReasonTagClass(reason)"
                size="small"
                :disable-transitions="true"
                style="white-space: nowrap;"
              >
                {{ reason }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="65" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                @click="handleFocusAbnormalStage(row.id)"
              >
                定位
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="totalAbnormalCount === 0" class="abnormal-task-empty">当前没有异常</div>
    </el-dialog>
    <el-dialog
      v-model="helpDialogVisible"
      title="帮助"
      width="600px"
      append-to-body
    >
      <div class="help-content">
        <p>这里是帮助内容。您可以在这里添加使用说明、操作指南等信息。</p>
        <p>例如：</p>
        <ul>
          <li>如何添加任务和阶段</li>
          <li>如何配置任务信息</li>
          <li>如何建立任务之间的连接关系</li>
          <li>如何处理异常任务</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElButton, ElIcon, ElMessage, ElAlert, ElDropdown, ElDropdownMenu, ElDropdownItem, ElTooltip } from 'element-plus'
import { Plus, RefreshLeft, Check, ZoomIn, Delete, ArrowDown, WarningFilled } from '@element-plus/icons-vue'
import '@/assets/icons/task_edit_icons/style.css'
import StageCard from './Stage/StageCard.vue'
import TaskCard from './Task/TaskCard.vue'
import ConnectionLine from './Connection/ConnectionLine.vue'
import ConnectionLinePreview from './Connection/ConnectionLinePreview.vue'
import { useCanvasZoom } from '../composables/canvas/useCanvasZoom'
import { useCanvasDrag } from '../composables/canvas/useCanvasDrag'
import { useDragToAdd } from '../composables/canvas/useDragToAdd'
import { useAbnormalTasks } from '../composables/task/useAbnormalTasks'
import { useAbnormalStages } from '../composables/stage/useAbnormalStages'
import { useCanvasLayout } from '../composables/canvas/useCanvasLayout'
import { useCanvasZoomControls } from '../composables/canvas/useCanvasZoomControls'
import { useTaskFocus } from '../composables/task/useTaskFocus'
import { useStageFocus } from '../composables/stage/useStageFocus'
import { useTaskVisibility } from '../composables/task/useTaskVisibility'
import { useCanvasEventHandlers } from '../composables/canvas/useCanvasEventHandlers'
import { useAbnormalTaskDialog } from '../composables/task/useAbnormalTaskDialog'

const props = defineProps({
  stages: {
    type: Array,
    default: () => []
  },
  connections: {
    type: Array,
    default: () => []
  },
  selectedStageId: {
    type: [String, Number],
    default: null
  },
  selectedTaskId: {
    type: [String, Number],
    default: null
  },
  selectedConnectionId: {
    type: [String, Number],
    default: null
  },
  projectName: {
    type: String,
    default: ''
  },
  previewConnection: {
    type: Object,
    default: null
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
  unassignedTasks: {
    type: Array,
    default: () => []
  },
  onTaskDragEnd: {
    type: Function,
    required: true
  },
  onCreateStage: {
    type: Function,
    required: true
  },
  onCreateTask: {
    type: Function,
    required: true
  },
  getUserDisplayName: {
    type: Function,
    default: null
  },
  findTaskById: {
    type: Function,
    required: true
  },
  findStageById: {
    type: Function,
    required: true
  },
  tasksGenerated: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'add-stage',
  'undo',
  'save',
  'save-and-generate',
  'organize-layout',
  'stage-select',
  'stage-edit',
  'stage-delete',
  'stage-resize-end',
  'stage-position-change',
  'task-select',
  'task-edit',
  'task-delete',
  'connection-start',
  'connection-panel-end',
  'connection-move',
  'connection-cancel',
  'connection-select',
  'connection-delete',
  'canvas-click'
])

const canvasRef = ref(null)
const { zoomLevel, handleWheel, resetZoom, zoomTo } = useCanvasZoom()
const { initCanvasDrag, cleanupCanvasDrag, isSpaceDown, isDragging: isCanvasDragging } = useCanvasDrag()

// 拖拽添加功能
const {
  isDraggingToAdd,
  dragType,
  previewPosition,
  mousePosition,
  overlappingStageId,
  previewStyle,
  isPreviewValid,
  startDragToAdd,
  updateDragPosition,
  endDragToAdd,
  cancelDragToAdd,
  resetDragToAdd
} = useDragToAdd()

// 异常任务
const { abnormalTasks, abnormalTaskCount, abnormalTaskType } = useAbnormalTasks(
  computed(() => props.stages || []),
  computed(() => props.unassignedTasks || [])
)

// 异常阶段
const { abnormalStages, abnormalStageCount } = useAbnormalStages(
  computed(() => props.stages || [])
)

// 总异常数（任务 + 阶段）
const totalAbnormalCount = computed(() => abnormalTaskCount.value + abnormalStageCount.value)

// 异常类型（如果有任务异常且不是只有时间异常，则显示红色；否则显示黄色）
const totalAbnormalType = computed(() => {
  if (totalAbnormalCount.value === 0) {
    return 'warning'
  }
  // 如果有任务异常且不是只有时间异常，返回 danger
  if (abnormalTaskCount.value > 0 && abnormalTaskType.value === 'danger') {
    return 'danger'
  }
  // 否则返回 warning
  return 'warning'
})

// 画布布局
const { canvasSize, canvasWrapperStyle } = useCanvasLayout(props, zoomLevel)

// 缩放控制
const { zoomPercentage, zoomOptions, handleZoomCommand } = useCanvasZoomControls(
  zoomLevel,
  resetZoom,
  zoomTo,
  canvasRef
)

// 任务定位
const { focusOnTask } = useTaskFocus(props.findTaskById, zoomTo, canvasRef)

// 阶段定位
const { focusOnStage } = useStageFocus(props.findStageById, zoomTo, canvasRef)

// 任务可见性
const unassignedTasksRef = computed(() => props.unassignedTasks)
const { getVisibleUnassignedTasks } = useTaskVisibility(unassignedTasksRef)

// 异常任务对话框
const { abnormalDialogVisible, handleAbnormalButtonClick, handleFocusAbnormalTask: handleFocusAbnormalTaskBase } = useAbnormalTaskDialog(
  totalAbnormalCount,
  focusOnTask
)

// 帮助对话框
const helpDialogVisible = ref(false)

// 包装定位函数，关闭对话框
const handleFocusAbnormalTask = (taskId) => {
  handleFocusAbnormalTaskBase(taskId)
}

// 定位异常阶段
const handleFocusAbnormalStage = (stageId) => {
  focusOnStage(stageId)
  abnormalDialogVisible.value = false
}

// 根据异常原因返回对应的标签样式类
const getReasonTagClass = (reason) => {
  // 时间关系异常 - 黄色（包括任务和阶段的时间异常）
  if (reason === '时间关系异常' || reason === '与前置阶段时间冲突' || reason === '与后置阶段时间冲突') {
    return 'abnormal-reason-tag--time-issue'
  }
  // 其他原因（信息缺失、未分配到阶段、位置超出阶段范围）- 红色
  return 'abnormal-reason-tag--invalid'
}

// 事件处理器（简单的 emit 转发）
const {
  handleUndo,
  handleSave,
  handleSaveAndGenerate,
  handleOrganizeLayout,
  handleCanvasClick,
  handleStageSelect,
  handleStageEdit,
  handleStageDelete,
  handleStageResizeEnd,
  handleStagePositionChange,
  handleTaskSelect,
  handleTaskEdit,
  handleTaskDelete,
  handleConnectionStart,
  handleConnectionPanelEnd,
  handleConnectionMove,
  handleConnectionCancel,
  handleConnectionSelect,
  handleConnectionDelete
} = useCanvasEventHandlers(emit)

// 工具栏按钮事件
const handleStageButtonMouseDown = (event) => {
  startDragToAdd('stage')
  event.preventDefault()
  event.stopPropagation()
}

const handleTaskButtonMouseDown = (event) => {
  startDragToAdd('task')
  event.preventDefault()
  event.stopPropagation()
}

// 画布事件
const handleWheelEvent = (event) => {
  handleWheel(event, canvasRef.value)
}

const handleCanvasMouseMove = (event) => {
  if (isDraggingToAdd.value) {
    updateDragPosition(event, canvasRef.value, zoomLevel.value, props.stages)
  }
}

const handleCanvasMouseUp = (event) => {
  if (isDraggingToAdd.value) {
    endDragToAdd(
      event,
      canvasRef.value,
      zoomLevel.value,
      props.stages,
      (position) => {
        props.onCreateStage(position)
      },
      (position, targetStage) => {
        props.onCreateTask(position, targetStage)
      }
    )
  }
}

const handleCanvasMouseLeave = () => {
  if (isDraggingToAdd.value) {
    cancelDragToAdd()
  }
}

// 全局鼠标事件处理
let handleGlobalMouseUp = null

onMounted(() => {
  // 初始化画布
  if (canvasRef.value) {
    // 初始滚动位置设置为左上角
    canvasRef.value.scrollLeft = 0
    canvasRef.value.scrollTop = 0
    
    // 初始化拖拽功能
    initCanvasDrag(canvasRef.value)
  }
  
  // 添加全局鼠标事件监听（用于处理鼠标在画布外松开的情况）
  handleGlobalMouseUp = (event) => {
    if (isDraggingToAdd.value) {
      // 检查鼠标是否在画布内
      if (canvasRef.value && !canvasRef.value.contains(event.target)) {
        cancelDragToAdd()
      }
    }
  }
  
  document.addEventListener('mouseup', handleGlobalMouseUp)
})

onUnmounted(() => {
  cleanupCanvasDrag()
  resetDragToAdd()
  if (handleGlobalMouseUp) {
    document.removeEventListener('mouseup', handleGlobalMouseUp)
  }
})

defineExpose({
  focusOnTask
})
</script>

<style scoped>
.workflow-canvas-container {
  flex: 1;
  min-height: 0; /* 使用flex时，设置min-height为0避免溢出 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.workflow-toolbar {
  flex-shrink: 0; /* 工具栏不收缩 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-shadow: var(--el-box-shadow-base);
  position: relative;
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.toolbar-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.toolbar-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-center > * {
  margin: 0 !important;
}

.toolbar-icon-button {
  width: 32px;
  height: 32px;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--el-border-radius-base);
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  min-height: 32px;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}

.toolbar-icon-button:hover {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.toolbar-icon-button:hover i {
  color: #ffffff;
}

.toolbar-icon-button:active {
  background-color: var(--el-color-primary-dark-2);
}

.toolbar-icon-button i {
  font-size: 20px;
  line-height: 1;
  color: var(--el-text-color-regular);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  margin: 0;
  background-color: var(--el-fill-color);
  flex-shrink: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}

.toolbar-right-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.abnormal-task-button-wrapper {
  position: relative;
  display: inline-block;
}

.abnormal-task-button {
  width: 60px;
  justify-content: center;
  
  /* 当没有异常任务时，禁用悬停交互和点击 */
  &.abnormal-task-button--no-hover {
    cursor: default;
    pointer-events: none;
    
    /* 保持默认样式，不显示悬停效果 */
    &:hover,
    &:focus,
    &:active {
      background-color: var(--el-button-bg-color) !important;
      border-color: var(--el-button-border-color) !important;
      color: var(--el-button-text-color) !important;
    }
  }
}

.abnormal-task-text {
  display: inline-block;
}

.abnormal-task-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 16px;
  height: 16px;
  color: var(--el-color-danger);
  z-index: 10;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border-radius: 50%;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

.help-button {
  width: 60px;
  justify-content: center;
  
  /* 确保与缩放按钮悬停样式一致 - 白色背景 */
  &:hover {
    background-color: #fff !important;
    border-color: var(--el-button-hover-border-color);
    color: var(--el-button-hover-text-color);
  }
}

.zoom-dropdown {
  :deep(.el-button) {
    width: 80px;
    justify-content: center;
  }
  
  :deep(.el-button .el-icon) {
    margin-left: 4px;
  }
  
  /* 确保缩放按钮与帮助按钮悬停样式一致 - 白色背景 */
  :deep(.el-button.is-plain:hover),
  :deep(.el-button.zoom-button:hover),
  :deep(.el-button.is-plain.is-hovering),
  :deep(.el-button.zoom-button.is-hovering),
  :deep(.el-button:hover.is-plain),
  :deep(.el-button:hover.zoom-button) {
    background-color: #fff !important;
    border-color: var(--el-button-hover-border-color) !important;
    color: var(--el-button-hover-text-color) !important;
  }
}

.help-content {
  line-height: 1.8;
  color: var(--el-text-color-regular);
  
  ul {
    margin: 12px 0;
    padding-left: 24px;
    
    li {
      margin: 8px 0;
    }
  }
}

.abnormal-task-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.4;
}

.abnormal-task-stage {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 0;
  line-height: 1.4;
}

.abnormal-task-id {
  color: var(--el-text-color-secondary);
  margin-right: 2px;
}

/* 异常原因标签样式 - 红色（信息缺失、未分配到阶段、位置超出阶段范围） */
.abnormal-reason-tag--invalid {
  border: 1px solid var(--el-color-danger) !important;
  background-color: var(--el-color-danger-light-9) !important;
  color: var(--el-color-danger) !important;
  border-radius: var(--el-border-radius-base) !important;
  height: 24px !important;
  line-height: 22px !important;
}

/* 异常原因标签样式 - 黄色（时间关系异常） */
.abnormal-reason-tag--time-issue {
  border: 1px solid var(--el-color-warning) !important;
  background-color: var(--el-color-warning-light-9) !important;
  color: var(--el-color-warning) !important;
  border-radius: var(--el-border-radius-base) !important;
  height: 24px !important;
  line-height: 22px !important;
}

/* td.el-table__cell 元素 - 删除上下4px的padding，保留左右padding */
:deep(.el-table__body-wrapper .el-table__body tr td.el-table__cell) {
  padding: 0 !important;
}

/* div.cell 元素 - 四向8px的padding */
:deep(.el-table__body-wrapper .el-table__body tr td .cell) {
  padding: 8px !important;
}

/* 异常原因列 - 防止文本截断，不显示省略号 */
:deep(.el-table__body-wrapper .el-table__body tr td:nth-child(3) .cell) {
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
  padding: 8px !important;
  line-height: 0 !important;
  display: flex !important;
  align-items: flex-start !important;
  flex-wrap: wrap !important;
  gap: 4px !important;
  align-content: flex-start !important;
}

/* 操作列单元格样式 - 内容居中 */
:deep(.el-table__body-wrapper .el-table__body tr td:last-child .cell) {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  padding: 8px !important;
}

.abnormal-task-empty {
  text-align: center;
  padding: 24px 0;
  color: var(--el-text-color-regular);
}

.workflow-canvas {
  flex: 1;
  min-height: 0; /* 重要：允许flex子元素缩小 */
  overflow: auto;
  position: relative;
  background: var(--el-bg-color-page);
}

.workflow-canvas.canvas-dragging * {
  pointer-events: none !important;
}

.canvas-wrapper {
  position: absolute;
  top: 0;
  left: 0;
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--el-bg-color-page);
  pointer-events: none;
  z-index: 0;
}

.canvas-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.task-action-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2000;
}

.workflow-canvas.canvas-dragging-to-add * {
  pointer-events: none !important;
}

.drag-to-add-button {
  user-select: none;
}

.drag-to-add-preview {
  position: absolute;
  border: 2px dashed var(--el-color-primary);
  background-color: rgba(64, 158, 255, 0.1);
  pointer-events: none;
  z-index: 10;
  border-radius: 8px;
}

.drag-to-add-preview--invalid {
  border-color: var(--el-color-danger);
  background-color: rgba(245, 108, 108, 0.1);
}

.drag-to-add-preview-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
}

.preview-icon-stage {
  width: 40px;
  height: 30px;
  border: 1px solid var(--el-text-color-regular);
  border-radius: 4px;
  background: var(--el-bg-color);
}

.preview-icon-stage-header {
  height: 8px;
  border-bottom: 1px solid var(--el-text-color-regular);
  background: var(--el-bg-color-page);
}

.preview-icon-stage-body {
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 4px;
}

.preview-icon-stage-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--el-text-color-regular);
}

.preview-icon-task {
  width: 24px;
  height: 24px;
  border: 1px solid var(--el-text-color-regular);
  border-radius: 4px;
  background: var(--el-bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-icon-task-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--el-text-color-regular);
}
</style>
