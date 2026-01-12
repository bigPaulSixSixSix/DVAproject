// composables/stage/useAbnormalStages.js
// 统一计算异常阶段列表

import { computed } from 'vue'
import { useStageTimeValidation } from './useStageTimeValidation'

/**
 * 统一计算异常阶段列表
 * 条件：
 *  - 时间冲突（hasTimeIssue === true）
 */
export const useAbnormalStages = (stagesSource) => {
  const { validateAllStagesTime, updateStageTimeIssueFlags } = useStageTimeValidation()

  const getSourceValue = (source) => {
    if (typeof source === 'function') {
      return source()
    }
    if (source && typeof source.value !== 'undefined') {
      return source.value
    }
    return source || []
  }

  const abnormalStages = computed(() => {
    const stages = getSourceValue(stagesSource) || []
    
    // 先更新所有阶段的时间异常标记
    const stagesWithFlags = updateStageTimeIssueFlags(stages)
    
    // 然后获取异常阶段列表
    const abnormalList = validateAllStagesTime(stagesWithFlags)
    
    return abnormalList
  })

  const abnormalStageCount = computed(() => abnormalStages.value.length)

  // 判断异常阶段的类型（阶段异常都是时间关系异常，所以都是 warning）
  const abnormalStageType = computed(() => {
    return 'warning'
  })

  return {
    abnormalStages,
    abnormalStageCount,
    abnormalStageType
  }
}

