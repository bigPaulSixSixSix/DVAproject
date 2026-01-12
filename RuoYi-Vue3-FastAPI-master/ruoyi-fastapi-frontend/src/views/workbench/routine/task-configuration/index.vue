<template>
    <div class="app-container">
    <div class="workflow-container" v-loading="loading" element-loading-text="加载中...">
      <!-- 阶段编辑弹窗 -->
      <el-dialog
        ref="stageEditDialogRef"
        v-model="stageEditDialogVisible"
        title="编辑阶段"
        width="500px"
        append-to-body
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        @close="handleStageEditDialogClose"
        @opened="handleStageEditDialogOpened"
        @closed="handleStageEditDialogClosed"
      >
        <el-form 
          ref="stageEditFormRef" 
          :model="stageEditForm" 
          :rules="stageEditRules" 
          label-width="80px"
        >
          <el-form-item label="阶段名称" prop="name">
            <el-input 
              v-model="stageEditForm.name" 
              placeholder="请输入阶段名称"
              :disabled="!isCurrentStageEditable"
            />
          </el-form-item>
          <el-form-item label="任务数量">
            <span>{{ stageEditForm.taskCount }}</span>
          </el-form-item>
          <el-form-item label="时间">
            <span :class="{ 'stage-edit-time-invalid': stageEditForm.hasInvalidTime }">
              {{ stageEditForm.timeRange }}
            </span>
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button 
              v-if="isCurrentStageEditable"
              type="danger" 
              @click="handleStageEditDelete"
            >
              删除
            </el-button>
            <el-button @click="handleStageEditCancel">取消</el-button>
            <el-button type="primary" @click="handleStageEditConfirm">确认</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 任务编辑弹窗 -->
      <TaskEditDialog
        ref="taskEditDialogRef"
        v-model:visible="taskEditDialogVisible"
        :form="taskEditForm"
        :rules="taskEditRules"
        :employee-options="employeeOptions"
        :approval-level-tree="approvalLevelTree"
        :update-approval-level-tree="updateApprovalLevelTree"
        :current-editing-task="currentEditingTask"
        :task-tabs="taskEditTabs"
        :active-tab-id="activeTaskTabId"
        :predecessor-task-list="computedPredecessorTaskList"
        :successor-task-list="computedSuccessorTaskList"
        :get-user-nick-name="getUserNickName"
        :handle-time-field-change="handleTimeFieldChange"
        :find-task-by-id="findTaskByIdWrapper"
        @close="handleTaskEditDialogClose"
        @confirm="handleTaskEditConfirm"
        @cancel="handleTaskEditCancel"
        @delete="handleTaskEditDelete"
        @tab-select="handleTaskTabSelect"
        @tab-close="handleTaskTabClose"
        @predecessor-task-edit="handlePredecessorTaskEdit"
        @predecessor-task-unlink="handlePredecessorTaskUnlink"
        @predecessor-task-delete="handlePredecessorTaskDelete"
        @successor-task-edit="handleSuccessorTaskEdit"
        @successor-task-unlink="handleSuccessorTaskUnlink"
        @successor-task-delete="handleSuccessorTaskDelete"
        @enter-key="handleTaskEditEnter"
        @esc-key="handleTaskEditEsc"
      />
      
      <!-- 只有在数据加载完成后才渲染WorkflowCanvas -->
      <WorkflowCanvas
        v-if="dataLoaded"
        :stages="workflowData?.stages || []"
        :unassigned-tasks="unassignedTasks"
        :connections="connections"
        :selected-stage-id="selectedStageId"
        :selected-task-id="selectedTaskId"
        :selected-connection-id="selectedConnectionId"
        :preview-connection="previewConnection"
        :connecting-source-id="connectionStart?.elementId || null"
        :connecting-source-type="connectionStart?.elementType || null"
        :connecting-target-id="connectingTargetElement?.elementId || null"
        :connecting-target-type="connectingTargetElement?.elementType || null"
        :connecting-source-position="connectionStart?.position || null"
        :on-task-drag-end="handleTaskDragEnd"
        :get-user-display-name="getUserNickName"
        :find-task-by-id="findTaskByIdWrapper"
        :find-stage-by-id="findStageByIdWrapper"
        :project-name="projectName"
        :tasks-generated="tasksGenerated"
        @add-stage="handleAddStage"
        @undo="handleUndo"
        @save="handleSave"
        @save-and-generate="handleSaveAndGenerate"
        @organize-layout="handleOrganizeLayout"
        @stage-select="handleStageSelect"
        @stage-edit="handleStageEdit"
        @stage-delete="handleStageDelete"
        @stage-resize-end="handleStageResizeEnd"
        @stage-position-change="handleStagePositionChange"
        @task-select="handleTaskSelect"
        @task-edit="handleTaskEdit"
        @task-delete="handleTaskDelete"
        @connection-start="handleConnectionStart"
        @connection-panel-end="handleConnectionPanelEnd"
        @connection-move="handleConnectionMove"
        @connection-cancel="handleConnectionCancel"
        @connection-select="handleConnectionSelect"
        @connection-delete="handleConnectionDelete"
        @canvas-click="handleCanvasClick"
        :on-create-stage="handleCreateStage"
        :on-create-task="handleCreateTask"
      />
    </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElDialog, ElForm, ElFormItem, ElInput, ElButton, ElMessageBox, ElMessage } from 'element-plus'
