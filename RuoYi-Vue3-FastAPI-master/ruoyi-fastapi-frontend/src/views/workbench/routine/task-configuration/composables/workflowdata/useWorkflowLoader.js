// composables/useWorkflowLoader.js
import { ElMessage } from 'element-plus'
import { fetchWorkflowByProjectId } from '@/api/workflow'

export const useWorkflowLoader = () => {
  /**
   * 加载工作流数据
   * @param {string|number} projectId - 项目ID
   * @param {Object} loadingRef - loading状态ref
   * @param {Object} workflowDataRef - 工作流数据ref
   * @param {Function} toFrontendFormat - 数据格式转换函数
   * @param {Object} workflowStore - 工作流store
   * @param {Function} startAutoSave - 启动自动保存函数
   * @param {Object} unassignedTasksRef - 阶段外任务数组的ref（可选）
   */
  const loadWorkflowData = async (
    projectId,
    loadingRef,
    workflowDataRef,
    toFrontendFormat,
    workflowStore,
    startAutoSave,
    unassignedTasksRef = null
  ) => {
    loadingRef.value = true
    try {
      // 调用后端接口获取数据
      const response = await fetchWorkflowByProjectId(projectId)
      
      // 检查响应数据
      const backendWorkflow = response?.data ?? response
      if (!backendWorkflow) {
        workflowDataRef.value = {
          projectId: projectId,
          name: '',
          stages: []
        }
        return
      }

      const formattedData = toFrontendFormat(backendWorkflow)
      workflowDataRef.value = {
        ...formattedData,
        projectId: projectId
      }
      // 确保projectId存在
      workflowDataRef.value.projectId = projectId
      
      // 更新阶段外的任务
      if (unassignedTasksRef && formattedData.unassignedTasks) {
        unassignedTasksRef.value = formattedData.unassignedTasks.map(task => ({
          ...task,
          projectId: task.projectId || projectId
        }))
      }
      
      // workflowStore 的主数据源引用应该在 index.vue 中初始化
      // 这里不需要额外操作，因为 workflowStore 的方法会直接操作主数据源
      
      // 启动自动保存
      startAutoSave(workflowDataRef)
      
      // 返回 tasksGenerated，供外部使用
      return formattedData.tasksGenerated ?? false
    } catch (error) {
      ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
      // 确保工作流数据不为空
      workflowDataRef.value = {
        projectId: projectId,
        name: '',
        stages: []
      }
    } finally {
      loadingRef.value = false
    }
  }

  return {
    loadWorkflowData
  }
}

