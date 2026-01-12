// composables/useTaskManagement.js
import { ElMessage, ElMessageBox } from 'element-plus'
import { useIdManager } from '../utils/useIdManager'
import { useStageTime } from '../stage/useStageTime'
import { updateStageAndRelatedStagesTimeIssueFlags } from '../stage/useStageTimeValidation'

export const useTaskManagement = () => {
  const { generateNewId, createTaskModel } = useIdManager()
  // 统一的任务查找函数（能查找阶段内和阶段外任务）
  const findTaskById = (taskId, workflowData, unassignedTasks) => {
    // 使用字符串比较确保类型一致
    const taskIdStr = String(taskId)
    
    // 先在阶段内查找
    if (workflowData?.stages) {
      for (const stage of workflowData.stages) {
        if (stage.tasks && Array.isArray(stage.tasks)) {
          const task = stage.tasks.find(t => String(t.id) === taskIdStr)
          if (task) {
            return { task, stage, isUnassigned: false }
          }
        }
      }
    }
    
    // 再在阶段外查找
    const unassignedTask = unassignedTasks.find(t => String(t.id) === taskIdStr)
    if (unassignedTask) {
      return { task: unassignedTask, stage: null, isUnassigned: true }
    }
    
    return null
  }

  // 根据绝对坐标查找任务所在的阶段
  const findStageByPosition = (absolutePosition, workflowData) => {
    if (!workflowData?.stages) return null
    
    const TASK_WIDTH = 198
    const TASK_HEIGHT = 100
    const taskRect = {
      x: absolutePosition.x,
      y: absolutePosition.y,
      width: TASK_WIDTH,
      height: TASK_HEIGHT
    }
    
    for (const stage of workflowData.stages) {
      const stageRect = {
        x: stage.position.x,
        y: stage.position.y,
        width: stage.position.width || 300,
        height: stage.position.height || 200
      }
      
      // 检查任务中心点是否在阶段内
      const taskCenterX = taskRect.x + taskRect.width / 2
      const taskCenterY = taskRect.y + taskRect.height / 2
      
      if (taskCenterX >= stageRect.x &&
          taskCenterX <= stageRect.x + stageRect.width &&
          taskCenterY >= stageRect.y &&
          taskCenterY <= stageRect.y + stageRect.height) {
        return stage
      }
    }
    
    return null
  }

  // 处理任务删除
  const handleTaskDelete = async (taskId, workflowData, unassignedTasksRef, removeAllTaskConnections, workflowStore, selectedTaskIdRef) => {
    if (!workflowData?.stages) {
      ElMessage.error('工作流数据未初始化')
      return
    }
    
    try {
      await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      // 查找任务
      const taskInfo = findTaskById(taskId, workflowData, unassignedTasksRef.value)
      if (!taskInfo) {
        ElMessage.error('未找到任务')
        return
      }
      
      // 清除连接关系
      removeAllTaskConnections(taskId)
      
      // 记录任务所在的阶段ID（如果任务在阶段内），用于后续更新阶段时间
      const stageIdBeforeDelete = !taskInfo.isUnassigned && taskInfo.stage ? taskInfo.stage.id : null
      
      // 从阶段中移除任务（如果在阶段内）
      if (!taskInfo.isUnassigned && taskInfo.stage) {
        taskInfo.stage.tasks = taskInfo.stage.tasks.filter(t => t.id !== taskId)
        workflowStore.removeTask(taskId)
        
        // 删除任务后，更新阶段的时间（重新计算阶段内所有任务的时间范围）
        const { updateStageTime } = useStageTime()
        const updatedStage = updateStageTime(taskInfo.stage)
        // 使用 Object.assign 确保响应式更新
        Object.assign(taskInfo.stage, {
          startTime: updatedStage.startTime,
          endTime: updatedStage.endTime,
          duration: updatedStage.duration
        })
      } else if (taskInfo.isUnassigned) {
        // 从阶段外任务数组中移除
        const index = unassignedTasksRef.value.findIndex(t => t.id === taskId)
        if (index !== -1) {
          unassignedTasksRef.value.splice(index, 1)
        }
      }
      
      // 如果任务在阶段内，更新阶段及其相关阶段的时间异常标记
      if (stageIdBeforeDelete) {
        // 创建 findStageById 函数
        const findStageById = (stageId) => {
          return workflowData.stages.find(s => String(s.id) === String(stageId)) || null
        }
        // 更新阶段及其相关阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(stageIdBeforeDelete, findStageById, workflowStore, workflowData)
      }
      
      if (selectedTaskIdRef.value === taskId) {
        selectedTaskIdRef.value = null
      }
      
      ElMessage.success('任务已删除')
    } catch {
      // 用户取消删除
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
   * 在指定位置创建新任务
   * @param {Object} position - 位置 { x, y }
   * @param {Object} targetStage - 目标阶段（如果任务在阶段内）
   * @param {Object} workflowData - 工作流数据
   * @param {Object} unassignedTasksRef - 未分配任务数组的ref
   * @param {Object} workflowStore - 工作流store
   * @returns {Object|null} 新创建的任务或null
   */
  const createTaskAtPosition = (position, targetStage, workflowData, unassignedTasksRef, workflowStore) => {
    if (!workflowData) {
      ElMessage.error('工作流数据未初始化')
      return null
    }
    
    const projectId = workflowData.projectId
    // 生成新的整数ID（基于已使用的ID自增）
    const newTaskId = generateNewId(workflowData, unassignedTasksRef?.value || [])
    const newTask = createTaskModel(newTaskId, '新任务', targetStage ? targetStage.id : null, projectId)
    newTask.position = {
      x: position.x,
      y: position.y
    }
    
    // 设置必要字段为null（新建任务缺少必要字段）
    newTask.startTime = null
    newTask.endTime = null
    newTask.jobNumber = null
    
    if (targetStage) {
      // 任务在阶段内，添加到阶段
      if (!targetStage.tasks) {
        targetStage.tasks = []
      }
      targetStage.tasks.push(newTask)
      // 注意：不需要调用 workflowStore.addTask，因为任务已经添加到 stage.tasks 中
      // workflowStore.tasks 主要用于独立的任务列表，而我们的任务是在 stage.tasks 中管理的
    } else {
      // 任务在阶段外，添加到未分配任务数组
      if (!unassignedTasksRef.value) {
        unassignedTasksRef.value = []
      }
      unassignedTasksRef.value.push(newTask)
    }
    
    ElMessage.success('已添加新任务')
    return newTask
  }

  /**
   * 处理任务选择
   * @param {string|number} taskId - 任务ID
   * @param {Object} selectedTaskIdRef - 选中的任务ID ref
   * @param {Object} selectedStageIdRef - 选中的阶段ID ref
   * @param {Object} selectedConnectionIdRef - 选中的连接线ID ref（可选）
   * @param {Object} workflowStore - 工作流store
   */
  const handleTaskSelect = (taskId, selectedTaskIdRef, selectedStageIdRef, workflowStore, selectedConnectionIdRef = null) => {
    selectedTaskIdRef.value = taskId
    selectedStageIdRef.value = null
    // 选中任务时，清除连接线选中状态
    if (selectedConnectionIdRef) {
      selectedConnectionIdRef.value = null
    }
    workflowStore.selectElement(taskId, 'task')
  }

  return {
    findTaskById,
    findStageById,
    findStageByPosition,
    handleTaskDelete,
    handleTaskSelect,
    createTaskAtPosition
  }
}

