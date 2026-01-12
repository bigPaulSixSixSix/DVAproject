// composables/useTaskDrag.js
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTaskDragSnapshot } from './useTaskDragSnapshot'
import { updateTaskAndRelatedTasksTimeIssueFlags } from './useTaskTimeValidation'
import { updateStageAndRelatedStagesTimeIssueFlags } from '../stage/useStageTimeValidation'
import { useStageTime } from '../stage/useStageTime'
import { useGridSnap } from '../canvas/useGridSnap'

const {
  restoreTaskSnapshot,
  clearTaskSnapshot
} = useTaskDragSnapshot()

const { snapToGrid } = useGridSnap()

const snapPosition = (position) => {
  if (!position) return position
  const snapped = snapToGrid(position) || {}
  return {
    ...position,
    x: snapped.x ?? position.x,
    y: snapped.y ?? position.y
  }
}

/**
 * 更新阶段时间异常标记的辅助函数
 * @param {Array<number|string>} stageIds - 需要更新的阶段ID数组
 * @param {Object} workflowDataRef - workflowData ref
 * @param {Object} workflowStore - workflowStore
 */
const updateStageTimeIssueFlagsForStages = (stageIds, workflowDataRef, workflowStore) => {
  // 使用传入的 workflowDataRef 或从 workflowStore 获取（与连接线保持一致）
  const workflowDataRefToUse = workflowDataRef || workflowStore?.workflowDataRef?.value
  if (workflowDataRefToUse && workflowDataRefToUse.value && workflowDataRefToUse.value.stages) {
    const findStageByIdForUpdate = (stageId) => {
      return workflowDataRefToUse.value.stages.find(s => String(s.id) === String(stageId)) || null
    }
    stageIds.forEach(stageId => {
      updateStageAndRelatedStagesTimeIssueFlags(stageId, findStageByIdForUpdate, workflowStore, workflowDataRefToUse)
    })
  }
}

