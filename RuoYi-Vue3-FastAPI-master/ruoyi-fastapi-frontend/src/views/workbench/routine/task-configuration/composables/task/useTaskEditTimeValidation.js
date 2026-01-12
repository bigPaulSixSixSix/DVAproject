// composables/task/useTaskEditTimeValidation.js
// 任务编辑对话框中的时间验证和警告消息逻辑

import { computed } from 'vue'
import { checkTaskTimeIssueDetails } from './useTaskTimeValidation'

/**
 * 任务编辑对话框中的时间验证 composable
 * 用于计算时间问题详情、警告消息等
 * 
 * @param {Object} options
 * @param {Object} options.currentEditingTask - 当前编辑的任务对象
 * @param {Object} options.form - 表单数据对象
 * @param {Function} options.findTaskById - 查找任务函数
 * @returns {Object} { timeIssueDetails, startTimeWarningMessage, endTimeWarningMessage, getTaskTimeIssueDetails, getDynamicRules }
 */
export const useTaskEditTimeValidation = ({ currentEditingTask, form, findTaskById }) => {
  // 获取当前编辑任务的时间问题详情（用于表单中的时间字段标黄）
  // 注意：需要创建一个临时任务对象，使用表单数据，但保留前置/后置任务关系
  const timeIssueDetails = computed(() => {
    if (!currentEditingTask.value || !findTaskById || !form.value) {
      return { hasIssue: false, startTimeIssue: false, endTimeIssue: false, isStartAfterEnd: false }
    }
    const taskInfo = findTaskById(currentEditingTask.value.id)
    if (!taskInfo || !taskInfo.task) {
      return { hasIssue: false, startTimeIssue: false, endTimeIssue: false, isStartAfterEnd: false }
    }
    // 创建一个临时任务对象，使用表单中的时间数据，但保留前置/后置任务关系
    const tempTask = {
      ...taskInfo.task,
      startTime: form.value.startTime,
      endTime: form.value.endTime,
      duration: form.value.duration
    }
    return checkTaskTimeIssueDetails(tempTask, findTaskById)
  })

  // 开始时间的警告消息
  const startTimeWarningMessage = computed(() => {
    const details = timeIssueDetails.value
    const hasStartTime = !!form.value?.startTime
    const hasEndTime = !!form.value?.endTime
    
    // 优先检查：开始时间是否晚于结束时间（只要两个时间都存在，就显示提示）
    // 这个检查的优先级最高，因为它是最基本的逻辑错误
    if (hasStartTime && hasEndTime && details.isStartAfterEnd) {
      return '开始时间不能晚于结束时间'
    }
    
    // 如果开始时间未选择，不显示冲突提示（让表单验证显示"请选择开始时间"）
    if (!hasStartTime) return ''
    
    // 如果有前置任务冲突，显示冲突提示
    // 注意：checkTaskTimeIssueDetails 已经确保在 isStartAfterEnd 为 true 时不会设置 startTimeIssue
    // 所以这里不需要再检查 !details.isStartAfterEnd
    if (details.startTimeIssue) {
      return '与前置任务的结束时间冲突'
    }
    return ''
  })

  // 结束时间的警告消息
  const endTimeWarningMessage = computed(() => {
    const details = timeIssueDetails.value
    const hasStartTime = !!form.value?.startTime
    const hasEndTime = !!form.value?.endTime
    
    // 优先检查：开始时间是否晚于结束时间（只要两个时间都存在，就显示提示）
    // 这个检查的优先级最高，因为它是最基本的逻辑错误
    if (hasStartTime && hasEndTime && details.isStartAfterEnd) {
      return '开始时间不能晚于结束时间'
    }
    
    // 如果结束时间未选择，检查是否有时间冲突
    if (!hasEndTime) {
      // 如果有时间冲突，显示冲突提示（优先级高于"请选择结束时间"）
      // 注意：checkTaskTimeIssueDetails 已经确保在 isStartAfterEnd 为 true 时不会设置 endTimeIssue
      if (details.endTimeIssue) {
        return '与后置任务的开始时间冲突'
      }
      // 如果没有时间冲突，返回空字符串，让表单验证显示"请选择结束时间"
      return ''
    }
    
    // 如果结束时间已选择，且有冲突，显示冲突提示
    // 注意：checkTaskTimeIssueDetails 已经确保在 isStartAfterEnd 为 true 时不会设置 endTimeIssue
    if (details.endTimeIssue) {
      return '与后置任务的开始时间冲突'
    }
    return ''
  })

  /**
   * 获取任务的时间问题详情（用于前后置任务列表）
   * 首先从任务模型中读取时间问题状态，然后再检查与当前任务的关系
   * 注意：使用表单数据（form.value）而不是原始任务数据，以便反映用户正在编辑的值
   * 
   * @param {Object} task - 要检查的任务对象
   * @param {boolean} isPredecessor - 是否为前置任务
   * @returns {Object} { hasIssue: boolean, startTimeIssue: boolean, endTimeIssue: boolean }
   */
  const getTaskTimeIssueDetails = (task, isPredecessor = false) => {
    if (!task || !findTaskById) {
      return { hasIssue: false, startTimeIssue: false, endTimeIssue: false }
    }
    
    // 首先从任务模型中读取时间问题状态（使用 checkTaskTimeIssueDetails）
    const taskTimeIssueDetails = checkTaskTimeIssueDetails(task, findTaskById)
    
    // 如果任务本身没有时间信息，直接返回
    if (!task.startTime || !task.endTime) {
      return taskTimeIssueDetails
    }
    
    // 然后检查与当前任务的关系（如果当前任务有时间信息）
    const currentStartTime = form.value?.startTime
    const currentEndTime = form.value?.endTime
    
    if (!currentStartTime || !currentEndTime) {
      // 如果当前任务没有时间信息，只返回任务本身的时间问题状态
      return taskTimeIssueDetails
    }
    
    // 合并任务本身的时间问题状态和与当前任务的关系问题
    const result = {
      hasIssue: taskTimeIssueDetails.hasIssue,
      startTimeIssue: taskTimeIssueDetails.startTimeIssue,
      endTimeIssue: taskTimeIssueDetails.endTimeIssue
    }
    
    if (isPredecessor) {
      // 前置任务：检查其结束时间是否晚于当前任务的开始时间-1天
      const currentStartDate = new Date(currentStartTime)
      currentStartDate.setHours(0, 0, 0, 0)
      const maxEndTime = new Date(currentStartDate)
      maxEndTime.setDate(maxEndTime.getDate() - 1)
      
      const taskEndTime = new Date(task.endTime)
      taskEndTime.setHours(0, 0, 0, 0)
      
      if (taskEndTime > maxEndTime) {
        result.hasIssue = true
        result.endTimeIssue = true
      }
    } else {
      // 后置任务：检查其开始时间是否早于当前任务的结束时间+1天
      const currentEndDate = new Date(currentEndTime)
      currentEndDate.setHours(0, 0, 0, 0)
      const minStartTime = new Date(currentEndDate)
      minStartTime.setDate(minStartTime.getDate() + 1)
      
      const taskStartTime = new Date(task.startTime)
      taskStartTime.setHours(0, 0, 0, 0)
      
      if (taskStartTime < minStartTime) {
        result.hasIssue = true
        result.startTimeIssue = true
      }
    }
    
    return result
  }

  /**
   * 获取动态验证规则
   * 当结束时间有冲突时，不显示"请选择结束时间"的验证提示
   * 
   * @param {Object} baseRules - 基础验证规则
   * @returns {Object} 动态验证规则
   */
  const getDynamicRules = (baseRules) => {
    const rules = { ...baseRules }
    
    // 如果结束时间有冲突，修改 endTime 的验证规则，使其在有冲突时不显示"请选择结束时间"
    const details = timeIssueDetails.value
    
    // 如果有冲突（endTimeIssue 为 true），修改验证规则
    if (details.endTimeIssue) {
      // 有冲突，不显示"请选择结束时间"的验证提示
      // 冲突提示由 endTimeWarningMessage 显示
      rules.endTime = [
        {
          validator: (rule, value, callback) => {
            // 如果有冲突，不显示"请选择结束时间"的验证提示
            // 冲突提示由 endTimeWarningMessage 显示
            callback()
          },
          trigger: ['blur', 'change']
        }
      ]
    }
    
    return rules
  }

  return {
    timeIssueDetails,
    startTimeWarningMessage,
    endTimeWarningMessage,
    getTaskTimeIssueDetails,
    getDynamicRules
  }
}

