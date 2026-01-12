// composables/connection/utils/useConnectionInitializer.js
// 连接初始化：从工作流数据构建连接数组

export const useConnectionInitializer = () => {
  const buildConnectionsFromWorkflow = (workflow, unassignedTasks = []) => {
    if (!workflow || !Array.isArray(workflow.stages)) return []

    const newConnections = []
    const seenKeys = new Set()

    const stageMap = new Map()
    const taskMap = new Map()

    workflow.stages.forEach(stage => {
      if (!stage) return
      stageMap.set(stage.id, stage)
      if (Array.isArray(stage.tasks)) {
        stage.tasks.forEach(task => {
          if (task) {
            taskMap.set(task.id, task)
          }
        })
      }
    })
    
    // 添加阶段外的任务到taskMap
    if (Array.isArray(unassignedTasks)) {
      unassignedTasks.forEach(task => {
        if (task) {
          taskMap.set(task.id, task)
        }
      })
    }

    const addConnection = (fromId, fromType, toId, toType) => {
      if (fromId == null || toId == null) return
      const key = `${fromType}-${fromId}->${toType}-${toId}`
      if (seenKeys.has(key)) return
      seenKeys.add(key)
      newConnections.push({
        id: `init_conn_${key}_${Math.random().toString(36).slice(2, 8)}`,
        from: { elementId: fromId, elementType: fromType },
        to: { elementId: toId, elementType: toType }
      })
    }

    workflow.stages.forEach(stage => {
      if (!stage) return
      if (Array.isArray(stage.predecessorStages)) {
        stage.predecessorStages.forEach(preStageId => {
          if (stageMap.has(preStageId)) {
            addConnection(preStageId, 'stage', stage.id, 'stage')
          }
        })
      }

      if (Array.isArray(stage.tasks)) {
        stage.tasks.forEach(task => {
          if (!task || !Array.isArray(task.predecessorTasks)) return
          task.predecessorTasks.forEach(preTaskId => {
            if (taskMap.has(preTaskId)) {
              addConnection(preTaskId, 'task', task.id, 'task')
            }
          })
        })
      }
    })
    
    // 处理阶段外任务的前置/后置任务连接
    if (Array.isArray(unassignedTasks)) {
      unassignedTasks.forEach(task => {
        if (!task || !Array.isArray(task.predecessorTasks)) return
        task.predecessorTasks.forEach(preTaskId => {
          if (taskMap.has(preTaskId)) {
            addConnection(preTaskId, 'task', task.id, 'task')
          }
        })
      })
    }

    return newConnections
  }

  const initConnections = (workflow, connectionsRef, workflowStore, unassignedTasks = []) => {
    const initialConnections = buildConnectionsFromWorkflow(workflow, unassignedTasks)
    connectionsRef.value = initialConnections
    if (workflowStore?.setConnections) {
      workflowStore.setConnections(initialConnections)
    }
    return initialConnections
  }

  return {
    buildConnectionsFromWorkflow,
    initConnections
  }
}

