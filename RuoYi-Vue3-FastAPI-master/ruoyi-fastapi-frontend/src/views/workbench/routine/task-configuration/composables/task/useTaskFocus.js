// composables/task/useTaskFocus.js
import { ElMessage } from 'element-plus'

/**
 * 任务定位功能
 * 用于定位和聚焦到特定任务
 */
export const useTaskFocus = (findTaskById, zoomTo, canvasRef) => {
  /**
   * 定位到指定任务
   * @param {string|number} taskId - 任务ID
   */
  const focusOnTask = (taskId) => {
    const taskInfo = findTaskById(taskId)
    // findTaskById 返回格式：{ task, stage, isUnassigned } 或 null
    if (!taskInfo || !taskInfo.task || !taskInfo.task.position) {
      ElMessage.warning('无法定位该任务')
      return
    }

    const TASK_WIDTH = 198
    const TASK_HEIGHT = 100
    const centerX = taskInfo.task.position.x + TASK_WIDTH / 2
    const centerY = taskInfo.task.position.y + TASK_HEIGHT / 2

    // 使用平滑滚动动画定位到任务
    zoomTo(canvasRef.value, 2, { x: centerX, y: centerY }, { animate: true, duration: 600 })
  }

  return {
    focusOnTask
  }
}

