// composables/utils/useUtils.js
// 工具函数集合

/**
 * 去重ID数组
 * @param {Array} ids - ID数组
 * @returns {Array} 去重后的ID数组
 */
export const dedupeIds = (ids = []) => {
  if (!Array.isArray(ids)) return []
  const seen = new Set()
  const result = []
  ids.forEach(id => {
    const key = String(id)
    if (!seen.has(key)) {
      seen.add(key)
      result.push(id)
    }
  })
  return result
}

/**
 * 检查任务字段是否缺失（用于红色标识）
 * 检查字段是否为 falsy（null、undefined、空字符串等）
 * 
 * @param {Object} task - 任务对象
 * @param {string} fieldName - 字段名称
 * @returns {boolean} 字段是否缺失
 */
export const isTaskFieldMissing = (task, fieldName) => {
  if (!task) return false
  const value = task[fieldName]
  // 使用与 TaskCard.vue 中相同的逻辑：!value 会检查 null、undefined、空字符串、0、false 等
  // 对于必填字段（startTime、endTime、jobNumber），如果为 falsy 就认为是缺失
  return !value
}

