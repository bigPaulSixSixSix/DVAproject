// composables/useWorkflowData.js
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { saveTaskConfig, saveTaskConfigAndGenerate } from '@/api/workflow'
import { useIdManager } from '../utils/useIdManager'
import { useTaskValidation } from '../task/useTaskValidation'
import { useCycleDetection } from '../connection/validation/useCycleDetection'
import dayjs from 'dayjs'
import { useStageTime } from '../stage/useStageTime'
import { useStageTimeValidation } from '../stage/useStageTimeValidation'
import { updateMultipleTaskTimeIssueFlags } from '../task/useTaskTimeValidation'
import { updateMultipleStageTimeIssueFlags } from '../stage/useStageTimeValidation'

export const useWorkflowData = () => {
  const { getInvalidTasks } = useTaskValidation()
  const { updateStageTime } = useStageTime()
  const { detectCycles } = useCycleDetection()
  const { updateStageTimeIssueFlags } = useStageTimeValidation()

  const formatDateForBackend = (value) => {
    if (!value) return null
    if (typeof value === 'string') {
      const normalized = value.includes('/') ? value.replace(/\//g, '-') : value
      const parsed = dayjs(normalized)
      return parsed.isValid() ? parsed.format('YYYY-MM-DD') : null
    }
    const parsed = dayjs(value)
    return parsed.isValid() ? parsed.format('YYYY-MM-DD') : null
  }

  /**
   * 确保 position 对象中的所有数值都是整数
   * 后端要求坐标必须是整数
   * @param {Object} position - 位置对象 { x, y, width?, height? }
   * @returns {Object} 转换后的位置对象
   */
  const normalizePosition = (position) => {
    if (!position || typeof position !== 'object') {
      return position
    }
    const normalized = {}
    if (position.x !== undefined && position.x !== null) {
      normalized.x = Math.round(Number(position.x))
    }
    if (position.y !== undefined && position.y !== null) {
      normalized.y = Math.round(Number(position.y))
    }
    if (position.width !== undefined && position.width !== null) {
      normalized.width = Math.round(Number(position.width))
    }
    if (position.height !== undefined && position.height !== null) {
      normalized.height = Math.round(Number(position.height))
    }
    return normalized
  }

  const workflowData = ref({
    id: 1,
    name: '',
    stages: []
  })
  const loading = ref(false)

  // 前端数据转后端数据
  const toBackendFormat = (workflowData, unassignedTasks = []) => {
    const projectId = workflowData.projectId
    
    // 在保存前，实时计算并更新所有阶段的时间
    const stages = workflowData.stages.map(stage => {
      // 更新阶段时间（实时计算）
      const updatedStage = updateStageTime(stage)
      // 注意：关系数据（predecessorStages/successorStages）应该使用原始 stage 对象的数据
      // 因为 updateStageTime 只更新时间，不会修改关系数据
      // 但为了确保数据一致性，我们使用 stage 对象的最新数据
      return {
        id: stage.id,
        name: stage.name,
        startTime: formatDateForBackend(updatedStage.startTime),
        endTime: formatDateForBackend(updatedStage.endTime),
        duration: updatedStage.duration,
        predecessorStages: Array.isArray(stage.predecessorStages) ? [...stage.predecessorStages] : [],
        successorStages: Array.isArray(stage.successorStages) ? [...stage.successorStages] : [],
        position: normalizePosition(stage.position),
        projectId: stage.projectId || projectId // 确保有projectId
      }
    })

    // 阶段内的任务
    const stageTasks = workflowData.stages.flatMap(stage =>
      stage.tasks.map(task => ({
        id: task.id,
        name: task.name,
        description: task.description,
        startTime: formatDateForBackend(task.startTime),
        duration: task.duration,
        endTime: formatDateForBackend(task.endTime),
        jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
        stageId: task.stageId,
        predecessorTasks: Array.isArray(task.predecessorTasks) ? [...task.predecessorTasks] : [],
        successorTasks: Array.isArray(task.successorTasks) ? [...task.successorTasks] : [],
        position: normalizePosition(task.position),
        projectId: task.projectId || projectId, // 确保有projectId
        approvalType: task.approvalType || 'sequential', // 审批类型
        approvalNodes: Array.isArray(task.approvalNodes) ? [...task.approvalNodes] : [] // 审批节点数组
      }))
    )

    // 阶段外的任务（stageId 为 null）
    const unassignedTasksFormatted = (unassignedTasks || []).map(task => ({
      id: task.id,
      name: task.name,
      description: task.description || '',
      startTime: formatDateForBackend(task.startTime),
      duration: task.duration,
      endTime: formatDateForBackend(task.endTime),
            jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
      stageId: null, // 阶段外的任务 stageId 为 null
      predecessorTasks: task.predecessorTasks || [],
      successorTasks: task.successorTasks || [],
      position: normalizePosition(task.position),
      projectId: task.projectId || projectId, // 确保有projectId
      approvalType: task.approvalType || 'specified', // 审批类型
      approvalNodes: Array.isArray(task.approvalNodes) ? [...task.approvalNodes] : [] // 审批节点数组
    }))

    // 合并所有任务
    const tasks = [...stageTasks, ...unassignedTasksFormatted]

    return { projectId, stages, tasks }
  }

  // 后端数据转前端数据
  const toFrontendFormat = (backendData) => {
    // 如果没有数据，返回空数组
    if (!backendData || !backendData.stages) {
      return { stages: [], unassignedTasks: [], tasksGenerated: false }
    }
    
    // 提取 tasksGenerated（项目级别，默认为 false 以兼容旧数据）
    const tasksGenerated = backendData.tasksGenerated ?? false

    // 辅助函数：将ID统一转换为数字类型
    const normalizeId = (id) => {
      if (id == null) return null
      const num = Number(id)
      return isNaN(num) ? id : num
    }

    // 辅助函数：将ID数组统一转换为数字类型
    const normalizeIdArray = (ids) => {
      if (!Array.isArray(ids)) return []
      return ids.map(id => normalizeId(id)).filter(id => id != null)
    }

    // 过滤掉null或undefined的阶段
    const validStages = backendData.stages.filter(stage => stage != null)

    // 如果后端数据已经包含了tasks（嵌套结构），直接使用
    if (validStages.some(stage => stage.tasks && Array.isArray(stage.tasks))) {
      // 同时过滤掉null的任务，并转换任务坐标为绝对坐标
      const processedStages = validStages.map(stage => {
        if (!Array.isArray(stage.tasks)) {
          return {
            ...stage,
            id: normalizeId(stage.id),
            predecessorStages: normalizeIdArray(stage.predecessorStages),
            successorStages: normalizeIdArray(stage.successorStages),
            isEditable: stage.isEditable ?? true, // 默认可编辑（兼容旧数据）
            tasks: []
          }
        }

        const validTasks = stage.tasks.filter(task => task != null)

        // 将任务的相对坐标转换为绝对坐标（相对于画布），并统一ID类型
        const tasksWithAbsolutePosition = validTasks.map(task => ({
          ...task,
          id: normalizeId(task.id),
          stageId: normalizeId(task.stageId),
          predecessorTasks: normalizeIdArray(task.predecessorTasks),
          successorTasks: normalizeIdArray(task.successorTasks),
          jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
          approvalType: task.approvalType || 'sequential', // 审批类型
          approvalNodes: normalizeIdArray(task.approvalNodes), // 审批节点数组
          isEditable: task.isEditable ?? true, // 默认可编辑（兼容旧数据）
          position: {
            ...task.position,
            // 如果 position 是字符串，需要解析；否则直接使用
            x: task.position.x + (stage.position?.x || 0),
            y: task.position.y + (stage.position?.y || 0)
          }
        }))

        return {
          ...stage,
          id: normalizeId(stage.id),
          predecessorStages: normalizeIdArray(stage.predecessorStages),
          successorStages: normalizeIdArray(stage.successorStages),
          isEditable: stage.isEditable ?? true, // 默认可编辑（兼容旧数据）
          tasks: tasksWithAbsolutePosition
        }
      })

      return { stages: processedStages, unassignedTasks: [], tasksGenerated }
    }

    // 如果是分离的结构（stages和tasks分开）
    if (backendData.tasks && Array.isArray(backendData.tasks)) {
      const validTasks = backendData.tasks.filter(task => task != null)
      const normalizedTasks = validTasks.map(task => ({
        ...task,
        id: normalizeId(task.id),
        stageId: normalizeId(task.stageId),
        predecessorTasks: normalizeIdArray(task.predecessorTasks),
        successorTasks: normalizeIdArray(task.successorTasks),
        jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
        approvalType: task.approvalType || 'sequential', // 审批类型
        approvalNodes: normalizeIdArray(task.approvalNodes), // 审批节点数组
        isEditable: task.isEditable ?? true, // 默认可编辑（兼容旧数据）
        position: task.position || { x: 0, y: 0 } // 确保有position
      }))
      
      // 分离阶段内的任务和阶段外的任务（stageId 为 null 或 undefined）
      const unassignedTasks = normalizedTasks.filter(task => 
        task.stageId == null || task.stageId === null || task.stageId === undefined
      )
      
      const stages = validStages.map(stage => {
        const stageId = normalizeId(stage.id)
        const stageTasks = normalizedTasks.filter(task => 
          task.stageId != null && Number(task.stageId) === Number(stageId)
        )
        return {
          ...stage,
          id: stageId,
          predecessorStages: normalizeIdArray(stage.predecessorStages),
          successorStages: normalizeIdArray(stage.successorStages),
          isEditable: stage.isEditable ?? true, // 默认可编辑（兼容旧数据）
          tasks: stageTasks
        }
      })
      
      return { stages, unassignedTasks, tasksGenerated }
    }

    // 返回空的阶段数组
    return { stages: [], unassignedTasks: [], tasksGenerated }
  }

  const validateWorkflow = (workflowData, unassignedTasks = []) => {
    const errors = []

    // 不再检查任务位置，允许有阶段外任务
    // 检查任务位置的代码已移除，允许任务在阶段外

    // 检查循环依赖（包括阶段外的任务）
    const allTasks = [
      ...workflowData.stages.flatMap(stage => stage.tasks),
      ...(unassignedTasks || [])
    ]
    const cycleErrors = detectCycles(workflowData.stages, allTasks)
    errors.push(...cycleErrors)

    return errors
  }

  /**
   * 更新工作流数据（从后端响应）
   * @param {Object} latestFormatted - 格式化后的前端数据
   * @param {string|number} projectId - 项目ID
   * @param {Object} unassignedTasksRef - 阶段外任务的ref（可选）
   */
  const updateWorkflowDataFromResponse = (latestFormatted, projectId, unassignedTasksRef) => {
    // 完全替换 workflowData，确保 Vue 能检测到所有变化（包括 stages 数组中的任务ID更新）
    // 创建全新的对象和数组，确保触发响应式更新
    // 深度克隆所有对象，确保每个任务对象都是全新的
    const newWorkflowData = {
      projectId,
      stages: latestFormatted.stages ? latestFormatted.stages.map(stage => ({
        id: stage.id,
        name: stage.name,
        startTime: stage.startTime,
        endTime: stage.endTime,
        duration: stage.duration,
        predecessorStages: stage.predecessorStages ? [...stage.predecessorStages] : [],
        successorStages: stage.successorStages ? [...stage.successorStages] : [],
        position: { ...stage.position },
        projectId: stage.projectId,
        isEditable: stage.isEditable ?? true, // 保留后端返回的 isEditable 字段
        tasks: stage.tasks ? stage.tasks.map(task => ({
          id: task.id,
          name: task.name,
          description: task.description,
          startTime: task.startTime,
          endTime: task.endTime,
          duration: task.duration,
          jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
          stageId: task.stageId,
          predecessorTasks: task.predecessorTasks ? [...task.predecessorTasks] : [],
          successorTasks: task.successorTasks ? [...task.successorTasks] : [],
          position: { ...task.position },
          projectId: task.projectId,
          approvalType: task.approvalType || 'specified',
          approvalNodes: Array.isArray(task.approvalNodes) ? [...task.approvalNodes] : [],
          isEditable: task.isEditable ?? true // 保留后端返回的 isEditable 字段
        })) : []
      })) : []
    }
    
    // 完全替换 workflowData.value（使用新对象）
    // 重要：必须完全替换整个对象，确保 Vue 能检测到 stages 数组的变化
    workflowData.value = newWorkflowData
    
    // 完全替换 unassignedTasks 数组（深度克隆每个任务对象）
    // 注意：unassignedTasksRef 是外部传入的 ref，需要更新它的 .value
    if (unassignedTasksRef) {
      const newUnassignedTasks = latestFormatted.unassignedTasks ? latestFormatted.unassignedTasks.map(task => ({
        id: task.id,
        name: task.name,
        description: task.description,
        startTime: task.startTime,
        endTime: task.endTime,
        duration: task.duration,
        jobNumber: task.jobNumber || task.assignee || null, // 兼容旧数据，优先使用 jobNumber
        stageId: task.stageId,
        predecessorTasks: task.predecessorTasks ? [...task.predecessorTasks] : [],
        successorTasks: task.successorTasks ? [...task.successorTasks] : [],
        position: { ...task.position },
        projectId: task.projectId,
        approvalType: task.approvalType || 'specified',
        approvalNodes: Array.isArray(task.approvalNodes) ? [...task.approvalNodes] : [],
        isEditable: task.isEditable ?? true // 保留后端返回的 isEditable 字段
      })) : []
      unassignedTasksRef.value.splice(0, unassignedTasksRef.value.length, ...newUnassignedTasks)
    }
  }

  /**
   * 更新任务和阶段的时间异常标记
   * @param {Object} unassignedTasksRef - 阶段外任务的ref（可选）
   */
  const updateTimeIssueFlagsAfterSave = (unassignedTasksRef) => {
    // 在显示弹窗前，先重新计算任务和阶段的时间异常标记
    // 这样在弹窗显示时，时间异常标记已经正确显示
    
    // 1. 重新计算任务的时间异常标记
    const findTaskById = (taskId) => {
      // 在阶段内查找
      for (const stage of workflowData.value.stages || []) {
        const task = stage.tasks?.find(t => t.id === taskId)
        if (task) {
          return { task, stage, isUnassigned: false }
        }
      }
      // 在阶段外查找
      if (unassignedTasksRef) {
        const task = unassignedTasksRef.value?.find(t => t.id === taskId)
        if (task) {
          return { task, stage: null, isUnassigned: true }
        }
      }
      return null
    }
    
    // 收集所有任务ID
    const allTaskIds = []
    if (workflowData.value.stages) {
      workflowData.value.stages.forEach(stage => {
        if (stage.tasks) {
          stage.tasks.forEach(task => {
            if (task.id) allTaskIds.push(task.id)
          })
        }
      })
    }
    if (unassignedTasksRef && unassignedTasksRef.value) {
      unassignedTasksRef.value.forEach(task => {
        if (task.id) allTaskIds.push(task.id)
      })
    }
    
    // 重新计算任务的时间异常标记
    if (allTaskIds.length > 0) {
      const simpleWorkflowStore = {
        updateTask: (taskId, updates) => {
          const taskInfo = findTaskById(taskId)
          if (taskInfo && taskInfo.task) {
            Object.assign(taskInfo.task, updates)
          }
        }
      }
      updateMultipleTaskTimeIssueFlags(allTaskIds, findTaskById, simpleWorkflowStore)
    }
    
    // 2. 重新计算阶段的时间异常标记
    if (workflowData.value && workflowData.value.stages) {
      const stages = workflowData.value.stages
      const findStageById = (stageId) => {
        return stages.find(s => s.id === stageId) || null
      }
      const simpleWorkflowStore = {
        updateStage: (stageId, updates) => {
          const stage = findStageById(stageId)
          if (stage) {
            Object.assign(stage, updates)
          }
        }
      }
      const allStageIds = stages.map(s => s.id)
      if (allStageIds.length > 0) {
        updateMultipleStageTimeIssueFlags(allStageIds, findStageById, stages, simpleWorkflowStore)
      }
    }
  }

  /**
   * 显示响应弹窗
   * @param {Object} response - 后端响应数据
   * @param {string} title - 弹窗标题
   * @param {string} type - 弹窗类型（'success' 或 'error'）
   */
  const showResponseAlert = async (response, title, type = 'success') => {
    await ElMessageBox.alert(
      `<pre style="text-align: left; max-height: 400px; overflow: auto; white-space: pre-wrap; word-wrap: break-word;">${JSON.stringify(response, null, 2)}</pre>`,
      title,
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定',
        type,
        width: '800px',
        showClose: false // 隐藏右上角关闭按钮，只能点击确定关闭
      }
    )
  }

  /**
   * 构建错误数据对象
   * @param {Error} error - 错误对象
   * @returns {Object} 错误数据对象
   */
  const buildErrorData = (error) => {
    return {
      message: error.message || '未知错误',
      response: error.response ? {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data
      } : null,
      stack: error.stack || null
    }
  }

  /**
   * 通用的保存工作流函数
   * @param {Function} apiCall - API调用函数
   * @param {Object} unassignedTasksRef - 阶段外任务的ref（可选）
   * @param {string} successTitle - 成功弹窗标题
   * @param {string} errorTitle - 错误弹窗标题
   * @param {string} errorLogPrefix - 错误日志前缀
   * @returns {Promise<Object>} 保存结果
   */
  const saveWorkflowInternal = async (apiCall, unassignedTasksRef, successTitle, errorTitle, errorLogPrefix) => {
    // 使用内部的 workflowData ref 和传入的 unassignedTasks ref
    const currentWorkflowData = workflowData.value
    const currentUnassignedTasks = unassignedTasksRef?.value || []
    
    const errors = validateWorkflow(currentWorkflowData, currentUnassignedTasks)

    if (errors.length > 0) {
      // 显示错误信息（只显示循环依赖等严重错误）
      showValidationErrors(errors)
      return { success: false, errors }
    }

    // 执行保存
    try {
      const backendData = toBackendFormat(currentWorkflowData, currentUnassignedTasks)
      const projectId = currentWorkflowData.projectId
      if (!projectId) {
        ElMessage.error('项目ID不能为空')
        return { success: false }
      }

      // 调用后端接口
      const response = await apiCall(backendData)
      
      // 保存成功后，使用后端返回的数据更新前端数据
      const backendWorkflow = response?.data ?? response ?? backendData
      const latestFormatted = toFrontendFormat(backendWorkflow)
      
      // 更新工作流数据
      updateWorkflowDataFromResponse(latestFormatted, projectId, unassignedTasksRef)
      
      // 更新时间异常标记
      updateTimeIssueFlagsAfterSave(unassignedTasksRef)
      
      // 弹窗显示返回的原始数据（成功情况）
      await showResponseAlert(response, successTitle, 'success')
      
      // 返回后端数据和格式化后的前端数据，供调用方使用
      return {
        success: true,
        backendData: backendWorkflow,
        frontendData: latestFormatted
      }
    } catch (error) {
      // 打印错误信息到控制台
      console.error(`${errorLogPrefix}:`, error)
      console.error('错误详情:', error.response || error.message)
      
      // 构建错误数据对象用于显示
      const errorData = buildErrorData(error)
      
      // 弹窗显示错误信息（错误情况）
      await showResponseAlert(errorData, errorTitle, 'error')
      
      return { success: false, error }
    }
  }

  /**
   * 保存工作流
   * @param {Object} unassignedTasksRef - 阶段外任务的ref（可选）
   * @returns {Promise<Object>} 保存结果
   */
  const saveWorkflow = async (unassignedTasksRef = null) => {
    return saveWorkflowInternal(
      saveTaskConfig,
      unassignedTasksRef,
      '保存成功 - 后端返回数据',
      '保存失败 - 后端返回数据',
      '任务保存失败'
    )
  }

  /**
   * 保存工作流并生成
   * @param {Object} unassignedTasksRef - 阶段外任务的ref（可选）
   * @returns {Promise<Object>} 保存结果
   */
  const saveWorkflowAndGenerate = async (unassignedTasksRef = null) => {
    return saveWorkflowInternal(
      saveTaskConfigAndGenerate,
      unassignedTasksRef,
      '保存并生成成功 - 后端返回数据',
      '保存并生成失败 - 后端返回数据',
      '任务保存并生成失败'
    )
  }

  const showValidationErrors = (errors) => {
    errors.forEach(error => {
      ElMessage.error(error.message)
    })
  }

  const updateTaskPosition = (taskId, newPosition, isValid) => {
    const task = findTaskById(taskId)
    if (!task) return

    task.position = newPosition
    task.isValidPosition = isValid
  }

  const findTaskById = (taskId) => {
    if (!workflowData.value) return null

    for (const stage of workflowData.value.stages) {
      const task = stage.tasks.find(t => t.id === taskId)
      if (task) return task
    }
    return null
  }

  const findStageById = (stageId) => {
    if (!workflowData.value) return null
    return workflowData.value.stages.find(s => s.id === stageId)
  }

  return {
    workflowData,
    loading,
    toBackendFormat,
    toFrontendFormat,
    validateWorkflow,
    saveWorkflow,
    saveWorkflowAndGenerate,
    updateTaskPosition,
    findTaskById,
    findStageById
  }
}
