// stores/workflowStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  updateStageInWorkflowData,
  updateTaskInWorkflowData,
  removeStageFromWorkflowData,
  removeTaskFromWorkflowData,
  addTaskToUnassigned,
  addConnectionToConnections
} from '../composables/workflowdata/useWorkflowDataOperations'

/**
 * 工作流Store
 * 重构后：不再存储重复的数据，而是提供操作主数据源的辅助方法
 * 主数据源：
 * - stages: workflowData.value.stages
 * - tasks: workflowData.value.stages[].tasks (阶段内) + unassignedTasks.value (阶段外)
 * - connections: connections ref (在 index.vue 中定义)
 */
export const useWorkflowStore = defineStore('workflow', () => {
  // UI 状态（保留，虽然可能没有被使用，但为了兼容性保留）
  const selectedElement = ref(null)
  const selectedElementType = ref(null) // 'stage' 或 'task'
  const isDragging = ref(false)
  const dragType = ref(null) // 'task' 或 'stage'
  const dragElement = ref(null)
  
  // 主数据源的引用（通过 init 方法设置，使用 ref 确保 Pinia 正确处理）
  const workflowDataRef = ref(null)
  const unassignedTasksRef = ref(null)
  const connectionsRef = ref(null)
  
  /**
   * 初始化主数据源引用
   * @param {Object} workflowData - workflowData ref
   * @param {Object} unassignedTasks - unassignedTasks ref
   * @param {Object} connections - connections ref
   */
  const init = (workflowData, unassignedTasks, connections) => {
    workflowDataRef.value = workflowData
    unassignedTasksRef.value = unassignedTasks
    connectionsRef.value = connections
  }
  
  /**
   * 设置 stages（用于兼容性，实际直接操作 workflowData.value.stages）
   * @deprecated 直接操作 workflowData.value.stages
   */
  const setStages = (newStages) => {
    if (workflowDataRef.value?.value) {
      workflowDataRef.value.value.stages = Array.isArray(newStages) ? newStages.map(stage => ({
        ...stage,
        tasks: Array.isArray(stage.tasks) ? stage.tasks.map(task => ({ ...task })) : []
      })) : []
    }
  }
  
  /**
   * 设置 tasks（用于兼容性，实际不需要，因为 tasks 在 stages 中）
   * @deprecated 不再使用
   */
  const setTasks = (newTasks) => {
    // 不再使用，因为 tasks 在 stages 中
  }
  
  /**
   * 设置 connections（用于兼容性，实际直接操作 connections ref）
   * @deprecated 直接操作 connections ref
   */
  const setConnections = (newConnections) => {
    if (connectionsRef.value?.value) {
      connectionsRef.value.value = newConnections
    }
  }
  
  const selectElement = (elementId, elementType) => {
    selectedElement.value = elementId
    selectedElementType.value = elementType
  }
  
  const clearSelection = () => {
    selectedElement.value = null
    selectedElementType.value = null
  }
  
  /**
   * 更新阶段（直接操作主数据源）
   */
  const updateStage = (stageId, updates) => {
    if (workflowDataRef.value) {
      updateStageInWorkflowData(workflowDataRef.value, stageId, updates)
    }
  }
  
  /**
   * 删除阶段（直接操作主数据源）
   */
  const removeStage = (stageId) => {
    if (workflowDataRef.value) {
      removeStageFromWorkflowData(workflowDataRef.value, stageId)
    }
  }
  
  /**
   * 更新任务（直接操作主数据源）
   */
  const updateTask = (taskId, updates) => {
    if (workflowDataRef.value && unassignedTasksRef.value) {
      updateTaskInWorkflowData(workflowDataRef.value, unassignedTasksRef.value, taskId, updates)
    }
  }
  
  /**
   * 删除任务（直接操作主数据源）
   */
  const removeTask = (taskId) => {
    if (workflowDataRef.value && unassignedTasksRef.value) {
      removeTaskFromWorkflowData(workflowDataRef.value, unassignedTasksRef.value, taskId)
    }
  }
  
  /**
   * 添加任务到阶段外（直接操作主数据源）
   */
  const addTask = (task) => {
    if (unassignedTasksRef.value) {
      addTaskToUnassigned(unassignedTasksRef.value, task)
    }
  }
  
  /**
   * 添加连接（直接操作主数据源）
   */
  const addConnection = (connection) => {
    if (connectionsRef.value) {
      addConnectionToConnections(connectionsRef.value, connection)
    }
  }
  
  /**
   * 获取 connections（用于兼容性）
   */
  const getConnections = () => {
    return connectionsRef.value?.value || []
  }
  
  const startDrag = (elementId, elementType) => {
    isDragging.value = true
    dragType.value = elementType
    dragElement.value = elementId
  }
  
  const endDrag = () => {
    isDragging.value = false
    dragType.value = null
    dragElement.value = null
  }
  
  const reset = () => {
    selectedElement.value = null
    selectedElementType.value = null
    isDragging.value = false
    dragType.value = null
    dragElement.value = null
  }
  
  return {
    // 初始化方法
    init,
    
    // 主数据源引用（暴露给外部使用，直接暴露 ref，外部通过 .value 访问）
    workflowDataRef,
    unassignedTasksRef,
    connectionsRef,
    
    // UI 状态（保留用于兼容性）
    selectedElement,
    selectedElementType,
    isDragging,
    dragType,
    dragElement,
    
    // 方法（直接操作主数据源）
    setStages,
    setTasks,
    setConnections,
    selectElement,
    clearSelection,
    updateStage,
    removeStage,
    addTask,
    updateTask,
    removeTask,
    addConnection,
    getConnections,
    startDrag,
    endDrag,
    reset
  }
})
