// composables/useStageEdit.js
// 阶段编辑相关逻辑

import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export const useStageEdit = () => {
  // 阶段编辑弹窗状态
  const stageEditDialogVisible = ref(false)
  const stageEditFormRef = ref(null)
  const currentEditingStage = ref(null)
  const stageEditForm = ref({
    name: '',
    taskCount: 0,
    timeRange: '',
    hasInvalidTime: false
  })

  // 阶段编辑表单验证规则
  const stageEditRules = {
    name: [
      { required: true, message: '请输入阶段名称', trigger: 'blur' },
      { min: 1, max: 50, message: '阶段名称长度在 1 到 50 个字符', trigger: 'blur' }
    ]
  }

  /**
   * 计算阶段的时间范围（遍历所有任务，找最早开始时间和最晚结束时间）
   * @param {Object} stage - 阶段对象
   * @returns {Object} 时间范围信息
   */
  const calculateStageTimeRange = (stage) => {
    if (!stage || !stage.tasks || stage.tasks.length === 0) {
      return {
        startTime: null,
        endTime: null,
        days: null,
        hasInvalidTime: true
      }
    }
    
    // 分别找到最早的开始时间和最晚的结束时间（即使它们不在同一个任务上）
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
    
    // 计算天数（包含首尾）- 只有当开始时间和结束时间都存在时才能计算
    const days = earliestStartTime && latestEndTime
      ? Math.floor((latestEndTime - earliestStartTime) / (1000 * 60 * 60 * 24)) + 1
      : null
    
    // 判断是否有无效时间（开始时间或结束时间缺失）
    const hasInvalidTime = !earliestStartTime || !latestEndTime
    
    return {
      startTime: earliestStartTime,
      endTime: latestEndTime,
      days: days,
      hasInvalidTime: hasInvalidTime
    }
  }

  /**
   * 格式化时间为 YYYY/MM/DD
   * @param {Date|string} date - 日期对象或日期字符串
   * @returns {string|null} 格式化后的日期字符串
   */
  const formatDateFull = (date) => {
    if (!date) return null
    if (typeof date === 'string') {
      if (/^\d{4}\/\d{2}\/\d{2}$/.test(date)) {
        return date
      }
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
   * 格式化时间范围显示
   * @param {Object} timeRange - 时间范围对象
   * @returns {string} 格式化后的时间范围字符串
   */
  const formatTimeRange = (timeRange) => {
    if (timeRange.hasInvalidTime) {
      if (!timeRange.startTime && !timeRange.endTime) {
        return '? - ? 共?天'
      } else if (!timeRange.startTime) {
        return `? - ${formatDateFull(timeRange.endTime)} 共?天`
      } else if (!timeRange.endTime) {
        return `${formatDateFull(timeRange.startTime)} - ? 共?天`
      }
    }
    
    if (timeRange.startTime && timeRange.endTime && timeRange.days !== null) {
      return `${formatDateFull(timeRange.startTime)} - ${formatDateFull(timeRange.endTime)} 共${timeRange.days}天`
    }
    
    return '? - ? 共?天'
  }

  /**
   * 打开阶段编辑弹窗
   * @param {Object} stage - 阶段对象
   */
  const openStageEditDialog = (stage) => {
    if (!stage) return
    
    currentEditingStage.value = stage
    stageEditForm.value.name = stage.name || ''
    stageEditForm.value.taskCount = (stage.tasks && Array.isArray(stage.tasks)) ? stage.tasks.length : 0
    
    // 计算时间范围
    const timeRange = calculateStageTimeRange(stage)
    stageEditForm.value.timeRange = formatTimeRange(timeRange)
    stageEditForm.value.hasInvalidTime = timeRange.hasInvalidTime
    
    stageEditDialogVisible.value = true
  }

  /**
   * 关闭阶段编辑弹窗
   */
  const closeStageEditDialog = () => {
    currentEditingStage.value = null
    stageEditForm.value.name = ''
    stageEditForm.value.taskCount = 0
    stageEditForm.value.timeRange = ''
    stageEditForm.value.hasInvalidTime = false
    if (stageEditFormRef.value) {
      stageEditFormRef.value.resetFields()
    }
  }

  /**
   * 确认阶段编辑
   * @param {Function} findStageById - 查找阶段函数
   * @param {Object} workflowStore - 工作流store
   * @returns {Promise<boolean>} 是否成功保存
   */
  const confirmStageEdit = async (findStageById, workflowStore) => {
    if (!stageEditFormRef.value) return false
    
    try {
      await stageEditFormRef.value.validate()
      
      if (!currentEditingStage.value) return false
      
      // 更新阶段名称
      const stage = findStageById(currentEditingStage.value.id)
      if (stage) {
        stage.name = stageEditForm.value.name
        // 直接修改 stage 对象即可，不需要额外更新 workflowStore
        ElMessage.success('阶段名称已更新')
        return true
      }
      
      return false
    } catch (error) {
      // 验证失败，不关闭弹窗
      console.error('表单验证失败:', error)
      return false
    }
  }

  /**
   * 获取当前编辑的阶段ID
   * @returns {string|number|null} 阶段ID
   */
  const getCurrentEditingStageId = () => {
    return currentEditingStage.value?.id || null
  }

  return {
    // 状态
    stageEditDialogVisible,
    stageEditFormRef,
    currentEditingStage,
    stageEditForm,
    stageEditRules,
    // 方法
    openStageEditDialog,
    closeStageEditDialog,
    confirmStageEdit,
    getCurrentEditingStageId,
    calculateStageTimeRange,
    formatDateFull,
    formatTimeRange
  }
}

