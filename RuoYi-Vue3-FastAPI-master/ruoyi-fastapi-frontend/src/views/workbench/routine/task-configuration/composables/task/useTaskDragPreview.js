// composables/useTaskDragPreview.js
// 任务拖拽预览相关逻辑

import { useGridSnap } from '../canvas/useGridSnap'

export const useTaskDragPreview = () => {
  const { snapToGrid } = useGridSnap()
  /**
   * 查找预览任务的索引
   * @param {string|number} taskId - 任务ID
   * @param {Array} unassignedTasks - 未分配任务数组
   * @returns {number} 预览任务索引，-1表示未找到
   */
  const findPreviewTaskIndex = (taskId, unassignedTasks) => {
    return unassignedTasks.findIndex(t => t.id === taskId && t._isPreview)
  }

  /**
   * 清除预览任务和拖拽标记
   * @param {string|number} taskId - 任务ID
   * @param {Array} unassignedTasks - 未分配任务数组
   * @param {Function} findTaskById - 查找任务函数
   */
  const clearPreviewTaskAndDragFlag = (taskId, unassignedTasks, findTaskById) => {
    // 先清除预览任务
    const previewIndex = findPreviewTaskIndex(taskId, unassignedTasks)
    if (previewIndex !== -1) {
      unassignedTasks.splice(previewIndex, 1)
    }
    // 然后清除拖拽标记，确保原始任务显示时位置已经更新
    const taskInfo = findTaskById(taskId)
    if (taskInfo?.task?._isDraggingOut) {
      delete taskInfo.task._isDraggingOut
    }
  }

  /**
   * 创建或更新预览任务
   * @param {Object} taskInfo - 任务信息
   * @param {Object} newPosition - 新位置
   * @param {Array} unassignedTasks - 未分配任务数组
   */
  const createOrUpdatePreviewTask = (taskInfo, newPosition, unassignedTasks) => {
    // 确保位置对齐到网格（整数）
    const snappedPosition = snapToGrid(newPosition)
    const previewIndex = findPreviewTaskIndex(taskInfo.task.id, unassignedTasks)
    if (previewIndex !== -1) {
      // 更新现有预览任务的位置 - 直接替换整个 position 对象以确保响应式更新
      const previewTask = unassignedTasks[previewIndex]
      previewTask.position = { x: snappedPosition.x, y: snappedPosition.y }
    } else {
      // 创建新的预览任务
      const previewTask = {
        ...taskInfo.task,
        position: { x: snappedPosition.x, y: snappedPosition.y },
        stageId: null,
        isValidPosition: false,
        _isPreview: true
      }
      delete previewTask._isDraggingOut
      unassignedTasks.push(previewTask)
    }
  }

  return {
    findPreviewTaskIndex,
    clearPreviewTaskAndDragFlag,
    createOrUpdatePreviewTask
  }
}

