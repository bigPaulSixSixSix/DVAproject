// composables/useTaskDragHandler.js
// 处理任务拖拽的完整流程，包括拖拽过程中的实时更新和最终确认

import { ElMessageBox } from 'element-plus'
import { useTaskDragSnapshot } from './useTaskDragSnapshot'
import { updateTaskAndRelatedTasksTimeIssueFlags } from './useTaskTimeValidation'
import { useGridSnap } from '../canvas/useGridSnap'

const { captureTaskSnapshot } = useTaskDragSnapshot()

export const useTaskDragHandler = () => {
  const { snapToGrid } = useGridSnap()
  /**
   * 处理任务拖拽过程中的实时更新（isFinal === false）
   * @param {Object} data - 拖拽数据
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageByPosition - 根据位置查找阶段函数
   * @param {Function} clearPreviewTaskAndDragFlag - 清除预览任务和拖拽标记函数
   * @param {Function} createOrUpdatePreviewTask - 创建或更新预览任务函数
   * @param {Function} findPreviewTaskIndex - 查找预览任务索引函数
   * @param {Object} workflowData - 工作流数据
   * @param {Object} unassignedTasks - 未分配任务数组
   */
  const handleTaskDragUpdate = (
    data,
    findTaskById,
    findStageByPosition,
    clearPreviewTaskAndDragFlag,
    createOrUpdatePreviewTask,
    findPreviewTaskIndex,
    workflowData,
    unassignedTasks
  ) => {
    const taskInfo = findTaskById(data.taskId)
    if (!taskInfo) {
      return
    }
    
    captureTaskSnapshot(taskInfo, data)
    
    // 检查已生成任务的限制：如果任务不可编辑，不允许移出原阶段
    if (taskInfo.task.isEditable === false && taskInfo.task.stageId != null) {
      // 如果目标位置不在阶段内，或者目标阶段不是原阶段，禁止移动
      if (!data.targetStage || String(data.targetStage.id) !== String(taskInfo.task.stageId)) {
        // 禁止移动，不更新位置，直接返回
        return
      }
    }
    
    const HEADER_HEIGHT = 60
    
    // 根据目标阶段更新任务坐标
    if (data.targetStage) {
      // 目标位置在阶段内：data.newPosition 是相对坐标（相对于目标阶段）
      let absolutePosition = {
        x: data.targetStage.position.x + data.newPosition.x,
        y: data.targetStage.position.y + data.newPosition.y + HEADER_HEIGHT
      }
      
      // 约束到画布边界（确保不超出左侧和上侧）
      absolutePosition = {
        x: Math.max(0, absolutePosition.x),
        y: Math.max(0, absolutePosition.y)
      }
      
      // 检查任务是否在不同阶段之间移动
      const currentStage = taskInfo.stage
      const isMovingBetweenStages = currentStage && currentStage.id !== data.targetStage.id
      
      // 如果任务在不同阶段之间移动，记录当前阶段ID到 data 中（用于最终确认时清除连接关系）
      // 注意：这里记录的是本次拖拽开始时的阶段，而不是 originalStageId（第一次拖拽时记录的）
      if (isMovingBetweenStages && !data._currentStageIdBeforeMove) {
        data._currentStageIdBeforeMove = currentStage.id
      }
      
      // 记录原始阶段ID（用于快照恢复）
      captureTaskSnapshot({ ...taskInfo, stage: currentStage }, data)
      
      // 确保 _isDragging 标记存在（在拖拽开始时已设置，这里确保它存在）
      // 这个标记用于禁用 transition，确保任务能实时跟随鼠标
      if (!taskInfo.task._isDragging) {
        taskInfo.task._isDragging = true
      }
      
      // 确保位置对齐到网格（整数）
      absolutePosition = snapToGrid(absolutePosition)
      
      // 如果任务在不同阶段之间移动，需要先从原阶段移除，再添加到目标阶段
      // 注意：在 isFinal === false 时，更新位置和视觉显示，同时更新 stageId 以确保连接验证能正确判断阶段归属
      // 最终的确认和清理工作由 useTaskDrag.js 在 isFinal === true 时处理
      if (isMovingBetweenStages) {
        // 更新任务的位置（用于视觉显示）
        taskInfo.task.position = { ...absolutePosition }
        // 更新 stageId，确保连接验证能正确判断任务所在的阶段
        taskInfo.task.stageId = data.targetStage.id
        taskInfo.task.isValidPosition = data.isValid
        
        // 清除预览任务和拖拽标记（在添加到目标阶段之前清除，确保任务能正确显示）
        clearPreviewTaskAndDragFlag(data.taskId, unassignedTasks, findTaskById)
        
        // 从原阶段移除任务（用于视觉显示）
        if (currentStage.tasks) {
          currentStage.tasks = currentStage.tasks.filter(t => t.id !== data.taskId)
        }
        // 添加到目标阶段（用于视觉显示）
        if (!data.targetStage.tasks) {
          data.targetStage.tasks = []
        }
        data.targetStage.tasks.push(taskInfo.task)
      } else {
        // 任务在同一个阶段内移动，直接更新位置
        // 先更新位置，确保位置更新是即时的
        taskInfo.task.position = { ...absolutePosition }
        taskInfo.task.isValidPosition = data.isValid
        
        // 清除预览任务和拖拽标记（如果任务从阶段外拖回阶段内）
        clearPreviewTaskAndDragFlag(data.taskId, unassignedTasks, findTaskById)
      }
      
      // 注意：_isDragging 标记在拖拽过程中保持，直到最终确认（isFinal === true）时才清除
      // 这样可以确保在整个拖拽过程中，transition 都被禁用，任务能实时跟随鼠标
    } else {
      // 目标位置在阶段外：data.newPosition 已经是绝对坐标
      if (taskInfo.isUnassigned) {
        // 如果任务原本就在阶段外，直接更新位置（不需要预览任务）
        // 约束到画布边界（确保不超出左侧和上侧）
        let constrainedPosition = {
          x: Math.max(0, data.newPosition.x),
          y: Math.max(0, data.newPosition.y)
        }
        // 确保位置对齐到网格（整数）
        constrainedPosition = snapToGrid(constrainedPosition)
        taskInfo.task.position = constrainedPosition
        taskInfo.task.isValidPosition = false
        
        // 清除预览任务（如果存在）
        const previewIndex = findPreviewTaskIndex(data.taskId, unassignedTasks)
        if (previewIndex !== -1) {
          unassignedTasks.splice(previewIndex, 1)
        }
      } else {
        // 如果任务原本在阶段内，标记为拖拽中（隐藏原始任务）
        if (!taskInfo.task._isDraggingOut) {
          taskInfo.task._isDraggingOut = true
        }
        
        // 约束到画布边界（确保不超出左侧和上侧）
        let constrainedPosition = {
          x: Math.max(0, data.newPosition.x),
          y: Math.max(0, data.newPosition.y)
        }
        // 确保位置对齐到网格（整数）
        constrainedPosition = snapToGrid(constrainedPosition)
        // 创建或更新预览任务（用于在阶段外显示）
        createOrUpdatePreviewTask(taskInfo, constrainedPosition, unassignedTasks)
      }
    }
  }

  /**
   * 处理任务拖拽最终确认前的连接关系检查（isFinal === true）
   * @param {Object} data - 拖拽数据
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageByPosition - 根据位置查找阶段函数
   * @param {Object} workflowData - 工作流数据
   * @param {Array} connections - 连接数组
   * @returns {Promise<boolean>} 是否继续执行（用户确认或无需确认）
   */
  const checkCrossStageConnections = async (
    data,
    findTaskById,
    findStageByPosition,
    workflowData,
    connections
  ) => {
    // 先清除预览任务和拖拽标记（确保清理干净）
    const finalTaskInfo = findTaskById(data.taskId)
    if (!finalTaskInfo) {
      return false
    }
    
    // 清除 _isDragging 标记（拖拽结束，恢复 transition）
    if (finalTaskInfo?.task?._isDragging) {
      delete finalTaskInfo.task._isDragging
    }
    
    // 检查任务是否跨阶段移动（在最终确认时）
    // 使用本次拖拽开始时的阶段ID（_currentStageIdBeforeMove），而不是 originalStageId
    // 因为 originalStageId 是第一次拖拽时记录的，而 _currentStageIdBeforeMove 是本次拖拽开始时的阶段
    const stageIdBeforeMove = data._currentStageIdBeforeMove 
      ? String(data._currentStageIdBeforeMove)
      : (data.originalStageId ? String(data.originalStageId) : (finalTaskInfo?.task?.stageId ? String(finalTaskInfo.task.stageId) : null))
    let targetStageId = null
    if (data.targetStage) {
      targetStageId = String(data.targetStage.id)
    } else if (data.newPosition) {
      // 如果没有提供 targetStage，根据位置查找目标阶段
      const targetStage = findStageByPosition(data.newPosition, workflowData)
      targetStageId = targetStage ? String(targetStage.id) : null
    }
    
    // 如果任务从一个阶段移动到另一个阶段，清除所有连接关系
    if (stageIdBeforeMove && targetStageId && stageIdBeforeMove !== targetStageId) {
      // 检查任务是否有连接关系
      const hasConnections = connections.some(conn => 
        (String(conn.from.elementId) === String(data.taskId) && conn.from.elementType === 'task') ||
        (String(conn.to.elementId) === String(data.taskId) && conn.to.elementType === 'task')
      )
      
      if (hasConnections) {
        // 显示确认对话框
        try {
          await ElMessageBox.confirm(
            '将任务移动到另一个阶段会取消所有连接关系，是否继续？',
            '确认操作',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          return true
        } catch {
          // 用户取消，不执行操作
          return false
        }
      }
    }
    
    return true
  }

  /**
   * 清除跨阶段移动任务的连接关系
   * @param {Object} data - 拖拽数据
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageByPosition - 根据位置查找阶段函数
   * @param {Function} removeAllTaskConnections - 清除任务连接函数
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   */
  const clearCrossStageConnections = async (
    data,
    findTaskById,
    findStageByPosition,
    removeAllTaskConnections,
    workflowData,
    workflowStore
  ) => {
    const finalTaskInfo = findTaskById(data.taskId)
    if (!finalTaskInfo) {
      return
    }
    
    // 检查任务是否跨阶段移动
    // 使用本次拖拽开始时的阶段ID（_currentStageIdBeforeMove），而不是 originalStageId
    // 因为 originalStageId 是第一次拖拽时记录的，而 _currentStageIdBeforeMove 是本次拖拽开始时的阶段
    // 注意：在 handleTaskDragUpdate 中，任务可能已经被移动到目标阶段，所以 finalTaskInfo.stage 可能是目标阶段
    const stageIdBeforeMove = data._currentStageIdBeforeMove 
      ? String(data._currentStageIdBeforeMove)
      : (finalTaskInfo.stage ? String(finalTaskInfo.stage.id) : null)
    let targetStageId = null
    if (data.targetStage) {
      targetStageId = String(data.targetStage.id)
    } else if (data.newPosition) {
      const targetStage = findStageByPosition(data.newPosition, workflowData)
      targetStageId = targetStage ? String(targetStage.id) : null
    }
    
    // 如果任务从一个阶段移动到另一个阶段，清除所有连接关系
    // 检查拖拽开始时的阶段和目标阶段是否不同
    if (stageIdBeforeMove && targetStageId && stageIdBeforeMove !== targetStageId) {
      // 在删除连接前，先获取所有相关任务ID（前置和后置），以便后续检查时间
      const relatedTaskIds = new Set([data.taskId])
      if (finalTaskInfo.task.predecessorTasks && Array.isArray(finalTaskInfo.task.predecessorTasks)) {
        finalTaskInfo.task.predecessorTasks.forEach(id => relatedTaskIds.add(id))
      }
      if (finalTaskInfo.task.successorTasks && Array.isArray(finalTaskInfo.task.successorTasks)) {
        finalTaskInfo.task.successorTasks.forEach(id => relatedTaskIds.add(id))
      }
      
      // 清除所有连接关系
      removeAllTaskConnections(data.taskId)
      
      // 清除任务的连接关系数组
      if (finalTaskInfo?.task) {
        finalTaskInfo.task.predecessorTasks = []
        finalTaskInfo.task.successorTasks = []
        workflowStore.updateTask(data.taskId, {
          predecessorTasks: [],
          successorTasks: []
        })
      }
      
      // 检查被拖拽任务及其相关任务的时间问题
      // 因为删除连接后，相关任务的时间约束可能发生变化
      if (workflowStore) {
        for (const id of relatedTaskIds) {
          await updateTaskAndRelatedTasksTimeIssueFlags(id, findTaskById, workflowStore)
        }
      }
    }
  }

  /**
   * 清理拖拽结束时的预览任务和标记
   * @param {Object} data - 拖拽数据
   * @param {Function} clearPreviewTaskAndDragFlag - 清除预览任务的方法
   * @param {Function} findTaskById - 查找任务方法
   * @param {Array} unassignedTasks - 未分配任务数组
   */
  const finalizeTaskDragCleanup = (
    data,
    clearPreviewTaskAndDragFlag,
    findTaskById,
    unassignedTasks
  ) => {
    if (!data?.taskId) return
    clearPreviewTaskAndDragFlag(data.taskId, unassignedTasks, findTaskById)
  }

  return {
    handleTaskDragUpdate,
    checkCrossStageConnections,
    clearCrossStageConnections,
    finalizeTaskDragCleanup
  }
}

