// composables/connection/interaction/usePreviewConnection.js
// 预览连接线相关逻辑

import { computed } from 'vue'
import { useConnectionUtils } from '../utils/useConnectionUtils'

export const usePreviewConnection = (
  isConnecting,
  connectionStart,
  previewConnectionPoint,
  connectingTargetElement,
  workflowData,
  unassignedTasks,
  getElementConnectionPoint
) => {
  const { normalizeId } = useConnectionUtils()

  // 查找元素（包括阶段外任务）
  const findElement = (elementInfo) => {
    if (!elementInfo || !elementInfo.elementId || !elementInfo.elementType) {
      return null
    }

    const elementType = elementInfo.elementType
    const elementId = normalizeId(elementInfo.elementId)
    
    const stages = workflowData.value?.stages || []
    if (elementType === 'stage') {
      const stage = stages.find(s => normalizeId(s.id) === elementId)
      if (stage) {
        return {
          ...stage,
          type: 'stage'
        }
      }
    } else if (elementType === 'task') {
      // 先在阶段内查找
      for (const stage of stages) {
        if (stage.tasks && Array.isArray(stage.tasks)) {
          const task = stage.tasks.find(t => normalizeId(t.id) === elementId)
          if (task) {
            return {
              ...task,
              type: 'task'
            }
          }
        }
      }
      // 再在阶段外查找
      const unassignedTask = unassignedTasks.value.find(t => normalizeId(t.id) === elementId)
      if (unassignedTask) {
        return {
          ...unassignedTask,
          type: 'task'
        }
      }
    }
    return null
  }

  // 计算预览连接线数据
  const previewConnection = computed(() => {
    if (!isConnecting.value || !connectionStart.value || !previewConnectionPoint.value) {
      return null
    }
    
    const fromElement = findElement(connectionStart.value)
    if (!fromElement) return null
    
    // 计算起始连接点位置
    const fromPoint = getElementConnectionPoint(
      fromElement,
      connectionStart.value.position === 'left' ? 'left' : 'right'
    )
    
    // 计算终点位置
    let toPoint = previewConnectionPoint.value
    
    // 如果鼠标在目标面板上，使用目标连接点位置
    if (connectingTargetElement.value) {
      const targetElement = findElement(connectingTargetElement.value)
      if (targetElement) {
        // 根据起始连接点的位置判断目标连接点的位置
        // 如果起始点是右侧（successor），目标点是左侧（predecessor）
        // 如果起始点是左侧（predecessor），目标点是右侧（successor）
        const targetPosition = connectionStart.value.position === 'right' ? 'left' : 'right'
        toPoint = getElementConnectionPoint(targetElement, targetPosition)
      }
    }
    
    return {
      fromPoint,
      toPoint
    }
  })

  return {
    previewConnection
  }
}

