// composables/connection/utils/useConnectionUtils.js
// 连接相关的通用工具函数

export const useConnectionUtils = () => {
  /**
   * 规范化ID为数字类型（临时ID除外）
   */
  const normalizeId = (id) => {
    if (id == null) return null
    if (typeof id === 'string' && id.startsWith('temp_')) {
      return id // 临时ID保持字符串类型
    }
    const num = Number(id)
    return Number.isNaN(num) ? id : num
  }

  /**
   * 比较两个ID是否相等（统一为数字类型后比较）
   */
  const idsEqual = (id1, id2) => {
    if (id1 == null || id2 == null) return false
    const normalized1 = normalizeId(id1)
    const normalized2 = normalizeId(id2)
    return normalized1 === normalized2
  }

  /**
   * 生成连接ID
   */
  const generateConnectionId = () => {
    return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  return {
    normalizeId,
    idsEqual,
    generateConnectionId
  }
}

