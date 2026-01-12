// composables/task/useTaskTimeValidation.js
// 任务时间检查相关逻辑

/**
 * 检查任务时间是否有问题
 * @param {Object} task - 任务对象
 * @param {Function} findTaskById - 查找任务函数
 * @returns {boolean} 是否有时间问题
 */
export const checkTaskTimeIssue = (task, findTaskById) => {
  if (!task) return false

  // 如果任务没有时间信息，不属于时间问题（属于信息不完全，用红色表示）
  if (!task.startTime || !task.endTime) {
    return false
  }

  const taskStartTime = new Date(task.startTime)
  const taskEndTime = new Date(task.endTime)

  // 检查开始时间是否晚于结束时间（这是时间异常）
  const taskStartDate = new Date(taskStartTime)
  taskStartDate.setHours(0, 0, 0, 0)
  const taskEndDate = new Date(taskEndTime)
  taskEndDate.setHours(0, 0, 0, 0)
  
  if (taskStartDate > taskEndDate) {
    return true
  }

  // 检查前置任务约束：任务的起始时间应该 >= 所有前置任务中最晚的结束时间 + 1天
  if (task.predecessorTasks && Array.isArray(task.predecessorTasks) && task.predecessorTasks.length > 0) {
    let latestPredecessorEndTime = null

    for (const preTaskId of task.predecessorTasks) {
      const preTaskInfo = findTaskById(preTaskId)
      if (preTaskInfo && preTaskInfo.task && preTaskInfo.task.endTime) {
        const preEndTime = new Date(preTaskInfo.task.endTime)
        if (!latestPredecessorEndTime || preEndTime > latestPredecessorEndTime) {
          latestPredecessorEndTime = preEndTime
        }
      }
    }

    if (latestPredecessorEndTime) {
      // 计算最晚结束时间 + 1天（只比较日期部分）
      const minStartTime = new Date(latestPredecessorEndTime)
      minStartTime.setDate(minStartTime.getDate() + 1)
      // 重置时间部分为0，只比较日期
      minStartTime.setHours(0, 0, 0, 0)
      const taskStartDate = new Date(taskStartTime)
      taskStartDate.setHours(0, 0, 0, 0)

      // 如果任务的开始时间早于最小开始时间，则有问题
      if (taskStartDate < minStartTime) {
        return true
      }
    }
  }

  // 检查后置任务约束：任务的结束时间应该 <= 所有后置任务中最早的开始时间 - 1天
  if (task.successorTasks && Array.isArray(task.successorTasks) && task.successorTasks.length > 0) {
    let earliestSuccessorStartTime = null

    for (const sucTaskId of task.successorTasks) {
      const sucTaskInfo = findTaskById(sucTaskId)
      if (sucTaskInfo && sucTaskInfo.task && sucTaskInfo.task.startTime) {
        const sucStartTime = new Date(sucTaskInfo.task.startTime)
        if (!earliestSuccessorStartTime || sucStartTime < earliestSuccessorStartTime) {
          earliestSuccessorStartTime = sucStartTime
        }
      }
    }

    if (earliestSuccessorStartTime) {
      // 计算最早开始时间 - 1天（只比较日期部分）
      const maxEndTime = new Date(earliestSuccessorStartTime)
      maxEndTime.setDate(maxEndTime.getDate() - 1)
      // 重置时间部分为0，只比较日期
      maxEndTime.setHours(0, 0, 0, 0)
      const taskEndDate = new Date(taskEndTime)
      taskEndDate.setHours(0, 0, 0, 0)

      // 如果任务的结束时间晚于最大结束时间，则有问题
      if (taskEndDate > maxEndTime) {
        return true
      }
    }
  }

  return false
}

/**
 * 检查任务时间问题，返回具体哪个字段有问题
 * @param {Object} task - 任务对象
 * @param {Function} findTaskById - 查找任务函数
 * @returns {Object} { hasIssue: boolean, startTimeIssue: boolean, endTimeIssue: boolean, startTimeConflictTask: Object|null, endTimeConflictTask: Object|null }
 */