import { getDicts } from '@/api/system/dict/data'
import useTagsViewStore from '@/store/modules/tagsView'
import useSettingsStore from '@/store/modules/settings'
import WorkflowCanvas from './components/WorkflowCanvas.vue'
import TaskEditDialog from './components/Task/TaskEditDialog.vue'
import { useWorkflowData } from './composables/workflowdata/useWorkflowData'
import { useWorkflowStore } from './stores/workflowStore'
import { useProjectStore } from './stores/projectStore'
import { useAutoSave } from './composables/system/useAutoSave'
// 从主文件统一导入连接相关功能
import { 
  useConnection,
  useConnectionLine
} from './composables/connection/useConnection'
import { useDragDrop } from './composables/canvas/useDragDrop'
import { useTaskManagement } from './composables/task/useTaskManagement'
import { useTaskDrag } from './composables/task/useTaskDrag'
import { useTaskDragHandler } from './composables/task/useTaskDragHandler'
import { useTaskDragEnd } from './composables/task/useTaskDragEnd'
import { useStageManagement } from './composables/stage/useStageManagement'
import { useStageEdit } from './composables/stage/useStageEdit'
import { useTaskEdit } from './composables/task/useTaskEdit'
import { useWorkflowLoader } from './composables/workflowdata/useWorkflowLoader'
import { useTaskDragPreview } from './composables/task/useTaskDragPreview'
import { useTaskValidation } from './composables/task/useTaskValidation'
import { useTaskEditController } from './composables/task/useTaskEditController'
import { useStageController } from './composables/stage/useStageController'
import { useWorkflowController } from './composables/workflowdata/useWorkflowController'
import { useWorkflowSave } from './composables/workflowdata/useWorkflowSave'
import { useWorkflowInitializer } from './composables/workflowdata/useWorkflowInitializer'
import { useDialogKeyboardHandler } from './composables/utils/useDialogKeyboardHandler'
import { useLayoutOrganizer } from './composables/layout/useLayoutOrganizer'

defineOptions({
  name: 'TaskConfiguration'
})

// 获取路由参数
const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.projectId)
const tagsViewStore = useTagsViewStore()
const settingsStore = useSettingsStore()

// 状态管理
const workflowStore = useWorkflowStore()
const projectStore = useProjectStore()
const { workflowData, loading, saveWorkflow, saveWorkflowAndGenerate, toFrontendFormat } = useWorkflowData()
const { startAutoSave, stopAutoSave, onBeforeUnload } = useAutoSave()
const { constrainTaskToStage } = useDragDrop()

// 本地状态
const selectedStageId = ref(null)
const selectedTaskId = ref(null)
const selectedConnectionId = ref(null)
const connections = ref([])
const unassignedTasks = ref([]) // 阶段外的任务
const taskEditDialogRef = ref(null)
const dataLoaded = ref(false) // 数据加载完成标志
const projectName = ref('') // 项目名称
const tasksGenerated = ref(false) // 项目是否已生成任务

