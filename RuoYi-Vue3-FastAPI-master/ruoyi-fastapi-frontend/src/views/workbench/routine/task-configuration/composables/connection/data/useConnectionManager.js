// composables/connection/data/useConnectionManager.js
// 连接数据管理：删除连接、更新关系、查找连接等

import { dedupeIds } from '../../utils/useUtils'
import { useConnectionUtils } from '../utils/useConnectionUtils'

export const useConnectionManager = () => {
  const { normalizeId, idsEqual } = useConnectionUtils()

  /**
   * 应用更新后的关系
   * @param {Object} updatedRelations - 更新后的关系
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   * @param {Object} workflowStore - 工作流store
   */
  const applyUpdatedRelations = (updatedRelations, findTaskById, findStageById, workflowStore) => {
    if (!updatedRelations) return

    // 辅助函数：将ID数组去重，保持原始类型（支持临时ID和数字ID）
    const normalizeIdArray = (ids) => {
      if (!Array.isArray(ids)) return []
      // 使用 dedupeIds 去重，保持原始ID类型
      return dedupeIds(ids)
    }

    const applyTaskUpdates = (updatedTask) => {
      if (!updatedTask) return
      const taskInfo = findTaskById(updatedTask.id)
      if (!taskInfo) return

      if (Array.isArray(updatedTask.predecessorTasks)) {
        // 统一转换为数字类型，并使用新数组确保响应式更新
        const normalizedPredecessorTasks = normalizeIdArray(updatedTask.predecessorTasks)
        taskInfo.task.predecessorTasks = [...normalizedPredecessorTasks]
      } else {
          taskInfo.task.predecessorTasks = []
      }
      
      if (Array.isArray(updatedTask.successorTasks)) {
        // 统一转换为数字类型，并使用新数组确保响应式更新
        const normalizedSuccessorTasks = normalizeIdArray(updatedTask.successorTasks)
        taskInfo.task.successorTasks = [...normalizedSuccessorTasks]
      } else {
          taskInfo.task.successorTasks = []
      }

      // 保持ID的原始类型（支持临时ID和数字ID）
      // 使用新数组确保响应式更新
      workflowStore.updateTask(updatedTask.id, {
        predecessorTasks: [...(taskInfo.task.predecessorTasks || [])],
        successorTasks: [...(taskInfo.task.successorTasks || [])]
      })
    }

    const applyStageUpdates = (updatedStage) => {
      if (!updatedStage) return
      const stage = findStageById(updatedStage.id)
      if (!stage) return

      if (Array.isArray(updatedStage.predecessorStages)) {
        // 统一转换为数字类型，并使用新数组确保响应式更新
        const normalizedPredecessorStages = normalizeIdArray(updatedStage.predecessorStages)
        stage.predecessorStages = [...normalizedPredecessorStages]
      } else {
          stage.predecessorStages = []
      }
      
      if (Array.isArray(updatedStage.successorStages)) {
        // 统一转换为数字类型，并使用新数组确保响应式更新
        const normalizedSuccessorStages = normalizeIdArray(updatedStage.successorStages)
        stage.successorStages = [...normalizedSuccessorStages]
      } else {
          stage.successorStages = []
      }

      // 保持ID的原始类型（支持临时ID和数字ID）
      // 使用新数组确保响应式更新
      workflowStore.updateStage(updatedStage.id, {
        predecessorStages: [...(stage.predecessorStages || [])],
        successorStages: [...(stage.successorStages || [])]
      })
    }

    applyTaskUpdates(updatedRelations.fromElement?.type === 'task' ? updatedRelations.fromElement : null)
    applyTaskUpdates(updatedRelations.toElement?.type === 'task' ? updatedRelations.toElement : null)

    applyStageUpdates(updatedRelations.fromElement?.type === 'stage' ? updatedRelations.fromElement : null)
    applyStageUpdates(updatedRelations.toElement?.type === 'stage' ? updatedRelations.toElement : null)
  }

  /**
   * 清除任务的所有连接关系
   * @param {string|number} taskId - 任务ID
   * @param {Array} connections - 连接数组
   * @param {Function} findTaskById - 查找任务函数
   * @returns {Object} { removedCount, filteredConnections }
   */
  const removeAllTaskConnections = (taskId, connections, findTaskById) => {
    // 规范化任务ID为数字类型
    const normalizedTaskId = normalizeId(taskId)
    
    // 1. 从 connections 数组中找到所有与该任务相关的连接
    const connectionsToRemove = connections.filter(conn => 
      (idsEqual(conn.from.elementId, normalizedTaskId) && conn.from.elementType === 'task') ||
      (idsEqual(conn.to.elementId, normalizedTaskId) && conn.to.elementType === 'task')
    )
    
    // 2. 在删除任务之前，先清除其他任务中对该任务的引用
    connectionsToRemove.forEach(conn => {
      const fromId = normalizeId(conn.from.elementId)
      const toId = normalizeId(conn.to.elementId)
      
      // 如果连接是从被删除任务出发的（A->B，删除A）
      if (idsEqual(fromId, normalizedTaskId)) {
        // 清除目标任务B中对A的引用（从B的predecessorTasks中移除A）
        const toTaskInfo = findTaskById(toId)
        if (toTaskInfo && toTaskInfo.task) {
          if (Array.isArray(toTaskInfo.task.predecessorTasks)) {
            toTaskInfo.task.predecessorTasks = toTaskInfo.task.predecessorTasks.filter(
              id => !idsEqual(id, normalizedTaskId)
            )
          }
        }
      }
      
      // 如果连接是指向被删除任务的（B->A，删除A）
      if (idsEqual(toId, normalizedTaskId)) {
        // 清除源任务B中对A的引用（从B的successorTasks中移除A）
        const fromTaskInfo = findTaskById(fromId)
        if (fromTaskInfo && fromTaskInfo.task) {
          if (Array.isArray(fromTaskInfo.task.successorTasks)) {
            fromTaskInfo.task.successorTasks = fromTaskInfo.task.successorTasks.filter(
              id => !idsEqual(id, normalizedTaskId)
            )
          }
        }
      }
    })
    
    // 3. 从 connections 数组中移除这些连接
    const filteredConnections = connections.filter(conn => 
      !((idsEqual(conn.from.elementId, normalizedTaskId) && conn.from.elementType === 'task') ||
        (idsEqual(conn.to.elementId, normalizedTaskId) && conn.to.elementType === 'task'))
    )
    
    // 4. 清除任务本身的连接关系（如果任务还存在）
    const taskInfo = findTaskById(taskId)
    if (taskInfo && taskInfo.task) {
      taskInfo.task.predecessorTasks = []
      taskInfo.task.successorTasks = []
    }
    
    return {
      removedCount: connectionsToRemove.length,
      filteredConnections
    }
  }

  /**
   * 删除单个连接线
   * @param {string} connectionId - 连接ID
   * @param {Array} connections - 连接数组
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   * @param {Object} workflowStore - 工作流store
   * @returns {Object} { success, filteredConnections }
   */
  const removeSingleConnection = (connectionId, connections, findTaskById, findStageById, workflowStore) => {
    const connection = connections.find(c => c.id === connectionId)
    if (!connection) {
      return { success: false, filteredConnections: connections }
    }

    const fromId = normalizeId(connection.from.elementId)
    const toId = normalizeId(connection.to.elementId)
    const fromType = connection.from.elementType
    const toType = connection.to.elementType

    // 更新元素的关系
    if (fromType === 'task' && toType === 'task') {
      const fromTaskInfo = findTaskById(fromId)
      const toTaskInfo = findTaskById(toId)

      if (fromTaskInfo && fromTaskInfo.task) {
        if (Array.isArray(fromTaskInfo.task.successorTasks)) {
          fromTaskInfo.task.successorTasks = fromTaskInfo.task.successorTasks.filter(
            id => !idsEqual(id, toId)
          )
          // 对于阶段外的任务，调用 updateTask 确保 store 同步
          if (fromTaskInfo.isUnassigned) {
            workflowStore.updateTask(fromId, {
              successorTasks: [...fromTaskInfo.task.successorTasks]
            })
          } else {
            // 对于阶段内的任务，也需要同步到 store
            workflowStore.updateTask(fromId, {
              successorTasks: [...fromTaskInfo.task.successorTasks]
            })
          }
        } else {
          fromTaskInfo.task.successorTasks = []
          if (fromTaskInfo.isUnassigned) {
            workflowStore.updateTask(fromId, {
              successorTasks: []
            })
          } else {
            workflowStore.updateTask(fromId, {
              successorTasks: []
            })
          }
        }
      }

      if (toTaskInfo && toTaskInfo.task) {
        if (Array.isArray(toTaskInfo.task.predecessorTasks)) {
          toTaskInfo.task.predecessorTasks = toTaskInfo.task.predecessorTasks.filter(
            id => !idsEqual(id, fromId)
          )
          // 对于阶段外的任务，调用 updateTask 确保 store 同步
          if (toTaskInfo.isUnassigned) {
            workflowStore.updateTask(toId, {
              predecessorTasks: [...toTaskInfo.task.predecessorTasks]
            })
          } else {
            // 对于阶段内的任务，也需要同步到 store
            workflowStore.updateTask(toId, {
              predecessorTasks: [...toTaskInfo.task.predecessorTasks]
            })
          }
        } else {
          toTaskInfo.task.predecessorTasks = []
          if (toTaskInfo.isUnassigned) {
            workflowStore.updateTask(toId, {
              predecessorTasks: []
            })
          } else {
            workflowStore.updateTask(toId, {
              predecessorTasks: []
            })
          }
        }
      }
    } else if ((fromType === 'task' && toType === 'stage') || (fromType === 'stage' && toType === 'task')) {
      // 处理任务到阶段的连接（虽然不应该存在，但如果存在需要清理）
      // 这种情况可能是由于之前的bug导致的，需要清理任务中的关系数据
      if (fromType === 'task') {
        const fromTaskInfo = findTaskById(fromId)
        if (fromTaskInfo && fromTaskInfo.task) {
          // 从任务的successorTasks中移除阶段ID
          if (Array.isArray(fromTaskInfo.task.successorTasks)) {
            fromTaskInfo.task.successorTasks = fromTaskInfo.task.successorTasks.filter(
              id => !idsEqual(id, toId)
            )
            workflowStore.updateTask(fromId, {
              successorTasks: [...fromTaskInfo.task.successorTasks]
            })
          }
        }
      }
      if (toType === 'task') {
        const toTaskInfo = findTaskById(toId)
        if (toTaskInfo && toTaskInfo.task) {
          // 从任务的predecessorTasks中移除阶段ID
          if (Array.isArray(toTaskInfo.task.predecessorTasks)) {
            toTaskInfo.task.predecessorTasks = toTaskInfo.task.predecessorTasks.filter(
              id => !idsEqual(id, fromId)
            )
            workflowStore.updateTask(toId, {
              predecessorTasks: [...toTaskInfo.task.predecessorTasks]
            })
          }
        }
      }
    } else if (fromType === 'stage' && toType === 'stage') {
      const fromStage = findStageById(fromId)
      const toStage = findStageById(toId)

      if (fromStage) {
        // 确保数组存在
        if (!Array.isArray(fromStage.successorStages)) {
          fromStage.successorStages = []
        }
        // 过滤掉目标阶段ID
        const filteredSuccessorStages = fromStage.successorStages.filter(
          id => !idsEqual(id, toId)
        )
        // 更新阶段对象（使用新数组，确保响应式更新）
        fromStage.successorStages = [...filteredSuccessorStages]
        // 同步到 store（确保数据一致性）
          workflowStore.updateStage(fromId, {
          successorStages: [...filteredSuccessorStages]
          })
      }

      if (toStage) {
        // 确保数组存在
        if (!Array.isArray(toStage.predecessorStages)) {
          toStage.predecessorStages = []
        }
        // 过滤掉源阶段ID
        const filteredPredecessorStages = toStage.predecessorStages.filter(
          id => !idsEqual(id, fromId)
        )
        // 更新阶段对象（使用新数组，确保响应式更新）
        toStage.predecessorStages = [...filteredPredecessorStages]
        // 同步到 store（确保数据一致性）
          workflowStore.updateStage(toId, {
          predecessorStages: [...filteredPredecessorStages]
          })
      }
    }

    // 从 connections 数组中移除连接
    const filteredConnections = connections.filter(c => c.id !== connectionId)

    return {
      success: true,
      filteredConnections
    }
  }

  /**
   * 根据两个任务ID找到连接线ID
   * @param {string|number} fromTaskId - 起始任务ID
   * @param {string|number} toTaskId - 目标任务ID
   * @param {Array} connections - 连接数组
   * @returns {string|null} 连接ID或null
   */
  const findConnectionByTaskIds = (fromTaskId, toTaskId, connections) => {
    if (!connections || !Array.isArray(connections)) return null
    
    const normalizedFromId = normalizeId(fromTaskId)
    const normalizedToId = normalizeId(toTaskId)
    
    const connection = connections.find(conn => {
      const connFromId = normalizeId(conn.from.elementId)
      const connToId = normalizeId(conn.to.elementId)
      return (
        idsEqual(connFromId, normalizedFromId) &&
        idsEqual(connToId, normalizedToId) &&
        conn.from.elementType === 'task' &&
        conn.to.elementType === 'task'
      )
    })
    
    return connection ? connection.id : null
  }

  /**
   * 清理任务中的无效关系数据（移除阶段ID，只保留任务ID）
   * @param {Function} findTaskById - 查找任务函数
   * @param {Function} findStageById - 查找阶段函数
   * @param {Object} workflowStore - 工作流store
   * @returns {number} 修复的任务数量
   */
  const cleanupInvalidTaskRelations = (findTaskById, findStageById, workflowStore) => {
    if (!findTaskById || !findStageById || !workflowStore) return 0
    
    let fixedCount = 0
    
    // 获取所有阶段ID集合
    const stageIds = new Set()
    const stages = workflowStore.stages || []
    stages.forEach(stage => {
      if (stage && stage.id != null) {
        stageIds.add(normalizeId(stage.id))
      }
    })
    
    // 检查所有任务
    stages.forEach(stage => {
      if (!stage || !Array.isArray(stage.tasks)) return
      stage.tasks.forEach(task => {
        if (!task) return
        let needsUpdate = false
        const updates = {}
        
        // 检查并清理 predecessorTasks 中的阶段ID
        if (Array.isArray(task.predecessorTasks)) {
          const validPredecessorTasks = task.predecessorTasks.filter(id => {
            const normalizedId = normalizeId(id)
            // 如果ID在阶段ID集合中，说明是阶段ID，应该移除
            if (stageIds.has(normalizedId)) {
              needsUpdate = true
              return false
            }
            // 检查是否是有效的任务ID
            const taskInfo = findTaskById(id)
            return taskInfo && taskInfo.task
          })
          if (needsUpdate || validPredecessorTasks.length !== task.predecessorTasks.length) {
            updates.predecessorTasks = validPredecessorTasks
            needsUpdate = true
          }
        }
        
        // 检查并清理 successorTasks 中的阶段ID
        if (Array.isArray(task.successorTasks)) {
          const validSuccessorTasks = task.successorTasks.filter(id => {
            const normalizedId = normalizeId(id)
            // 如果ID在阶段ID集合中，说明是阶段ID，应该移除
            if (stageIds.has(normalizedId)) {
              needsUpdate = true
              return false
            }
            // 检查是否是有效的任务ID
            const taskInfo = findTaskById(id)
            return taskInfo && taskInfo.task
          })
          if (needsUpdate || validSuccessorTasks.length !== task.successorTasks.length) {
            updates.successorTasks = validSuccessorTasks
            needsUpdate = true
          }
        }
        
        // 如果有需要更新的数据，执行更新
        if (needsUpdate && Object.keys(updates).length > 0) {
          workflowStore.updateTask(task.id, updates)
          fixedCount++
        }
      })
    })
    
    // 检查阶段外任务
    const unassignedTasks = workflowStore.unassignedTasks || []
    unassignedTasks.forEach(task => {
      if (!task) return
      let needsUpdate = false
      const updates = {}
      
      // 检查并清理 predecessorTasks 中的阶段ID
      if (Array.isArray(task.predecessorTasks)) {
        const validPredecessorTasks = task.predecessorTasks.filter(id => {
          const normalizedId = normalizeId(id)
          if (stageIds.has(normalizedId)) {
            needsUpdate = true
            return false
          }
          const taskInfo = findTaskById(id)
          return taskInfo && taskInfo.task
        })
        if (needsUpdate || validPredecessorTasks.length !== task.predecessorTasks.length) {
          updates.predecessorTasks = validPredecessorTasks
          needsUpdate = true
        }
      }
      
      // 检查并清理 successorTasks 中的阶段ID
      if (Array.isArray(task.successorTasks)) {
        const validSuccessorTasks = task.successorTasks.filter(id => {
          const normalizedId = normalizeId(id)
          if (stageIds.has(normalizedId)) {
            needsUpdate = true
            return false
          }
          const taskInfo = findTaskById(id)
          return taskInfo && taskInfo.task
        })
        if (needsUpdate || validSuccessorTasks.length !== task.successorTasks.length) {
          updates.successorTasks = validSuccessorTasks
          needsUpdate = true
        }
      }
      
      // 如果有需要更新的数据，执行更新
      if (needsUpdate && Object.keys(updates).length > 0) {
        workflowStore.updateTask(task.id, updates)
        fixedCount++
      }
    })
    
    return fixedCount
  }

  return {
    applyUpdatedRelations,
    removeAllTaskConnections,
    removeSingleConnection,
    findConnectionByTaskIds,
    cleanupInvalidTaskRelations
  }
}

