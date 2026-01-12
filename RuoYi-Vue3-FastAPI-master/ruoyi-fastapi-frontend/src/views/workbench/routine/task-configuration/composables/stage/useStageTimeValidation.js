// composables/stage/useStageTimeValidation.js
// 阶段时间校验：检查阶段间的时间关系

import { useStageTime } from './useStageTime'

/**
 * 阶段时间校验 composable
 */
export const useStageTimeValidation = () => {
  const { calculateStageTimeRange } = useStageTime()

  /**
   * 检查阶段是否有时间异常（前置阶段的结束时间需要早于后置阶段的开始时间）
   * @param {Object} stage - 阶段对象
   * @param {Array} allStages - 所有阶段数组
   * @returns {Object} { hasTimeIssue: boolean, reasons: string[] }
   */
  const validateStageTime = (stage, allStages = []) => {
    if (!stage) {
      return { hasTimeIssue: false, reasons: [] }
    }

    const reasons = []
    
    // 计算当前阶段的时间范围
    const stageTimeRange = calculateStageTimeRange(stage)
    
    // 如果没有时间信息，不进行校验（由其他校验处理）
    if (!stageTimeRange.startTime || !stageTimeRange.endTime) {
      return { hasTimeIssue: false, reasons: [] }
    }

    // 辅助函数：只比较日期部分，忽略时间
    const compareDateOnly = (date1, date2) => {
      if (!date1 || !date2) return 0
      const d1 = new Date(date1)
      const d2 = new Date(date2)
      d1.setHours(0, 0, 0, 0)
      d2.setHours(0, 0, 0, 0)
      return d1.getTime() - d2.getTime()
    }

    // 检查前置阶段
    if (stage.predecessorStages && Array.isArray(stage.predecessorStages)) {
      stage.predecessorStages.forEach(preStageId => {
        const preStage = allStages.find(s => s.id === preStageId)
        if (preStage) {
          const preStageTimeRange = calculateStageTimeRange(preStage)
          if (preStageTimeRange.endTime && stageTimeRange.startTime) {
            // 前置阶段的结束时间应该早于当前阶段的开始时间（只比较日期部分）
            // 如果前置阶段结束日期 >= 当前阶段开始日期，则冲突
            if (compareDateOnly(preStageTimeRange.endTime, stageTimeRange.startTime) >= 0) {
              reasons.push('与前置阶段时间冲突')
            }
          }
        }
      })
    }

    // 检查后置阶段
    if (stage.successorStages && Array.isArray(stage.successorStages)) {
      stage.successorStages.forEach(sucStageId => {
        const sucStage = allStages.find(s => s.id === sucStageId)
        if (sucStage) {
          const sucStageTimeRange = calculateStageTimeRange(sucStage)
          if (stageTimeRange.endTime && sucStageTimeRange.startTime) {
            // 当前阶段的结束时间应该早于后置阶段的开始时间（只比较日期部分）
            // 如果当前阶段结束日期 >= 后置阶段开始日期，则冲突
            if (compareDateOnly(stageTimeRange.endTime, sucStageTimeRange.startTime) >= 0) {
              reasons.push('与后置阶段时间冲突')
            }
          }
        }
      })
    }

    return {
      hasTimeIssue: reasons.length > 0,
      reasons: reasons
    }
  }

  /**
   * 批量校验所有阶段的时间
   * @param {Array} stages - 阶段数组
   * @returns {Array} 异常阶段列表
   */
  const validateAllStagesTime = (stages = []) => {
    const abnormalStages = []
    
    stages.forEach(stage => {
      const validation = validateStageTime(stage, stages)
      if (validation.hasTimeIssue) {
        abnormalStages.push({
          id: stage.id,
          name: stage.name || '未命名',
          reasons: validation.reasons,
          stage: stage
        })
      }
    })
    
    return abnormalStages
  }

  /**
   * 更新阶段的时间异常标记
   * @param {Array} stages - 阶段数组
   * @returns {Array} 更新后的阶段数组（不修改原数组）
   */
  const updateStageTimeIssueFlags = (stages = []) => {
    return stages.map(stage => {
      const validation = validateStageTime(stage, stages)
      return {
        ...stage,
        hasTimeIssue: validation.hasTimeIssue
      }
    })
  }

  /**
   * 检查阶段是否有时间问题（类似 checkTaskTimeIssue）
   * @param {Object} stage - 阶段对象
   * @param {Array} allStages - 所有阶段数组
   * @returns {boolean} 是否有时间问题
   */
  const checkStageTimeIssue = (stage, allStages = []) => {
    const validation = validateStageTime(stage, allStages)
    return validation.hasTimeIssue
  }

  return {
    validateStageTime,
    validateAllStagesTime,
    updateStageTimeIssueFlags,
    checkStageTimeIssue
  }
}

/**
 * 检查阶段是否有时间问题（导出为独立函数，与 checkTaskTimeIssue 保持一致）
 * @param {Object} stage - 阶段对象
 * @param {Array} allStages - 所有阶段数组
 * @returns {boolean} 是否有时间问题
 */
