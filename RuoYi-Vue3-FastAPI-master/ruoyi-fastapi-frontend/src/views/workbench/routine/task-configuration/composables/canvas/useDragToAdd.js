// composables/useDragToAdd.js
import { ref, computed } from 'vue'
import { useGridSnap } from './useGridSnap'
import { ElMessage, ElMessageBox } from 'element-plus'

/**
 * 拖拽添加功能
 * 处理从工具栏按钮拖拽到画布创建阶段/任务的逻辑
 */
export const useDragToAdd = () => {
  const { snapToGrid, gridSize } = useGridSnap()
  
  // 拖拽状态
  const isDraggingToAdd = ref(false)
  const dragType = ref(null) // 'stage' 或 'task'
  const previewPosition = ref({ x: 0, y: 0 })
  const mousePosition = ref({ x: 0, y: 0 })
  const overlappingStageId = ref(null) // 如果拖拽到阶段上，记录阶段ID
  
  // 阶段最小尺寸
  const STAGE_MIN_WIDTH = 400
  const STAGE_MIN_HEIGHT = 250
  
  // 任务尺寸
  const TASK_WIDTH = 196
  const TASK_HEIGHT = 100
  
  /**
   * 检查两个矩形是否重叠
   */
  const isRectOverlapping = (rect1, rect2) => {
    return !(
      rect1.x + rect1.width <= rect2.x ||
      rect2.x + rect2.width <= rect1.x ||
      rect1.y + rect1.height <= rect2.y ||
      rect2.y + rect2.height <= rect1.y
    )
  }
  
  /**
   * 检查点是否在矩形内
   */
  const isPointInRect = (point, rect) => {
    return (
      point.x >= rect.x &&
      point.x <= rect.x + rect.width &&
      point.y >= rect.y &&
      point.y <= rect.y + rect.height
    )
  }
  
  /**
   * 检查任务中心点是否在阶段内
   */
  const isTaskInStage = (taskPosition, stage) => {
    const taskCenterX = taskPosition.x + TASK_WIDTH / 2
    const taskCenterY = taskPosition.y + TASK_HEIGHT / 2
    
    const stageRect = {
      x: stage.position.x,
      y: stage.position.y,
      width: stage.position.width || 300,
      height: stage.position.height || 200
    }
    
    return isPointInRect({ x: taskCenterX, y: taskCenterY }, stageRect)
  }
  
  /**
   * 检查阶段是否与已有阶段重叠
   */
  const checkStageOverlap = (position, stages, excludeStageId = null) => {
    const newStageRect = {
      x: position.x,
      y: position.y,
      width: STAGE_MIN_WIDTH,
      height: STAGE_MIN_HEIGHT
    }
    
    for (const stage of stages) {
      if (excludeStageId && stage.id === excludeStageId) continue
      
      const existingStageRect = {
        x: stage.position.x,
        y: stage.position.y,
        width: stage.position.width || 300,
        height: stage.position.height || 200
      }
      
      if (isRectOverlapping(newStageRect, existingStageRect)) {
        return stage
      }
    }
    
    return null
  }
  
  /**
   * 查找任务应该放置的阶段
   */
  const findTargetStageForTask = (position, stages) => {
    for (const stage of stages) {
      if (isTaskInStage(position, stage)) {
        return stage
      }
    }
    return null
  }
  
  /**
   * 将画布坐标转换为考虑缩放后的坐标
   * @param {number} canvasX - 屏幕坐标 X
   * @param {number} canvasY - 屏幕坐标 Y
   * @param {HTMLElement} canvasElement - 画布元素
   * @param {number} zoomLevel - 缩放级别
   * @returns {Object} 世界坐标 { x, y }
   */
  const canvasToWorld = (canvasX, canvasY, canvasElement, zoomLevel) => {
    if (!canvasElement) return { x: 0, y: 0 }
    
    // 获取画布元素相对于视口的位置（不受 CSS transform 影响）
    const rect = canvasElement.getBoundingClientRect()
    const scrollLeft = canvasElement.scrollLeft || 0
    const scrollTop = canvasElement.scrollTop || 0
    
    // 计算鼠标相对于画布的位置（考虑滚动）
    const relativeX = canvasX - rect.left + scrollLeft
    const relativeY = canvasY - rect.top + scrollTop
    
    // 转换为世界坐标（除以缩放级别）
    // 因为 canvas-wrapper 有 transform: scale(zoomLevel)，所以需要除以缩放级别
    const worldX = relativeX / zoomLevel
    const worldY = relativeY / zoomLevel
    
    return { x: worldX, y: worldY }
  }
  
  /**
   * 开始拖拽添加
   */
  const startDragToAdd = (type) => {
    isDraggingToAdd.value = true
    dragType.value = type
    overlappingStageId.value = null
  }
  
  /**
   * 更新拖拽位置
   */
  const updateDragPosition = (event, canvasElement, zoomLevel, stages) => {
    if (!isDraggingToAdd.value) return
    
    const worldPos = canvasToWorld(event.clientX, event.clientY, canvasElement, zoomLevel)
    mousePosition.value = worldPos
    
    // 计算元素中心点对齐的位置
    // 鼠标位置应该对应元素的中心点，而不是左上角
    let centerAlignedPos
    if (dragType.value === 'stage') {
      centerAlignedPos = {
        x: worldPos.x - STAGE_MIN_WIDTH / 2,
        y: worldPos.y - STAGE_MIN_HEIGHT / 2
      }
    } else {
      centerAlignedPos = {
        x: worldPos.x - TASK_WIDTH / 2,
        y: worldPos.y - TASK_HEIGHT / 2
      }
    }
    
    // 网格对齐
    const snappedPos = snapToGrid(centerAlignedPos)
    previewPosition.value = snappedPos
    
    // 检查重叠
    if (dragType.value === 'stage') {
      const overlappingStage = checkStageOverlap(snappedPos, stages)
      overlappingStageId.value = overlappingStage ? overlappingStage.id : null
    } else {
      overlappingStageId.value = null
    }
  }
  
  /**
   * 结束拖拽并创建元素
   */
  const endDragToAdd = async (event, canvasElement, zoomLevel, stages, onCreateStage, onCreateTask) => {
    if (!isDraggingToAdd.value) return
    
    const worldPos = canvasToWorld(event.clientX, event.clientY, canvasElement, zoomLevel)
    
    // 计算元素中心点对齐的位置（与 updateDragPosition 保持一致）
    let centerAlignedPos
    if (dragType.value === 'stage') {
      centerAlignedPos = {
        x: worldPos.x - STAGE_MIN_WIDTH / 2,
        y: worldPos.y - STAGE_MIN_HEIGHT / 2
      }
    } else {
      centerAlignedPos = {
        x: worldPos.x - TASK_WIDTH / 2,
        y: worldPos.y - TASK_HEIGHT / 2
      }
    }
    
    const snappedPos = snapToGrid(centerAlignedPos)
    
    // 检查阶段重叠
    if (dragType.value === 'stage') {
      const overlappingStage = checkStageOverlap(snappedPos, stages)
      if (overlappingStage) {
        await ElMessageBox.alert(
          '不允许在已有阶段上创建新阶段，请选择其他位置',
          '提示',
          {
            confirmButtonText: '确定',
            type: 'warning'
          }
        )
        resetDragToAdd()
        return
      }
      
      // 创建阶段
      onCreateStage(snappedPos)
    } else if (dragType.value === 'task') {
      // 查找目标阶段
      const targetStage = findTargetStageForTask(snappedPos, stages)
      
      // 创建任务
      onCreateTask(snappedPos, targetStage)
    }
    
    resetDragToAdd()
  }
  
  /**
   * 取消拖拽
   */
  const cancelDragToAdd = () => {
    resetDragToAdd()
  }
  
  /**
   * 重置拖拽状态
   */
  const resetDragToAdd = () => {
    isDraggingToAdd.value = false
    dragType.value = null
    previewPosition.value = { x: 0, y: 0 }
    mousePosition.value = { x: 0, y: 0 }
    overlappingStageId.value = null
  }
  
  /**
   * 计算预览元素的样式
   */
  const previewStyle = computed(() => {
    if (!isDraggingToAdd.value) return null
    
    if (dragType.value === 'stage') {
      return {
        left: `${previewPosition.value.x}px`,
        top: `${previewPosition.value.y}px`,
        width: `${STAGE_MIN_WIDTH}px`,
        height: `${STAGE_MIN_HEIGHT}px`
      }
    } else {
      return {
        left: `${previewPosition.value.x}px`,
        top: `${previewPosition.value.y}px`,
        width: `${TASK_WIDTH}px`,
        height: `${TASK_HEIGHT}px`
      }
    }
  })
  
  /**
   * 预览元素是否有效（阶段不重叠，任务可以放置）
   */
  const isPreviewValid = computed(() => {
    if (!isDraggingToAdd.value) return false
    
    if (dragType.value === 'stage') {
      return overlappingStageId.value === null
    } else {
      return true // 任务总是可以创建
    }
  })
  
  return {
    // 状态
    isDraggingToAdd,
    dragType,
    previewPosition,
    mousePosition,
    overlappingStageId,
    previewStyle,
    isPreviewValid,
    
    // 方法
    startDragToAdd,
    updateDragPosition,
    endDragToAdd,
    cancelDragToAdd,
    resetDragToAdd,
    
    // 常量
    STAGE_MIN_WIDTH,
    STAGE_MIN_HEIGHT,
    TASK_WIDTH,
    TASK_HEIGHT
  }
}

