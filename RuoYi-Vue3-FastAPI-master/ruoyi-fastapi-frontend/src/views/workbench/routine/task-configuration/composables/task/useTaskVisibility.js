// composables/task/useTaskVisibility.js
import { computed } from 'vue'

/**
 * 任务可见性控制
 * 用于过滤和显示任务（如过滤拖拽中的任务）
 */
export const useTaskVisibility = (unassignedTasks) => {
  // 过滤掉拖拽中的阶段外任务（避免显示副本）
  // 如果任务有预览版本（_isPreview），则隐藏原始任务（_isDraggingOut）
  const getVisibleUnassignedTasks = computed(() => {
    if (!unassignedTasks.value || !Array.isArray(unassignedTasks.value)) {
      return []
    }
    
    // 找出所有有预览版本的任务ID
    const previewTaskIds = new Set(
      unassignedTasks.value
        .filter(t => t._isPreview)
        .map(t => t.id)
    )
    
    // 过滤：只显示预览任务，或者没有预览版本的非拖拽中任务
    return unassignedTasks.value.filter(task => {
      // 如果是预览任务，总是显示
      if (task._isPreview) return true
      // 如果有预览版本，隐藏原始任务
      if (previewTaskIds.has(task.id)) return false
      // 如果是拖拽中的任务，隐藏
      if (task._isDraggingOut) return false
      // 其他情况显示
      return true
    })
  })

  return {
    getVisibleUnassignedTasks
  }
}

