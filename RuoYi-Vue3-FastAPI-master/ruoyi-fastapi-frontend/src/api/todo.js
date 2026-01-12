import request from '@/utils/request'

/**
 * 我的任务相关API
 */

// 获取我的任务分类统计
export function getMyTaskCategories() {
  return request({
    url: '/todo/my/tasks/categories',
    method: 'get'
  })
}

// 获取我的任务列表
export function getMyTaskList(params) {
  return request({
    url: '/todo/my/tasks/list',
    method: 'get',
    params: params
  })
}

// 获取任务详情
export function getTaskDetail(taskId) {
  return request({
    url: `/todo/task/${taskId}/detail`,
    method: 'get'
  })
}

// 获取其他任务详情（用于弹窗）
export function getTaskDetailSimple(taskId) {
  return request({
    url: `/todo/task/${taskId}/detail/simple`,
    method: 'get'
  })
}

// 提交任务
export function submitTask(taskId, data) {
  return request({
    url: `/todo/submit/${taskId}`,
    method: 'post',
    data: data
  })
}

// 重新提交任务
export function resubmitTask(taskId, data) {
  return request({
    url: `/todo/resubmit/${taskId}`,
    method: 'post',
    data: data
  })
}

// 审批同意
export function approveTask(applyId, data) {
  return request({
    url: `/todo/approve/${applyId}`,
    method: 'post',
    data: data
  })
}

// 审批驳回
export function rejectTask(applyId, data) {
  return request({
    url: `/todo/reject/${applyId}`,
    method: 'post',
    data: data
  })
}

// 生成任务（从项目配置生成任务执行记录）
export function generateTasks(projectId) {
  return request({
    url: `/todo/generate/${projectId}`,
    method: 'post'
  })
}

// 获取工作台任务统计
export function getWorkbenchTaskStats() {
  return request({
    url: '/todo/workbench/stats',
    method: 'get'
  })
}

/**
 * 历史任务相关API
 */

// 获取历史任务分类统计
export function getHistoryTaskCategories() {
  return request({
    url: '/todo/history/tasks/categories',
    method: 'get'
  })
}

// 获取历史任务列表
export function getHistoryTaskList(params) {
  return request({
    url: '/todo/history/tasks/list',
    method: 'get',
    params: params
  })
}
