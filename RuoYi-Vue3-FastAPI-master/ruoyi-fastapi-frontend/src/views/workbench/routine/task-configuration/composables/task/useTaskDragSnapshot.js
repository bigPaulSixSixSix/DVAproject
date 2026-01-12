// 统一管理任务拖拽过程中的快照记录、恢复与清理

const clearDataSnapshot = (data) => {
  if (!data) return
  delete data._initialStateCaptured
  delete data.originalStageId
  delete data.originalPosition
  delete data.originalIsUnassigned
}

const clearTaskSnapshotFields = (task) => {
  if (!task) return
  delete task._dragSnapshotCaptured
  delete task._originalStageId
  delete task._originalPosition
  delete task._originalIsUnassigned
}

const removePreviewTask = (taskId, unassignedTasksRef) => {
  if (!unassignedTasksRef?.value) return
  const idStr = String(taskId)
  const previewIndex = unassignedTasksRef.value.findIndex(
    t => String(t.id) === idStr && t._isPreview
  )
  if (previewIndex !== -1) {
    unassignedTasksRef.value.splice(previewIndex, 1)
  }
}

export const useTaskDragSnapshot = () => {
  /**
   * 捕获任务拖拽开始时的快照，写入 task 对象与 data
   */
  const captureTaskSnapshot = (taskInfo, dragData) => {
    if (!taskInfo?.task) return
    const task = taskInfo.task
    if (!task._dragSnapshotCaptured) {
      task._dragSnapshotCaptured = true
      task._originalStageId = taskInfo.stage ? taskInfo.stage.id : null
      task._originalPosition = task.position ? { ...task.position } : null
      task._originalIsUnassigned = Boolean(taskInfo.isUnassigned)
    }
    if (!dragData?._initialStateCaptured) {
      dragData.originalStageId = task._originalStageId
      dragData.originalPosition = task._originalPosition
      dragData.originalIsUnassigned = task._originalIsUnassigned
      dragData._initialStateCaptured = true
    }
  }
  
  /**
   * 将任务快照写回 dragData，确保后续逻辑能够获取原始阶段及坐标
   */
  const hydrateDataFromSnapshot = (dragData, taskInfo) => {
    if (!dragData || !taskInfo?.task) return
    const task = taskInfo.task
    if (task._originalStageId != null && dragData.originalStageId == null) {
      dragData.originalStageId = task._originalStageId
    }
    if (task._originalPosition && !dragData.originalPosition) {
      dragData.originalPosition = { ...task._originalPosition }
    }
    if (task._originalIsUnassigned != null && dragData.originalIsUnassigned == null) {
      dragData.originalIsUnassigned = task._originalIsUnassigned
    }
  }
  
  /**
   * 清理快照（task + dragData）
   */
  const clearTaskSnapshot = (dragData, task) => {
    clearDataSnapshot(dragData)
    clearTaskSnapshotFields(task)
  }
  
  /**
   * 恢复任务到拖拽开始前的状态
   */
  const restoreTaskSnapshot = (
    dragData,
    workflowData,
    unassignedTasksRef,
    findTaskById,
    findStageById
  ) => {
    const taskId = dragData?.taskId
    if (!taskId) return
    const taskInfo = findTaskById(taskId, workflowData, unassignedTasksRef.value)
    if (!taskInfo || !taskInfo.task) return
    
    const task = taskInfo.task
    const hasSnapshot = task._dragSnapshotCaptured || dragData._initialStateCaptured
    if (!hasSnapshot) return
    
    const idStr = String(taskId)
    
    removePreviewTask(taskId, unassignedTasksRef)
    
    if (taskInfo.stage?.tasks) {
      taskInfo.stage.tasks = taskInfo.stage.tasks.filter(t => String(t.id) !== idStr)
    }
    if (taskInfo.isUnassigned) {
      const idx = unassignedTasksRef.value.findIndex(t => String(t.id) === idStr)
      if (idx !== -1) {
        unassignedTasksRef.value.splice(idx, 1)
      }
    }
    
    const originalStageId = task._originalStageId ?? dragData.originalStageId ?? null
    const originalIsUnassigned = task._originalIsUnassigned ?? dragData.originalIsUnassigned ?? false
    const originalPosition = task._originalPosition ?? dragData.originalPosition ?? null
    
    if (originalIsUnassigned || originalStageId == null) {
      task.stageId = null
      task.isValidPosition = false
      if (originalPosition) {
        task.position = { ...originalPosition }
      }
      const exists = unassignedTasksRef.value.find(t => String(t.id) === idStr)
      if (!exists) {
        unassignedTasksRef.value.push(task)
      }
    } else {
      const originalStage = findStageById
        ? findStageById(originalStageId, workflowData)
        : null
      if (originalStage) {
        if (!originalStage.tasks) {
          originalStage.tasks = []
        }
        const exists = originalStage.tasks.find(t => String(t.id) === idStr)
        if (!exists) {
          originalStage.tasks.push(task)
        }
        task.stageId = originalStage.id
      } else {
        task.stageId = null
      }
      task.isValidPosition = true
      if (originalPosition) {
        task.position = { ...originalPosition }
      }
    }
    
    delete task._isDragging
    delete task._isDraggingOut
    clearTaskSnapshot(dragData, task)
  }
  
  return {
    captureTaskSnapshot,
    hydrateDataFromSnapshot,
    clearTaskSnapshot,
    restoreTaskSnapshot
  }
}


