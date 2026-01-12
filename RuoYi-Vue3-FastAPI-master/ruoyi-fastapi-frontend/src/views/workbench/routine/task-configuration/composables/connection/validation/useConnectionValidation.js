// composables/connection/validation/useConnectionValidation.js
// 统一的连接验证入口，聚合所有验证逻辑

import { shouldSkipValidation } from '../config/testConfig'
import { useCycleDetection } from './useCycleDetection'

/**
 * 统一的连接验证 composable
 * 聚合所有验证逻辑，统一管理验证开关
 */
export const useConnectionValidation = () => {
  const { validateConnection: validateCycle } = useCycleDetection()

  /**
   * 规范化ID为数字类型
   */
  const normalizeId = (id) => {
    if (id == null) return null
    const num = Number(id)
    return Number.isNaN(num) ? id : num
  }

  /**
   * 比较两个ID是否相等（支持数字和字符串）
   */
  const idsEqual = (id1, id2) => {
    if (id1 == null || id2 == null) return false
    return String(id1) === String(id2)
  }

  /**
   * 统一的连接验证入口
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @param {Array} connections - 现有连接数组
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   * @returns {Object} { valid: boolean, message?: string, reason?: string }
   */
  const validateConnection = (
    fromElement,
    toElement,
    connections,
    findTaskById,
    findStageById
  ) => {
    const skipValidation = shouldSkipValidation()

    // 如果关闭了前端验证，直接返回成功
    if (skipValidation) {
      return { valid: true }
    }

    // 1. 检查自连接（任务 / 阶段都不允许与自身连接）
    const normalizedFromId = normalizeId(fromElement?.id)
    const normalizedToId = normalizeId(toElement?.id)
    const fromType = fromElement?.type
    const toType = toElement?.type

    if (idsEqual(normalizedFromId, normalizedToId) && fromType === toType) {
      let reason = '不能连接自身'
      if (fromType === 'task') {
        reason = '任务不能与自身建立连接'
      } else if (fromType === 'stage') {
        reason = '阶段不能与自身建立连接'
      }
      return {
        valid: false,
        message: reason,
        reason: 'self_connection'
      }
    }

    // 2. 检查类型是否匹配（只能同类型连接）
    if (fromType !== toType) {
      return {
        valid: false,
        message: '只能连接相同类型的元素（任务与任务，阶段与阶段）',
        reason: 'type_mismatch'
      }
    }

    // 3. 检查任务连接限制（任务必须在阶段内，且不能跨阶段连接）
    if (fromType === 'task' && toType === 'task') {
      const fromTaskInfo = findTaskById?.(fromElement.id)
      const toTaskInfo = findTaskById?.(toElement.id)

      // 检查源任务是否在阶段外
      if (!fromTaskInfo || fromTaskInfo.isUnassigned) {
        return {
          valid: false,
          message: '阶段外的任务不允许建立连接关系',
          reason: 'unassigned_task_from'
        }
      }

      // 检查目标任务是否在阶段外
      if (!toTaskInfo || toTaskInfo.isUnassigned) {
        return {
          valid: false,
          message: '阶段外的任务不允许建立连接关系',
          reason: 'unassigned_task_to'
        }
      }

      // 检查是否跨阶段连接（两个任务必须在同一个阶段内）
      // 使用 taskInfo.stage?.id 而不是 task.stageId，因为 stage 是通过 findTaskById 找到的实际阶段
      // 这样可以确保即使 task.stageId 还没有更新，也能正确判断任务所在的阶段
      const fromStageId = normalizeId(fromTaskInfo.stage?.id ?? fromTaskInfo.task?.stageId)
      const toStageId = normalizeId(toTaskInfo.stage?.id ?? toTaskInfo.task?.stageId)

      if (fromStageId != null && toStageId != null && !idsEqual(fromStageId, toStageId)) {
        return {
          valid: false,
          message: '不允许跨阶段的任务连接',
          reason: 'cross_stage_connection'
        }
      }

      // 检查编辑限制：如果目标任务不可编辑，这是前置关系（从其他任务连接到它），禁止
      if (toTaskInfo.task && toTaskInfo.task.isEditable === false) {
        return {
          valid: false,
          message: '不允许编辑已生成任务的前置关系',
          reason: 'uneditable_predecessor'
        }
      }

      // 检查编辑限制：如果源任务不可编辑，且目标任务也不可编辑，禁止（后置关系只能添加未生成任务）
      if (fromTaskInfo.task && fromTaskInfo.task.isEditable === false) {
        if (toTaskInfo.task && toTaskInfo.task.isEditable === false) {
          return {
            valid: false,
            message: '已生成的任务只能添加未生成的任务作为后置',
            reason: 'uneditable_successor'
          }
        }
      }
    }

    // 4. 检查阶段连接限制（类似任务的限制）
    if (fromType === 'stage' && toType === 'stage') {
      const fromStage = findStageById?.(fromElement.id)
      const toStage = findStageById?.(toElement.id)

      // 检查编辑限制：如果目标阶段不可编辑，这是前置关系，禁止
      if (toStage && toStage.isEditable === false) {
        return {
          valid: false,
          message: '不允许编辑已生成阶段的前置关系',
          reason: 'uneditable_predecessor_stage'
        }
      }

      // 检查编辑限制：如果源阶段不可编辑，且目标阶段也不可编辑，禁止
      if (fromStage && fromStage.isEditable === false) {
        if (toStage && toStage.isEditable === false) {
          return {
            valid: false,
            message: '已生成的阶段只能添加未生成的阶段作为后置',
            reason: 'uneditable_successor_stage'
          }
        }
      }
    }

    // 5. 检查循环依赖（回环检测）
    const cycleValidation = validateCycle(fromElement, toElement, connections)
    if (!cycleValidation.valid) {
      return {
        valid: false,
        message: cycleValidation.message || '此连接会创建循环依赖，请检查任务/阶段的执行顺序',
        reason: 'cycle_detected'
      }
    }

    // 所有验证通过
    return { valid: true }
  }

  return {
    validateConnection
  }
}

