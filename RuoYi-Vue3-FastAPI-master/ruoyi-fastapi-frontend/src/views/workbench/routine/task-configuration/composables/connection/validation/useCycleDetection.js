// composables/connection/validation/useCycleDetection.js
// 循环依赖检测逻辑

import { shouldSkipValidation } from '../config/testConfig'

export const useCycleDetection = () => {
  const normalizeId = (id) => {
    if (id == null) return null
    // 所有非临时ID统一转换为数字类型
    // 如果是字符串临时ID（temp_xxx），保持字符串；其他情况统一转换为数字
    if (typeof id === 'string' && id.startsWith('temp_')) {
      return id // 临时ID保持字符串类型
    }
    const num = Number(id)
    // 如果转换失败（NaN），保持原始值；否则统一返回数字类型
    return Number.isNaN(num) ? id : num
  }

  const normalizeIdArray = (ids) => {
    if (!Array.isArray(ids)) return []
    return ids
      .map(normalizeId)
      .filter(id => id != null)
  }

  // 基于connections数组构建邻接表（用于回环检测）
  const buildAdjacencyMapFromConnections = (connections, type) => {
    const adjacency = new Map()

    connections.forEach(conn => {
      if (conn.from.elementType !== type || conn.to.elementType !== type) return
      
      const fromId = normalizeId(conn.from.elementId)
      const toId = normalizeId(conn.to.elementId)
      
      if (fromId == null || toId == null) return

      if (!adjacency.has(fromId)) {
        adjacency.set(fromId, [])
      }
      const successors = adjacency.get(fromId)
      if (!successors.includes(toId)) {
        successors.push(toId)
      }
    })

    return adjacency
  }

  // 基于elements构建邻接表（用于保存时的完整检测）
  const buildAdjacencyMap = (elements, type) => {
    const adjacency = new Map()

    elements.forEach(element => {
      if (!element || element.type !== type) return
      const id = normalizeId(element.id)
      if (id == null) return

      const successors = type === 'task'
        ? normalizeIdArray(element.successorTasks)
        : normalizeIdArray(element.successorStages)

      adjacency.set(id, successors)
    })

    return adjacency
  }

  const hasPath = (adjacency, startId, targetId) => {
    if (startId == null || targetId == null) return false

    // 规范化ID，确保与邻接表的key类型一致（都是数字或临时ID字符串）
    const normalizedStartId = normalizeId(startId)
    const normalizedTargetId = normalizeId(targetId)
    
    // 如果起始和目标相同，直接返回false（自连接在别处处理）
    if (normalizedStartId === normalizedTargetId) {
      return false
    }

    const visited = new Set()
    const stack = [normalizedStartId]

    while (stack.length > 0) {
      const current = stack.pop()

      // 检查是否到达目标（使用严格相等，因为ID已经规范化）
      if (current === normalizedTargetId) {
        return true
      }

      // 检查是否已访问
      if (visited.has(current)) {
        continue
      }

      visited.add(current)

      // 获取邻居节点（邻接表的key已经是规范化后的ID）
      const neighbors = adjacency.get(current) || []
      neighbors.forEach(neighbor => {
        // 规范化邻居ID
        const normalizedNeighbor = normalizeId(neighbor)
        if (!visited.has(normalizedNeighbor)) {
          stack.push(normalizedNeighbor)
        }
      })
    }

    return false
  }

  const detectLocalCycle = (fromElement, toElement, connections) => {
    if (!fromElement || !toElement) return false

    const type = fromElement.type
    if (type !== toElement.type) {
      // 不同类型的元素不会形成循环（在其他地方已有类型校验）
      return false
    }

    // 规范化ID
    const normalizedFromId = normalizeId(fromElement.id)
    const normalizedToId = normalizeId(toElement.id)
    
    // 检查ID是否有效
    if (normalizedFromId == null || normalizedToId == null) {
      return false
    }

    // 基于connections数组构建邻接表（只检测实际存在的连接）
    // 注意：这里不包含即将创建的新连接，因为我们只检测现有连接是否会形成循环
    const adjacency = buildAdjacencyMapFromConnections(connections || [], type)
    
    // 通过检查从 toElement 到 fromElement 是否存在路径来判断是否会形成循环
    // 如果存在路径，那么添加 fromElement -> toElement 就会形成循环
    return hasPath(adjacency, normalizedToId, normalizedFromId)
  }
  
  const validateConnection = (fromElement, toElement, connections) => {
    // 检查验证开关状态
    const skipValidation = shouldSkipValidation()
    
    // 如果关闭了前端验证，直接返回成功
    if (skipValidation) {
      return { valid: true }
    }
    
    const wouldCreateCycle = detectLocalCycle(fromElement, toElement, connections)
    
    if (wouldCreateCycle) {
      return {
        valid: false,
        message: '此连接会创建循环依赖，请检查任务/阶段的执行顺序'
      }
    }
    
    return { valid: true }
  }
  
  const detectCycles = (stages, tasks) => {
    // 如果关闭了前端验证，直接返回空错误数组
    if (shouldSkipValidation()) {
      return []
    }
    
    const errors = []
    
    // 检测阶段间的循环依赖
    const stageCycles = detectStageCycles(stages)
    if (stageCycles.length > 0) {
      errors.push({
        type: 'stage_cycle',
        message: '检测到阶段间存在循环依赖',
        cycles: stageCycles
      })
    }
    
    // 检测任务间的循环依赖
    const taskCycles = detectTaskCycles(tasks)
    if (taskCycles.length > 0) {
      errors.push({
        type: 'task_cycle',
        message: '检测到任务间存在循环依赖',
        cycles: taskCycles
      })
    }
    
    return errors
  }
  
  const detectStageCycles = (stages) => {
    const adjacency = new Map()
    stages.forEach(stage => {
      if (!stage) return
      const id = normalizeId(stage.id)
      if (id == null) return
      adjacency.set(id, normalizeIdArray(stage.successorStages))
    })
    return findCycles(adjacency)
  }
  
  const detectTaskCycles = (tasks) => {
    const adjacency = new Map()
    tasks.forEach(task => {
      if (!task) return
      const id = normalizeId(task.id)
      if (id == null) return
      adjacency.set(id, normalizeIdArray(task.successorTasks))
    })
    return findCycles(adjacency)
  }
  
  const findCycles = (graph) => {
    const visited = new Set()
    const recursionStack = new Set()
    const cycles = []
    
    const dfs = (node, path) => {
      if (recursionStack.has(node)) {
        // 找到循环
        const cycleStart = path.indexOf(node)
        cycles.push(path.slice(cycleStart))
        return
      }
      
      if (visited.has(node)) {
        return
      }
      
      visited.add(node)
      recursionStack.add(node)
      
      const neighbors = graph.get(node) || []
      neighbors.forEach(neighbor => {
        dfs(neighbor, [...path, node])
      })
      
      recursionStack.delete(node)
    }
    
    graph.forEach((_, node) => {
      if (!visited.has(node)) {
        dfs(node, [])
      }
    })
    
    return cycles
  }
  
  return {
    validateConnection,
    detectCycles
  }
}