export const checkTaskTimeIssueDetails = (task, findTaskById) => {
  const result = {
    hasIssue: false,
    startTimeIssue: false,
    endTimeIssue: false,
    isStartAfterEnd: false, // 开始时间是否晚于结束时间
    startTimeConflictTask: null, // 与开始时间冲突的前置任务
    endTimeConflictTask: null // 与结束时间冲突的后置任务
  }

  if (!task) return result

  // 如果任务没有时间信息，不属于时间问题
  if (!task.startTime || !task.endTime) {
    return result
  }

  const taskStartTime = new Date(task.startTime)
  const taskEndTime = new Date(task.endTime)

  // 检查开始时间是否晚于结束时间（这是时间异常，两个字段都有问题）
  const taskStartDate = new Date(taskStartTime)
  taskStartDate.setHours(0, 0, 0, 0)
  const taskEndDate = new Date(taskEndTime)
  taskEndDate.setHours(0, 0, 0, 0)
  
  if (taskStartDate > taskEndDate) {
    result.hasIssue = true
    result.startTimeIssue = true
    result.endTimeIssue = true
    result.isStartAfterEnd = true
    return result
  }

  // 检查前置任务约束：任务的起始时间应该 >= 所有前置任务中最晚的结束时间 + 1天
  if (task.predecessorTasks && Array.isArray(task.predecessorTasks) && task.predecessorTasks.length > 0) {
    let latestPredecessorEndTime = null
    let latestPredecessorTask = null

    for (const preTaskId of task.predecessorTasks) {
      const preTaskInfo = findTaskById(preTaskId)
      if (preTaskInfo && preTaskInfo.task && preTaskInfo.task.endTime) {
        const preEndTime = new Date(preTaskInfo.task.endTime)
        if (!latestPredecessorEndTime || preEndTime > latestPredecessorEndTime) {
          latestPredecessorEndTime = preEndTime
          latestPredecessorTask = preTaskInfo.task
        }
      }
    }

    if (latestPredecessorEndTime) {
      const minStartTime = new Date(latestPredecessorEndTime)
      minStartTime.setDate(minStartTime.getDate() + 1)
      minStartTime.setHours(0, 0, 0, 0)
      const taskStartDate = new Date(taskStartTime)
      taskStartDate.setHours(0, 0, 0, 0)

      if (taskStartDate < minStartTime) {
        result.hasIssue = true
        result.startTimeIssue = true
        result.startTimeConflictTask = latestPredecessorTask
      }
    }
  }

  // 检查后置任务约束：任务的结束时间应该 <= 所有后置任务中最早的开始时间 - 1天
  if (task.successorTasks && Array.isArray(task.successorTasks) && task.successorTasks.length > 0) {
    let earliestSuccessorStartTime = null
    let earliestSuccessorTask = null

    for (const sucTaskId of task.successorTasks) {
      const sucTaskInfo = findTaskById(sucTaskId)
      if (sucTaskInfo && sucTaskInfo.task && sucTaskInfo.task.startTime) {
        const sucStartTime = new Date(sucTaskInfo.task.startTime)
        if (!earliestSuccessorStartTime || sucStartTime < earliestSuccessorStartTime) {
          earliestSuccessorStartTime = sucStartTime
          earliestSuccessorTask = sucTaskInfo.task
        }
      }
    }

    if (earliestSuccessorStartTime) {
      const maxEndTime = new Date(earliestSuccessorStartTime)
      maxEndTime.setDate(maxEndTime.getDate() - 1)
      maxEndTime.setHours(0, 0, 0, 0)
      const taskEndDate = new Date(taskEndTime)
      taskEndDate.setHours(0, 0, 0, 0)

      if (taskEndDate > maxEndTime) {
        result.hasIssue = true
        result.endTimeIssue = true
        result.endTimeConflictTask = earliestSuccessorTask
      }
    }
  }

  return result
}

/**
 * 更新任务的时间问题标记
 * @param {string|number} taskId - 任务ID
 * @param {Function} findTaskById - 查找任务函数
 * @param {Object} workflowStore - 工作流store
 */
