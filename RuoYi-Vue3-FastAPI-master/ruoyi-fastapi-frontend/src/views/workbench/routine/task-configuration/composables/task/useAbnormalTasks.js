import { computed } from 'vue'

/**
 * 统一计算异常任务列表
 * 条件：
 *  - 未分配到阶段
 *  - 位置信息无效（isValidPosition === false）
 *  - 必填信息缺失（startTime / endTime / assignee）
 *  - 时间冲突（hasTimeIssue === true）
 */
export const useAbnormalTasks = (stagesSource, unassignedTasksSource) => {
  const getSourceValue = (source) => {
    if (typeof source === 'function') {
      return source()
    }
    if (source && typeof source.value !== 'undefined') {
      return source.value
    }
    return source || []
  }

  const abnormalTasks = computed(() => {
    const result = []

    const addTask = (task, stage = null, isUnassigned = false) => {
      if (!task || task._isPreview || task._isDeleting) return

      const reasons = []

      if (isUnassigned) {
        reasons.push('未分配到阶段')
      }

      if (!isUnassigned && task.isValidPosition === false) {
        reasons.push('位置超出阶段范围')
      }

      const missingFields = []
      if (!task.startTime) missingFields.push('开始时间')
      if (!task.endTime) missingFields.push('结束时间')
      if (!task.jobNumber && !task.assignee) missingFields.push('负责人') // 兼容旧数据
      // 检查审批节点是否配置：approvalNodes 应该是数组，如果为空数组或不存在，则认为未配置
      // 但如果审批类型为"none"（无需审批），则不需要检查审批层级
      const approvalType = task.approvalType || 'sequential'
      if (approvalType !== 'none') {
        if (!task.approvalNodes || !Array.isArray(task.approvalNodes) || task.approvalNodes.length === 0) {
          missingFields.push('审批层级')
        }
      }
      if (missingFields.length > 0) {
        reasons.push(`信息缺失：${missingFields.join('、')}`)
      }

      if (task.hasTimeIssue) {
        reasons.push('时间关系异常')
      }

      if (reasons.length === 0) return

      result.push({
        id: task.id,
        name: task.name || '未命名任务',
        stageId: stage?.id ?? null,
        stageName: stage?.name || (isUnassigned ? '未分配阶段' : '未知阶段'),
        reasons,
        position: task.position || { x: 0, y: 0 },
        rawTask: task
      })
    }

    const stages = getSourceValue(stagesSource) || []
    stages.forEach(stage => {
      if (stage?.tasks) {
        stage.tasks.forEach(task => addTask(task, stage, false))
      }
    })

    const unassignedTasks = getSourceValue(unassignedTasksSource) || []
    unassignedTasks.forEach(task => addTask(task, null, true))

    return result
  })

  const abnormalTaskCount = computed(() => abnormalTasks.value.length)

  // 判断异常任务的类型，用于设置按钮颜色
  // 返回 'danger'（红色）如果有信息缺失、未分配到阶段、位置超出阶段范围的异常
  // 返回 'warning'（黄色）如果只有时间关系异常
  const abnormalTaskType = computed(() => {
    if (abnormalTaskCount.value === 0) {
      return 'warning' // 默认值，虽然按钮会被禁用
    }

    // 检查是否有非时间关系异常的异常任务
    const hasNonTimeIssue = abnormalTasks.value.some(task => {
      return task.reasons.some(reason => {
        // 检查是否是时间关系异常以外的异常
        return reason !== '时间关系异常'
      })
    })

    // 如果有非时间关系异常的异常，返回 'danger'（红色）
    if (hasNonTimeIssue) {
      return 'danger'
    }

    // 如果只有时间关系异常，返回 'warning'（黄色）
    return 'warning'
  })

  return {
    abnormalTasks,
    abnormalTaskCount,
    abnormalTaskType
  }
}

