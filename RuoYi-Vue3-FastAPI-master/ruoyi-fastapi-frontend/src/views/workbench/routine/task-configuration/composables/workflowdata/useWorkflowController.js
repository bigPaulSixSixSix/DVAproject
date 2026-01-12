import { ElMessage } from 'element-plus'
import { nextTick } from 'vue'

/**
 * 工作流控制器
 * 处理工作流的保存、创建等操作
 */
export const useWorkflowController = ({
  workflowData,
  workflowStore,
  unassignedTasks,
  selectedStageId,
  selectedTaskId,
  selectedConnectionId,
  validateBeforeSave,
  saveWorkflow,
  createStageAtPosition,
  createTaskAtPosition,
  initConnectionsFromWorkflow = null
}) => {
  const handleUndo = () => {
    ElMessage.info('撤销功能待实现')
  }

  const handleSave = async () => {
    if (!workflowData.value || !workflowData.value.stages) {
      ElMessage.error('工作流数据未初始化')
      return false
    }

    // 不再阻止保存，允许有阶段外任务
    const validation = validateBeforeSave(unassignedTasks.value)
    // 即使有阶段外任务也允许保存，不再阻止

    // 保存时直接传入 unassignedTasks ref
    // saveWorkflow 会直接使用内部的 workflowData ref（和这里的 workflowData 是同一个）
    const result = await saveWorkflow(unassignedTasks)
    
    // saveWorkflow 已经更新了内部的 workflowData ref（和这里的 workflowData 是同一个）
    // 所以不需要再次更新，只需要返回结果
    return result?.success ?? false
  }

  const handleCanvasClick = () => {
    selectedStageId.value = null
    selectedTaskId.value = null
    selectedConnectionId.value = null
    workflowStore.clearSelection()
  }

  const handleCreateStage = (position) => {
    createStageAtPosition(position, workflowData.value, workflowStore)
  }

  const handleCreateTask = (position, targetStage) => {
    createTaskAtPosition(position, targetStage, workflowData.value, unassignedTasks, workflowStore)
  }

  return {
    handleUndo,
    handleSave,
    handleCanvasClick,
    handleCreateStage,
    handleCreateTask
  }
}