export const updateTaskTimeIssueFlag = (taskId, findTaskById, workflowStore) => {
  const taskInfo = findTaskById(taskId)
  if (!taskInfo || !taskInfo.task) return

  const hasTimeIssue = checkTaskTimeIssue(taskInfo.task, findTaskById)
  
  // 更新任务对象上的标记（用于UI显示）
  taskInfo.task.hasTimeIssue = hasTimeIssue
  
  // 更新到 store（如果需要持久化）
  if (workflowStore) {
    workflowStore.updateTask(taskId, {
      hasTimeIssue
    })
  }
}

/**
 * 批量更新多个任务的时间问题标记
 * @param {Array<string|number>} taskIds - 任务ID数组
 * @param {Function} findTaskById - 查找任务函数
 * @param {Object} workflowStore - 工作流store
 */
export const updateMultipleTaskTimeIssueFlags = (taskIds, findTaskById, workflowStore) => {
  if (!Array.isArray(taskIds)) return
  
  taskIds.forEach(taskId => {
    updateTaskTimeIssueFlag(taskId, findTaskById, workflowStore)
  })
}

/**
 * 更新任务及其相关任务（前置和后置）的时间问题标记
 * 当修改一个任务的时间后，需要检查：
 * 1. 该任务本身
 * 2. 它的所有前置任务（因为该任务的开始时间可能影响前置任务的结束时间约束）
 * 3. 它的所有后置任务（因为该任务的结束时间可能影响后置任务的开始时间约束）
 * @param {string|number} taskId - 任务ID
 * @param {Function} findTaskById - 查找任务函数
 * @param {Object} workflowStore - 工作流store
 * @param {Object} workflowData - workflowData ref（可选，如果传入则用于更新阶段时间异常标记）
 */
export const updateTaskAndRelatedTasksTimeIssueFlags = async (taskId, findTaskById, workflowStore, workflowData = null) => {
  const taskInfo = findTaskById(taskId)
  if (!taskInfo || !taskInfo.task) return

  // 收集需要检查的任务ID（去重）
  const taskIdsToCheck = new Set([taskId])

  // 添加所有前置任务
  if (taskInfo.task.predecessorTasks && Array.isArray(taskInfo.task.predecessorTasks)) {
    taskInfo.task.predecessorTasks.forEach(preTaskId => {
      taskIdsToCheck.add(preTaskId)
    })
  }

  // 添加所有后置任务
  if (taskInfo.task.successorTasks && Array.isArray(taskInfo.task.successorTasks)) {
    taskInfo.task.successorTasks.forEach(sucTaskId => {
      taskIdsToCheck.add(sucTaskId)
    })
  }

  // 批量更新所有相关任务的时间检查标记
  updateMultipleTaskTimeIssueFlags(Array.from(taskIdsToCheck), findTaskById, workflowStore)
  
  // 更新相关阶段的时间异常标记（任务时间变化可能影响阶段时间）
  // 注意：如果传入了 workflowData，说明外部已经处理了阶段更新（如 useTaskEdit.js），这里跳过以避免重复调用
  // 如果没有传入 workflowData，尝试从 workflowStore 获取并更新阶段
  if (workflowStore && taskInfo && taskInfo.stage && !workflowData) {
    // 只有在没有传入 workflowData 的情况下才更新阶段（避免与外部调用重复）
    // 使用动态导入，避免循环依赖（因为 useStageTimeValidation 不依赖 useTaskTimeValidation）
    try {
      const { updateStageAndRelatedStagesTimeIssueFlags } = await import('../stage/useStageTimeValidation')
      // 尝试从 workflowStore 获取 workflowData
      if (workflowStore.workflowDataRef?.value) {
        // 创建 findStageById 函数（从 workflowStore 获取）
        const findStageById = (stageId) => {
          const workflowDataValue = workflowStore.workflowDataRef.value.value
          if (!workflowDataValue || !workflowDataValue.stages) return null
          return workflowDataValue.stages.find(s => s.id === stageId) || null
        }
        const workflowDataFromStore = workflowStore.workflowDataRef.value
        updateStageAndRelatedStagesTimeIssueFlags(taskInfo.stage.id, findStageById, workflowStore, workflowDataFromStore)
      }
    } catch (error) {
      // 如果导入失败，跳过阶段更新（避免不必要的错误）
      console.warn('Failed to import useStageTimeValidation:', error)
    }
    // 如果 workflowStore 中也没有 workflowData，则跳过阶段更新（避免不必要的警告）
  }
}

