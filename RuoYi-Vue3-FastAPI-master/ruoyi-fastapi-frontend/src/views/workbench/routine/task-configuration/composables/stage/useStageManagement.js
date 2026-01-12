// composables/useStageManagement.js
import { ElMessage, ElMessageBox } from 'element-plus'
import { useIdManager } from '../utils/useIdManager'

export const useStageManagement = () => {
  const { generateNewId, createStageModel } = useIdManager()
  const normalizeId = (id) => {
    if (id === null || id === undefined) return null
    return String(id)
  }

  const removeStageReferencesFromOthers = (stageId, workflowData, workflowStore) => {
    const stageIdStr = normalizeId(stageId)
    if (!workflowData?.stages || !stageIdStr) return
    workflowData.stages.forEach(stage => {
      if (!stage || normalizeId(stage.id) === stageIdStr) return
      let updated = false
      if (Array.isArray(stage.predecessorStages)) {
        const filtered = stage.predecessorStages.filter(id => normalizeId(id) !== stageIdStr)
        if (filtered.length !== stage.predecessorStages.length) {
          stage.predecessorStages = filtered
          updated = true
        }
      }
      if (Array.isArray(stage.successorStages)) {
        const filtered = stage.successorStages.filter(id => normalizeId(id) !== stageIdStr)
        if (filtered.length !== stage.successorStages.length) {
          stage.successorStages = filtered
          updated = true
        }
      }
      if (updated) {
        workflowStore.updateStage(stage.id, {
          predecessorStages: stage.predecessorStages ? [...stage.predecessorStages] : [],
          successorStages: stage.successorStages ? [...stage.successorStages] : []
        })
      }
    })
  }

  const cleanupConnectionsAfterStageRemoval = (
    stageId,
    stageTasks = [],
    connectionsRef = null,
    workflowStore
  ) => {
    const stageIdStr = normalizeId(stageId)
    const taskIdSet = new Set(
      stageTasks
        .map(task => normalizeId(task?.id))
        .filter(id => id !== null)
    )

    const shouldRemoveConnection = (connection) => {
      if (!connection || !connection.from || !connection.to) return false
      const fromId = normalizeId(connection.from.elementId)
      const toId = normalizeId(connection.to.elementId)
      const fromType = connection.from.elementType
      const toType = connection.to.elementType

      if (fromType === 'stage' && fromId === stageIdStr) return true
      if (toType === 'stage' && toId === stageIdStr) return true
      if (fromType === 'task' && taskIdSet.has(fromId)) return true
      if (toType === 'task' && taskIdSet.has(toId)) return true
      return false
    }

    const filterConnections = (list = []) => {
      if (!Array.isArray(list)) return []
      return list.filter(conn => !shouldRemoveConnection(conn))
    }

    let filteredConnections = null
    if (connectionsRef) {
      if (Object.prototype.hasOwnProperty.call(connectionsRef, 'value')) {
        filteredConnections = filterConnections(connectionsRef.value)
        connectionsRef.value = filteredConnections
      } else if (Array.isArray(connectionsRef)) {
        filteredConnections = filterConnections(connectionsRef)
        connectionsRef.splice(0, connectionsRef.length, ...filteredConnections)
      }
    }

    // 直接操作 connections ref（主数据源）
    if (connectionsRef) {
      if (Object.prototype.hasOwnProperty.call(connectionsRef, 'value')) {
        connectionsRef.value = filteredConnections || filterConnections(connectionsRef.value)
      } else if (Array.isArray(connectionsRef)) {
        connectionsRef.splice(0, connectionsRef.length, ...(filteredConnections || filterConnections(connectionsRef)))
      }
    }
    
    // 同步到 workflowStore（用于兼容性，workflowStore.setConnections 会直接操作 connectionsRef）
    if (workflowStore && typeof workflowStore.setConnections === 'function') {
      const currentConnections = filteredConnections || (connectionsRef?.value || connectionsRef || [])
      workflowStore.setConnections(currentConnections)
    }
  }

  /**
   * 根据ID查找阶段
   * @param {string|number} stageId - 阶段ID
   * @param {Object} workflowData - 工作流数据
   * @returns {Object|null} 阶段对象或null
   */
  const findStageById = (stageId, workflowData) => {
    if (!workflowData || !workflowData.stages) return null
    return workflowData.stages.find(stage => String(stage.id) === String(stageId)) || null
  }

  /**
   * 添加新阶段
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   * @returns {Object|null} 新创建的阶段或null
   */
  const handleAddStage = (workflowData, workflowStore) => {
    if (!workflowData || !workflowData.stages) {
      ElMessage.error('工作流数据未初始化')
      return null
    }
    
    const projectId = workflowData.projectId
    // 生成新的整数ID（基于已使用的ID自增）
    const newStageId = generateNewId(workflowData)
    const newStage = createStageModel(newStageId, '新阶段', projectId)
    newStage.position = {
      x: 100 + (workflowData.stages.length * 400),
      y: 100,
      width: 300,
      height: 200
    }
    
    // 只添加到 workflowData.stages，因为 workflowStore.stages 和 workflowData.stages 是同一个引用
    workflowData.stages.push(newStage)
    // 注意：不需要调用 workflowStore.addStage，因为它们是同一个数组引用
    
    ElMessage.success('已添加新阶段')
    return newStage
  }

  /**
   * 在指定位置创建新阶段
   * @param {Object} position - 位置 { x, y }
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   * @returns {Object|null} 新创建的阶段或null
   */
  const createStageAtPosition = (position, workflowData, workflowStore) => {
    if (!workflowData || !workflowData.stages) {
      ElMessage.error('工作流数据未初始化')
      return null
    }
    
    const projectId = workflowData.projectId
    // 生成新的整数ID（基于已使用的ID自增）
    const newStageId = generateNewId(workflowData)
    const newStage = createStageModel(newStageId, '新阶段', projectId)
    newStage.position = {
      x: position.x,
      y: position.y,
      width: 400, // 使用最小宽度
      height: 250 // 使用最小高度
    }
    
    // 只添加到 workflowData.stages，因为 workflowStore.stages 和 workflowData.stages 是同一个引用
    workflowData.stages.push(newStage)
    // 注意：不需要调用 workflowStore.addStage，因为它们是同一个数组引用
    
    ElMessage.success('已添加新阶段')
    return newStage
  }

  /**
   * 删除阶段
   * @param {string|number} stageId - 阶段ID
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   * @param {Object} selectedStageIdRef - 选中的阶段ID ref
   * @returns {Promise<boolean>} 是否删除成功
   */
  const handleStageDelete = async (stageId, workflowData, workflowStore, selectedStageIdRef, connectionsRef = null) => {
    if (!workflowData || !workflowData.stages) {
      ElMessage.error('工作流数据未初始化')
      return false
    }
    
    try {
      await ElMessageBox.confirm('确定要删除这个阶段吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      const stageIdStr = normalizeId(stageId)
      const stageToDelete = workflowData.stages.find(s => normalizeId(s.id) === stageIdStr)
      
      workflowData.stages = workflowData.stages.filter(s => normalizeId(s.id) !== stageIdStr)
      // 删除阶段（直接操作主数据源）
      if (workflowData.stages) {
        const stageIdStr = normalizeId(stageId)
        workflowData.stages = workflowData.stages.filter(s => normalizeId(s.id) !== stageIdStr)
      }
      // 同时通过 workflowStore 删除（用于兼容性）
      workflowStore.removeStage(stageId)
      
      if (selectedStageIdRef && normalizeId(selectedStageIdRef.value) === stageIdStr) {
        selectedStageIdRef.value = null
      }
      
      removeStageReferencesFromOthers(stageId, workflowData, workflowStore)
      cleanupConnectionsAfterStageRemoval(stageId, stageToDelete?.tasks || [], connectionsRef, workflowStore)
      
      ElMessage.success('阶段已删除')
      return true
    } catch {
      // 用户取消删除
      return false
    }
  }

  /**
   * 处理阶段调整大小结束
   * @param {Object} data - 调整大小数据
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   */
  const handleStageResizeEnd = (data, workflowData, workflowStore) => {
    if (!workflowData || !workflowData.stages) return
    
    const stage = workflowData.stages.find(s => s.id === data.stageId)
    if (stage) {
      // 更新尺寸
      stage.position.width = data.newSize.width
      stage.position.height = data.newSize.height
      
      // 如果位置发生变化，也更新位置（用于左侧和上侧调整时）
      if (data.newPosition) {
        stage.position.x = data.newPosition.x
        stage.position.y = data.newPosition.y
      }
      
      // 更新阶段位置（直接操作主数据源）
      if (stage) {
        stage.position = { ...stage.position, ...data.position }
      }
      // 同时通过 workflowStore 更新（用于兼容性）
      workflowStore.updateStage(data.stageId, { position: stage.position })
    }
  }

  /**
   * 处理阶段位置变化
   * @param {Object} data - 位置变化数据
   * @param {Object} workflowData - 工作流数据
   * @param {Object} workflowStore - 工作流store
   */
  const handleStagePositionChange = (data, workflowData, workflowStore) => {
    if (!workflowData || !workflowData.stages) return
    
    const stage = workflowData.stages.find(s => s.id === data.stageId)
    if (stage) {
      // 保存旧的位置
      const oldPosition = { ...stage.position }
      
      // 约束到画布边界（确保不超出左侧和上侧）
      const constrainedPosition = {
        x: Math.max(0, data.newPosition.x),
        y: Math.max(0, data.newPosition.y)
      }
      
      // 更新阶段位置
      stage.position.x = constrainedPosition.x
      stage.position.y = constrainedPosition.y
      
      // 计算位移量（应该在更新前计算，使用约束后的位置）
      const deltaX = constrainedPosition.x - oldPosition.x
      const deltaY = constrainedPosition.y - oldPosition.y
      
      // 更新内部所有任务的位置（保持相对位置不变）
      if (stage.tasks && Array.isArray(stage.tasks)) {
        stage.tasks.forEach(task => {
          task.position.x += deltaX
          task.position.y += deltaY
        })
      }
      
      // 更新阶段位置（直接操作主数据源）
      if (stage) {
        stage.position = { ...stage.position, ...data.position }
      }
      // 同时通过 workflowStore 更新（用于兼容性）
      workflowStore.updateStage(data.stageId, { position: stage.position })
    }
  }

  /**
   * 处理阶段选择
   * @param {string|number} stageId - 阶段ID
   * @param {Object} selectedStageIdRef - 选中的阶段ID ref
   * @param {Object} selectedTaskIdRef - 选中的任务ID ref
   * @param {Object} selectedConnectionIdRef - 选中的连接线ID ref（可选）
   * @param {Object} workflowStore - 工作流store
   */
  const handleStageSelect = (stageId, selectedStageIdRef, selectedTaskIdRef, workflowStore, selectedConnectionIdRef = null) => {
    selectedStageIdRef.value = stageId
    selectedTaskIdRef.value = null
    // 选中阶段时，清除连接线选中状态
    if (selectedConnectionIdRef) {
      selectedConnectionIdRef.value = null
    }
    workflowStore.selectElement(stageId, 'stage')
  }

  return {
    findStageById,
    handleAddStage,
    createStageAtPosition,
    handleStageDelete,
    handleStageResizeEnd,
    handleStagePositionChange,
    handleStageSelect
  }
}

