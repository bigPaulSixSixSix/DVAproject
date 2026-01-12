// composables/task/useAbnormalTaskDialog.js
import { ref } from 'vue'

/**
 * 异常任务对话框管理
 * 管理异常任务对话框的显示状态和交互
 */
export const useAbnormalTaskDialog = (abnormalTaskCount, focusOnTask) => {
  const abnormalDialogVisible = ref(false)

  // 打开异常任务对话框
  const handleAbnormalButtonClick = () => {
    if (abnormalTaskCount.value === 0) return
    abnormalDialogVisible.value = true
  }

  // 定位异常任务并关闭对话框
  const handleFocusAbnormalTask = (taskId) => {
    focusOnTask(taskId)
    abnormalDialogVisible.value = false
  }

  return {
    abnormalDialogVisible,
    handleAbnormalButtonClick,
    handleFocusAbnormalTask
  }
}