// 初始化 workflowStore 的主数据源引用
workflowStore.init(workflowData, unassignedTasks, connections)

// 计算是否有阶段外任务

// 使用 composables
const { findTaskById, findStageById, findStageByPosition, handleTaskDelete: deleteTask, handleTaskSelect: selectTask, createTaskAtPosition } = useTaskManagement()
const { createTaskDragEndHandler } = useTaskDragEnd()
const { validateBeforeSave } = useTaskValidation()

// 包装函数，适配原有调用方式
const findTaskByIdWrapper = (taskId) => {
  return findTaskById(taskId, workflowData.value, unassignedTasks.value)
}

const findStageByIdWrapper = (stageId) => {
  return findStageById(stageId, workflowData.value)
}

// 计算当前编辑的阶段是否可编辑
const isCurrentStageEditable = computed(() => {
  const stageId = getCurrentEditingStageId()
  if (!stageId) return true
  const stage = findStageByIdWrapper(stageId)
  return stage?.isEditable !== false
})

const { 
  handleAddStage: addStage,
  createStageAtPosition,
  handleStageDelete: deleteStage, 
  handleStageResizeEnd: resizeStage, 
  handleStagePositionChange: changeStagePosition, 
  handleStageSelect: selectStage 
} = useStageManagement()
const { loadWorkflowData: loadWorkflow } = useWorkflowLoader()
const { findPreviewTaskIndex, clearPreviewTaskAndDragFlag, createOrUpdatePreviewTask } = useTaskDragPreview()
const { 
  stageEditDialogVisible, 
  stageEditFormRef, 
  stageEditForm, 
  stageEditRules,
  openStageEditDialog, 
  closeStageEditDialog, 
  confirmStageEdit,
  getCurrentEditingStageId
} = useStageEdit()

const {
  taskEditDialogVisible,
  taskEditFormRef,
  taskEditForm,
  taskEditRules,
  currentEditingTask,
  employeeOptions,
  approvalLevelTree,
  updateApprovalLevelTree,
  taskEditTabs,
  activeTaskTabId,
  openTaskEditDialog,
  closeTaskEditDialog,
  confirmTaskEdit,
  setActiveTaskTab,
  closeTaskTab,
  isTaskTabDirty,
  markTaskTabAsSaved,
  getCurrentEditingTaskId,
  getPredecessorTaskCount,
  getSuccessorTaskCount,
  getPredecessorTaskList,
  getSuccessorTaskList,
  getTaskStageName,
  handleTimeFieldChange,
  loadEmployeeList,
  getUserDisplayName,
  getUserNickName
} = useTaskEdit()

// 计算前置任务列表（响应式更新）
const computedPredecessorTaskList = computed(() => {
  if (!currentEditingTask.value) return []
  // 每次都从最新数据中获取任务信息
  const taskInfo = findTaskByIdWrapper(currentEditingTask.value.id)
  const task = taskInfo ? taskInfo.task : currentEditingTask.value
  return getPredecessorTaskList(task, findTaskByIdWrapper)
})

// 计算后置任务列表（响应式更新）
const computedSuccessorTaskList = computed(() => {
  if (!currentEditingTask.value) return []
  // 每次都从最新数据中获取任务信息
  const taskInfo = findTaskByIdWrapper(currentEditingTask.value.id)
  const task = taskInfo ? taskInfo.task : currentEditingTask.value
  return getSuccessorTaskList(task, findTaskByIdWrapper)
})

