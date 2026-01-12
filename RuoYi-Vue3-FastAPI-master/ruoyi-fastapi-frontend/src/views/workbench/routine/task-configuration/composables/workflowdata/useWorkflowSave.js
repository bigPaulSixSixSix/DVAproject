// composables/useWorkflowSave.js
import { nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { updateMultipleStageTimeIssueFlags } from '../stage/useStageTimeValidation'

/**
 * 工作流保存处理器
 * 处理保存后的完整逻辑：更新统计信息、重新验证等
 */
export const useWorkflowSave = ({
  projectId,
  workflowData,
  unassignedTasks,
  projectStore,
  findTaskById,
  workflowStore,
  handleSaveInternal,
  saveWorkflowAndGenerate,
  initConnectionsFromWorkflow = null
}) => {
  /**
   * 更新项目统计信息
   * @param {string|number} projectId - 项目ID
   */
  const updateProjectStats = (projectId) => {
    if (!projectId) return
    
    // 收集所有任务（阶段内 + 阶段外）
    const allTasks = [
      ...(workflowData.value?.stages?.flatMap(stage => stage.tasks || []) || []),
      ...(unassignedTasks.value || [])
    ]
    
    // 更新项目统计信息
    projectStore.initProjectStats(projectId, {
      ...workflowData.value,
      allTasks: allTasks
    })
  }

  /**
   * 重新验证所有任务（保存后）
   * 因为后端返回的数据可能更新了任务ID（临时ID -> 真实ID），需要重新验证
   */
  const revalidateAllTasks = async () => {
    const { initializeAllTaskValidation, collectAllTasks } = await import('./useTaskValidationInitializer')
    
    // 收集所有任务
    const { allTaskIds } = collectAllTasks(workflowData.value, unassignedTasks.value)
    
    if (allTaskIds.length > 0) {
      // 重新初始化所有验证标记
      await initializeAllTaskValidation(
        workflowData.value,
        unassignedTasks.value,
        findTaskById,
        workflowStore
      )
    }
  }

  /**
   * 重新验证所有阶段的时间异常标记（保存后）
   * 因为后端返回的数据可能更新了阶段ID或时间信息，需要重新验证
   */
  const revalidateAllStages = () => {
    if (workflowData.value && workflowData.value.stages && workflowStore) {
      const stages = workflowData.value.stages
      // 创建 findStageById 函数
      const findStageById = (stageId) => {
        return stages.find(s => s.id === stageId) || null
      }
      // 批量更新所有阶段的时间异常标记（使用和任务一致的逻辑）
      const allStageIds = stages.map(s => s.id)
      updateMultipleStageTimeIssueFlags(allStageIds, findStageById, stages, workflowStore)
    }
  }

  /**
   * 统一的保存后处理逻辑
   * @param {boolean} success - 保存是否成功
   */
  const handleAfterSave = async (success) => {
    if (success && projectId.value) {
      // 等待 DOM 更新完成，确保 workflowData.value 和 unassignedTasks.value 已经是最新数据
      await nextTick()
      
      // 重新初始化连接（使用最新数据）
      if (typeof initConnectionsFromWorkflow === 'function') {
        initConnectionsFromWorkflow(
          workflowData.value,
          unassignedTasks.value || []
        )
      }
      
      // 更新项目统计信息
      updateProjectStats(projectId.value)
      
      // 重新验证所有任务
      await revalidateAllTasks()
      
      // 再次等待，确保任务验证完成后再验证阶段
      await nextTick()
      
      // 重新验证所有阶段的时间异常标记
      revalidateAllStages()
    }
  }

  /**
   * 处理保存操作
   * @returns {Promise<boolean>} 保存是否成功
   */
  const handleSave = async () => {
    try {
      // 1. 显示确认弹窗
      await ElMessageBox.confirm(
        '是否确认保存任务配置？',
        '保存确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      // 用户取消，不执行保存
      return false
    }

    // 2. 调用内部的保存逻辑（包含接口调用、数据更新、弹窗显示）
    const success = await handleSaveInternal()
    
    // 3. 执行保存后的统一处理
    await handleAfterSave(success)
    
    return success
  }

  /**
   * 处理保存并生成操作
   * @returns {Promise<boolean>} 保存是否成功
   */
  const handleSaveAndGenerate = async () => {
    if (!saveWorkflowAndGenerate) {
      ElMessage.error('保存并生成功能未初始化')
      return false
    }

    try {
      // 1. 显示确认弹窗
      await ElMessageBox.confirm(
        '是否确认保存任务并生成？注意：点击确认后，所有允许生成的任务都将直接生成。',
        '保存并生成确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      // 用户取消，不执行保存
      return false
    }

    // 2. 调用保存并生成逻辑（包含接口调用、数据更新、弹窗显示）
    const result = await saveWorkflowAndGenerate(unassignedTasks)
    const success = result?.success ?? false

    // 3. 执行保存后的统一处理
    await handleAfterSave(success)

    return success
  }

  return {
    handleSave,
    handleSaveAndGenerate,
    updateProjectStats,
    revalidateAllTasks
  }
}

