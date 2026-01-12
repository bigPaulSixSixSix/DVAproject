// composables/connection/creation/useConnectionCreator.js
// 连接创建逻辑：整合验证、构建、日志等

import { ElMessage } from 'element-plus'
import { useConnectionValidation } from '../validation/useConnectionValidation'
import { useConnectionBuilder } from './useConnectionBuilder'
import { useConnectionLogger } from '../utils/useConnectionLogger'
import { useConnectionUtils } from '../utils/useConnectionUtils'

export const useConnectionCreator = () => {
  const { validateConnection } = useConnectionValidation()
  const { buildConnection } = useConnectionBuilder()
  const { logConnectionCreation, logConnectionFailure, collectElementInfo } = useConnectionLogger()
  const { normalizeId, idsEqual } = useConnectionUtils()

  /**
   * 创建连接（完整流程：验证 -> 构建 -> 应用关系 -> 日志）
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @param {Object} context - 上下文对象
   * @param {Function} applyUpdatedRelations - 应用更新关系的函数（从 data 模块传入，避免循环依赖）
   * @returns {Object|null} 连接结果或 null
   */
  const createConnectionBetweenElements = (fromElement, toElement, context, applyUpdatedRelations) => {
    const {
      connections,
      connectionStart,
      findTaskById,
      findStageById,
      workflowStore
    } = context

    // 1. 根据起始连接点的位置确定连接方向（在验证之前确定，确保验证使用正确的方向）
    let finalFrom = fromElement
    let finalTo = toElement
    
    if (connectionStart?.position === 'left') {
      // 从左侧连接点开始，表示 to 是 from 的前置，即 to -> from
      // 所以交换 from 和 to
      finalFrom = toElement
      finalTo = fromElement
    }

    // 2. 统一验证（使用确定后的连接方向）
    const validation = validateConnection(
      finalFrom,
      finalTo,
      connections,
      findTaskById,
      findStageById
    )
    
    if (!validation.valid) {
      // 验证失败，显示错误消息并记录日志
      ElMessage.warning(validation.message)
      logConnectionFailure(finalFrom, finalTo, validation.message, findTaskById, findStageById)
      return null
    }
    
    // 3. 检查是否已存在同方向的连接（使用确定后的连接方向）
    const normalizedFromId = normalizeId(finalFrom?.id)
    const normalizedToId = normalizeId(finalTo?.id)
    const fromType = finalFrom?.type
    const toType = finalTo?.type

    const existingConnection = connections.find(conn =>
      conn.from.elementType === fromType &&
      conn.to.elementType === toType &&
      idsEqual(conn.from.elementId, normalizedFromId) &&
      idsEqual(conn.to.elementId, normalizedToId)
    )
    
    if (existingConnection) {
      const reason = '这两个元素之间已存在连接'
      ElMessage.warning(reason)
      logConnectionFailure(finalFrom, finalTo, reason, findTaskById, findStageById)
      return null
    }
    
    // 4. 从实际对象中获取现有的关系数据，确保关系数据能够正确累积
    if (finalFrom.type === 'task') {
      const fromTaskInfo = findTaskById(finalFrom.id)
      if (fromTaskInfo && fromTaskInfo.task) {
        finalFrom = {
          ...finalFrom,
          predecessorTasks: fromTaskInfo.task.predecessorTasks || [],
          successorTasks: fromTaskInfo.task.successorTasks || []
        }
      }
    } else if (finalFrom.type === 'stage') {
      const fromStage = findStageById(finalFrom.id)
      if (fromStage) {
        finalFrom = {
          ...finalFrom,
          predecessorStages: fromStage.predecessorStages || [],
          successorStages: fromStage.successorStages || []
        }
      }
    }
    
    if (finalTo.type === 'task') {
      const toTaskInfo = findTaskById(finalTo.id)
      if (toTaskInfo && toTaskInfo.task) {
        finalTo = {
          ...finalTo,
          predecessorTasks: toTaskInfo.task.predecessorTasks || [],
          successorTasks: toTaskInfo.task.successorTasks || []
        }
      }
    } else if (finalTo.type === 'stage') {
      const toStage = findStageById(finalTo.id)
      if (toStage) {
        finalTo = {
          ...finalTo,
          predecessorStages: toStage.predecessorStages || [],
          successorStages: toStage.successorStages || []
        }
      }
    }
    
    // 5. 构建连接对象
    const result = buildConnection(finalFrom, finalTo)
    
    if (!result) {
      return null
    }
    
    // 6. 添加到连接数组（主数据源）
    connections.push(result.connection)
    // 同时通过 workflowStore 添加（用于兼容性，会直接操作 connections ref）
    if (workflowStore && typeof workflowStore.addConnection === 'function') {
      workflowStore.addConnection(result.connection)
    }
    
    // 7. 应用更新后的关系（通过参数传入，避免循环依赖）
    // 注意：applyUpdatedRelations 必须从外部传入，由 useConnection.js 提供
    if (!applyUpdatedRelations) {
      console.error('useConnectionCreator: applyUpdatedRelations 函数未提供')
      return null
    }
    applyUpdatedRelations(result.updatedRelations, findTaskById, findStageById, workflowStore)
    
    // 8. 记录日志（使用确定后的连接方向）
    const fromInfo = collectElementInfo(finalFrom, finalFrom.type, findTaskById, findStageById)
    const toInfo = collectElementInfo(finalTo, finalTo.type, findTaskById, findStageById)
    
    logConnectionCreation(
      result.connection,
      fromInfo,
      toInfo,
      result.updatedRelations,
      connections.length
    )

    return result
  }

  return {
    createConnectionBetweenElements
  }
}