// 使用连接功能主入口（统一调用一次）
const {
  // 核心功能
  createConnection: createConnectionWrapper,
  deleteConnection: removeSingleConnection,
  initConnectionsFromWorkflow,
  removeAllTaskConnections: removeAllTaskConnectionsWrapper,
  findConnectionByTaskIds,
  getElementConnectionPoint,
  
  // 交互处理
  isConnecting,
  connectionStart,
  previewConnectionPoint,
  connectingTargetElement,
  handleConnectionStart: handleConnectionStartInternal,
  handleConnectionMove: handleConnectionMoveInternal,
  handleConnectionCancel: handleConnectionCancelInternal,
  handleConnectionPanelEnd: handleConnectionPanelEndInternal,
  
  // 预览连接
  previewConnection,
  
  // 控制器方法
  handleConnectionSelect: handleConnectionSelectBase,
  handleConnectionDelete: handleConnectionDeleteBase
} = useConnection({
  connections,
  workflowStore,
  findTaskById: findTaskByIdWrapper,
  findStageById: findStageByIdWrapper,
  workflowData,
  unassignedTasks
})

// 包装连接创建和删除函数，适配原有调用方式
const applyConnectionCreation = (fromElement, toElement) => {
  return createConnectionWrapper(fromElement, toElement)
}

const applyConnectionRemoval = (connectionId) => {
  return removeSingleConnection(connectionId)
}

// 连接控制器：使用主文件提供的接口
const handleConnectionSelect = (connectionId) => {
  handleConnectionSelectBase(connectionId, selectedConnectionId, selectedStageId, selectedTaskId)
}

const handleConnectionDelete = async (connectionId) => {
  // 如果传入了 connectionId，使用传入的；否则使用选中的 connectionId
  const targetConnectionId = connectionId || selectedConnectionId.value
  await handleConnectionDeleteBase(targetConnectionId, selectedConnectionId)
}

const {
  handleAddStage,
  handleStageSelect,
  handleStageEdit,
  handleStageEditDialogClose,
  handleStageEditCancel,
  handleStageEditConfirm,
  handleStageEditDelete,
  handleStageDelete,
  handleStageResizeEnd,
  handleStagePositionChange
} = useStageController({
  workflowData,
  workflowStore,
  selectedStageId,
  selectedTaskId,
  selectedConnectionId,
  connectionsRef: connections,
  stageEditDialogVisible,
  addStage,
  selectStage,
  deleteStage,
  resizeStage,
  changeStagePosition,
  openStageEditDialog,
  closeStageEditDialog,
  confirmStageEdit,
  getCurrentEditingStageId,
  findStageById: findStageByIdWrapper
})

const handleConnectionStart = (data) => {
  handleConnectionStartInternal(data)
}

const handleConnectionMove = (moveData) => {
  handleConnectionMoveInternal(moveData)
}

const handleConnectionCancel = () => {
  handleConnectionCancelInternal()
}

const handleConnectionPanelEnd = (data) => {
  handleConnectionPanelEndInternal(data)
}

const {
  handleUndo: handleUndoInternal,
  handleSave: handleSaveInternal,
  handleCanvasClick,
  handleCreateStage,
  handleCreateTask
} = useWorkflowController({
  workflowData,
  workflowStore,
  unassignedTasks,
  selectedStageId,
  selectedTaskId,
  selectedConnectionId,
  validateBeforeSave,
  saveWorkflow,
  createStageAtPosition,
  createTaskAtPosition,
  initConnectionsFromWorkflow
})

// 使用布局整理器
const { organizeLayout } = useLayoutOrganizer()

// 使用工作流保存处理器（包含保存后的完整逻辑）
const { handleSave, handleSaveAndGenerate } = useWorkflowSave({
  projectId,
  workflowData,
  unassignedTasks,
  projectStore,
  findTaskById: findTaskByIdWrapper,
  workflowStore,
  handleSaveInternal,
  saveWorkflowAndGenerate,
  initConnectionsFromWorkflow
})

// 处理整理布局
const handleOrganizeLayout = () => {
  if (!workflowData.value) {
    ElMessage.warning('工作流数据未加载')
    return
  }

  try {
    // 计算新布局
    const layoutResult = organizeLayout(workflowData.value, unassignedTasks.value)

    // 应用任务位置
    layoutResult.taskPositions.forEach((position, taskId) => {
      const taskInfo = findTaskByIdWrapper(taskId)
      if (taskInfo && taskInfo.task) {
        taskInfo.task.position = { ...position }
      }
    })

    // 应用阶段位置和尺寸
    layoutResult.stagePositions.forEach((position, stageId) => {
      const stage = workflowData.value.stages.find(s => String(s.id) === stageId)
      if (stage) {
        stage.position = { ...position }
        
        // 更新阶段尺寸
        const size = layoutResult.stageSizes.get(stageId)
        if (size) {
          stage.position.width = size.width
          stage.position.height = size.height
        }
      }
    })

    ElMessage.success('布局整理完成')
  } catch (error) {
    console.error('整理布局失败:', error)
    ElMessage.error('整理布局失败: ' + (error.message || '未知错误'))
  }
}

