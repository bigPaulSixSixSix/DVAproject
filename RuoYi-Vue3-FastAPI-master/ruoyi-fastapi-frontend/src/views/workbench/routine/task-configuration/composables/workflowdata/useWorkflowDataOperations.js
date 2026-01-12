// composables/useWorkflowDataOperations.js
/**
 * 工作流数据操作辅助函数
 * 直接操作主数据源（workflowData.value.stages 和 unassignedTasks.value）
 * 替代 workflowStore 中的数据存储操作
 */

/**
 * 更新阶段
 * @param {Object} workflowData - workflowData ref
 * @param {string|number} stageId - 阶段ID
 * @param {Object} updates - 要更新的字段
 */
export const updateStageInWorkflowData = (workflowData, stageId, updates) => {
  if (!workflowData?.value?.stages) return
  
  const stageIdStr = String(stageId)
  const stage = workflowData.value.stages.find(s => String(s.id) === stageIdStr)
  if (stage) {
    Object.assign(stage, updates)
  }
}

/**
 * 更新任务（支持阶段内和阶段外的任务）
 * @param {Object} workflowData - workflowData ref
 * @param {Object} unassignedTasks - unassignedTasks ref
 * @param {string|number} taskId - 任务ID
 * @param {Object} updates - 要更新的字段
 */
export const updateTaskInWorkflowData = (workflowData, unassignedTasks, taskId, updates) => {
  const taskIdStr = String(taskId)
  
  // 先查找阶段内的任务
  if (workflowData?.value?.stages) {
    for (const stage of workflowData.value.stages) {
      if (stage.tasks && Array.isArray(stage.tasks)) {
        const task = stage.tasks.find(t => String(t.id) === taskIdStr)
        if (task) {
          Object.assign(task, updates)
          return
        }
      }
    }
  }
  
  // 如果没找到，查找阶段外的任务
  if (unassignedTasks?.value) {
    const task = unassignedTasks.value.find(t => String(t.id) === taskIdStr)
    if (task) {
      Object.assign(task, updates)
    }
  }
}

/**
 * 删除阶段
 * @param {Object} workflowData - workflowData ref
 * @param {string|number} stageId - 阶段ID
 */
export const removeStageFromWorkflowData = (workflowData, stageId) => {
  if (!workflowData?.value?.stages) return
  
  const stageIdStr = String(stageId)
  workflowData.value.stages = workflowData.value.stages.filter(s => String(s.id) !== stageIdStr)
}

/**
 * 删除任务（支持阶段内和阶段外的任务）
 * @param {Object} workflowData - workflowData ref
 * @param {Object} unassignedTasks - unassignedTasks ref
 * @param {string|number} taskId - 任务ID
 */
export const removeTaskFromWorkflowData = (workflowData, unassignedTasks, taskId) => {
  const taskIdStr = String(taskId)
  
  // 先查找阶段内的任务
  if (workflowData?.value?.stages) {
    for (const stage of workflowData.value.stages) {
      if (stage.tasks && Array.isArray(stage.tasks)) {
        const index = stage.tasks.findIndex(t => String(t.id) === taskIdStr)
        if (index !== -1) {
          stage.tasks.splice(index, 1)
          return
        }
      }
    }
  }
  
  // 如果没找到，查找阶段外的任务
  if (unassignedTasks?.value) {
    const index = unassignedTasks.value.findIndex(t => String(t.id) === taskIdStr)
    if (index !== -1) {
      unassignedTasks.value.splice(index, 1)
    }
  }
}

/**
 * 添加任务到阶段外
 * @param {Object} unassignedTasks - unassignedTasks ref
 * @param {Object} task - 任务对象
 */
export const addTaskToUnassigned = (unassignedTasks, task) => {
  if (!unassignedTasks?.value) {
    unassignedTasks.value = []
  }
  unassignedTasks.value.push(task)
}

/**
 * 添加连接
 * @param {Object} connections - connections ref
 * @param {Object} connection - 连接对象
 */
export const addConnectionToConnections = (connections, connection) => {
  if (!connections?.value) {
    connections.value = []
  }
  connections.value.push(connection)
}

