// composables/connection/useConnection.js
// 主文件：统一对外接口，所有外部调用都应该从这个文件导入

// 导入子模块
import { useConnectionValidation } from './validation/useConnectionValidation'
import { useCycleDetection } from './validation/useCycleDetection'
import { useConnectionCreator } from './creation/useConnectionCreator'
import { useConnectionBuilder } from './creation/useConnectionBuilder'
import { useConnectionManager } from './data/useConnectionManager'
import { useConnectionHandlers } from './interaction/useConnectionHandlers'
import { usePreviewConnection } from './interaction/usePreviewConnection'
import { useConnectionInitializer } from './utils/useConnectionInitializer'
import { useConnectionLogger, setConnectionLoggingEnabled } from './utils/useConnectionLogger'
import { useConnectionLine } from './rendering/useConnectionLine'
import { useConnectionUtils } from './utils/useConnectionUtils'
import { updateTaskAndRelatedTasksTimeIssueFlags } from '../task/useTaskTimeValidation'
import { updateStageAndRelatedStagesTimeIssueFlags } from '../stage/useStageTimeValidation'
import { useStageTime } from '../stage/useStageTime'
import { nextTick } from 'vue'

/**
 * 连接功能主入口
 * 统一对外提供所有连接相关的功能
 */
export const useConnection = (context = {}) => {
  const {
    connections,
    workflowStore,
    findTaskById,
    findStageById,
    workflowData,
    unassignedTasks
  } = context

  // 初始化各个子模块
  const { validateConnection } = useConnectionValidation()
  const { detectCycles } = useCycleDetection()
  const { buildConnection } = useConnectionBuilder()
  const { applyUpdatedRelations, removeAllTaskConnections, removeSingleConnection, findConnectionByTaskIds, cleanupInvalidTaskRelations } = useConnectionManager()
  const { createConnectionBetweenElements: createConnectionInternal } = useConnectionCreator()
  const { initConnections, buildConnectionsFromWorkflow } = useConnectionInitializer()
  const { logConnectionCreation, logConnectionFailure, collectElementInfo } = useConnectionLogger()
  const { getElementConnectionPoint, getConnectionPoints, calculateBezierPath } = useConnectionLine()
  const { normalizeId, idsEqual, generateConnectionId } = useConnectionUtils()

  // 连接交互处理
  const connectionHandlers = useConnectionHandlers(findTaskById)
  const {
    isConnecting,
    connectionStart: connectionStartRef,
    previewConnectionPoint,
    connectingTargetElement,
    handleConnectionStart: handleConnectionStartInternal,
    handleConnectionMove: handleConnectionMoveInternal,
    handleConnectionCancel: handleConnectionCancelInternal,
    handleConnectionPanelEnd: handleConnectionPanelEndInternalBase
  } = connectionHandlers

  // 包装 handleConnectionPanelEnd，传入创建连接函数
  const handleConnectionPanelEndInternal = async (data) => {
    await handleConnectionPanelEndInternalBase(data, async (fromElement, toElement) => {
      await createConnection(fromElement, toElement)
    })
  }

  // 预览连接线
  const { previewConnection } = usePreviewConnection(
    isConnecting,
    connectionStartRef,
    previewConnectionPoint,
    connectingTargetElement,
    workflowData,
    unassignedTasks,
    getElementConnectionPoint
  )

  /**
   * 创建连接（对外接口）
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @returns {Promise<Object|null>} 连接结果或 null
   */
  const createConnection = async (fromElement, toElement) => {
    if (!connections || !workflowStore || !findTaskById || !findStageById) {
      console.error('useConnection: 缺少必要的上下文参数')
      return null
    }

    const result = createConnectionInternal(
      fromElement,
      toElement,
      {
        connections: connections.value || connections,
        connectionStart: connectionStartRef.value,
        findTaskById,
        findStageById,
        workflowStore
      },
      applyUpdatedRelations
    )

    if (result) {
      // 更新连接数组（如果是 ref）
      if (connections.value) {
        workflowStore.setConnections(connections.value)
      }
      
      // 建立连接后，检查被操作的任务及其相关任务的时间问题
      if (fromElement && fromElement.type === 'task') {
        updateTaskAndRelatedTasksTimeIssueFlags(fromElement.id, findTaskById, workflowStore, workflowData)
      }
      
      // 建立阶段连接后，需要先更新阶段的时间，然后再更新阶段的时间异常标记
      const { updateStageTime } = useStageTime()
      if (fromElement && fromElement.type === 'stage') {
        // 先更新阶段的时间（重新计算阶段内所有任务的时间范围）
        // 直接使用传入的 workflowData，而不是通过 workflowStore
        const workflowDataValue = workflowData?.value
        if (workflowDataValue && workflowDataValue.stages) {
          const stage = workflowDataValue.stages.find(s => s.id === fromElement.id)
          if (stage) {
            const updatedStage = updateStageTime(stage)
            // 使用 Object.assign 确保响应式更新
            Object.assign(stage, {
              startTime: updatedStage.startTime,
              endTime: updatedStage.endTime,
              duration: updatedStage.duration
            })
          }
        }
        // 然后更新阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(fromElement.id, findStageById, workflowStore, workflowData)
        await nextTick()
      }
      if (toElement && toElement.type === 'stage') {
        // 先更新阶段的时间（重新计算阶段内所有任务的时间范围）
        // 直接使用传入的 workflowData，而不是通过 workflowStore
        const workflowDataValue = workflowData?.value
        if (workflowDataValue && workflowDataValue.stages) {
          const stage = workflowDataValue.stages.find(s => s.id === toElement.id)
          if (stage) {
            const updatedStage = updateStageTime(stage)
            // 使用 Object.assign 确保响应式更新
            Object.assign(stage, {
              startTime: updatedStage.startTime,
              endTime: updatedStage.endTime,
              duration: updatedStage.duration
            })
          }
        }
        // 然后更新阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(toElement.id, findStageById, workflowStore, workflowData)
        await nextTick()
      }
    }

    return result
  }

  /**
   * 删除连接（对外接口）
   * @param {string} connectionId - 连接ID
   * @returns {Promise<Object>} { success, filteredConnections }
   */
  const deleteConnection = async (connectionId) => {
    if (!connections || !workflowStore || !findTaskById || !findStageById) {
      console.error('useConnection: 缺少必要的上下文参数')
      return { success: false, filteredConnections: connections?.value || connections }
    }

    // 在删除前获取连接信息，以便后续检查时间
    const connectionsArray = connections.value || connections
    const connection = connectionsArray.find(c => c.id === connectionId)
    const fromElement = connection ? { id: connection.from.elementId, type: connection.from.elementType } : null
    const toElement = connection ? { id: connection.to.elementId, type: connection.to.elementType } : null

    const result = removeSingleConnection(
      connectionId,
      connectionsArray,
      findTaskById,
      findStageById,
      workflowStore
    )

    if (result.success) {
      // 更新连接数组（如果是 ref）
      if (connections.value) {
        connections.value = result.filteredConnections
        workflowStore.setConnections(connections.value)
      } else {
        // 如果不是 ref，直接更新
        connections.splice(0, connections.length, ...result.filteredConnections)
      }
      
      // 删除连接后，检查相关任务的时间问题
      if (fromElement && fromElement.type === 'task') {
        updateTaskAndRelatedTasksTimeIssueFlags(fromElement.id, findTaskById, workflowStore, workflowData)
      }
      if (toElement && toElement.type === 'task') {
        updateTaskAndRelatedTasksTimeIssueFlags(toElement.id, findTaskById, workflowStore, workflowData)
      }
      
      // 删除阶段连接后，需要先更新阶段的时间，然后再更新阶段的时间异常标记
      const { updateStageTime } = useStageTime()
      if (fromElement && fromElement.type === 'stage') {
        // 先更新阶段的时间（重新计算阶段内所有任务的时间范围）
        // 直接使用传入的 workflowData，而不是通过 workflowStore
        const workflowDataValue = workflowData?.value
        if (workflowDataValue && workflowDataValue.stages) {
          const stage = workflowDataValue.stages.find(s => s.id === fromElement.id)
          if (stage) {
            const updatedStage = updateStageTime(stage)
            // 使用 Object.assign 确保响应式更新
            Object.assign(stage, {
              startTime: updatedStage.startTime,
              endTime: updatedStage.endTime,
              duration: updatedStage.duration
            })
          }
        }
        // 然后更新阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(fromElement.id, findStageById, workflowStore, workflowData)
        await nextTick()
      }
      if (toElement && toElement.type === 'stage') {
        // 先更新阶段的时间（重新计算阶段内所有任务的时间范围）
        // 直接使用传入的 workflowData，而不是通过 workflowStore
        const workflowDataValue = workflowData?.value
        if (workflowDataValue && workflowDataValue.stages) {
          const stage = workflowDataValue.stages.find(s => s.id === toElement.id)
          if (stage) {
            const updatedStage = updateStageTime(stage)
            // 使用 Object.assign 确保响应式更新
            Object.assign(stage, {
              startTime: updatedStage.startTime,
              endTime: updatedStage.endTime,
              duration: updatedStage.duration
            })
          }
        }
        // 然后更新阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(toElement.id, findStageById, workflowStore, workflowData)
        await nextTick()
      }
      
      // 清理可能存在的无效关系数据（任务successorTasks/predecessorTasks中包含阶段ID）
      cleanupInvalidTaskRelations(findTaskById, findStageById, workflowStore)
    }

    return result
  }

  /**
   * 初始化连接（从工作流数据构建连接数组）
   * @param {Object} workflow - 工作流数据
   * @param {Array} unassignedTasksArray - 阶段外任务数组
   * @returns {Array} 初始化的连接数组
   */
  const initConnectionsFromWorkflow = (workflow, unassignedTasksArray = []) => {
    const connectionsRef = connections?.value ? connections : { value: [] }
    const result = initConnections(workflow, connectionsRef, workflowStore, unassignedTasksArray)
    
    // 初始化连接后，清理可能存在的无效关系数据（任务successorTasks/predecessorTasks中包含阶段ID）
    if (findTaskById && findStageById && workflowStore) {
      cleanupInvalidTaskRelations(findTaskById, findStageById, workflowStore)
    }
    
    return result
  }

  /**
   * 处理连接开始（对外接口）
   */
  const handleConnectionStart = (data) => {
    handleConnectionStartInternal(data)
  }

  /**
   * 处理连接移动（对外接口）
   */
  const handleConnectionMove = (moveData) => {
    handleConnectionMoveInternal(moveData)
  }

  /**
   * 处理连接取消（对外接口）
   */
  const handleConnectionCancel = () => {
    handleConnectionCancelInternal()
  }

  /**
   * 处理连接面板结束（对外接口）
   */
  const handleConnectionPanelEnd = (data) => {
    handleConnectionPanelEndInternal(data)
  }

  /**
   * 处理连接选择（对外接口）
   */
  const handleConnectionSelect = (connectionId, selectedConnectionId, selectedStageId, selectedTaskId) => {
    if (selectedConnectionId) selectedConnectionId.value = connectionId
    if (selectedStageId) selectedStageId.value = null
    if (selectedTaskId) selectedTaskId.value = null
    if (workflowStore) workflowStore.clearSelection()
  }

  /**
   * 处理连接删除（带确认对话框）
   */
  const handleConnectionDelete = async (connectionId, selectedConnectionId) => {
    if (!connectionId) return

    try {
      const { ElMessageBox } = await import('element-plus')
      await ElMessageBox.confirm('确定要删除这条连接线吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      const result = await deleteConnection(connectionId)
      if (result.success) {
        if (selectedConnectionId) selectedConnectionId.value = null
        const { ElMessage } = await import('element-plus')
        ElMessage.success('连接线已删除')
      } else {
        const { ElMessage } = await import('element-plus')
        ElMessage.error('删除连接线失败')
      }
    } catch {
      // 用户取消
    }
  }

  /**
   * 清除任务的所有连接关系（对外接口）
   */
  const removeAllTaskConnectionsWrapper = (taskId) => {
    if (!connections || !findTaskById) {
      console.error('useConnection: 缺少必要的上下文参数')
      return 0
    }

    const connectionsArray = connections.value || connections
    const result = removeAllTaskConnections(taskId, connectionsArray, findTaskById)
    
    // 更新连接数组
    if (connections.value) {
      connections.value = result.filteredConnections
      if (workflowStore) {
        workflowStore.setConnections(connections.value)
      }
    } else {
      connections.splice(0, connections.length, ...result.filteredConnections)
    }
    
    return result.removedCount
  }

  // 返回所有对外接口
  return {
    // 核心功能
    createConnection,
    deleteConnection,
    initConnectionsFromWorkflow,
    buildConnectionsFromWorkflow,
    
    // 交互处理
    isConnecting,
    connectionStart: connectionStartRef, // 返回内部的 connectionStartRef
    previewConnectionPoint,
    connectingTargetElement,
    handleConnectionStart,
    handleConnectionMove,
    handleConnectionCancel,
    handleConnectionPanelEnd,
    handleConnectionSelect,
    handleConnectionDelete,
    
    // 管理功能
    removeAllTaskConnections: removeAllTaskConnectionsWrapper,
    removeSingleConnection,
    findConnectionByTaskIds,
    applyUpdatedRelations,
    cleanupInvalidTaskRelations: () => cleanupInvalidTaskRelations(findTaskById, findStageById, workflowStore),
    
    // 验证功能
    validateConnection,
    detectCycles,
    
    // 渲染功能
    getElementConnectionPoint,
    getConnectionPoints,
    calculateBezierPath,
    previewConnection,
    
    // 工具功能
    normalizeId,
    idsEqual,
    generateConnectionId,
    
    // 日志功能
    logConnectionCreation,
    logConnectionFailure,
    collectElementInfo,
    setConnectionLoggingEnabled
  }
}

// 导出子模块（供特殊需求使用）
export { useConnectionValidation } from './validation/useConnectionValidation'
export { useCycleDetection } from './validation/useCycleDetection'
export { useConnectionCreator } from './creation/useConnectionCreator'
export { useConnectionBuilder } from './creation/useConnectionBuilder'
export { useConnectionManager } from './data/useConnectionManager'
export { useConnectionHandlers } from './interaction/useConnectionHandlers'
export { usePreviewConnection } from './interaction/usePreviewConnection'
export { useConnectionInitializer } from './utils/useConnectionInitializer'
export { useConnectionLogger, setConnectionLoggingEnabled } from './utils/useConnectionLogger'
export { useConnectionLine } from './rendering/useConnectionLine'
export { useConnectionUtils } from './utils/useConnectionUtils'

