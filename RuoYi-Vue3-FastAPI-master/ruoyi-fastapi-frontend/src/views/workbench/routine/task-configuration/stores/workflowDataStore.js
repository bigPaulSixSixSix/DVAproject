// stores/workflowDataStore.js
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// localStorage 键名
const STORAGE_KEY = 'workflowDataStore'

/**
 * 工作流数据Store
 * 存储每个项目的工作流数据: { projectId: { projectId, name, stages: [...] } }
 * 使用 localStorage 持久化存储
 */
export const useWorkflowDataStore = defineStore('workflowData', () => {
  // 从 localStorage 加载数据
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch (error) {
      console.error('从 localStorage 加载工作流数据失败:', error)
    }
    return {}
  }

  // 保存到 localStorage
  const saveToStorage = (data) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('保存工作流数据到 localStorage 失败:', error)
      // 如果存储空间不足，尝试清理旧数据
      if (error.name === 'QuotaExceededError') {
        console.warn('localStorage 存储空间不足，尝试清理旧数据')
        // 可以在这里添加清理逻辑
      }
    }
  }

  // 初始化：从 localStorage 加载数据
  const workflowDataMap = ref(loadFromStorage())
  
  // 监听数据变化，自动保存到 localStorage
  watch(
    workflowDataMap,
    (newValue) => {
      saveToStorage(newValue)
    },
    { deep: true }
  )
  
  /**
   * 获取项目的工作流数据
   * @param {string|number} projectId - 项目ID
   * @returns {Object|null} 工作流数据
   */
  const getWorkflowData = (projectId) => {
    return workflowDataMap.value[projectId] || null
  }
  
  /**
   * 设置项目的工作流数据
   * @param {string|number} projectId - 项目ID
   * @param {Object} workflowData - 工作流数据
   */
  const setWorkflowData = (projectId, workflowData) => {
    workflowDataMap.value[projectId] = {
      ...workflowData,
      projectId: projectId
    }
    // 手动触发保存（watch 会自动保存，但为了确保立即保存，这里也调用一次）
    saveToStorage(workflowDataMap.value)
  }
  
  /**
   * 检查项目是否有工作流数据
   * @param {string|number} projectId - 项目ID
   * @returns {boolean}
   */
  const hasWorkflowData = (projectId) => {
    return !!workflowDataMap.value[projectId]
  }
  
  /**
   * 删除项目的工作流数据
   * @param {string|number} projectId - 项目ID
   */
  const deleteWorkflowData = (projectId) => {
    delete workflowDataMap.value[projectId]
    // 手动触发保存
    saveToStorage(workflowDataMap.value)
  }
  
  /**
   * 获取所有项目的工作流数据
   * @returns {Object} 所有项目的工作流数据
   */
  const getAllWorkflowData = () => {
    return workflowDataMap.value
  }

  /**
   * 清空所有数据（用于调试或重置）
   */
  const clearAllData = () => {
    workflowDataMap.value = {}
    localStorage.removeItem(STORAGE_KEY)
  }
  
  return {
    workflowDataMap,
    getWorkflowData,
    setWorkflowData,
    hasWorkflowData,
    deleteWorkflowData,
    getAllWorkflowData,
    clearAllData
  }
})

