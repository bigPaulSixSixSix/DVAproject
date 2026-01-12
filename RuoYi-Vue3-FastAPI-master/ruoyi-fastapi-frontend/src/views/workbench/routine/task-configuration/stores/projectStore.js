// stores/projectStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 项目统计信息Store
 * 存储每个项目的统计信息: 阶段数量、任务数量、创建时间、修改时间
 */
export const useProjectStore = defineStore('project', () => {
  // 项目统计信息: { projectId: { stageCount, taskCount, createTime, updateTime } }
  const projectStats = ref({})
  
  /**
   * 获取项目的统计信息
   * @param {string|number} projectId - 项目ID
   * @returns {Object} 统计信息
   */
  const getProjectStats = (projectId) => {
    if (!projectStats.value[projectId]) {
      projectStats.value[projectId] = {
        stageCount: 0,
        taskCount: 0,
        createTime: null,
        updateTime: null
      }
    }
    return projectStats.value[projectId]
  }
  
  /**
   * 获取所有项目的统计信息
   * @returns {Object} 所有项目的统计信息
   */
  const getAllProjectStats = () => {
    return projectStats.value
  }
  
  /**
   * 更新项目的统计信息
   * @param {string|number} projectId - 项目ID
   * @param {Object} stats - 统计信息
   */
  const updateProjectStats = (projectId, stats) => {
    const currentStats = getProjectStats(projectId)
    projectStats.value[projectId] = {
      ...currentStats,
      ...stats,
      updateTime: new Date().toISOString()
    }
  }
  
  /**
   * 更新项目的阶段数量
   * @param {string|number} projectId - 项目ID
   * @param {number} stageCount - 阶段数量
   */
  const updateStageCount = (projectId, stageCount) => {
    const stats = getProjectStats(projectId)
    stats.stageCount = stageCount
    stats.updateTime = new Date().toISOString()
  }
  
  /**
   * 更新项目的任务数量
   * @param {string|number} projectId - 项目ID
   * @param {number} taskCount - 任务数量
   */
  const updateTaskCount = (projectId, taskCount) => {
    const stats = getProjectStats(projectId)
    stats.taskCount = taskCount
    stats.updateTime = new Date().toISOString()
  }
  
  /**
   * 初始化项目统计信息(从工作流数据计算)
   * @param {string|number} projectId - 项目ID
   * @param {Object} workflowData - 工作流数据
   *   可能的数据格式：
   *   1. 前端格式：{ stages: [...], allTasks: [...] } 或 { stages: [...] }
   *   2. 后端格式：{ stages: [...], tasks: [...] }（tasks 包含所有任务，阶段内和阶段外）
   */
  const initProjectStats = (projectId, workflowData) => {
    const stages = workflowData?.stages || []
    
    // 计算任务数量
    let allTasks = []
    
    // 优先使用 allTasks（前端格式，已包含阶段外的任务）
    if (workflowData?.allTasks && Array.isArray(workflowData.allTasks)) {
      allTasks = workflowData.allTasks
    }
    // 其次使用 tasks（后端格式，包含所有任务）
    else if (workflowData?.tasks && Array.isArray(workflowData.tasks)) {
      allTasks = workflowData.tasks
    }
    // 最后回退到只计算阶段内的任务
    else {
      allTasks = stages.flatMap(stage => stage.tasks || [])
    }
    
    const stats = {
      stageCount: stages.length,
      taskCount: allTasks.length,
      updateTime: new Date().toISOString()
    }
    
    // 如果是第一次初始化,设置创建时间
    const currentStats = projectStats.value[projectId]
    if (!currentStats || !currentStats.createTime) {
      stats.createTime = new Date().toISOString()
    } else {
      stats.createTime = currentStats.createTime
    }
    
    projectStats.value[projectId] = stats
  }
  
  /**
   * 重置项目统计信息
   * @param {string|number} projectId - 项目ID
   */
  const resetProjectStats = (projectId) => {
    projectStats.value[projectId] = {
      stageCount: 0,
      taskCount: 0,
      createTime: null,
      updateTime: null
    }
  }
  
  return {
    projectStats,
    getProjectStats,
    getAllProjectStats,
    updateProjectStats,
    updateStageCount,
    updateTaskCount,
    initProjectStats,
    resetProjectStats
  }
})

