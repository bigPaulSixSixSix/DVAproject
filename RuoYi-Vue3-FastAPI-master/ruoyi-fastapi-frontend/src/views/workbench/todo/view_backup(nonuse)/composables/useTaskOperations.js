import { ElMessage, ElMessageBox } from 'element-plus'
import { submitTask, resubmitTask, approveTask, rejectTask } from '@/api/todo'

/**
 * 任务操作相关逻辑
 */
export function useTaskOperations() {
  // 提交任务
  const handleSubmit = async (taskId, submitText) => {
    try {
      const data = {
        submitText: submitText || '',
        submitImages: []
      }
      const res = await submitTask(taskId, data)
      if (res.code === 200) {
        ElMessage.success('提交成功')
        return true
      }
    } catch (error) {
      console.error('提交任务失败:', error)
      return false
    }
  }

  // 重新提交任务
  const handleResubmit = async (taskId, submitText) => {
    try {
      const data = {
        submitText: submitText || '',
        submitImages: []
      }
      const res = await resubmitTask(taskId, data)
      if (res.code === 200) {
        ElMessage.success('重新提交成功')
        return true
      }
    } catch (error) {
      console.error('重新提交任务失败:', error)
      return false
    }
  }

  // 审批同意
  const handleApprove = async (applyId, approvalComment) => {
    try {
      const data = {
        approvalComment: approvalComment || '同意'
      }
      const res = await approveTask(applyId, data)
      if (res.code === 200) {
        ElMessage.success('审批成功')
        return true
      }
    } catch (error) {
      console.error('审批失败:', error)
      return false
    }
  }

  // 审批驳回
  const handleReject = async (applyId, rejectReason) => {
    if (!rejectReason || !rejectReason.trim()) {
      ElMessage.warning('驳回时必须填写审批意见')
      return false
    }
    try {
      const data = {
        approvalComment: rejectReason
      }
      const res = await rejectTask(applyId, data)
      if (res.code === 200) {
        ElMessage.success('已驳回')
        return true
      }
    } catch (error) {
      console.error('驳回失败:', error)
      return false
    }
  }

  // 确认提交（不显示确认框，直接提交，因为已经在调用前通过ElMessageBox.prompt获取了内容）
  const confirmSubmit = async (taskId, submitText, taskStatus) => {
    if (taskStatus === 4) {
      // 驳回状态，使用重新提交
      return await handleResubmit(taskId, submitText)
    } else {
      // 进行中状态，使用提交
      return await handleSubmit(taskId, submitText)
    }
  }

  // 确认审批（不显示确认框，直接审批，因为已经在调用前通过ElMessageBox.prompt获取了内容）
  const confirmApprove = async (applyId, approvalComment) => {
    return await handleApprove(applyId, approvalComment)
  }

  // 确认驳回
  const confirmReject = async (applyId) => {
    try {
      const { value: rejectReason } = await ElMessageBox.prompt(
        '请输入驳回原因',
        '驳回任务',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputType: 'textarea',
          inputPlaceholder: '请填写驳回原因',
          inputValidator: (value) => {
            if (!value || !value.trim()) {
              return '驳回原因不能为空'
            }
            return true
          }
        }
      )
      return await handleReject(applyId, rejectReason)
    } catch {
      return false
    }
  }

  return {
    handleSubmit,
    handleResubmit,
    handleApprove,
    handleReject,
    confirmSubmit,
    confirmApprove,
    confirmReject
  }
}