const handleUndo = handleUndoInternal

const {
  handleTaskTabSelect,
  handleTaskTabClose,
  handleTaskEdit,
  handleTaskEditDialogClose,
  handleTaskEditCancel,
  handleTaskEditConfirm,
  handleTaskEditDelete,
  handleTaskDelete,
  handlePredecessorTaskEdit,
  handlePredecessorTaskUnlink,
  handlePredecessorTaskDelete,
  handleSuccessorTaskEdit,
  handleSuccessorTaskUnlink,
  handleSuccessorTaskDelete
} = useTaskEditController({
  openTaskEditDialog,
  closeTaskEditDialog,
  setActiveTaskTab,
  closeTaskTab,
  isTaskTabDirty,
  markTaskTabAsSaved,
  confirmTaskEdit,
  getCurrentEditingTaskId,
  activeTaskTabId,
  taskEditDialogRef,
  findTaskById: findTaskByIdWrapper,
  deleteTask,
  workflowData,
  unassignedTasks,
  removeAllTaskConnections: removeAllTaskConnectionsWrapper,
  workflowStore,
  selectedTaskId,
  applyConnectionRemoval,
  connections,
  findConnectionByTaskIds
})

const handleTaskDragEnd = createTaskDragEndHandler({
  findTaskById: findTaskByIdWrapper,
  findStageById: findStageByIdWrapper,
  findStageByPosition: (pos) => findStageByPosition(pos, workflowData.value),
  clearPreviewTaskAndDragFlag,
  createOrUpdatePreviewTask,
  findPreviewTaskIndex,
  workflowData: workflowData.value,
  unassignedTasksRef: unassignedTasks,
  removeAllTaskConnections: removeAllTaskConnectionsWrapper,
  workflowStore,
  connectionsRef: connections,
  workflowDataRef: workflowData // 传入 workflowData ref（与连接线保持一致）
})

// 预览连接线已在 useConnection 中定义

// 更新页面标题
const updatePageTitle = async (projectId) => {
  try {
    // 从字典获取项目名称
    const dictResponse = await getDicts('sys_task_project')
    const dictProjects = dictResponse.data || []
    const project = dictProjects.find(p => p.dictValue === projectId)
    const name = project ? project.dictLabel : projectId
    projectName.value = name
    
    // 更新路由meta中的title
    const newTitle = `任务配置-${name}`
    if (route.meta) {
      route.meta.title = newTitle
    }
    
    // 等待下一个tick，确保标签页已经添加
    await nextTick()
    // 再等待一个tick，确保标签页组件已经渲染
    await nextTick()
    
    // 更新标签页标题 - 确保path匹配
    const currentPath = route.path
    const updateData = {
      ...route,
      path: currentPath,
      fullPath: route.fullPath || currentPath,
      title: newTitle, // 直接设置title属性
      meta: {
        ...route.meta,
        title: newTitle
      }
    }
    
    tagsViewStore.updateVisitedView(updateData)
    
    // 更新设置中的标题
    settingsStore.setTitle(newTitle)
  } catch (error) {
    console.error('更新页面标题失败:', error)
  }
}

// 使用工作流初始化器（包含加载后的完整初始化逻辑）
const { loadAndInitializeWorkflow: loadWorkflowData } = useWorkflowInitializer({
  projectId,
  workflowData,
  unassignedTasks,
  projectStore,
  workflowStore,
  initConnectionsFromWorkflow,
  findTaskById: findTaskByIdWrapper,
  loadEmployeeList,
  loadWorkflow,
  loading,
  toFrontendFormat,
  startAutoSave,
  dataLoaded,
  tasksGenerated
})

