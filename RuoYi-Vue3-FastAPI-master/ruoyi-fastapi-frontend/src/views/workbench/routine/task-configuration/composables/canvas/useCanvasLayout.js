// composables/useCanvasLayout.js
import { computed } from 'vue'

/**
 * 画布布局计算相关功能
 * 包括画布尺寸计算、包装器样式等
 */
export const useCanvasLayout = (props, zoomLevel) => {
  // 计算画布尺寸（基于所有元素的位置）
  const canvasSize = computed(() => {
    const EXTRA_PADDING = 400 // 额外缓冲空间
    const MIN_WIDTH = 5000 // 最小宽度
    const MIN_HEIGHT = 5000 // 最小高度
    
    let maxX = 0
    let maxY = 0
    
    // 检查所有阶段
    if (props.stages && props.stages.length > 0) {
      props.stages.forEach(stage => {
        if (stage.position) {
          const stageRight = stage.position.x + (stage.position.width || 0)
          const stageBottom = stage.position.y + (stage.position.height || 0)
          maxX = Math.max(maxX, stageRight)
          maxY = Math.max(maxY, stageBottom)
          
          // 检查阶段内的任务
          if (stage.tasks && stage.tasks.length > 0) {
            stage.tasks.forEach(task => {
              if (task.position) {
                const TASK_WIDTH = 196
                const TASK_HEIGHT = 100
                const taskRight = task.position.x + TASK_WIDTH
                const taskBottom = task.position.y + TASK_HEIGHT
                maxX = Math.max(maxX, taskRight)
                maxY = Math.max(maxY, taskBottom)
              }
            })
          }
        }
      })
    }
    
    // 检查阶段外任务
    if (props.unassignedTasks && props.unassignedTasks.length > 0) {
      props.unassignedTasks.forEach(task => {
        // 跳过预览任务和拖拽中的任务
        if (task._isPreview || task._isDraggingOut) return
        
        if (task.position) {
          const TASK_WIDTH = 196
          const TASK_HEIGHT = 100
          const taskRight = task.position.x + TASK_WIDTH
          const taskBottom = task.position.y + TASK_HEIGHT
          maxX = Math.max(maxX, taskRight)
          maxY = Math.max(maxY, taskBottom)
        }
      })
    }
    
    // 计算最终尺寸：如果元素超出当前画布，则扩容（超出部分 + 400px额外空间）
    // 否则使用最小尺寸
    const width = maxX > MIN_WIDTH ? maxX + EXTRA_PADDING : MIN_WIDTH
    const height = maxY > MIN_HEIGHT ? maxY + EXTRA_PADDING : MIN_HEIGHT
    
    return {
      width: `${width}px`,
      height: `${height}px`
    }
  })

  // canvas-wrapper 的样式
  const canvasWrapperStyle = computed(() => ({
    transform: `scale(${zoomLevel.value})`,
    transformOrigin: 'top left',
    width: canvasSize.value.width,
    height: canvasSize.value.height
  }))

  return {
    canvasSize,
    canvasWrapperStyle
  }
}

