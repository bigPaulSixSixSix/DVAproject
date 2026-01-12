export const useTaskValidation = () => {
  const validateTaskPosition = (task, stages) => {
    // 任务的位置已经是画布绝对坐标
    const taskRect = {
      x: task.position.x,
      y: task.position.y,
      width: 198, // 任务卡片固定宽度（调整为 198px，使得偏置 + 宽度 = 8的倍数）
      height: 100 // 任务卡片固定高度
    }
    
    // 检查任务是否在任何一个阶段内
    return stages.some(stage => {
      const stageRect = {
        x: stage.position.x,
        y: stage.position.y,
        width: stage.position.width || 300, // 默认值
        height: stage.position.height || 200 // 默认值
      }
      
      return isRectInsideRect(taskRect, stageRect)
    })
  }
  
  const isRectInsideRect = (inner, outer) => {
    return inner.x >= outer.x &&
           inner.y >= outer.y &&
           inner.x + inner.width <= outer.x + outer.width &&
           inner.y + inner.height <= outer.y + outer.height
  }
  
  const validateTaskInRealTime = (task, stages) => {
    const isValid = validateTaskPosition(task, stages)
    
    return {
      isValid,
      message: isValid ? null : '任务必须放置在阶段内'
    }
  }
  
  const getInvalidTasks = (tasks, stages) => {
    return tasks.filter(task => !validateTaskPosition(task, stages))
  }
  
  /**
   * 保存前验证（允许有阶段外任务时也能保存）
   * @param {Array} unassignedTasks - 未分配任务数组
   * @returns {Object} 验证结果 { valid: boolean, message?: string }
   */
  const validateBeforeSave = (unassignedTasks) => {
    // 允许有阶段外任务时也能保存，不再阻止保存
    // 如果有阶段外任务，可以给出提示，但不阻止保存
    if (unassignedTasks && unassignedTasks.length > 0) {
      // 可以选择性地给出提示，但不阻止保存
      // ElMessage.info(`存在 ${unassignedTasks.length} 个阶段外的任务，将一并保存`)
    }
    return { valid: true }
  }

  return {
    validateTaskPosition,
    validateTaskInRealTime,
    getInvalidTasks,
    validateBeforeSave
  }
}
