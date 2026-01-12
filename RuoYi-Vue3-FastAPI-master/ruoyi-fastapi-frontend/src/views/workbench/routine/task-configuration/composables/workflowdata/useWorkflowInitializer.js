// composables/useWorkflowInitializer.js
/**
 * 工作流初始化器
 * 处理加载后的完整初始化逻辑：确保 projectId、初始化统计、初始化连接、初始化验证等
 */
import { useStageTimeValidation } from '../stage/useStageTimeValidation'

export const useWorkflowInitializer = ({
  projectId,
  workflowData,
  unassignedTasks,
  projectStore,
  workflowStore,
  initConnectionsFromWorkflow,
  findTaskById,
  loadEmployeeList,
  loadWorkflow,
  loading,
  toFrontendFormat,
  startAutoSave,
  dataLoaded,
  tasksGenerated
}) => {
  /**
   * 确保所有阶段和任务都有 projectId 字段
   * @param {string|number} projectId - 项目ID
   */
  const ensureProjectId = (projectId) => {
    // 确保所有阶段都有 projectId
    if (workflowData.value?.stages) {
      workflowData.value.stages.forEach(stage => {
        if (!stage.projectId) {
          stage.projectId = projectId
        }
        // 确保阶段内的任务都有 projectId
        if (stage.tasks) {
          stage.tasks.forEach(task => {
            if (!task.projectId) {
              task.projectId = projectId
            }
          })
        }
      })
    }
    
    // 确保阶段外的任务都有 projectId
    if (unassignedTasks.value) {
      unassignedTasks.value.forEach(task => {
        if (!task.projectId) {
          task.projectId = projectId
        }
      })
    }
  }

  /**
   * 初始化项目统计信息
   * @param {string|number} projectId - 项目ID
   */
  const initializeProjectStats = (projectId) => {
    // 收集所有任务（阶段内 + 阶段外）
    const allTasks = [
      ...(workflowData.value?.stages?.flatMap(stage => stage.tasks || []) || []),
      ...(unassignedTasks.value || [])
    ]
    
    // 初始化项目统计信息
    projectStore.initProjectStats(projectId, {
      ...workflowData.value,
      allTasks: allTasks
    })
  }

  /**
   * 初始化连接
   */
  const initializeConnections = () => {
    if (typeof initConnectionsFromWorkflow === 'function') {
      initConnectionsFromWorkflow(workflowData.value, unassignedTasks.value)
    }
  }

  /**
   * 初始化所有任务的验证标记
   */
  const initializeTaskValidation = async () => {
    const { initializeAllTaskValidation } = await import('./useTaskValidationInitializer')
    
    await initializeAllTaskValidation(
      workflowData.value,
      unassignedTasks.value,
      findTaskById,
      workflowStore
    )
  }

  /**
   * 初始化所有阶段的时间异常标记
   */
  const initializeStageTimeValidation = () => {
    const { updateStageTimeIssueFlags } = useStageTimeValidation()
    
    if (workflowData.value && workflowData.value.stages) {
      const stages = workflowData.value.stages
      const updatedStages = updateStageTimeIssueFlags(stages)
      
      // 更新阶段的时间异常标记（直接修改原对象）
      updatedStages.forEach(updatedStage => {
        const originalStage = stages.find(s => s.id === updatedStage.id)
        if (originalStage && updatedStage.hasTimeIssue !== undefined) {
          originalStage.hasTimeIssue = updatedStage.hasTimeIssue
        }
      })
    }
  }

  /**
   * 加载并初始化工作流数据
   * @returns {Promise<void>}
   */
  const loadAndInitializeWorkflow = async () => {
    if (!projectId.value) {
      console.error('项目ID不能为空')
      dataLoaded.value = false
      return
    }
    
    // 重置数据加载标志
    dataLoaded.value = false
    
    try {
      // 1. 先加载员工列表，确保负责人能正确显示
      await loadEmployeeList()
      
      // 2. 加载工作流数据
      const loadedTasksGenerated = await loadWorkflow(
        projectId.value,
        loading,
        workflowData,
        toFrontendFormat,
        workflowStore,
        startAutoSave,
        unassignedTasks
      )
      
      // 更新 tasksGenerated 状态
      if (tasksGenerated && typeof loadedTasksGenerated !== 'undefined') {
        tasksGenerated.value = loadedTasksGenerated
      }
      
      // 3. 确保所有阶段和任务都有 projectId 字段
      ensureProjectId(projectId.value)
      
      // 4. 初始化项目统计信息
      initializeProjectStats(projectId.value)
      
      // 5. 初始化连接
      initializeConnections()
      
      // 6. 初始化所有任务的验证标记
      await initializeTaskValidation()
      
      // 7. 初始化所有阶段的时间异常标记
      initializeStageTimeValidation()
      
      // 8. 数据加载完成
      dataLoaded.value = true
    } catch (error) {
      console.error('加载工作流数据失败:', error)
      dataLoaded.value = false
      throw error
    }
  }

  return {
    loadAndInitializeWorkflow,
    ensureProjectId,
    initializeProjectStats,
    initializeConnections,
    initializeTaskValidation,
    initializeStageTimeValidation
  }
}

