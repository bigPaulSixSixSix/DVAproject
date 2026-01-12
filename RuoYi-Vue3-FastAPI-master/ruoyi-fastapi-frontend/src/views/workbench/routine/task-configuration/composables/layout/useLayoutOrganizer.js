// composables/layout/useLayoutOrganizer.js
// 布局整理功能：使用Sugiyama层次布局算法重新排列任务和阶段

import { useGridSnap } from '../canvas/useGridSnap'

/**
 * 布局整理器
 * 使用Sugiyama层次布局算法重新计算任务和阶段的位置
 */
export const useLayoutOrganizer = () => {
  const { snapToGrid, gridSize } = useGridSnap()
  // 常量定义
  const TASK_WIDTH = 196
  const TASK_HEIGHT = 100
  const TASK_BORDER_WIDTH = 1 // 任务边框宽度（左右各1px，共2px）
  const HEADER_HEIGHT = 60
  const BORDER_WIDTH = 4 // 阶段边框宽度
  const TASK_SPACING = 40 // 任务间距
  const STAGE_SPACING = 80 // 阶段间距
  const STAGE_PADDING = 40 // 阶段内边距（任务到阶段边界的距离）
  
  // 任务实际占用尺寸（包含边框）
  const TASK_ACTUAL_WIDTH = TASK_WIDTH + TASK_BORDER_WIDTH * 2
  const TASK_ACTUAL_HEIGHT = TASK_HEIGHT + TASK_BORDER_WIDTH * 2

  /**
   * 构建有向图的邻接表
   * @param {Array} elements - 元素数组（任务或阶段）
   * @param {string} predecessorKey - 前置关系字段名（'predecessorTasks' 或 'predecessorStages'）
   * @param {string} successorKey - 后置关系字段名（'successorTasks' 或 'successorStages'）
   * @returns {Map} 邻接表，key为元素ID，value为后置元素ID数组
   */
  const buildAdjacencyMap = (elements, predecessorKey, successorKey) => {
    const adjacencyMap = new Map()
    const elementMap = new Map()

    // 创建元素映射
    elements.forEach(element => {
      if (element && element.id != null) {
        elementMap.set(String(element.id), element)
        adjacencyMap.set(String(element.id), [])
      }
    })

    // 构建邻接关系（从predecessor和successor两个方向）
    elements.forEach(element => {
      if (!element || element.id == null) return

      const elementId = String(element.id)

      // 从successorTasks/successorStages构建：element -> successors
      const successors = element[successorKey] || []
      successors.forEach(successorId => {
        const successorIdStr = String(successorId)
        if (elementMap.has(successorIdStr)) {
          const currentSuccessors = adjacencyMap.get(elementId) || []
          if (!currentSuccessors.includes(successorIdStr)) {
            currentSuccessors.push(successorIdStr)
          }
        }
      })

      // 从predecessorTasks/predecessorStages构建：predecessors -> element
      const predecessors = element[predecessorKey] || []
      predecessors.forEach(predecessorId => {
        const predecessorIdStr = String(predecessorId)
        if (elementMap.has(predecessorIdStr)) {
          const currentSuccessors = adjacencyMap.get(predecessorIdStr) || []
          if (!currentSuccessors.includes(elementId)) {
            currentSuccessors.push(elementId)
          }
        }
      })
    })

    return adjacencyMap
  }

  /**
   * 拓扑排序（用于确定层次）
   * @param {Map} adjacencyMap - 邻接表
   * @returns {Array} 排序后的元素ID数组
   */
  const topologicalSort = (adjacencyMap) => {
    const inDegree = new Map()
    const queue = []
    const result = []

    // 初始化入度
    adjacencyMap.forEach((successors, id) => {
      inDegree.set(id, 0)
    })

    // 计算入度
    adjacencyMap.forEach((successors, id) => {
      successors.forEach(successorId => {
        const currentInDegree = inDegree.get(successorId) || 0
        inDegree.set(successorId, currentInDegree + 1)
      })
    })

    // 找到所有入度为0的节点
    inDegree.forEach((degree, id) => {
      if (degree === 0) {
        queue.push(id)
      }
    })

    // 拓扑排序
    while (queue.length > 0) {
      const current = queue.shift()
      result.push(current)

      const successors = adjacencyMap.get(current) || []
      successors.forEach(successorId => {
        const currentInDegree = inDegree.get(successorId)
        inDegree.set(successorId, currentInDegree - 1)
        if (inDegree.get(successorId) === 0) {
          queue.push(successorId)
        }
      })
    }

    return result
  }

  /**
   * 将元素分配到层次
   * @param {Map} adjacencyMap - 邻接表
   * @param {Array} sortedIds - 拓扑排序后的ID数组
   * @returns {Map} 层次映射，key为层次（从0开始），value为该层次的元素ID数组
   */
  const assignLayers = (adjacencyMap, sortedIds) => {
    const layerMap = new Map()
    const elementLayer = new Map()

    // 初始化所有元素在0层
    sortedIds.forEach(id => {
      elementLayer.set(id, 0)
    })

    // 根据依赖关系分配层次
    sortedIds.forEach(id => {
      const predecessors = []
      adjacencyMap.forEach((successors, predId) => {
        if (successors.includes(id)) {
          predecessors.push(predId)
        }
      })

      if (predecessors.length > 0) {
        const maxPredLayer = Math.max(...predecessors.map(predId => elementLayer.get(predId) || 0))
        elementLayer.set(id, maxPredLayer + 1)
      }
    })

    // 构建层次映射
    elementLayer.forEach((layer, id) => {
      if (!layerMap.has(layer)) {
        layerMap.set(layer, [])
      }
      layerMap.get(layer).push(id)
    })

    return layerMap
  }

  /**
   * 计算阶段内任务的布局
   * @param {Object} stage - 阶段对象
   * @returns {Object} 布局结果，包含任务位置和阶段尺寸
   */
  const layoutTasksInStage = (stage) => {
    const tasks = stage.tasks || []
    if (tasks.length === 0) {
      // 如果没有任务，返回默认阶段尺寸
      return {
        taskPositions: new Map(),
        stageWidth: 300,
        stageHeight: HEADER_HEIGHT + STAGE_PADDING * 2
      }
    }

    // 构建任务邻接表
    const adjacencyMap = buildAdjacencyMap(tasks, 'predecessorTasks', 'successorTasks')
    
    // 拓扑排序
    const sortedTaskIds = topologicalSort(adjacencyMap)
    
    // 如果拓扑排序结果不完整，使用所有任务ID
    const allTaskIds = tasks.map(t => String(t.id))
    const finalSortedIds = sortedTaskIds.length === allTaskIds.length 
      ? sortedTaskIds 
      : allTaskIds

    // 分配层次
    const layerMap = assignLayers(adjacencyMap, finalSortedIds)

    // 计算每层的最大高度（同一层的任务垂直排列）
    const layerHeights = []
    layerMap.forEach((taskIds, layer) => {
      const layerHeight = taskIds.length * TASK_ACTUAL_HEIGHT + (taskIds.length - 1) * TASK_SPACING
      layerHeights.push(layerHeight)
    })

    // 总宽度 = 层数 * 任务实际宽度 + (层数-1) * 间距
    const totalWidth = layerMap.size > 0 
      ? layerMap.size * TASK_ACTUAL_WIDTH + (layerMap.size - 1) * TASK_SPACING 
      : TASK_ACTUAL_WIDTH
    // 总高度 = 所有层中的最大高度（layerHeights已经包含了任务实际高度）
    const totalHeight = layerHeights.length > 0 
      ? Math.max(...layerHeights, TASK_ACTUAL_HEIGHT) 
      : TASK_ACTUAL_HEIGHT

    // 计算任务位置（相对坐标，相对于阶段内容区）
    // 每一层的任务竖向排列，层与层之间横向排列
    const taskPositions = new Map()
    let currentX = 0 // 层的位置（横向）
    
    layerMap.forEach((taskIds, layer) => {
      const layerHeight = taskIds.length * TASK_ACTUAL_HEIGHT + (taskIds.length - 1) * TASK_SPACING
      const startY = (totalHeight - layerHeight) / 2 // 垂直居中对齐

      // 同一层的任务垂直排列
      let currentY = startY
      taskIds.forEach((taskId) => {
        taskPositions.set(taskId, { x: currentX, y: currentY })
        currentY += TASK_ACTUAL_HEIGHT + TASK_SPACING
      })

      // 移动到下一层（横向）
      currentX += TASK_ACTUAL_WIDTH + TASK_SPACING
    })

    // 计算阶段尺寸（包含内边距）
    let stageWidth = totalWidth + STAGE_PADDING * 2
    let stageHeight = HEADER_HEIGHT + totalHeight + STAGE_PADDING * 2
    
    // 尺寸向上取整到网格的倍数
    stageWidth = Math.ceil(stageWidth / gridSize) * gridSize
    stageHeight = Math.ceil(stageHeight / gridSize) * gridSize

    return {
      taskPositions,
      stageWidth,
      stageHeight
    }
  }

  /**
   * 计算所有阶段的布局
   * @param {Array} stages - 阶段数组
   * @param {Map} stageTaskLayouts - 阶段内任务布局结果映射
   * @returns {Object} 布局结果，包含阶段位置
   */
  const layoutStages = (stages, stageTaskLayouts) => {
    if (stages.length === 0) {
      return {
        stagePositions: new Map()
      }
    }

    // 构建阶段邻接表
    const adjacencyMap = buildAdjacencyMap(stages, 'predecessorStages', 'successorStages')
    
    // 拓扑排序
    const sortedStageIds = topologicalSort(adjacencyMap)
    
    // 如果拓扑排序结果不完整，使用所有阶段ID
    const allStageIds = stages.map(s => String(s.id))
    const finalSortedIds = sortedStageIds.length === allStageIds.length 
      ? sortedStageIds 
      : allStageIds

    // 分配层次
    const layerMap = assignLayers(adjacencyMap, finalSortedIds)

    // 计算阶段位置
    // 阶段也是：每一层的阶段竖向排列，层与层之间横向排列
    const stagePositions = new Map()
    const START_OFFSET = 400 // 距离左上角400px的偏移量
    // 起始位置对齐到网格
    const snappedStartOffset = snapToGrid({ x: START_OFFSET, y: START_OFFSET })
    const alignedStartX = snappedStartOffset.x ?? START_OFFSET
    const alignedStartY = snappedStartOffset.y ?? START_OFFSET
    let currentX = alignedStartX
    let maxStageHeight = 0 // 记录所有阶段的最大高度，用于垂直对齐

    // 第一遍：计算每层的最大宽度和最大高度
    const layerMaxWidths = []
    const layerMaxHeights = []
    
    layerMap.forEach((stageIds, layer) => {
      let maxWidth = 0
      let maxHeight = 0
      
      stageIds.forEach(stageId => {
        const layout = stageTaskLayouts.get(stageId)
        if (layout) {
          maxWidth = Math.max(maxWidth, layout.stageWidth)
          maxHeight = Math.max(maxHeight, layout.stageHeight)
        } else {
          maxHeight = Math.max(maxHeight, HEADER_HEIGHT + STAGE_PADDING * 2)
        }
      })
      
      layerMaxWidths.push(maxWidth)
      layerMaxHeights.push(maxHeight)
      maxStageHeight = Math.max(maxStageHeight, maxHeight)
    })

    // 第二遍：计算阶段位置
    // 每一层的阶段竖向排列，层与层之间横向排列
    layerMap.forEach((stageIds, layer) => {
      const layerMaxWidth = layerMaxWidths[layer]
      const layerMaxHeight = layerMaxHeights[layer]

      // 如果当前层有多个阶段，垂直排列
      if (stageIds.length > 1) {
        let currentY = alignedStartY
        stageIds.forEach(stageId => {
          const layout = stageTaskLayouts.get(stageId)
          let stageHeight = layout ? layout.stageHeight : HEADER_HEIGHT + STAGE_PADDING * 2
          
          // 位置对齐到网格
          const snappedPos = snapToGrid({ x: currentX, y: currentY })
          const snappedX = snappedPos.x ?? currentX
          const snappedY = snappedPos.y ?? currentY
          
          stagePositions.set(stageId, { x: snappedX, y: snappedY })
          
          // 下一个阶段的Y位置也要对齐到网格
          const nextY = currentY + stageHeight + STAGE_SPACING
          const snappedNextY = snapToGrid({ y: nextY }).y ?? nextY
          currentY = snappedNextY
        })
      } else {
        // 单个阶段，垂直居中（相对于所有阶段的最大高度）
        const stageId = stageIds[0]
        const layout = stageTaskLayouts.get(stageId)
        let stageHeight = layout ? layout.stageHeight : HEADER_HEIGHT + STAGE_PADDING * 2
        let centerY = alignedStartY + (maxStageHeight - stageHeight) / 2
        centerY = Math.max(alignedStartY, centerY)
        
        // 位置对齐到网格
        const snappedPos = snapToGrid({ x: currentX, y: centerY })
        const snappedX = snappedPos.x ?? currentX
        const snappedY = snappedPos.y ?? centerY
        
        stagePositions.set(stageId, { x: snappedX, y: snappedY })
      }

      // 移动到下一层（横向），位置对齐到网格
      const nextX = currentX + layerMaxWidth + STAGE_SPACING
      const snappedNextX = snapToGrid({ x: nextX }).x ?? nextX
      currentX = snappedNextX
    })

    return {
      stagePositions
    }
  }

  /**
   * 整理布局主函数
   * @param {Object} workflowData - 工作流数据
   * @param {Array} unassignedTasks - 阶段外任务数组
   * @returns {Object} 布局结果，包含所有任务和阶段的新位置
   */
  const organizeLayout = (workflowData, unassignedTasks = []) => {
    const stages = workflowData?.stages || []
    
    // 第一步：计算每个阶段内任务的布局
    const stageTaskLayouts = new Map()
    const allTaskPositions = new Map() // 存储所有任务的绝对位置

    stages.forEach(stage => {
      const layout = layoutTasksInStage(stage)
      stageTaskLayouts.set(String(stage.id), layout)
    })

    // 第二步：计算阶段的布局
    const stageLayout = layoutStages(stages, stageTaskLayouts)

    // 第三步：计算任务的绝对位置（阶段位置 + 任务相对位置）
    stages.forEach(stage => {
      const stageId = String(stage.id)
      const stagePos = stageLayout.stagePositions.get(stageId)
      const taskLayout = stageTaskLayouts.get(stageId)

      if (stagePos && taskLayout) {
        taskLayout.taskPositions.forEach((relPos, taskId) => {
          // 任务的绝对位置 = 阶段位置 + 阶段内边距 + 任务相对位置
          // y坐标需要加上阶段头部高度
          let absoluteX = stagePos.x + STAGE_PADDING + relPos.x
          let absoluteY = stagePos.y + HEADER_HEIGHT + STAGE_PADDING + relPos.y
          
          // 位置对齐到网格
          const snappedPos = snapToGrid({ x: absoluteX, y: absoluteY })
          absoluteX = snappedPos.x ?? absoluteX
          absoluteY = snappedPos.y ?? absoluteY
          
          allTaskPositions.set(taskId, { x: absoluteX, y: absoluteY })
        })
      }
    })

    // 处理阶段外任务（放在最下面）
    // 计算所有阶段的最大Y坐标和最大高度
    let maxStageY = 0
    let maxStageHeight = 0
    
    if (stages.length > 0) {
      stageLayout.stagePositions.forEach((pos, stageId) => {
        maxStageY = Math.max(maxStageY, pos.y)
        const size = stageTaskLayouts.get(stageId)
        if (size) {
          maxStageHeight = Math.max(maxStageHeight, size.stageHeight)
        }
      })
    }
    
    // 阶段外任务放在最下面，水平排列
    const START_OFFSET = 400
    // 起始位置对齐到网格
    const snappedStartOffset = snapToGrid({ x: START_OFFSET, y: START_OFFSET })
    const alignedStartX = snappedStartOffset.x ?? START_OFFSET
    const alignedStartY = snappedStartOffset.y ?? START_OFFSET
    
    let unassignedStartY = maxStageY + maxStageHeight + (stages.length > 0 ? STAGE_SPACING * 2 : alignedStartY)
    let unassignedX = alignedStartX
    
    // 计算出的位置对齐到网格
    const snappedStartPos = snapToGrid({ x: unassignedX, y: unassignedStartY })
    unassignedX = snappedStartPos.x ?? unassignedX
    unassignedStartY = snappedStartPos.y ?? unassignedStartY
    
    unassignedTasks.forEach((task) => {
      const taskId = String(task.id)
      
      // 位置对齐到网格
      const snappedPos = snapToGrid({ x: unassignedX, y: unassignedStartY })
      const snappedX = snappedPos.x ?? unassignedX
      const snappedY = snappedPos.y ?? unassignedStartY
      
      allTaskPositions.set(taskId, {
        x: snappedX,
        y: snappedY
      })
      unassignedX += TASK_ACTUAL_WIDTH + TASK_SPACING
    })

    return {
      taskPositions: allTaskPositions,
      stagePositions: stageLayout.stagePositions,
      stageSizes: new Map(Array.from(stageTaskLayouts.entries()).map(([id, layout]) => [
        id,
        { width: layout.stageWidth, height: layout.stageHeight }
      ]))
    }
  }

  return {
    organizeLayout
  }
}

