// composables/stage/useStageTime.js
// 阶段时间计算和格式化

import { computed } from 'vue'

/**
 * 阶段时间相关的 composable
 */
export const useStageTime = () => {
  /**
   * 计算阶段时间范围（从所有任务中最早开始时间到最晚结束时间）
   * @param {Object} stage - 阶段对象
   * @returns {Object} 时间范围信息
   */
  const calculateStageTimeRange = (stage) => {
    if (!stage || !stage.tasks || stage.tasks.length === 0) {
      return {
        startTime: null,
        endTime: null,
        days: null,
        formattedStartTime: null,
        formattedEndTime: null,
        displayText: '-'
      }
    }
    
    // 分别找到最早的开始时间和最晚的结束时间
    let earliestStartTime = null
    let latestEndTime = null
    
    stage.tasks.forEach(task => {
      // 处理开始时间
      if (task.startTime) {
        const startDate = new Date(task.startTime)
        if (!earliestStartTime || startDate < earliestStartTime) {
          earliestStartTime = startDate
        }
      }
      
      // 处理结束时间
      if (task.endTime) {
        const endDate = new Date(task.endTime)
        if (!latestEndTime || endDate > latestEndTime) {
          latestEndTime = endDate
        }
      }
    })
    
    // 格式化时间
    const formattedStartTime = formatDate(earliestStartTime)
    const formattedEndTime = formatDate(latestEndTime)
    
    // 计算天数（包含首尾）
    const days = earliestStartTime && latestEndTime
      ? Math.floor((latestEndTime - earliestStartTime) / (1000 * 60 * 60 * 24)) + 1
      : null
    
    // 生成显示文本
    let displayText = '-'
    if (formattedStartTime && formattedEndTime && days !== null) {
      displayText = `${formattedStartTime}-${formattedEndTime} 共${days}天`
    } else if (formattedStartTime && formattedEndTime) {
      displayText = `${formattedStartTime}-${formattedEndTime}`
    }
    
    return {
      startTime: earliestStartTime,
      endTime: latestEndTime,
      days: days,
      formattedStartTime: formattedStartTime,
      formattedEndTime: formattedEndTime,
      displayText: displayText
    }
  }

  /**
   * 格式化时间为 YYYY/MM/DD
   * @param {Date|string} date - 日期对象或日期字符串
   * @returns {string|null} 格式化后的日期字符串
   */
  const formatDate = (date) => {
    if (!date) return null
    if (typeof date === 'string') {
      // 如果已经是 YYYY/MM/DD 格式，直接返回
      if (/^\d{4}\/\d{2}\/\d{2}$/.test(date)) {
        return date
      }
      // 如果是 YYYY-MM-DD 格式，转换为 YYYY/MM/DD
      if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return date.replace(/-/g, '/')
      }
    }
    const d = new Date(date)
    if (Number.isNaN(d.getTime())) {
      return null
    }
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}/${month}/${day}`
  }

  /**
   * 更新阶段的时间信息（实时计算并更新到 stage 对象）
   * @param {Object} stage - 阶段对象
   * @returns {Object} 更新后的阶段对象（不修改原对象）
   */
  const updateStageTime = (stage) => {
    const timeRange = calculateStageTimeRange(stage)
    return {
      ...stage,
      // 如果计算出的时间为 null，保持为 null（允许后端发送 null）
      startTime: timeRange.formattedStartTime || null,
      endTime: timeRange.formattedEndTime || null,
      duration: timeRange.days || null
    }
  }

  return {
    calculateStageTimeRange,
    formatDate,
    updateStageTime
  }
}

