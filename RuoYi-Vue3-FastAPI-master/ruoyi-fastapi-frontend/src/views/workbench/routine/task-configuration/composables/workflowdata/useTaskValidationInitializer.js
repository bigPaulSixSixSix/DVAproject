// composables/useTaskValidationInitializer.js
/**
 * 任务验证初始化器
 * 用于初始化任务的验证标记（位置验证、时间验证）
 */

// 任务位置验证常量
const HEADER_HEIGHT = 60
const TASK_WIDTH = 198
const TASK_HEIGHT = 100

/**
 * 验证任务位置是否在阶段内
 * @param {Object} task - 任务对象
 * @param {Object} stage - 阶段对象（如果任务在阶段内）
 * @returns {boolean} 位置是否有效
 */
const validateTaskPosition = (task, stage) => {
  if (!stage) {
    // 阶段外的任务：位置无效
    return false
  }
  
  // 阶段内的任务：验证位置
  // 注意：任务位置是绝对坐标，需要考虑阶段头部高度
  const relativeX = task.position.x - stage.position.x
  const relativeY = task.position.y - stage.position.y - HEADER_HEIGHT
  
  // 检查任务是否在阶段内容区内
  const stageContentWidth = stage.position.width || 300
  const stageContentHeight = (stage.position.height || 200) - HEADER_HEIGHT
  
  return relativeX >= 0 &&
         relativeY >= 0 &&
         relativeX + TASK_WIDTH <= stageContentWidth &&
         relativeY + TASK_HEIGHT <= stageContentHeight
}

/**
 * 初始化所有任务的位置验证标记
 * @param {Object} workflowData - 工作流数据
 * @param {Array} unassignedTasks - 阶段外的任务数组
 */
export const initializeTaskPositionValidation = (workflowData, unassignedTasks = []) => {
  const allTasksWithStage = []
  
  // 收集阶段内的任务
  if (workflowData?.stages) {
    workflowData.stages.forEach(stage => {
      if (stage.tasks) {
        stage.tasks.forEach(task => {
          allTasksWithStage.push({ task, stage })
        })
      }
    })
  }
  
  // 收集阶段外的任务
  if (unassignedTasks && Array.isArray(unassignedTasks)) {
    unassignedTasks.forEach(task => {
      allTasksWithStage.push({ task, stage: null })
    })
  }
  
  // 设置位置验证标记
  allTasksWithStage.forEach(({ task, stage }) => {
    task.isValidPosition = validateTaskPosition(task, stage)
  })
}

/**
 * 初始化所有任务的时间验证标记
 * @param {Array} taskIds - 任务ID数组
 * @param {Function} findTaskById - 查找任务的函数
 * @param {Object} workflowStore - 工作流store
 */
export const initializeTaskTimeValidation = async (taskIds, findTaskById, workflowStore) => {
  if (!taskIds || taskIds.length === 0) {
    return
  }
  
  const { updateMultipleTaskTimeIssueFlags } = await import('../task/useTaskTimeValidation')
  updateMultipleTaskTimeIssueFlags(taskIds, findTaskById, workflowStore)
}

/**
 * 收集所有任务ID和任务及其所属阶段
 * @param {Object} workflowData - 工作流数据
 * @param {Array} unassignedTasks - 阶段外的任务数组
 * @returns {Object} { allTaskIds, allTasksWithStage }
 */
export const collectAllTasks = (workflowData, unassignedTasks = []) => {
  const allTaskIds = []
  const allTasksWithStage = []
  
  // 收集阶段内的任务
  if (workflowData?.stages) {
    workflowData.stages.forEach(stage => {
      if (stage.tasks) {
        stage.tasks.forEach(task => {
          if (task.id) {
            allTaskIds.push(task.id)
            allTasksWithStage.push({ task, stage })
          }
        })
      }
    })
  }
  
  // 收集阶段外的任务
  if (unassignedTasks && Array.isArray(unassignedTasks)) {
    unassignedTasks.forEach(task => {
      if (task.id) {
        allTaskIds.push(task.id)
        allTasksWithStage.push({ task, stage: null })
      }
    })
  }
  
  return { allTaskIds, allTasksWithStage }
}

/**
 * 初始化所有任务的验证标记（位置验证、时间验证）
 * @param {Object} workflowData - 工作流数据
 * @param {Array} unassignedTasks - 阶段外的任务数组
 * @param {Function} findTaskById - 查找任务的函数
 * @param {Object} workflowStore - 工作流store
 */
export const initializeAllTaskValidation = async (
  workflowData,
  unassignedTasks = [],
  findTaskById,
  workflowStore
) => {
  // 收集所有任务
  const { allTaskIds, allTasksWithStage } = collectAllTasks(workflowData, unassignedTasks)
  
  // 1. 位置验证：检查任务是否在阶段内（设置 isValidPosition 标记）
  allTasksWithStage.forEach(({ task, stage }) => {
    task.isValidPosition = validateTaskPosition(task, stage)
  })
  
  // 2. 时间验证：检查任务时间是否有问题（设置 hasTimeIssue 标记）
  if (allTaskIds.length > 0) {
    await initializeTaskTimeValidation(allTaskIds, findTaskById, workflowStore)
  }
}

