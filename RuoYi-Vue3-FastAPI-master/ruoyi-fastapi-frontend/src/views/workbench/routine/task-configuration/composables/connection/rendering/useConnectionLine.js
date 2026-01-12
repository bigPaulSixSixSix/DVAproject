// composables/connection/rendering/useConnectionLine.js
// 连接线渲染相关逻辑

export const useConnectionLine = () => {
  const calculateBezierPath = (fromPoint, toPoint) => {
    // 水平延伸距离（从连接点向外延伸的距离）
    const HORIZONTAL_OFFSET = 0
    
    // 计算起点水平延伸后的位置（向右延伸）
    const startExtensionX = fromPoint.x + HORIZONTAL_OFFSET
    const startExtensionY = fromPoint.y
    
    // 计算终点水平延伸后的位置（向左延伸）
    const endExtensionX = toPoint.x - HORIZONTAL_OFFSET
    const endExtensionY = toPoint.y
    
    // 计算曲线中间部分的控制点
    // 使用延伸点之间的实际距离来计算控制点
    const curveDistance = Math.abs(endExtensionX - startExtensionX)
    const verticalDistance = Math.abs(endExtensionY - startExtensionY)
    
    // 控制点偏移量：根据实际距离动态调整，但不超过100
    // 这样可以确保曲线在中间部分有合适的弯曲
    const controlOffset = Math.min(curveDistance / 2, verticalDistance / 2, 100)
    
    // 使用一条完整的三次贝塞尔曲线，确保起点和终点处都是水平方向
    // 第一个控制点：在起点右侧，确保起点处曲线方向水平（向右）
    // 通过设置控制点的Y坐标与起点相同，确保起点处切线方向水平
    const cp1 = {
      x: fromPoint.x + HORIZONTAL_OFFSET + controlOffset,
      y: fromPoint.y
    }
    
    // 第二个控制点：在终点左侧，确保终点处曲线方向水平（向左）
    // 通过设置控制点的Y坐标与终点相同，确保终点处切线方向水平
    const cp2 = {
      x: toPoint.x - HORIZONTAL_OFFSET - controlOffset,
      y: toPoint.y
    }
    
    // 如果起点和终点太近，使用简单的直线
    if (Math.abs(toPoint.x - fromPoint.x) < HORIZONTAL_OFFSET * 2) {
      return `M ${fromPoint.x} ${fromPoint.y} L ${toPoint.x} ${toPoint.y}`
    }
    
    // 构建平滑的贝塞尔曲线路径
    // 曲线从起点开始，第一个控制点确保起点处水平向右
    // 曲线到达终点，第二个控制点确保终点处水平向左
    // 中间部分通过控制点偏移实现平滑弯曲
    return `M ${fromPoint.x} ${fromPoint.y} C ${cp1.x} ${cp1.y}, ${cp2.x} ${cp2.y}, ${toPoint.x} ${toPoint.y}`
  }
  
  const getElementConnectionPoint = (element, position) => {
    // 计算元素的连接点位置（连接点中心）
    // 连接点CSS: left: -6px 或 right: -6px，容器12px x 12px
    // 这意味着连接点容器中心在元素边界上
    // 连接点内部的dot有border: 2px，但中心仍然是容器中心
    const TASK_WIDTH = 196 // 任务卡片固定宽度（与 TaskCard.vue 保持一致）
    const TASK_HEIGHT = 100 // 任务卡片固定高度
    const TASK_BORDER = 1 // TaskCard的border宽度（1px）
    
    if (element.type === 'stage') {
      const stage = element
      // StageCard使用box-sizing: border-box，所以width包括border
      // 连接点中心在元素边界上
      if (position === 'left') {
        return {
          x: stage.position.x,
          y: stage.position.y + stage.position.height / 2
        }
      } else {
        return {
          x: stage.position.x + stage.position.width,
          y: stage.position.y + stage.position.height / 2
        }
      }
    } else if (element.type === 'task') {
      const task = element
      // 使用硬编码偏移值精确对齐连接点中心
      // 连接点CSS: left: -6px 或 right: -6px, 容器12px x 12px, top: 50%
      // TaskCard: width 196px, height 100px, border 1px
      // 通过实际测量得出的精确偏移值
      const X_OFFSET_LEFT = 3   // 左侧连接点的X偏移（相对于position.x）
      const X_OFFSET_RIGHT = 197 // 右侧连接点的X偏移（相对于position.x，即196+1）
      const Y_OFFSET = 51.5        // Y偏移（相对于position.y，即height/2）
      
      if (position === 'left') {
        return {
          x: task.position.x + X_OFFSET_LEFT,
          y: task.position.y + Y_OFFSET
        }
      } else {
        return {
          x: task.position.x + X_OFFSET_RIGHT,
          y: task.position.y + Y_OFFSET
        }
      }
    }
    
    return { x: 0, y: 0 }
  }
  
  const getConnectionPoints = (fromElementInfo, toElementInfo, stages, unassignedTasks = []) => {
    if (!stages || stages.length === 0) {
      return { fromPoint: { x: 0, y: 0 }, toPoint: { x: 0, y: 0 } }
    }
    
    // 从 stages 中查找实际的元素数据（包括阶段外任务）
    const findElement = (elementInfo) => {
      if (!elementInfo || !elementInfo.elementId || !elementInfo.elementType) {
        return null
      }
      
      if (elementInfo.elementType === 'stage') {
        const stage = stages.find(s => String(s.id) === String(elementInfo.elementId))
        if (stage) {
          return {
            ...stage,
            type: 'stage'
          }
        }
      } else if (elementInfo.elementType === 'task') {
        // 先在所有的 stage 中查找 task
        for (const stage of stages) {
          if (stage.tasks && Array.isArray(stage.tasks)) {
            const task = stage.tasks.find(t => String(t.id) === String(elementInfo.elementId))
            if (task) {
              return {
                ...task,
                type: 'task'
              }
            }
          }
        }
        // 如果没找到，再在阶段外任务中查找
        if (unassignedTasks && Array.isArray(unassignedTasks)) {
          const task = unassignedTasks.find(t => String(t.id) === String(elementInfo.elementId))
          if (task) {
            return {
              ...task,
              type: 'task'
            }
          }
        }
      }
      return null
    }
    
    const fromElement = findElement(fromElementInfo)
    const toElement = findElement(toElementInfo)
    
    if (!fromElement || !toElement) {
      return { fromPoint: { x: 0, y: 0 }, toPoint: { x: 0, y: 0 } }
    }
    
    // 计算连接点位置
    const fromPoint = getElementConnectionPoint(fromElement, 'right')
    const toPoint = getElementConnectionPoint(toElement, 'left')
    
    return { fromPoint, toPoint }
  }
  
  return {
    calculateBezierPath,
    getElementConnectionPoint,
    getConnectionPoints
  }
}

