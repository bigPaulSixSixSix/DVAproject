// composables/canvas/useDragDrop.js
import { useGridSnap } from './useGridSnap'
import { useTaskValidation } from '../task/useTaskValidation'
import { ElMessage } from 'element-plus'

export const useDragDrop = () => {
  const { snapToGrid, gridSize } = useGridSnap()
  const { validateTaskInRealTime } = useTaskValidation()
  
  // 约束位置，确保不超出画布左边界（x >= 0）和上边界（y >= 0）
  const constrainToCanvasBounds = (position) => {
    const constrained = {
      x: Math.max(0, position.x),
      y: Math.max(0, position.y)
    }
    // 确保约束后的位置对齐到网格（整数）
    return snapToGrid(constrained)
  }
  
  // 约束任务位置，使其不超出阶段边界，但允许完全显示
  // 注意：返回的位置会自动对齐到网格，确保是整数
  const constrainTaskToStage = (taskPosition, stage) => {
    const TASK_WIDTH = 196 // 调整为 198px，使得 偏置(2px) + 宽度(198px) = 200px = 8的倍数，右边界对齐网格
    const TASK_HEIGHT = 100
    const HEADER_HEIGHT = 60
    const BORDER_WIDTH = 4 // stage-card 的边框宽度，使用 border-box
    
    // 阶段"内容区"边界
    // 任务的坐标系统相对于 stage.position（外边界）定义
    // stage.position.x 是左外边界，stage.position.y 是上外边界
    // 由于使用 border-box，width 和 height 包含了边框
    // 左边界和上边界：使用外边界（已验证正确）
    // 右边界和底边界：需要减去边框宽度，得到内容区的实际右/底边界
    const stageLeft = stage.position.x
    const stageTop = stage.position.y + HEADER_HEIGHT
    // 右边界：外边界 + 宽度 - 边框（因为 width 包含边框，右外边界 - 边框 = 内容区右边界）
    const stageRight = stage.position.x + stage.position.width - BORDER_WIDTH
    // 底边界：外边界 + 高度 - 边框（因为 height 包含边框，底外边界 - 边框 = 内容区底边界）
    const stageBottom = stage.position.y + stage.position.height - BORDER_WIDTH
    
    // 任务边界
    const taskLeft = taskPosition.x
    const taskTop = taskPosition.y
    const taskRight = taskPosition.x + TASK_WIDTH
    const taskBottom = taskPosition.y + TASK_HEIGHT
    
    let constrainedX = taskPosition.x
    let constrainedY = taskPosition.y
    
    // 水平约束：如果任务超出左边界，让它紧贴左边界
    if (taskLeft < stageLeft) {
      constrainedX = stageLeft
    }
    // 如果任务超出右边界，让它紧贴右边界
    if (taskRight > stageRight) {
      constrainedX = stageRight - TASK_WIDTH
    }
    
    // 垂直约束：如果任务超出上边界，让它紧贴上边界
    if (taskTop < stageTop) {
      constrainedY = stageTop
    }
    // 如果任务超出下边界，让它紧贴下边界
    if (taskBottom > stageBottom) {
      constrainedY = stageBottom - TASK_HEIGHT
    }
    
    // 确保约束后的位置对齐到网格（整数），避免小数坐标
    const constrained = { x: constrainedX, y: constrainedY }
    return snapToGrid(constrained)
  }
  
  // 找到任务所在的阶段
  const findTaskStage = (task, stages) => {
    for (const stage of stages) {
      if (stage.tasks && stage.tasks.some(t => t.id === task.id)) {
        return stage
      }
    }
    return null
  }
  
  // 根据绝对坐标查找任务所在的阶段（用于检查目标位置）
  // 支持两种模式：
  // 1. 如果传入的是任务位置（有 width/height），使用任务左上角和中心点判断
  // 2. 如果传入的是鼠标位置（点），直接判断点是否在阶段内
  const findStageByPosition = (absolutePosition, stages) => {
    if (!stages || stages.length === 0) return null
    
    // 判断是点位置还是任务位置
    const isPoint = !absolutePosition.width && !absolutePosition.height
    
    let taskRect
    if (isPoint) {
      // 鼠标位置：使用一个很小的矩形来表示点
      taskRect = {
        x: absolutePosition.x,
        y: absolutePosition.y,
        width: 1,
        height: 1
      }
    } else {
      // 任务位置：使用传入的宽度和高度
      taskRect = {
        x: absolutePosition.x,
        y: absolutePosition.y,
        width: absolutePosition.width || 198,
        height: absolutePosition.height || 100
      }
    }
    
    for (const stage of stages) {
      const stageRect = {
        x: stage.position.x,
        y: stage.position.y,
        width: stage.position.width || 300,
        height: stage.position.height || 200
      }
      
      if (isPoint) {
        // 对于鼠标位置，直接判断点是否在阶段内（包括头部区域）
        // 注意：阶段头部高度是 60px，但鼠标位置判断应该包括整个阶段区域
        if (taskRect.x >= stageRect.x &&
            taskRect.x <= stageRect.x + stageRect.width &&
            taskRect.y >= stageRect.y &&
            taskRect.y <= stageRect.y + stageRect.height) {
          return stage
        }
      } else {
        // 对于任务位置，检查任务左上角或中心点是否在阶段内
        const taskLeft = taskRect.x
        const taskTop = taskRect.y
        const taskCenterX = taskRect.x + taskRect.width / 2
        const taskCenterY = taskRect.y + taskRect.height / 2
        
        const leftTopInStage = taskLeft >= stageRect.x &&
                               taskLeft <= stageRect.x + stageRect.width &&
                               taskTop >= stageRect.y &&
                               taskTop <= stageRect.y + stageRect.height
        
        const centerInStage = taskCenterX >= stageRect.x &&
                              taskCenterX <= stageRect.x + stageRect.width &&
                              taskCenterY >= stageRect.y &&
                              taskCenterY <= stageRect.y + stageRect.height
        
        if (leftTopInStage || centerInStage) {
          return stage
        }
      }
    }
    
    return null
  }
  
  const handleTaskDrag = (task, stages, zoomLevel, onDragEnd) => {
    let isDragging = false
    let startPosition = null
    let initialPosition = null
    let canvas = null
    let canvasRect = null
    let taskElement = null
    
    // 拖拽过程中的位置更新回调（只用于视觉更新，不触发确认对话框）
    const onDragUpdate = (taskId, newPosition, isValid, targetStage) => {
      onDragEnd(taskId, newPosition, isValid, false, targetStage) // false 表示不是最终确认
    }
    
    // 拖拽结束时的最终确认回调（只在 mouseup 时调用）
    const onDragFinal = (taskId, newPosition, isValid, targetStage) => {
      onDragEnd(taskId, newPosition, isValid, true, targetStage) // true 表示是最终确认
    }
    
    const handleMouseDown = (event) => {
      event.preventDefault()
      event.stopPropagation()
      
      isDragging = true
      // 在拖拽开始时设置 _isDragging 标记，禁用 transition
      if (task && !task._isDragging) {
        task._isDragging = true
      }
      
      // 获取画布相对于窗口的位置
      canvas = event.target.closest('.workflow-canvas')
      if (!canvas) return
      
      // 缓存任务元素，用于添加/移除 dragging 类
      taskElement = event.target.closest('.task-card')
      if (taskElement) {
        taskElement.classList.add('task-card--dragging')
      }
      
      canvasRect = canvas.getBoundingClientRect()
      const scrollLeft = canvas.scrollLeft || 0
      const scrollTop = canvas.scrollTop || 0
      
      // 计算起始位置（考虑缩放和滚动）
      const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
      
      startPosition = { x: relativeX, y: relativeY }
      
      // 判断任务是否在阶段内：检查 stageId 属性
      // 如果 stageId 为 null 或 undefined，说明任务在阶段外，task.position 已经是绝对坐标
      // 如果 stageId 存在，说明任务在阶段内，task.position 是相对坐标（因为 task 来自 getTaskWithRelativePosition）
      const HEADER_HEIGHT = 60
      if (task.stageId != null) {
        // 任务在阶段内：task.position 是相对坐标，需要转换为绝对坐标
        const taskStage = findTaskStage(task, stages)
        if (taskStage) {
          // 将相对坐标转换为绝对坐标作为 initialPosition
          initialPosition = {
            x: task.position.x + taskStage.position.x,
            y: task.position.y + taskStage.position.y + HEADER_HEIGHT
          }
        } else {
          // 如果找不到阶段，但 stageId 存在，可能是数据不一致，使用相对坐标作为后备方案
          initialPosition = { ...task.position }
        }
      } else {
        // 任务在阶段外：task.position 已经是绝对坐标，直接使用
        initialPosition = { ...task.position }
      }
      
      // 添加全局事件监听
      document.addEventListener('mousemove', handleMouseMove, { passive: false })
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    let rafId = null
    let lastMouseX = 0
    let lastMouseY = 0
    
    const updatePosition = () => {
      if (!isDragging || !canvas) return
      
      // 更新 canvasRect（可能因为滚动改变）
      canvasRect = canvas.getBoundingClientRect()
      const scrollLeft = canvas.scrollLeft || 0
      const scrollTop = canvas.scrollTop || 0
      
      // 使用最新的鼠标位置（从 handleMouseMove 传入）
      const relativeX = (lastMouseX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (lastMouseY - canvasRect.top + scrollTop) / zoomLevel.value
      
      // 计算偏移量
      const deltaX = relativeX - startPosition.x
      const deltaY = relativeY - startPosition.y
      
      let newPosition = {
        x: initialPosition.x + deltaX,
        y: initialPosition.y + deltaY
      }
      
      // 应用网格对齐
      newPosition = snapToGrid(newPosition)
      
      // 约束到画布边界（确保不超出左侧和上侧）
      newPosition = constrainToCanvasBounds(newPosition)
      
      // 使用鼠标位置来判断是否在阶段内（而不是任务位置），这样可以更准确地反映用户意图
      // 鼠标位置代表用户想要放置任务的位置
      const mousePosition = { x: relativeX, y: relativeY }
      const targetStage = findStageByPosition(mousePosition, stages)
      
      // 检查已生成任务的限制：如果任务不可编辑，不允许移出原阶段
      if (task.isEditable === false && task.stageId != null) {
        // 如果目标位置不在阶段内，或者目标阶段不是原阶段，禁止移动
        if (!targetStage || String(targetStage.id) !== String(task.stageId)) {
          // 禁止移动，不更新位置，直接返回
          return
        }
      }
      
      // 如果鼠标位置在阶段内：应用约束，然后转换为相对坐标
      if (targetStage) {
        const HEADER_HEIGHT = 60
        // newPosition 是绝对坐标（因为 initialPosition 是绝对坐标），直接进行约束
        const constrained = constrainTaskToStage(newPosition, targetStage)
        // 再次约束到画布边界（阶段约束后可能超出边界）
        const finalConstrained = constrainToCanvasBounds(constrained)
        // 转换为相对坐标（相对于 stage-content）：x 相对于 stage 左边界，y 相对于 stage-content 顶部（需要减去 HEADER_HEIGHT）
        newPosition = {
          x: finalConstrained.x - targetStage.position.x,
          y: finalConstrained.y - targetStage.position.y - HEADER_HEIGHT
        }
        // 传递相对坐标和有效状态（拖拽过程中，不触发确认对话框）
        onDragUpdate(task.id, newPosition, true, targetStage)
      } else {
        // 如果鼠标位置不在任何阶段内：直接使用绝对坐标，不应用约束
        // 传递绝对坐标和无效状态（表示在阶段外，拖拽过程中，不触发确认对话框）
        onDragUpdate(task.id, newPosition, false, null)
      }
      
      rafId = null
    }
    
    const handleMouseMove = (event) => {
      if (!isDragging) return
      event.preventDefault()
      event.stopPropagation()
      
      // 直接更新鼠标位置
      lastMouseX = event.clientX
      lastMouseY = event.clientY
      
      // 使用 requestAnimationFrame 节流，但确保每次都会更新
      // 如果已经有 pending 的 RAF，取消它并重新调度，确保使用最新的鼠标位置
      if (rafId !== null) {
        cancelAnimationFrame(rafId)
      }
      rafId = requestAnimationFrame(updatePosition)
    }
    
    const handleMouseUp = (event) => {
      if (!isDragging) return
      event.preventDefault()
      event.stopPropagation()
      
      isDragging = false
      
      // 移除 dragging 类
      if (taskElement) {
        taskElement.classList.remove('task-card--dragging')
        taskElement = null
      }
      
      // 取消 pending 的 RAF
      if (rafId !== null) {
        cancelAnimationFrame(rafId)
        rafId = null
      }
      
      // 获取画布位置
      if (canvas) {
        canvasRect = canvas.getBoundingClientRect()
        const scrollLeft = canvas.scrollLeft || 0
        const scrollTop = canvas.scrollTop || 0
        
        // 计算当前位置（考虑缩放和滚动）
        const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
        const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
        
        // 计算偏移量
        const deltaX = relativeX - startPosition.x
        const deltaY = relativeY - startPosition.y
        
        let newPosition = snapToGrid({
          x: initialPosition.x + deltaX,
          y: initialPosition.y + deltaY
        })
        
        // 约束到画布边界（确保不超出左侧和上侧）
        newPosition = constrainToCanvasBounds(newPosition)
        
        // 使用鼠标位置来判断是否在阶段内（而不是任务位置），这样可以更准确地反映用户意图
        const mousePosition = { x: relativeX, y: relativeY }
        const targetStage = findStageByPosition(mousePosition, stages)
        
        // 如果鼠标位置在阶段内：应用约束，然后转换为相对坐标
        if (targetStage) {
          const HEADER_HEIGHT = 60
          // newPosition 是绝对坐标（因为 initialPosition 是绝对坐标），直接进行约束
          const constrained = constrainTaskToStage(newPosition, targetStage)
          // 再次约束到画布边界（阶段约束后可能超出边界）
          const finalConstrained = constrainToCanvasBounds(constrained)
          // 转换为相对坐标（相对于 stage-content）：x 相对于 stage 左边界，y 相对于 stage-content 顶部（需要减去 HEADER_HEIGHT）
          newPosition = {
            x: finalConstrained.x - targetStage.position.x,
            y: finalConstrained.y - targetStage.position.y - HEADER_HEIGHT
          }
          // 传递相对坐标和有效状态（最终确认，会触发确认对话框）
          onDragFinal(task.id, newPosition, true, targetStage)
        } else {
          // 如果鼠标位置不在任何阶段内：直接使用绝对坐标，不应用约束
          // 传递绝对坐标和无效状态（表示在阶段外，最终确认，会触发确认对话框）
          onDragFinal(task.id, newPosition, false, null)
        }
      }
      
      // 移除全局事件监听
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      
      // 清理缓存
      canvas = null
      canvasRect = null
    }
    
    return { handleMouseDown }
  }
  
  const handleStageDrag = (stage, zoomLevel, onDragEnd) => {
    let isDragging = false
    let startPosition = null
    let initialPosition = null
    let canvas = null
    let canvasRect = null
    let stageElement = null
    
    const handleMouseDown = (event) => {
      event.preventDefault()
      event.stopPropagation()
      
      isDragging = true
      // 获取画布相对于窗口的位置
      canvas = event.target.closest('.workflow-canvas')
      if (!canvas) return
      
      // 缓存阶段元素，用于添加/移除 dragging 类
      stageElement = event.target.closest('.stage-card')
      if (stageElement) {
        stageElement.classList.add('stage-card--dragging')
      }
      
      canvasRect = canvas.getBoundingClientRect()
      const scrollLeft = canvas.scrollLeft || 0
      const scrollTop = canvas.scrollTop || 0
      
      // 计算起始位置（考虑缩放和滚动）
      const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
      
      startPosition = { x: relativeX, y: relativeY }
      initialPosition = { ...stage.position }
      
      // 添加全局事件监听
      document.addEventListener('mousemove', handleMouseMove, { passive: false })
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    let rafId = null
    let lastMouseX = 0
    let lastMouseY = 0
    
    const updatePosition = () => {
      if (!isDragging || !canvas) return
      
      // 更新 canvasRect（可能因为滚动改变）
      canvasRect = canvas.getBoundingClientRect()
      const scrollLeft = canvas.scrollLeft || 0
      const scrollTop = canvas.scrollTop || 0
      
      // 使用最新的鼠标位置
      const relativeX = (lastMouseX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (lastMouseY - canvasRect.top + scrollTop) / zoomLevel.value
      
      // 计算偏移量
      const deltaX = relativeX - startPosition.x
      const deltaY = relativeY - startPosition.y
      
      let newPosition = {
        x: initialPosition.x + deltaX,
        y: initialPosition.y + deltaY
      }
      
      // 约束到画布边界（确保不超出左侧和上侧）
      newPosition = constrainToCanvasBounds(newPosition)
      
      // 更新阶段位置
      onDragEnd(stage.id, newPosition)
      
      rafId = null
    }
    
    const handleMouseMove = (event) => {
      if (!isDragging) return
      event.preventDefault()
      event.stopPropagation()
      
      // 直接更新鼠标位置
      lastMouseX = event.clientX
      lastMouseY = event.clientY
      
      // 使用 requestAnimationFrame 节流，但确保每次都会更新
      if (rafId === null) {
        rafId = requestAnimationFrame(updatePosition)
      }
    }
    
    const handleMouseUp = (event) => {
      if (!isDragging) return
      event.preventDefault()
      event.stopPropagation()
      
      isDragging = false
      
      // 移除 dragging 类
      if (stageElement) {
        stageElement.classList.remove('stage-card--dragging')
        stageElement = null
      }
      
      // 取消 pending 的 RAF
      if (rafId !== null) {
        cancelAnimationFrame(rafId)
        rafId = null
      }
      
      // 获取画布位置
      if (canvas) {
        canvasRect = canvas.getBoundingClientRect()
        const scrollLeft = canvas.scrollLeft || 0
        const scrollTop = canvas.scrollTop || 0
        
        // 计算当前位置（考虑缩放和滚动）
        const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
        const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
        
        // 计算偏移量
        const deltaX = relativeX - startPosition.x
        const deltaY = relativeY - startPosition.y
        
        let newPosition = snapToGrid({
          x: initialPosition.x + deltaX,
          y: initialPosition.y + deltaY
        })
        
        // 约束到画布边界（确保不超出左侧和上侧）
        newPosition = constrainToCanvasBounds(newPosition)
        
        // 更新阶段位置
        onDragEnd(stage.id, newPosition)
      }
      
      // 移除全局事件监听
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      
      // 清理缓存
      canvas = null
      canvasRect = null
    }
    
    return { handleMouseDown }
  }
  
  // 计算阶段内任务的最小边界（用于限制缩小）
  const calculateTasksBoundary = (stage) => {
    if (!stage.tasks || stage.tasks.length === 0) {
      return {
        minX: 0,
        minY: 0,
        maxX: 0,
        maxY: 0
      }
    }
    
    const TASK_WIDTH = 198 // 调整为 198px，使得 偏置(2px) + 宽度(198px) = 200px = 8的倍数
    const TASK_HEIGHT = 100
    const HEADER_HEIGHT = 60
    
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity
    
    stage.tasks.forEach(task => {
      // 任务位置是绝对坐标，需要转换为相对于阶段的坐标
      const relativeX = task.position.x - stage.position.x
      const relativeY = task.position.y - (stage.position.y + HEADER_HEIGHT)
      
      minX = Math.min(minX, relativeX)
      minY = Math.min(minY, relativeY)
      maxX = Math.max(maxX, relativeX + TASK_WIDTH)
      maxY = Math.max(maxY, relativeY + TASK_HEIGHT)
    })
    
    // 如果没有任务，返回默认值
    if (minX === Infinity) {
      return { minX: 0, minY: 0, maxX: 0, maxY: 0 }
    }
    
    return { minX, minY, maxX, maxY }
  }

  // 修正 - 计算任务边界for阶段缩放应传入内容区顶点
  const calculateTasksBoundaryFor = (stage, tentativeX, tentativeY) => {
    if (!stage.tasks || stage.tasks.length === 0) {
      return { minX: 0, minY: 0, maxX: 0, maxY: 0 }
    }
    const TASK_WIDTH = 196
    const TASK_HEIGHT = 100
    const HEADER_HEIGHT = 60
    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity
    // 认定内容区实际顶部 = tentativeY + HEADER_HEIGHT
    const contentTop = tentativeY + HEADER_HEIGHT
    stage.tasks.forEach(task => {
      const relativeX = task.position.x - tentativeX
      const relativeY = task.position.y - contentTop
      minX = Math.min(minX, relativeX)
      minY = Math.min(minY, relativeY)
      maxX = Math.max(maxX, relativeX + TASK_WIDTH)
      maxY = Math.max(maxY, relativeY + TASK_HEIGHT)
    })
    if (minX === Infinity) {
      return { minX: 0, minY: 0, maxX: 0, maxY: 0 }
    }
    return { minX, minY, maxX, maxY }
  }

  const handleStageResize = (stage, zoomLevel, direction, onResizeEnd) => {
    let isResizing = false
    let startPosition = null, startSize = null, startStagePosition = null
    let rafId = null, lastEvent = null;
    let lastProposed = null // 缓存最后一次预览结果
    let mouseupHandled = false // 防重复
    const clamp = (val, min) => (val < min ? min : val);
    const bestSnap = (desired, min, max, g) => {
      const r = Math.round(desired / g) * g
      const f = Math.floor(desired / g) * g
      const c = Math.ceil(desired / g) * g
      const cands = [desired, r, f, c]
      let best = desired
      let bestErr = Infinity
      for (const v of cands) {
        const clamped = clamp(v, min)
        const err = Math.abs(clamped - desired)
        if (err < bestErr) {
          bestErr = err
          best = clamped
        }
      }
      return best
    }

    // 缓存任务边界，避免预览与落点期间发生计算偏差
    let cachedTasksBoundary = null
    
    const handleMouseDown = (event) => {
      event.preventDefault()
      event.stopPropagation()
      
      isResizing = true
      
      // 在调整大小开始时设置 _isResizing 标记，禁用 transition
      if (stage && !stage._isResizing) {
        stage._isResizing = true
        // 同时给阶段内的所有任务添加标记，禁用任务的 transition
        if (stage.tasks && Array.isArray(stage.tasks)) {
          stage.tasks.forEach(task => {
            if (!task._stageResizing) {
              task._stageResizing = true
            }
          })
        }
      }
      
      // 获取画布相对于窗口的位置
      const canvas = event.target.closest('.workflow-canvas')
      if (!canvas) return
      
      const canvasRect = canvas.getBoundingClientRect()
      const scrollLeft = canvas.scrollLeft || 0
      const scrollTop = canvas.scrollTop || 0
      
      // 计算起始位置（考虑缩放和滚动）
      const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
      
      startPosition = { x: relativeX, y: relativeY }
      startSize = { width: stage.position.width, height: stage.position.height }
      startStagePosition = { x: stage.position.x, y: stage.position.y }
      cachedTasksBoundary = calculateTasksBoundary(stage)
      lastProposed = { x: stage.position.x, y: stage.position.y, width: stage.position.width, height: stage.position.height }
      mouseupHandled = false
      
      // 添加全局事件监听
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    const updateResize = () => {
      if (!isResizing || !lastEvent) return
      const event = lastEvent
      lastEvent = null
      const canvas = event.target.closest('.workflow-canvas') || document.querySelector('.workflow-canvas')
      if (!canvas) return
      const canvasRect = canvas.getBoundingClientRect(), scrollLeft = canvas.scrollLeft || 0, scrollTop = canvas.scrollTop || 0
      const relativeX = (event.clientX - canvasRect.left + scrollLeft) / zoomLevel.value
      const relativeY = (event.clientY - canvasRect.top + scrollTop) / zoomLevel.value
      const deltaX = relativeX - startPosition.x, deltaY = relativeY - startPosition.y
      const MIN_WIDTH = 400, MIN_HEIGHT = 250
      // 计算固定边（右边界和底边界，这些在调整左边/上边时保持不变）
      const right = startStagePosition.x + startSize.width
      const bottom = startStagePosition.y + startSize.height
      let newX = startStagePosition.x, newY = startStagePosition.y, newWidth = startSize.width, newHeight = startSize.height
      if (direction.includes('e')) {
        const candidateWidth = startSize.width + deltaX
        const candidateX = startStagePosition.x
        const tasksBoundary = calculateTasksBoundaryFor(stage, candidateX, startStagePosition.y)
        const BORDER_WIDTH = 2 // stage-card 的边框宽度
        // tasksBoundary.maxX 是相对于内容区左边界的内容区右边界位置
        // 需要加上左边框宽度转换为整个阶段的最小宽度
        const minWidthByTasks = Math.max(MIN_WIDTH, tasksBoundary.maxX + BORDER_WIDTH)
        newWidth = Math.max(candidateWidth, minWidthByTasks)
        newX = candidateX
      }
      if (direction.includes('w')) {
        const desiredLeft = startStagePosition.x + deltaX
        // 计算所有任务的最左端（绝对坐标）
        let minTaskLeft = Infinity
        if (stage.tasks && stage.tasks.length > 0) {
          stage.tasks.forEach(task => {
            if (task.position.x < minTaskLeft) minTaskLeft = task.position.x
          })
        } else {
          minTaskLeft = desiredLeft // 如果没有任务，不限制
        }
        const newXMinByMinWidth = right - MIN_WIDTH
        // 新的左边不能超过最左侧任务的左边
        const newXMaxByTasks = minTaskLeft
        let clampX = desiredLeft
        clampX = Math.min(clampX, newXMinByMinWidth)
        clampX = Math.min(clampX, newXMaxByTasks)
        newX = clampX
        newWidth = right - newX
      }
      if (direction.includes('s')) {
        const candidateHeight = startSize.height + deltaY
        const candidateY = startStagePosition.y
        const tasksBoundary = calculateTasksBoundaryFor(stage, startStagePosition.x, candidateY)
        const HEADER_HEIGHT = 60
        const BORDER_WIDTH = 2 // stage-card 的边框宽度
        // tasksBoundary.maxY 是相对于内容区顶部的内容区底部位置
        // contentTop = stage.position.y + HEADER_HEIGHT（没有考虑上边框）
        // 要转换为整个阶段的最小高度：上边框 + HEADER_HEIGHT + maxY + 底边框
        const minHeightByTasks = Math.max(MIN_HEIGHT, tasksBoundary.maxY + HEADER_HEIGHT + BORDER_WIDTH * 2)
        newHeight = Math.max(candidateHeight, minHeightByTasks)
        newY = candidateY
      }
      if (direction.includes('n')) {
        const desiredTop = startStagePosition.y + deltaY
        const HEADER_HEIGHT = 60
        // 计算所有任务的最上端（绝对坐标）
        // 任务位置是相对于阶段内容区的，所以需要考虑 HEADER_HEIGHT
        let minTaskTop = Infinity
        if (stage.tasks && stage.tasks.length > 0) {
          stage.tasks.forEach(task => {
            // task.position.y 是绝对坐标（相对于画布），已经是内容区的坐标
            // 但我们需要的是相对于整个阶段的位置，所以需要加上 HEADER_HEIGHT
            // 实际上 task.position.y 已经是绝对坐标，我们直接用它
            if (task.position.y < minTaskTop) minTaskTop = task.position.y
          })
        } else {
          minTaskTop = desiredTop + HEADER_HEIGHT // 如果没有任务，至少保留 header
        }
        const newYMinByMinHeight = bottom - MIN_HEIGHT
        // 新的上边不能超过最上侧任务的上边
        // 由于任务是相对于内容区的，我们需要确保阶段的上边不会超过任务位置减去 HEADER_HEIGHT
        const newYMaxByTasks = minTaskTop - HEADER_HEIGHT
        let clampY = desiredTop
        clampY = Math.min(clampY, newYMinByMinHeight)
        clampY = Math.min(clampY, newYMaxByTasks)
        newY = clampY
        newHeight = bottom - newY
      }
      // 预览时也应用网格对齐，确保预览和最终结果一致，避免跳跃
      // right 和 bottom 在上面已经定义，这里直接使用
      let snappedX = newX, snappedY = newY, snappedWidth = newWidth, snappedHeight = newHeight
      
      if (direction.includes('w')) {
        const BORDER_WIDTH = 2
        // 先计算约束，确保最小值也是网格对齐的
        let minWidthByTasks = MIN_WIDTH
        if (stage.tasks && stage.tasks.length > 0) {
          const tasksBoundary = calculateTasksBoundaryFor(stage, newX, startStagePosition.y)
          minWidthByTasks = Math.max(MIN_WIDTH, tasksBoundary.maxX + BORDER_WIDTH)
        }
        const minWidthSnapped = Math.ceil(minWidthByTasks / gridSize) * gridSize
        // 计算最大允许的 x（对应最小宽度）
        const maxXByMinWidth = right - minWidthSnapped
        // 应用约束：newX 不能超过 maxXByMinWidth，也不能超过任务边界
        let minTaskLeft = Infinity
        if (stage.tasks && stage.tasks.length > 0) {
          stage.tasks.forEach(task => {
            if (task.position.x < minTaskLeft) minTaskLeft = task.position.x
          })
        } else {
          minTaskLeft = newX // 如果没有任务，不限制
        }
        const maxXByTasks = minTaskLeft
        const constrainedX = Math.min(newX, maxXByMinWidth, maxXByTasks)
        // 约束到画布边界（确保不超出左侧）
        const constrainedXWithBounds = Math.max(0, constrainedX)
        // 网格对齐（向下取整，因为我们要限制最大值）
        snappedX = Math.floor(constrainedXWithBounds / gridSize) * gridSize
        // 再次确保不超出边界（网格对齐后可能小于0）
        snappedX = Math.max(0, snappedX)
        // 重新计算宽度，确保不小于最小值
        snappedWidth = right - snappedX
        snappedWidth = Math.max(snappedWidth, minWidthSnapped)
        snappedX = right - snappedWidth
        // 最终确保不超出边界
        snappedX = Math.max(0, snappedX)
      }
      if (direction.includes('n')) {
        const HEADER_HEIGHT = 60
        const BORDER_WIDTH = 2
        // 先计算约束，确保最小值也是网格对齐的
        let minHeightByTasks = MIN_HEIGHT
        if (stage.tasks && stage.tasks.length > 0) {
          const tasksBoundary = calculateTasksBoundaryFor(stage, startStagePosition.x, newY)
          minHeightByTasks = Math.max(MIN_HEIGHT, tasksBoundary.maxY + HEADER_HEIGHT + BORDER_WIDTH * 2)
        }
        const minHeightSnapped = Math.ceil(minHeightByTasks / gridSize) * gridSize
        // 计算最大允许的 y（对应最小高度）
        const maxYByMinHeight = bottom - minHeightSnapped
        // 应用约束：newY 不能超过 maxYByMinHeight，也不能超过任务边界
        let minTaskTop = Infinity
        if (stage.tasks && stage.tasks.length > 0) {
          stage.tasks.forEach(task => {
            if (task.position.y < minTaskTop) minTaskTop = task.position.y
          })
        } else {
          minTaskTop = newY + HEADER_HEIGHT // 如果没有任务，至少保留 header
        }
        const maxYByTasks = minTaskTop - HEADER_HEIGHT
        const constrainedY = Math.min(newY, maxYByMinHeight, maxYByTasks)
        // 约束到画布边界（确保不超出上侧）
        const constrainedYWithBounds = Math.max(0, constrainedY)
        // 网格对齐（向下取整，因为我们要限制最大值）
        snappedY = Math.floor(constrainedYWithBounds / gridSize) * gridSize
        // 再次确保不超出边界（网格对齐后可能小于0）
        snappedY = Math.max(0, snappedY)
        // 重新计算高度，确保不小于最小值
        snappedHeight = bottom - snappedY
        snappedHeight = Math.max(snappedHeight, minHeightSnapped)
        snappedY = bottom - snappedHeight
        // 最终确保不超出边界
        snappedY = Math.max(0, snappedY)
      }
      if (direction.includes('e')) {
        const BORDER_WIDTH = 2
        const tasksBoundary = calculateTasksBoundaryFor(stage, startStagePosition.x, startStagePosition.y)
        const minWidthByTasks = Math.max(MIN_WIDTH, tasksBoundary.maxX + BORDER_WIDTH)
        // 确保最小值也是网格对齐的（向上取整到最近的网格倍数）
        const minWidthSnapped = Math.ceil(minWidthByTasks / gridSize) * gridSize
        // 先应用约束，再网格对齐，使用向上取整确保不小于最小值
        const constrainedWidth = Math.max(newWidth, minWidthSnapped)
        snappedWidth = Math.ceil(constrainedWidth / gridSize) * gridSize
        // 再次确保不小于最小值（双重保险）
        snappedWidth = Math.max(snappedWidth, minWidthSnapped)
      }
      if (direction.includes('s')) {
        const HEADER_HEIGHT = 60
        const BORDER_WIDTH = 2
        const tasksBoundary = calculateTasksBoundaryFor(stage, startStagePosition.x, startStagePosition.y)
        const minHeightByTasks = Math.max(MIN_HEIGHT, tasksBoundary.maxY + HEADER_HEIGHT + BORDER_WIDTH * 2)
        // 确保最小值也是网格对齐的（向上取整到最近的网格倍数）
        const minHeightSnapped = Math.ceil(minHeightByTasks / gridSize) * gridSize
        // 先应用约束，再网格对齐，使用向上取整确保不小于最小值
        const constrainedHeight = Math.max(newHeight, minHeightSnapped)
        snappedHeight = Math.ceil(constrainedHeight / gridSize) * gridSize
        // 再次确保不小于最小值（双重保险）
        snappedHeight = Math.max(snappedHeight, minHeightSnapped)
      }
      
      lastProposed = { x: snappedX, y: snappedY, width: snappedWidth, height: snappedHeight }
      
      // 实时更新 stage.position（预览），确保阶段能实时跟随鼠标
      stage.position.x = snappedX
      stage.position.y = snappedY
      stage.position.width = snappedWidth
      stage.position.height = snappedHeight
      
      rafId = null
    }

    const handleMouseMove = (event) => {
      if (!isResizing) return
      event.preventDefault()
      event.stopPropagation()
      lastEvent = event
      if (rafId === null) {
        rafId = requestAnimationFrame(updateResize)
      }
    }
    
    const handleMouseUp = (event) => {
      if (!isResizing || mouseupHandled) return
      event.preventDefault()
      event.stopPropagation()
      mouseupHandled = true
      isResizing = false
      
      // 清除 _isResizing 标记（调整大小结束，恢复 transition）
      if (stage && stage._isResizing) {
        delete stage._isResizing
        // 同时清除阶段内所有任务的标记
        if (stage.tasks && Array.isArray(stage.tasks)) {
          stage.tasks.forEach(task => {
            if (task._stageResizing) {
              delete task._stageResizing
            }
          })
        }
      }
      
      if (lastProposed) {
        // 预览时已经应用了约束和网格对齐，直接使用最后预览的结果，保证"所见即所得"
        const { x: px, y: py, width: pw, height: ph } = lastProposed
        onResizeEnd(stage.id, { width: pw, height: ph }, { x: px, y: py })
      }
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
    
    return { handleMouseDown }
  }
  
  return {
    handleTaskDrag,
    handleStageDrag,
    handleStageResize,
    constrainTaskToStage
  }
}