export const useTaskDrag = () => {
  // 处理任务拖拽结束
  const handleTaskDragEnd = async (
    data,
    workflowData,
    unassignedTasksRef,
    findTaskById,
    findStageByPosition,
    removeAllTaskConnections,
    constrainTaskToStage,
    workflowStore,
    connectionsRef,
    findStageById,
    workflowDataRef = null
  ) => {
    if (!workflowData?.stages) return
    
    const { taskId, newPosition, isValid, targetStage: providedTargetStage } = data
    
    // 查找任务的当前位置（阶段内还是阶段外）
    const taskInfo = findTaskById(taskId, workflowData, unassignedTasksRef.value)
    if (!taskInfo) return
    
    // 检查已生成任务的限制：如果任务不可编辑，不允许移出原阶段
    if (taskInfo.task.isEditable === false && taskInfo.task.stageId != null) {
      // 计算目标阶段
      let targetStage = providedTargetStage
      if (!targetStage) {
        // 计算绝对坐标以查找目标阶段
        let absolutePosition
        if (providedTargetStage) {
          absolutePosition = {
            x: providedTargetStage.position.x + newPosition.x,
            y: providedTargetStage.position.y + newPosition.y + 60
          }
        } else {
          absolutePosition = newPosition
        }
        targetStage = findStageByPosition(absolutePosition, workflowData)
      }
      
      // 如果目标位置不在阶段内，或者目标阶段不是原阶段，禁止移动
      if (!targetStage || String(targetStage.id) !== String(taskInfo.task.stageId)) {
        // 禁止移动，直接返回（不显示任何提示）
        return
      }
    }
    
    const HEADER_HEIGHT = 60
    
    // 计算绝对坐标
    let absolutePosition
    if (providedTargetStage) {
      // 如果提供了 targetStage，说明 newPosition 是相对坐标（相对于 targetStage）
      absolutePosition = {
        x: providedTargetStage.position.x + newPosition.x,
        y: providedTargetStage.position.y + newPosition.y + HEADER_HEIGHT
      }
    } else {
      // 如果没有提供 targetStage，说明 newPosition 是绝对坐标
      absolutePosition = newPosition
    }
    // 确保最终写入的位置对齐到网格（整数）
    absolutePosition = snapPosition(absolutePosition)
    
    // 约束到画布边界（确保不超出左侧和上侧）
    absolutePosition = {
      x: Math.max(0, absolutePosition.x),
      y: Math.max(0, absolutePosition.y)
    }
    
    // 使用提供的 targetStage，如果没有提供则重新查找
    const targetStage = providedTargetStage || findStageByPosition(absolutePosition, workflowData)
    
    // 检查任务是否有连接关系（只检查 connections 数组，因为连接线是由 connections 数组来绘制的）
    // 注意：使用 connectionsRef.value 来获取最新的 connections 数组
    const hasConnections = () => {
      // 只检查 connections 数组中是否有与该任务相关的连接
      // 任务的 predecessorTasks/successorTasks 只是数据字段，不应该作为判断依据
      // 因为连接线是由 connections 数组来绘制的
      const currentConnections = connectionsRef.value || []
      if (Array.isArray(currentConnections) && currentConnections.length > 0) {
        const hasConnectionInArray = currentConnections.some(conn => 
          (String(conn.from.elementId) === String(taskId) && conn.from.elementType === 'task') ||
          (String(conn.to.elementId) === String(taskId) && conn.to.elementType === 'task')
        )
        if (hasConnectionInArray) return true
      }
      
      return false
    }
    
    // 情况1：任务从阶段内拖到阶段外
    if (!taskInfo.isUnassigned && !targetStage) {
      // 检查任务是否有连接关系（每次都要检查最新的连接关系）
      if (hasConnections()) {
        // 显示确认对话框
        try {
          await ElMessageBox.confirm(
            '将任务拖出阶段会取消所有连接关系，是否继续？',
            '确认操作',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        } catch {
          // 用户取消，不执行操作，恢复任务到初始状态
          restoreTaskSnapshot(data, workflowData, unassignedTasksRef, findTaskById, findStageById)
          return
        }
      }
      
      // 清除所有连接关系（无论是否有提示，都要清除）
      // 在删除连接前，先获取所有相关任务ID（前置和后置），以便后续检查时间
      const relatedTaskIds = new Set([taskId])
      if (taskInfo.task.predecessorTasks && Array.isArray(taskInfo.task.predecessorTasks)) {
        taskInfo.task.predecessorTasks.forEach(id => relatedTaskIds.add(id))
      }
      if (taskInfo.task.successorTasks && Array.isArray(taskInfo.task.successorTasks)) {
        taskInfo.task.successorTasks.forEach(id => relatedTaskIds.add(id))
      }
      
      removeAllTaskConnections(taskId)
      
      // 检查被拖拽任务及其相关任务的时间问题
      // 因为删除连接后，相关任务的时间约束可能发生变化
      if (workflowStore) {
        for (const id of relatedTaskIds) {
          await updateTaskAndRelatedTasksTimeIssueFlags(id, findTaskById, workflowStore)
        }
      }
      
      // 从阶段中移除任务
      const originalStage = taskInfo.stage
      originalStage.tasks = originalStage.tasks.filter(t => t.id !== taskId)
      
      // 更新原始阶段的时间（因为任务移出后，阶段时间可能变化）
      const { updateStageTime } = useStageTime()
      const updatedOriginalStage = updateStageTime(originalStage)
      Object.assign(originalStage, {
        startTime: updatedOriginalStage.startTime,
        endTime: updatedOriginalStage.endTime,
        duration: updatedOriginalStage.duration
      })
      
      // 更新原始阶段及其相关阶段的时间异常标记
      updateStageTimeIssueFlagsForStages([originalStage.id], workflowDataRef, workflowStore)
      
      // 添加到阶段外任务数组
      const task = { ...taskInfo.task }
      // 确保位置对齐到网格（整数）
      task.position = snapPosition(absolutePosition)
      task.stageId = null
      task.isValidPosition = false
      unassignedTasksRef.value.push(task)
      
      clearTaskSnapshot(data, taskInfo.task)
      return
    }
    
    // 情况2：任务从阶段外拖到阶段内
    if (taskInfo.isUnassigned && targetStage) {
      // 应用阶段约束
      const constrainedPosition = constrainTaskToStage(absolutePosition, targetStage)
      
      // 从阶段外任务数组中移除
      const taskIndex = unassignedTasksRef.value.findIndex(t => t.id === taskId)
      if (taskIndex !== -1) {
        const task = unassignedTasksRef.value[taskIndex]
        
        // 注意：不要清除连接关系，也不要自动建立连接
        // 因为连接关系已经在第一次拖出阶段时被清除了（需求1）
        // 拖回阶段内时，任务应该没有任何连接关系，需要手动重新建立（需求3）
        // 但是，需要确保任务本身的连接关系数组是空的
        // 同时，需要确保 connections 数组中没有与该任务相关的连接
        task.predecessorTasks = []
        task.successorTasks = []
        
        // 确保 connections 数组中没有与该任务相关的连接（双重保险）
        const currentConnections = connectionsRef.value || []
        const filteredConnections = currentConnections.filter(conn => 
          !((String(conn.from.elementId) === String(taskId) && conn.from.elementType === 'task') ||
            (String(conn.to.elementId) === String(taskId) && conn.to.elementType === 'task'))
        )
        connectionsRef.value = filteredConnections
        
        // 添加到目标阶段
        task.position = constrainedPosition
        task.stageId = targetStage.id
        task.isValidPosition = true
        
        if (!targetStage.tasks) {
          targetStage.tasks = []
        }
        targetStage.tasks.push(task)
        
        // 从阶段外任务数组中移除
        unassignedTasksRef.value.splice(taskIndex, 1)
        
        // 更新目标阶段的时间（因为任务移入后，阶段时间可能变化）
        const { updateStageTime } = useStageTime()
        const updatedTargetStage = updateStageTime(targetStage)
        Object.assign(targetStage, {
          startTime: updatedTargetStage.startTime,
          endTime: updatedTargetStage.endTime,
          duration: updatedTargetStage.duration
        })
        
        // 更新目标阶段及其相关阶段的时间异常标记
        updateStageTimeIssueFlagsForStages([targetStage.id], workflowDataRef, workflowStore)
        
        // 不再通过 workflowStore.addTask 重复添加阶段外任务
      }
      
      clearTaskSnapshot(data, taskInfo.task)
      return
    }
    
    // 规范化阶段ID
    const recordedStageId = data.originalStageId != null
      ? data.originalStageId
      : taskInfo.task?.stageId
    const normalizedRecordedStageId = recordedStageId != null ? String(recordedStageId) : null
    const normalizedTargetStageId = targetStage ? String(targetStage.id) : null
    
    // 情况3：任务在阶段内移动（仅当记录的阶段ID与目标阶段一致时）
    // 注意：需要检查任务当前实际所在的阶段，而不是只检查 originalStageId
    // 因为任务可能已经从其他阶段移回原阶段，此时需要清除跨阶段连接
    const currentStageId = taskInfo.stage ? String(taskInfo.stage.id) : null
    const isSameStageMove =
      !taskInfo.isUnassigned &&
      targetStage &&
      normalizedRecordedStageId &&
      normalizedTargetStageId &&
      normalizedRecordedStageId === normalizedTargetStageId
    
    if (isSameStageMove) {
      // 检查任务当前实际所在的阶段是否与目标阶段一致
      // 如果不一致，说明任务是从其他阶段移回的，需要清除跨阶段连接
      // 注意：这里需要在 clearCrossStageConnections 之后执行，但 clearCrossStageConnections 已经处理了跨阶段移动的情况
      // 所以这里只需要处理"同一阶段内移动"的情况，不需要再检查跨阶段连接
      
      // 确保位置对齐到网格（整数）
      const snappedPosition = snapPosition(absolutePosition)
      // 更新任务位置
      taskInfo.task.position = snappedPosition
      taskInfo.task.isValidPosition = isValid
      // 确保 stageId 正确
      taskInfo.task.stageId = targetStage.id
      
      workflowStore.updateTask(taskId, { position: snappedPosition, isValidPosition: isValid, stageId: targetStage.id })
      clearTaskSnapshot(data, taskInfo.task)
      return
    }
    
    // 情况4：任务在阶段外移动
    if (taskInfo.isUnassigned && !targetStage) {
      // 确保位置对齐到网格（整数）
      const snappedPosition = snapPosition(absolutePosition)
      // 更新任务位置
      taskInfo.task.position = snappedPosition
      taskInfo.task.isValidPosition = false
      clearTaskSnapshot(data, taskInfo.task)
      return
    }
    
    // 情况5：任务从一个阶段拖到另一个阶段
    // 跨阶段移动时，必须清除所有连接关系（因为不允许跨阶段连接）
    // 判断条件：任务原本在阶段内，目标也在阶段内，但任务的 stageId 和目标阶段ID不同
    // 注意：在 isFinal === false 时，任务可能已经被移动到新阶段（视觉上），但 stageId 可能还是原始阶段ID
    // 所以通过比较 taskInfo.task.stageId 和 targetStage.id 来判断是否跨阶段移动
    // 使用 data.originalStageId（在拖拽过程中记录的）或 taskInfo.task.stageId 作为原始阶段ID
    const originalStageId = normalizedRecordedStageId
    const isCrossStageMove = !taskInfo.isUnassigned && 
                             targetStage && 
                             originalStageId && 
                             normalizedTargetStageId && 
                             originalStageId !== normalizedTargetStageId
    
    if (isCrossStageMove) {
      // 注意：这里不再显示确认对话框，因为已经在 checkCrossStageConnections 中显示过了
      // 如果 checkCrossStageConnections 返回 true，说明用户已经确认，这里直接清除连接即可
      
      // 清除所有连接关系（无论是否有提示，都要清除）
      // 在删除连接前，先获取所有相关任务ID（前置和后置），以便后续检查时间
      const relatedTaskIds = new Set([taskId])
      if (taskInfo.task.predecessorTasks && Array.isArray(taskInfo.task.predecessorTasks)) {
        taskInfo.task.predecessorTasks.forEach(id => relatedTaskIds.add(id))
      }
      if (taskInfo.task.successorTasks && Array.isArray(taskInfo.task.successorTasks)) {
        taskInfo.task.successorTasks.forEach(id => relatedTaskIds.add(id))
      }
      
      removeAllTaskConnections(taskId)
      
      // 检查被拖拽任务及其相关任务的时间问题
      // 因为删除连接后，相关任务的时间约束可能发生变化
      if (workflowStore) {
        for (const id of relatedTaskIds) {
          await updateTaskAndRelatedTasksTimeIssueFlags(id, findTaskById, workflowStore)
        }
      }
      
      // 应用约束并转换坐标
      const constrainedPosition = constrainTaskToStage(absolutePosition, targetStage)
      
      // 找到原始阶段（使用 originalStageId，因为 taskInfo.stage 可能是目标阶段）
      const originalStage = findStageById ? findStageById(originalStageId, workflowData) : null
      
      // 从原始阶段移除任务（如果任务还在原始阶段中）
      if (originalStage && originalStage.tasks) {
        originalStage.tasks = originalStage.tasks.filter(t => String(t.id) !== String(taskId))
      }
      
      // 检查任务是否已经在目标阶段中（可能在拖拽过程中已经被添加）
      const existingTaskInTargetStage = targetStage.tasks?.find(t => String(t.id) === String(taskId))
      
      // 更新任务对象的 stageId（直接修改原对象，确保引用一致）
      // 如果任务已经在目标阶段中，也要更新目标阶段中的任务对象
      const taskToUpdate = existingTaskInTargetStage || taskInfo.task
      taskToUpdate.stageId = targetStage.id
      taskToUpdate.position = constrainedPosition
      taskToUpdate.isValidPosition = true
      // 清除任务的连接关系数组
      taskToUpdate.predecessorTasks = []
      taskToUpdate.successorTasks = []
      
      // 如果任务不在目标阶段中，添加到目标阶段
      if (!existingTaskInTargetStage) {
      if (!targetStage.tasks) {
        targetStage.tasks = []
      }
        targetStage.tasks.push(taskToUpdate)
      }
      
      // 更新原始阶段和目标阶段的时间（因为任务移出/移入后，阶段时间可能变化）
      const { updateStageTime } = useStageTime()
      
      // 更新原始阶段的时间
      if (originalStage) {
        const updatedOriginalStage = updateStageTime(originalStage)
        Object.assign(originalStage, {
          startTime: updatedOriginalStage.startTime,
          endTime: updatedOriginalStage.endTime,
          duration: updatedOriginalStage.duration
        })
      }
      
      // 更新目标阶段的时间
      const updatedTargetStage = updateStageTime(targetStage)
      Object.assign(targetStage, {
        startTime: updatedTargetStage.startTime,
        endTime: updatedTargetStage.endTime,
        duration: updatedTargetStage.duration
      })
      
      // 更新原始阶段和目标阶段及其相关阶段的时间异常标记
      const stageIdsToUpdate = originalStage ? [originalStage.id, targetStage.id] : [targetStage.id]
      updateStageTimeIssueFlagsForStages(stageIdsToUpdate, workflowDataRef, workflowStore)
      
      // 注意：workflowStore.updateTask 只更新 tasks.value（阶段外的任务），不更新 stage.tasks
      // 阶段内的任务已经通过直接修改 stage.tasks 数组更新了
      // 由于任务对象已经被直接修改，并且已经添加到 targetStage.tasks 中，所以 findTaskById 应该能正确找到更新后的任务
      clearTaskSnapshot(data, taskInfo.task)
    }
    
    // 没有阶段变化或已经处理完毕，清理初始状态
    clearTaskSnapshot(data, taskInfo.task)
  }

  return {
    handleTaskDragEnd
  }
}

