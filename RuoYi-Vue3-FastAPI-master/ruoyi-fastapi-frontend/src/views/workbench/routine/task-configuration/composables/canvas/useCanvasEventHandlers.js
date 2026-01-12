// composables/useCanvasEventHandlers.js

/**
 * 画布事件处理器
 * 统一管理画布相关的简单事件处理函数
 * 这些函数主要是简单的 emit 转发，保持组件代码简洁
 */
export const useCanvasEventHandlers = (emit) => {
  // 工具栏操作
  const handleUndo = () => {
    emit('undo')
  }

  const handleSave = () => {
    emit('save')
  }

  const handleSaveAndGenerate = () => {
    emit('save-and-generate')
  }

  const handleOrganizeLayout = () => {
    emit('organize-layout')
  }

  // 画布交互
  const handleCanvasClick = () => {
    emit('canvas-click')
  }

  // 阶段相关
  const handleStageSelect = (stageId) => {
    emit('stage-select', stageId)
  }

  const handleStageEdit = (stage) => {
    emit('stage-edit', stage)
  }

  const handleStageDelete = (stageId) => {
    emit('stage-delete', stageId)
  }

  const handleStageResizeEnd = (data) => {
    emit('stage-resize-end', data)
  }

  const handleStagePositionChange = (data) => {
    emit('stage-position-change', data)
  }

  // 任务相关
  const handleTaskSelect = (taskId) => {
    emit('task-select', taskId)
  }

  const handleTaskEdit = (task) => {
    emit('task-edit', task)
  }

  const handleTaskDelete = (taskId) => {
    emit('task-delete', taskId)
  }

  // 连接相关
  const handleConnectionStart = (data) => {
    emit('connection-start', data)
  }

  const handleConnectionPanelEnd = (data) => {
    emit('connection-panel-end', data)
  }

  const handleConnectionMove = (data) => {
    emit('connection-move', data)
  }

  const handleConnectionCancel = () => {
    emit('connection-cancel')
  }

  const handleConnectionSelect = (connectionId) => {
    emit('connection-select', connectionId)
  }

  const handleConnectionDelete = (connectionId) => {
    emit('connection-delete', connectionId)
  }

  return {
    // 工具栏
    handleUndo,
    handleSave,
    handleSaveAndGenerate,
    handleOrganizeLayout,
    // 画布
    handleCanvasClick,
    // 阶段
    handleStageSelect,
    handleStageEdit,
    handleStageDelete,
    handleStageResizeEnd,
    handleStagePositionChange,
    // 任务
    handleTaskSelect,
    handleTaskEdit,
    handleTaskDelete,
    // 连接
    handleConnectionStart,
    handleConnectionPanelEnd,
    handleConnectionMove,
    handleConnectionCancel,
    handleConnectionSelect,
    handleConnectionDelete
  }
}

