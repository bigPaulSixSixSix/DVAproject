import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * 聚合任务编辑弹窗、选项卡、删除等相关操作，供 index.vue 调用
 * @param {Object} options
 */
export const useTaskEditController = (options) => {
  const {
    // task edit composable暴露
    openTaskEditDialog,
    closeTaskEditDialog,
    setActiveTaskTab,
    closeTaskTab,
    isTaskTabDirty,
    markTaskTabAsSaved,
    confirmTaskEdit,
    getCurrentEditingTaskId,
    activeTaskTabId,
    taskEditDialogRef,
    // 业务依赖
    findTaskById,
    deleteTask,
    workflowData,
    unassignedTasks,
    removeAllTaskConnections,
    workflowStore,
    selectedTaskId,
    // 连接相关
    applyConnectionRemoval,
    connections,
    findConnectionByTaskIds
  } = options

  const handleTaskTabSelect = async (taskId) => {
    await setActiveTaskTab(taskId, findTaskById)
  }

  const handleTaskTabClose = async (taskId, { force = false } = {}) => {
    if (!taskId) return false
    if (!force && isTaskTabDirty(taskId)) {
      try {
        await ElMessageBox.confirm('当前任务有未保存的修改，确定要关闭吗？', '提示', {
          type: 'warning'
        })
      } catch (error) {
        return false
      }
    }
    await closeTaskTab(taskId, findTaskById)
    return true
  }

  const handleTaskEdit = async (task) => {
    await openTaskEditDialog(task, findTaskById)
  }

  const handleTaskEditDialogClose = () => {
    closeTaskEditDialog()
  }

  const handleTaskEditCancel = async (skipConfirm = false) => {
    if (!activeTaskTabId.value) return
    // 如果 skipConfirm 为 true，强制关闭（跳过确认）
    await handleTaskTabClose(activeTaskTabId.value, { force: skipConfirm })
  }

  // 内部方法：执行实际的保存逻辑
  const _performTaskEditConfirm = async () => {
    if (!activeTaskTabId.value) return
    const formRef = taskEditDialogRef.value?.formRef
    const success = await confirmTaskEdit(findTaskById, workflowStore, formRef, workflowData)
    if (success) {
      markTaskTabAsSaved(activeTaskTabId.value)
      await handleTaskTabClose(activeTaskTabId.value, { force: true })
    }
  }

  // 公开方法：处理任务编辑确认（会弹出确认框）
  const handleTaskEditConfirm = async (skipConfirm = false) => {
    if (!activeTaskTabId.value) return
    if (!skipConfirm) {
      try {
        await ElMessageBox.confirm('是否保存当前任务的修改？', '保存确认', { type: 'warning' })
      } catch (error) {
        return
      }
    }
    await _performTaskEditConfirm()
  }

  const performTaskDeletion = async (taskId) => {
    await deleteTask(
      taskId,
      workflowData.value,
      unassignedTasks,
      removeAllTaskConnections,
      workflowStore,
      selectedTaskId
    )
    await closeTaskTab(taskId, findTaskById)
  }

  const handleTaskEditDelete = async () => {
    const taskId = getCurrentEditingTaskId()
    if (!taskId) {
      return
    }
    try {
      await ElMessageBox.confirm('删除任务将同时移除所有关联关系，是否继续？', '删除确认', {
        type: 'warning'
      })
    } catch (error) {
      return
    }
    await performTaskDeletion(taskId)
  }

  const handleTaskDelete = async (taskId) => {
    await performTaskDeletion(taskId)
  }

  const handlePredecessorTaskEdit = async (task) => {
    await handleTaskEdit(task)
  }

  const handleSuccessorTaskEdit = async (task) => {
    await handleTaskEdit(task)
  }

  // 通用的删除连接线方法（复用画布上删除连接线的逻辑）
  const deleteConnectionById = async (connectionId) => {
    if (!connectionId) {
      ElMessage.warning('未找到连接关系')
      return
    }

    try {
      await ElMessageBox.confirm('确定要删除这条连接线吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      const result = applyConnectionRemoval(connectionId)
      if (result.success) {
        ElMessage.success('连接线已删除')
      } else {
        ElMessage.error('删除连接线失败')
      }
    } catch {
      // 用户取消
    }
  }

  const handlePredecessorTaskUnlink = async (predecessorTask) => {
    const currentTaskId = getCurrentEditingTaskId()
    if (!currentTaskId || !predecessorTask || !predecessorTask.id) {
      ElMessage.error('无法获取任务信息')
      return
    }

    // 前置任务 -> 当前任务（from: 前置任务, to: 当前任务）
    const connectionId = findConnectionByTaskIds(predecessorTask.id, currentTaskId, connections.value)
    await deleteConnectionById(connectionId)
  }

  const handleSuccessorTaskUnlink = async (successorTask) => {
    const currentTaskId = getCurrentEditingTaskId()
    if (!currentTaskId || !successorTask || !successorTask.id) {
      ElMessage.error('无法获取任务信息')
      return
    }

    // 当前任务 -> 后置任务（from: 当前任务, to: 后置任务）
    const connectionId = findConnectionByTaskIds(currentTaskId, successorTask.id, connections.value)
    await deleteConnectionById(connectionId)
  }

  const handlePredecessorTaskDelete = async (task) => {
    await handleTaskDelete(task.id)
  }

  const handleSuccessorTaskDelete = async (task) => {
    await handleTaskDelete(task.id)
  }

  return {
    handleTaskTabSelect,
    handleTaskTabClose,
    handleTaskEdit,
    handleTaskEditDialogClose,
    handleTaskEditCancel,
    handleTaskEditConfirm,
    handleTaskEditDelete,
    handleTaskDelete,
    handlePredecessorTaskEdit,
    handlePredecessorTaskUnlink,
    handlePredecessorTaskDelete,
    handleSuccessorTaskEdit,
    handleSuccessorTaskUnlink,
    handleSuccessorTaskDelete
  }
}