const handleTaskSelect = (taskId) => {
  selectTask(taskId, selectedTaskId, selectedStageId, workflowStore, selectedConnectionId)
}

// 监听路由变化，更新标题和重新加载数据
watch(() => route.params.projectId, async (newProjectId, oldProjectId) => {
  if (newProjectId) {
    await updatePageTitle(newProjectId)
    // 如果项目ID变化，重新加载数据
    if (newProjectId !== oldProjectId) {
      await loadWorkflowData()
    }
  }
}, { immediate: false }) // 改为 false，避免与 onMounted 重复调用

// 阶段编辑键盘事件处理
const handleStageEditEnter = async () => {
  console.log('[调试] handleStageEditEnter 被调用, isMessageBoxShowing:', isMessageBoxShowing)
  if (!stageEditDialogVisible.value) {
    console.log('[调试] 阶段编辑弹窗未打开，返回')
    return
  }
  
  // 检查是否有 ElMessageBox 正在显示
  if (isMessageBoxShowing) {
    console.log('[调试] ElMessageBox 正在显示，忽略 Enter 键，让 Element Plus 自己处理')
    return
  }
  
  // 阶段编辑直接保存，不需要确认框（与按钮点击行为一致）
  console.log('[调试] 直接调用 handleStageEditConfirm')
  await handleStageEditConfirm()
}