export const checkStageTimeIssue = (stage, allStages = []) => {
  const validation = useStageTimeValidation()
  return validation.checkStageTimeIssue(stage, allStages)
}

/**
 * 更新阶段的时间问题标记（直接修改阶段对象，用于实时更新UI）
 * @param {string|number} stageId - 阶段ID
 * @param {Function} findStageById - 查找阶段函数
 * @param {Array} allStages - 所有阶段数组（用于校验阶段间关系）
 * @param {Object} workflowStore - 工作流store
 */
export const updateStageTimeIssueFlag = (stageId, findStageById, allStages, workflowStore) => {
  const stage = findStageById(stageId)
  if (!stage) {
    return
  }

  const hasTimeIssue = checkStageTimeIssue(stage, allStages)
  
  // 更新阶段对象上的标记（用于UI显示）
  stage.hasTimeIssue = hasTimeIssue
  
  // 更新到 store（如果需要持久化）
  if (workflowStore) {
    workflowStore.updateStage(stageId, {
      hasTimeIssue
    })
  }
}

/**
 * 批量更新多个阶段的时间问题标记
 * @param {Array<string|number>} stageIds - 阶段ID数组
 * @param {Function} findStageById - 查找阶段函数
 * @param {Array} allStages - 所有阶段数组（用于校验阶段间关系）
 * @param {Object} workflowStore - 工作流store
 */
export const updateMultipleStageTimeIssueFlags = (stageIds, findStageById, allStages, workflowStore) => {
  if (!Array.isArray(stageIds)) {
    return
  }
  
  stageIds.forEach(stageId => {
    updateStageTimeIssueFlag(stageId, findStageById, allStages, workflowStore)
  })
}

/**
 * 更新阶段及其相关阶段的时间异常标记
 * 当修改一个阶段的时间或连接关系后，需要检查：
 * 1. 该阶段本身
 * 2. 它的所有前置阶段（因为该阶段的开始时间可能影响前置阶段的结束时间约束）
 * 3. 它的所有后置阶段（因为该阶段的结束时间可能影响后置阶段的开始时间约束）
 * @param {string|number} stageId - 阶段ID
 * @param {Function} findStageById - 查找阶段函数（可选，如果不提供则从 workflowData 中获取）
 * @param {Object} workflowStore - 工作流store（用于更新 store）
 * @param {Object} workflowData - workflowData ref（主数据源，优先使用）
 */
export const updateStageAndRelatedStagesTimeIssueFlags = (stageId, findStageById, workflowStore, workflowData = null) => {
  // 优先使用传入的 workflowData，如果没有则尝试从 workflowStore 获取
  let workflowDataValue = null
  if (workflowData) {
    // 检查 workflowData 是否是 ref
    if (workflowData && typeof workflowData === 'object' && 'value' in workflowData) {
      workflowDataValue = workflowData.value
    } else {
      // 如果不是 ref，可能已经是值了，直接使用
      workflowDataValue = workflowData
    }
  } else if (workflowStore?.workflowDataRef?.value) {
    // 从 workflowStore 获取 workflowData ref，然后获取其值
    const workflowDataRef = workflowStore.workflowDataRef.value
    if (workflowDataRef && typeof workflowDataRef === 'object' && 'value' in workflowDataRef) {
      workflowDataValue = workflowDataRef.value
    } else {
      // 如果 workflowDataRef.value 不是 ref，可能已经是值了
      workflowDataValue = workflowDataRef
    }
  }
  
  if (!workflowDataValue || !workflowDataValue.stages) {
    // 静默失败，不输出警告（因为可能在某些场景下不需要更新阶段）
    return
  }
  
  const workflowDataFinal = workflowDataValue
  
  // 创建内部 findStageById 函数，确保直接访问响应式对象
  const internalFindStageById = (id) => {
    return workflowDataFinal.stages.find(s => String(s.id) === String(id)) || null
  }
  
  // 使用内部 findStageById 或传入的 findStageById
  const getStageById = findStageById || internalFindStageById
  const stage = getStageById(stageId)
  if (!stage) {
    return
  }
    
  // 收集需要检查的阶段ID（去重）
  const stageIdsToCheck = new Set([stageId])
    
  // 添加所有前置阶段
  if (stage.predecessorStages && Array.isArray(stage.predecessorStages)) {
    stage.predecessorStages.forEach(preStageId => {
      stageIdsToCheck.add(preStageId)
    })
  }
    
  // 添加所有后置阶段
  if (stage.successorStages && Array.isArray(stage.successorStages)) {
    stage.successorStages.forEach(sucStageId => {
      stageIdsToCheck.add(sucStageId)
    })
  }
    
  // 批量更新所有相关阶段的时间检查标记
  // 使用内部 findStageById 确保直接访问响应式对象
  // 需要传入所有阶段数组，因为校验阶段间关系需要所有阶段数据
  updateMultipleStageTimeIssueFlags(
    Array.from(stageIdsToCheck),
    internalFindStageById,
    workflowDataFinal.stages,
    workflowStore
  )
}

