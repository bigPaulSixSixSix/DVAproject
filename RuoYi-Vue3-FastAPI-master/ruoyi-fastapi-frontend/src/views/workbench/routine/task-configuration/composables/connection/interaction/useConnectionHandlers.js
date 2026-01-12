// composables/connection/interaction/useConnectionHandlers.js
// 连接交互处理：开始、移动、结束、取消

import { ref } from 'vue'
import { shouldSkipValidation } from '../config/testConfig'
import { useConnectionUtils } from '../utils/useConnectionUtils'

export const useConnectionHandlers = (findTaskById) => {
  const { normalizeId } = useConnectionUtils()

  // 连接状态
  const isConnecting = ref(false)
  const connectionStart = ref(null)
  const previewConnectionPoint = ref(null) // 预览连接线的终点（鼠标位置）
  const connectingTargetElement = ref(null) // 当前悬停的目标元素

  /**
   * 处理连接开始
   * @param {Object} data - 连接开始数据
   */
  const handleConnectionStart = (data) => {
    const normalizedData = {
      ...data,
      elementId: normalizeId(data.elementId)
    }

    isConnecting.value = true
    connectionStart.value = normalizedData
    previewConnectionPoint.value = null
    connectingTargetElement.value = null
  }

  /**
   * 处理连接移动
   * @param {Object} moveData - 移动数据
   */
  const handleConnectionMove = (moveData) => {
    if (!isConnecting.value || !connectionStart.value) return
    previewConnectionPoint.value = { x: moveData.x, y: moveData.y }

    const startType = connectionStart.value?.elementType
    const targetElement = moveData.targetElement
    let nextTarget = null

    if (targetElement && startType) {
      // 如果起始类型是阶段，目标类型是任务，则查找任务所在的阶段
      if (startType === 'stage' && targetElement.elementType === 'task') {
        if (findTaskById) {
          const taskInfo = findTaskById(normalizeId(targetElement.elementId))
          // 如果任务在阶段内，使用任务所在的阶段作为目标
          if (taskInfo && taskInfo.stage && !taskInfo.isUnassigned) {
            nextTarget = {
              elementType: 'stage',
              elementId: normalizeId(taskInfo.stage.id)
            }
          } else if (shouldSkipValidation()) {
            // 如果关闭了验证，允许阶段连接到阶段外的任务（使用任务本身作为目标）
            nextTarget = {
              elementType: 'task',
              elementId: normalizeId(targetElement.elementId)
            }
          }
          // 如果任务在阶段外且验证开启，不设置 nextTarget，表示无法连接
        }
      } else if (targetElement.elementType === startType) {
        // 同类型元素，直接使用目标元素
        nextTarget = {
          elementType: targetElement.elementType,
          elementId: normalizeId(targetElement.elementId)
        }
      }
    }

    connectingTargetElement.value = nextTarget
  }

  /**
   * 处理连接取消
   */
  const handleConnectionCancel = () => {
    // 取消连接操作，清除所有连接相关的状态
    isConnecting.value = false
    connectionStart.value = null
    previewConnectionPoint.value = null
    connectingTargetElement.value = null
  }

  /**
   * 处理连接面板结束
   * @param {Object} data - 连接结束数据
   * @param {Function} createConnectionBetweenElements - 创建连接函数
   */
  const handleConnectionPanelEnd = async (data, createConnectionBetweenElements) => {
    if (!isConnecting.value || !connectionStart.value) return
    
    // 清除预览
    previewConnectionPoint.value = null
    connectingTargetElement.value = null
    
    // 创建连接
    const fromElement = {
      id: normalizeId(connectionStart.value.elementId),
      type: connectionStart.value.elementType
    }
    
    let toElement = {
      id: normalizeId(data.elementId),
      type: data.elementType
    }
    
    // 如果起始类型是阶段，目标类型是任务，则查找任务所在的阶段
    if (fromElement.type === 'stage' && toElement.type === 'task') {
      if (findTaskById) {
        const taskInfo = findTaskById(toElement.id)
        // 如果任务在阶段内，使用任务所在的阶段作为目标
        if (taskInfo && taskInfo.stage && !taskInfo.isUnassigned) {
          toElement = {
            id: normalizeId(taskInfo.stage.id),
            type: 'stage'
          }
        } else if (shouldSkipValidation()) {
          // 如果关闭了验证，允许阶段连接到阶段外的任务（保持任务作为目标）
          toElement = {
            id: normalizeId(toElement.id),
            type: 'task'
          }
        } else {
          // 如果任务在阶段外且验证开启，无法建立连接，直接返回
          isConnecting.value = false
          connectionStart.value = null
          return
        }
      }
    }
    
    // 调用创建连接方法（内部会进行所有检查，包括阶段外任务检查）
    // 注意：createConnectionBetweenElements 可能是 async 函数，需要 await
    try {
      await createConnectionBetweenElements(fromElement, toElement)
    } finally {
    isConnecting.value = false
    connectionStart.value = null
    }
  }

  return {
    isConnecting,
    connectionStart,
    previewConnectionPoint,
    connectingTargetElement,
    handleConnectionStart,
    handleConnectionMove,
    handleConnectionCancel,
    handleConnectionPanelEnd
  }
}

