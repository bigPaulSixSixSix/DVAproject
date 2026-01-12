// composables/connection/creation/useConnectionBuilder.js
// 连接对象构建：创建连接对象和更新关系数据

import { useConnectionUtils } from '../utils/useConnectionUtils'

export const useConnectionBuilder = () => {
  const { normalizeId, generateConnectionId } = useConnectionUtils()

  /**
   * 创建连接对象（不进行验证，验证已在上一层完成）
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @returns {Object} { connection, updatedRelations }
   */
  const buildConnection = (fromElement, toElement) => {
    // 规范化ID为数字类型（临时ID除外）
    const fromId = normalizeId(fromElement.id)
    const toId = normalizeId(toElement.id)
    
    // 创建连接对象
    const connection = {
      id: generateConnectionId(),
      from: { elementId: fromId, elementType: fromElement.type },
      to: { elementId: toId, elementType: toElement.type }
    }
    
    // 更新元素的前置/后置关系（保持原始ID类型）
    const updatedRelations = updateElementRelations(
      { ...fromElement, id: fromId },
      { ...toElement, id: toId }
    )
    
    return {
      connection,
      updatedRelations
    }
  }

  /**
   * 更新元素的前置/后置关系
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @returns {Object} 更新后的关系对象
   */
  const updateElementRelations = (fromElement, toElement) => {
    // 注意：这里只是更新关系数据，实际的元素更新需要在调用方处理
    // 因为我们需要确保响应式更新
    const fromId = normalizeId(fromElement.id)
    const toId = normalizeId(toElement.id)
    
    // 辅助函数：将数组中的ID去重并规范化
    const normalizeIds = (ids) => {
      if (!Array.isArray(ids)) return []
      // 规范化每个ID，然后使用 Set 去重
      const normalized = ids.map(id => normalizeId(id)).filter(id => id != null)
      return [...new Set(normalized)]
    }
    
    // 重要：只有当 fromElement 和 toElement 类型相同时，才更新关系数据
    // 防止错误地将阶段ID添加到任务的successorTasks中，或将任务ID添加到阶段的successorStages中
    const isSameType = fromElement.type === toElement.type
    
    return {
      fromElement: {
        ...fromElement,
        id: fromId,
        // 只有当类型相同时才更新关系
        successorTasks: (fromElement.type === 'task' && isSameType)
          ? normalizeIds([...(fromElement.successorTasks || []), toId])
          : fromElement.successorTasks,
        successorStages: (fromElement.type === 'stage' && isSameType)
          ? normalizeIds([...(fromElement.successorStages || []), toId])
          : fromElement.successorStages
      },
      toElement: {
        ...toElement,
        id: toId,
        // 只有当类型相同时才更新关系
        predecessorTasks: (toElement.type === 'task' && isSameType)
          ? normalizeIds([...(toElement.predecessorTasks || []), fromId])
          : toElement.predecessorTasks,
        predecessorStages: (toElement.type === 'stage' && isSameType)
          ? normalizeIds([...(toElement.predecessorStages || []), fromId])
          : toElement.predecessorStages
      }
    }
  }

  return {
    buildConnection,
    updateElementRelations
  }
}

