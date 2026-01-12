/**
 * 阶段相关交互控制器，将 index.vue 中的阶段逻辑集中到此
 */
export const useStageController = ({
  workflowData,
  workflowStore,
  selectedStageId,
  selectedTaskId,
  selectedConnectionId,
  connectionsRef = null,
  stageEditDialogVisible,
  addStage,
  selectStage,
  deleteStage,
  resizeStage,
  changeStagePosition,
  openStageEditDialog,
  closeStageEditDialog,
  confirmStageEdit,
  getCurrentEditingStageId,
  findStageById
}) => {
  const handleAddStage = () => {
    addStage(workflowData.value, workflowStore)
  }

  const handleStageSelect = (stageId) => {
    selectStage(stageId, selectedStageId, selectedTaskId, workflowStore, selectedConnectionId)
  }

  const handleStageEdit = (stage) => {
    openStageEditDialog(stage)
  }

  const handleStageEditDialogClose = () => {
    closeStageEditDialog()
  }

  const handleStageEditCancel = () => {
    stageEditDialogVisible.value = false
  }

  // 内部方法：执行实际的保存逻辑
  const _performStageEditConfirm = async () => {
    const success = await confirmStageEdit(findStageById, workflowStore)
    if (success) {
      stageEditDialogVisible.value = false
    }
  }

  // 公开方法：处理阶段编辑确认（会弹出确认框）
  const handleStageEditConfirm = async (skipConfirm = false) => {
    if (!skipConfirm) {
      // 阶段编辑不需要确认框，直接保存
      // 但为了保持一致性，这里可以添加确认框
      // 目前阶段编辑没有确认框，所以直接执行
    }
    await _performStageEditConfirm()
  }

  const handleStageEditDelete = async () => {
    const stageId = getCurrentEditingStageId()
    if (!stageId) {
      return
    }
    stageEditDialogVisible.value = false
    await handleStageDelete(stageId)
  }

  const handleStageDelete = async (stageId) => {
    await deleteStage(stageId, workflowData.value, workflowStore, selectedStageId, connectionsRef)
  }

  const handleStageResizeEnd = (data) => {
    resizeStage(data, workflowData.value, workflowStore)
  }

  const handleStagePositionChange = (data) => {
    changeStagePosition(data, workflowData.value, workflowStore)
  }

  return {
    handleAddStage,
    handleStageSelect,
    handleStageEdit,
    handleStageEditDialogClose,
    handleStageEditCancel,
    handleStageEditConfirm,
    handleStageEditDelete,
    handleStageDelete,
    handleStageResizeEnd,
    handleStagePositionChange
  }
}

