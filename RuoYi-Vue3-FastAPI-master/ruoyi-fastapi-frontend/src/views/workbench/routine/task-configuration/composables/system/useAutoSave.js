// composables/useAutoSave.js
import { ref } from 'vue'
import { saveWorkflowDraft } from '@/api/workflow'

export const useAutoSave = () => {
  const saveInterval = ref(null)
  const lastSaveTime = ref(null)
  
  const startAutoSave = (workflowData) => {
    saveInterval.value = setInterval(async () => {
      if (workflowData.value) {
        try {
          await saveWorkflowDraft(workflowData.value.id, workflowData.value)
          lastSaveTime.value = new Date()
        } catch (error) {
          // 自动保存失败，静默处理
        }
      }
    }, 5 * 60 * 1000) // 5分钟
  }
  
  const stopAutoSave = () => {
    if (saveInterval.value) {
      clearInterval(saveInterval.value)
      saveInterval.value = null
    }
  }
  
  const onBeforeUnload = (workflowData) => {
    // 页面关闭前保存
    if (workflowData.value) {
      saveWorkflowDraft(workflowData.value.id, workflowData.value)
    }
  }
  
  return {
    startAutoSave,
    stopAutoSave,
    onBeforeUnload,
    lastSaveTime
  }
}
