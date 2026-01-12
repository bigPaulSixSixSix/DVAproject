// composables/connection/utils/useConnectionLogger.js
// 连接创建日志相关逻辑

import { ElMessage } from 'element-plus'
import { shouldEnableConnectionLogging } from '../config/testConfig'

// 使用配置文件中的开关
let connectionLoggingEnabled = shouldEnableConnectionLogging()

export const setConnectionLoggingEnabled = (enabled) => {
  connectionLoggingEnabled = !!enabled
}

export const useConnectionLogger = () => {
  /**
   * 记录连接创建日志并下载
   * @param {Object} connection - 连接对象
   * @param {Object} fromInfo - 起始元素信息
   * @param {Object} toInfo - 目标元素信息
   * @param {Object} updatedRelations - 更新后的关系
   * @param {number} totalConnections - 当前所有连接数量
   */
  const logConnectionCreation = (
    connection,
    fromInfo,
    toInfo,
    updatedRelations,
    totalConnections
  ) => {
    if (!connectionLoggingEnabled) {
      ElMessage.success('连接已建立')
      return
    }

    const logContent = `=== 连接建立成功 ===
时间: ${new Date().toLocaleString()}

连接对象:
${JSON.stringify(connection, null, 2)}

起始元素 (fromElement):
${JSON.stringify(fromInfo, null, 2)}

目标元素 (toElement):
${JSON.stringify(toInfo, null, 2)}

更新后的关系 (updatedRelations):
${JSON.stringify(updatedRelations, null, 2)}

当前所有连接数量: ${totalConnections}

========================
`

    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `connection_log_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('连接已建立')
  }

  /**
   * 收集元素信息（用于日志）
   * @param {Object} element - 元素对象
   * @param {string} elementType - 元素类型 ('task' | 'stage')
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   * @returns {Object} 元素信息对象
   */
  const collectElementInfo = (element, elementType, findTaskById, findStageById) => {
    if (elementType === 'task') {
      const taskInfo = findTaskById(element.id)
      return taskInfo ? {
        id: taskInfo.task.id,
        type: 'task',
        name: taskInfo.task.name,
        stageId: taskInfo.task.stageId,
        position: taskInfo.task.position,
        predecessorTasks: taskInfo.task.predecessorTasks || [],
        successorTasks: taskInfo.task.successorTasks || [],
        isUnassigned: taskInfo.isUnassigned
      } : { error: '任务未找到' }
    } else {
      const stage = findStageById(element.id)
      return stage ? {
        id: stage.id,
        type: 'stage',
        name: stage.name,
        position: stage.position,
        predecessorStages: stage.predecessorStages || [],
        successorStages: stage.successorStages || [],
        tasks: stage.tasks?.map(t => ({ id: t.id, name: t.name })) || []
      } : { error: '阶段未找到' }
    }
  }

  /**
   * 记录回环检测失败的日志
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @param {Array} allElements - 所有元素
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   */
  const logCycleDetectionFailure = (
    fromElement,
    toElement,
    allElements,
    findTaskById,
    findStageById
  ) => {
    if (!connectionLoggingEnabled) {
      return
    }

    const fromInfo = collectElementInfo(fromElement, fromElement.type, findTaskById, findStageById)
    const toInfo = collectElementInfo(toElement, toElement.type, findTaskById, findStageById)

    const logContent = `=== 回环检测失败 ===
时间: ${new Date().toLocaleString()}

尝试建立的连接:
从 ${fromElement.type} (ID: ${fromElement.id}, 名称: ${fromElement.name || '未知'})
到 ${toElement.type} (ID: ${toElement.id}, 名称: ${toElement.name || '未知'})

起始元素 (fromElement):
${JSON.stringify(fromInfo, null, 2)}

目标元素 (toElement):
${JSON.stringify(toInfo, null, 2)}

所有元素信息:
${JSON.stringify(allElements.map(el => ({
  id: el.id,
  type: el.type,
  name: el.name,
  successorTasks: el.successorTasks || [],
  successorStages: el.successorStages || [],
  predecessorTasks: el.predecessorTasks || [],
  predecessorStages: el.predecessorStages || []
})), null, 2)}

========================
`

    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cycle_detection_failure_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  /**
   * 记录连接创建失败的日志
   * @param {Object} fromElement - 起始元素
   * @param {Object} toElement - 目标元素
   * @param {string} reason - 失败原因
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   */
  const logConnectionFailure = (
    fromElement,
    toElement,
    reason,
    findTaskById,
    findStageById
  ) => {
    if (!connectionLoggingEnabled) {
      return
    }

    const fromInfo = collectElementInfo(fromElement, fromElement.type, findTaskById, findStageById)
    const toInfo = collectElementInfo(toElement, toElement.type, findTaskById, findStageById)

    const logContent = `=== 连接创建失败 ===
时间: ${new Date().toLocaleString()}

失败原因: ${reason}

尝试建立的连接:
从 ${fromElement.type} (ID: ${fromElement.id}, 名称: ${fromElement.name || '未知'})
到 ${toElement.type} (ID: ${toElement.id}, 名称: ${toElement.name || '未知'})

起始元素 (fromElement):
${JSON.stringify(fromInfo, null, 2)}

目标元素 (toElement):
${JSON.stringify(toInfo, null, 2)}

========================
`

    const blob = new Blob([logContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `connection_failure_${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    logConnectionCreation,
    logCycleDetectionFailure,
    logConnectionFailure,
    collectElementInfo
  }
}

