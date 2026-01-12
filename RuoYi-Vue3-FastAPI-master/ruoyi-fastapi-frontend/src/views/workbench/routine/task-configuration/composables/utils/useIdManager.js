// composables/useIdManager.js
export const useIdManager = () => {
  /**
   * 从工作流数据中提取所有已使用的ID（包括阶段和任务）
   * @param {Object} workflowData - 工作流数据
   * @param {Array} unassignedTasks - 阶段外的任务数组
   * @returns {Set<number>} 已使用的ID集合
   */
  const getAllUsedIds = (workflowData, unassignedTasks = []) => {
    const usedIds = new Set()
    
    // 收集阶段ID
    if (workflowData?.stages) {
      workflowData.stages.forEach(stage => {
        if (stage?.id != null && typeof stage.id === 'number') {
          usedIds.add(stage.id)
        }
        // 收集阶段内的任务ID
        if (stage?.tasks && Array.isArray(stage.tasks)) {
          stage.tasks.forEach(task => {
            if (task?.id != null && typeof task.id === 'number') {
              usedIds.add(task.id)
            }
          })
        }
      })
    }
    
    // 收集阶段外的任务ID
    if (Array.isArray(unassignedTasks)) {
      unassignedTasks.forEach(task => {
        if (task?.id != null && typeof task.id === 'number') {
          usedIds.add(task.id)
        }
      })
    }
    
    return usedIds
  }
  
  /**
   * 生成新的临时ID（负数，自减）
   * @param {Object} workflowData - 工作流数据
   * @param {Array} unassignedTasks - 阶段外的任务数组（可选）
   * @returns {number} 新的临时ID（负数，如 -1, -2, -3...）
   */
  const generateNewId = (workflowData, unassignedTasks = []) => {
    const usedIds = getAllUsedIds(workflowData, unassignedTasks)
    
    // 找出最小的负数ID（临时ID），如果没有则从-1开始
    let minTempId = 0
    const tempIds = Array.from(usedIds).filter(id => id < 0)
    if (tempIds.length > 0) {
      minTempId = Math.min(...tempIds)
    }
    
    // 返回最小临时ID - 1（更小的负数）
    return minTempId - 1
  }
  
  /**
   * 判断是否为临时ID（负数）
   * @param {number|string} id - 要判断的ID
   * @returns {boolean} 是否为临时ID
   */
  const isTempId = (id) => {
    if (id == null) return false
    const numId = Number(id)
    return !isNaN(numId) && numId < 0
  }
  
  // 创建阶段模型
  const createStageModel = (id, name, projectId = null) => {
    return {
      id: id, // 整数ID
      name: name,
      startTime: null,
      endTime: null,
      duration: 0,
      tasks: [],
      predecessorStages: [],
      successorStages: [],
      position: { x: 0, y: 0, width: 300, height: 200 },
      projectId: projectId, // 项目ID
      isEditable: true, // 新建阶段默认为可编辑（未生成状态）
      isNew: true, // 新建元素标记（现在所有新建的都是true）
      createdAt: new Date(),
      updatedAt: new Date()
    }
  }
  
  // 创建任务模型
  const createTaskModel = (id, name, stageId, projectId = null) => {
    return {
      id: id, // 整数ID
      name: name,
      description: '',
      startTime: null,
      duration: 1,
      endTime: null,
      jobNumber: null, // 负责人工号
      stageId: stageId,
      predecessorTasks: [],
      successorTasks: [],
      position: { x: 10, y: 50 },
      projectId: projectId, // 项目ID
      approvalType: 'sequential', // 审批类型：'sequential'（逐级审批）或 'specified'（指定编制审批）
      approvalNodes: [], // 审批节点：数组类型，存储编制ID（即使只有一个，也要存成数组）
      isEditable: true, // 新建任务默认为可编辑（未生成状态）
      isNew: true, // 新建元素标记（现在所有新建的都是true）
      createdAt: new Date(),
      updatedAt: new Date()
    }
  }
  
  return {
    generateNewId,
    generateTempId: generateNewId, // 保持向后兼容，但实际使用generateNewId
    isTempId,
    getAllUsedIds,
    createStageModel,
    createTaskModel
  }
}
