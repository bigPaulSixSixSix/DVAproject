// composables/useTaskDragEnd.js
// 封装任务拖拽结束处理的完整逻辑

import { useTaskDragHandler } from './useTaskDragHandler'
import { useTaskDrag } from './useTaskDrag'
import { useTaskDragSnapshot } from './useTaskDragSnapshot'
import { useDragDrop } from '../canvas/useDragDrop'

export const useTaskDragEnd = () => {
  const { handleTaskDragUpdate, checkCrossStageConnections, clearCrossStageConnections, finalizeTaskDragCleanup } = useTaskDragHandler()
  const { handleTaskDragEnd: dragTaskEnd } = useTaskDrag()
  const { constrainTaskToStage } = useDragDrop()
  const { hydrateDataFromSnapshot, restoreTaskSnapshot } = useTaskDragSnapshot()

  /**
   * 处理任务拖拽结束
   * @param {Object} data - 拖拽数据
   * @param {Object} context - 上下文对象，包含所有需要的依赖
   * @returns {Promise<void>}
   */
  const handleTaskDragEnd = async (data, context) => {
    const {
      findTaskById,
      findStageByPosition,
      clearPreviewTaskAndDragFlag,
      createOrUpdatePreviewTask,
      findPreviewTaskIndex,
      workflowData,
      unassignedTasksRef,
      removeAllTaskConnections,
      workflowStore,
      connectionsRef,
      findStageById,
      workflowDataRef: contextWorkflowDataRef
    } = context
    
    // 从 context 获取 workflowDataRef 或从 workflowStore 获取（与连接线保持一致）
    const workflowDataRef = contextWorkflowDataRef || workflowStore?.workflowDataRef?.value

    const snapshotInfo = findTaskById(data.taskId)
    hydrateDataFromSnapshot(data, snapshotInfo)

    // 只在最终确认时（isFinal === true）才触发确认对话框和最终处理
    // 拖拽过程中的更新（isFinal === false）只更新位置，不触发确认对话框
    if (data.isFinal === false) {
      handleTaskDragUpdate(
        data,
        findTaskById,
        findStageByPosition,
        clearPreviewTaskAndDragFlag,
        createOrUpdatePreviewTask,
        findPreviewTaskIndex,
        workflowData,
        unassignedTasksRef.value
      )
      return
    }

    // 最终确认：检查跨阶段连接关系
    const shouldContinue = await checkCrossStageConnections(
      data,
      findTaskById,
      findStageByPosition,
      workflowData,
      connectionsRef.value
    )
    
    if (!shouldContinue) {
      restoreTaskSnapshot(
        data,
        workflowData,
        unassignedTasksRef,
        findTaskById,
        findStageById
      )
      finalizeTaskDragCleanup(
        data,
        clearPreviewTaskAndDragFlag,
        findTaskById,
        unassignedTasksRef.value
      )
      return
    }
    
    // 清除跨阶段连接关系
    await clearCrossStageConnections(
      data,
      findTaskById,
      findStageByPosition,
      removeAllTaskConnections,
      workflowData,
      workflowStore
    )
    
    // 调用最终的拖拽结束处理
    // 传入 workflowDataRef（与连接线保持一致）
    await dragTaskEnd(
      data,
      workflowData,
      unassignedTasksRef,
      findTaskById,
      findStageByPosition,
      removeAllTaskConnections,
      constrainTaskToStage,
      workflowStore,
      connectionsRef,
      context.findStageById,
      workflowDataRef
    )
    
    finalizeTaskDragCleanup(
      data,
      clearPreviewTaskAndDragFlag,
      findTaskById,
      unassignedTasksRef.value
    )
  }

  const createTaskDragEndHandler = (context) => {
    return (data) => handleTaskDragEnd(data, context)
  }

  return {
    handleTaskDragEnd,
    createTaskDragEndHandler
  }
}

