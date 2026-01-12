/**
 * 时间工具函数
 */

/**
 * 计算剩余时间
 * @param {string} deadline - 截止时间，格式：YYYY-MM-DD HH:MM:SS
 * @returns {string} 剩余时间描述
 */
export function calculateRemainingTime(deadline) {
  if (!deadline) return ''
  
  const now = new Date()
  const deadlineDate = new Date(deadline.replace(/-/g, '/'))
  const diff = deadlineDate.getTime() - now.getTime()
  
  if (diff < 0) {
    // 已逾期
    const absDiff = Math.abs(diff)
    const hours = Math.floor(absDiff / (1000 * 60 * 60))
    const minutes = Math.floor((absDiff % (1000 * 60 * 60)) / (1000 * 60))
    
    if (hours < 24) {
      return `逾期${hours}小时${minutes}分`
    } else {
      const days = Math.floor(hours / 24)
      const remainingHours = hours % 24
      return `逾期${days}天${remainingHours}小时`
    }
  } else {
    // 未逾期
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    
    if (hours < 24) {
      return `剩余${hours}小时${minutes}分`
    } else {
      const days = Math.floor(hours / 24)
      const remainingHours = hours % 24
      return `剩余${days}天${remainingHours}小时`
    }
  }
}

/**
 * 格式化时间显示
 * @param {string} timeStr - 时间字符串，格式：YYYY-MM-DD HH:MM:SS
 * @param {boolean} showTime - 是否显示时分秒
 * @returns {string} 格式化后的时间
 */
export function formatTime(timeStr, showTime = true) {
  if (!timeStr) return ''
  if (showTime) {
    return timeStr
  } else {
    return timeStr.split(' ')[0]
  }
}