const handleStageEditEsc = async () => {
  console.log('[调试] handleStageEditEsc 被调用, isMessageBoxShowing:', isMessageBoxShowing)
  if (!stageEditDialogVisible.value) {
    console.log('[调试] 阶段编辑弹窗未打开，返回')
    return
  }
  
  // 检查是否有 ElMessageBox 正在显示
  if (isMessageBoxShowing) {
    console.log('[调试] ElMessageBox 正在显示，忽略 Esc 键，让 Element Plus 自己处理')
    return
  }
  
  // 检查是否有修改
  const currentStage = findStageByIdWrapper(getCurrentEditingStageId())
  const hasChanges = currentStage && currentStage.name !== stageEditForm.value.name
  console.log('[调试] 是否有修改:', hasChanges)
  
  if (hasChanges) {
    console.log('[调试] 有修改，显示确认取消对话框')
    isMessageBoxShowing = true
    try {
      const result = await ElMessageBox.confirm('当前有未保存的修改，确定要取消吗？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      })
      console.log('[调试] 用户确认取消，调用 handleStageEditCancel')
      handleStageEditCancel()
    } catch (error) {
      console.log('[调试] 用户取消操作，错误:', error)
      // 用户点击取消按钮，不执行任何操作，保持在编辑弹窗中
    } finally {
      // 等待一个 tick 确保弹窗完全关闭
      await nextTick()
      isMessageBoxShowing = false
      console.log('[调试] ElMessageBox 已关闭，重置标志位')
    }
  } else {
    console.log('[调试] 无修改，直接调用 handleStageEditCancel')
    handleStageEditCancel()
  }
}

// 任务编辑键盘事件处理
const handleTaskEditEnter = async () => {
  console.log('[调试] handleTaskEditEnter 被调用, isMessageBoxShowing:', isMessageBoxShowing)
  if (!taskEditDialogVisible.value) {
    console.log('[调试] 任务编辑弹窗未打开，返回')
    return
  }
  
  // 检查是否有 ElMessageBox 正在显示
  if (isMessageBoxShowing) {
    console.log('[调试] ElMessageBox 正在显示，忽略 Enter 键，让 Element Plus 自己处理')
    return
  }
  
  console.log('[调试] 准备显示确认保存对话框')
  isMessageBoxShowing = true
  try {
    await ElMessageBox.confirm('是否保存当前任务的修改？', '保存确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    console.log('[调试] 用户确认保存，调用 handleTaskEditConfirm（跳过确认）')
    // 跳过确认，直接执行保存逻辑
    await handleTaskEditConfirm(true)
  } catch (error) {
    console.log('[调试] 用户取消保存操作')
    // 用户取消，不执行任何操作
  } finally {
    // 等待一个 tick 确保弹窗完全关闭
    await nextTick()
    isMessageBoxShowing = false
    console.log('[调试] ElMessageBox 已关闭，重置标志位')
  }
}

const handleTaskEditEsc = async () => {
  console.log('[调试] handleTaskEditEsc 被调用, isMessageBoxShowing:', isMessageBoxShowing)
  if (!taskEditDialogVisible.value) {
    console.log('[调试] 任务编辑弹窗未打开，返回')
    return
  }
  
  // 检查是否有 ElMessageBox 正在显示
  if (isMessageBoxShowing) {
    console.log('[调试] ElMessageBox 正在显示，忽略 Esc 键，让 Element Plus 自己处理')
    return
  }
  
  // 检查是否有修改
  const hasChanges = activeTaskTabId.value && isTaskTabDirty(activeTaskTabId.value)
  console.log('[调试] 是否有修改:', hasChanges)
  
  if (hasChanges) {
    console.log('[调试] 有修改，显示确认取消对话框')
    isMessageBoxShowing = true
    try {
      const result = await ElMessageBox.confirm('当前有未保存的修改，确定要取消吗？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      })
      console.log('[调试] 用户确认取消，调用 handleTaskEditCancel（跳过确认）')
      // 跳过确认，直接关闭（因为已经确认过了）
      await handleTaskEditCancel(true)
    } catch (error) {
      console.log('[调试] 用户取消操作，错误:', error)
      // 用户点击取消按钮，不执行任何操作，保持在编辑弹窗中
    } finally {
      // 等待一个 tick 确保弹窗完全关闭
      await nextTick()
      isMessageBoxShowing = false
      console.log('[调试] ElMessageBox 已关闭，重置标志位')
    }
  } else {
    console.log('[调试] 无修改，直接调用 handleTaskEditCancel')
    await handleTaskEditCancel()
  }
}

// 注意：不再使用全局键盘事件处理，改为在弹窗元素上直接监听

// 标志位：跟踪是否有确认弹窗正在显示
let isMessageBoxShowing = false

// 阶段编辑弹窗 ref
const stageEditDialogRef = ref(null)
// 阶段编辑弹窗键盘事件处理
const handleStageEditKeyboardEnter = () => {
  handleStageEditEnter()
}

const handleStageEditKeyboardEsc = () => {
  handleStageEditEsc()
}

// 使用弹窗键盘事件处理 composable
const { setup: setupStageKeyboardHandler, cleanup: cleanupStageKeyboardHandler } = useDialogKeyboardHandler({
  dialogSelector: () => {
    // 直接通过类名查找（Element Plus Dialog 会添加到 body）
    // 因为 Vue 3 中 Element Plus Dialog 的 ref 结构可能不稳定，直接使用 DOM 查询更可靠
    const dialogs = document.querySelectorAll('.el-dialog')
    if (dialogs.length > 0) {
      // 返回最后一个（最上层的）弹窗
      return dialogs[dialogs.length - 1]
    }
    return null
  },
  onEnter: handleStageEditKeyboardEnter,
  onEsc: handleStageEditKeyboardEsc,
  isMessageBoxShowing: () => isMessageBoxShowing,
  debug: false
})

// 阶段编辑弹窗打开/关闭处理
const handleStageEditDialogOpened = () => {
  nextTick(() => {
    setupStageKeyboardHandler()
  })
}

const handleStageEditDialogClosed = () => {
  cleanupStageKeyboardHandler()
}

// 任务编辑弹窗的键盘事件由 TaskEditDialog 组件内部处理，这里不需要额外代码

// 生命周期
onMounted(async () => {
  // 加载数据
  loadWorkflowData()
})

onUnmounted(() => {
  stopAutoSave()
  onBeforeUnload(workflowData)
  // 确保移除所有事件监听
  handleStageEditDialogClosed()
})
</script>

<style scoped>
.stage-edit-time-invalid {
  color: var(--el-color-danger);
}
.app-container {
  height: calc(100vh - 94px); /* 94px = navbar(50px) + tags-view(44px) */
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.workflow-container {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
