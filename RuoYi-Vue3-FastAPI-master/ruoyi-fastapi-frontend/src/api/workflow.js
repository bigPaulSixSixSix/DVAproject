import request from '@/utils/request'

const API_LOG_ENABLED = false
const apiLog = (...args) => {
  if (API_LOG_ENABLED) {
    console.log(...args)
  }
}

// 根据项目ID获取工作流数据
export function fetchWorkflowByProjectId(projectId) {
  apiLog('API调用: fetchWorkflowByProjectId', { projectId })
  return request({
    url: `/task/project/${projectId}`,
    method: 'get'
  })
}

export function fetchTaskProjectList() {
  apiLog('API调用: fetchTaskProjectList')
  return request({
    url: '/task/project/list',
    method: 'get'
  })
}

// 获取工作流数据(保留原方法,可能其他地方还在使用)
export function getWorkflowData(workflowId) {
  apiLog('API调用: getWorkflowData', { workflowId })
  // TODO: 后端完成后替换为真实请求
  // return request({
  //   url: `/workflow/${workflowId}`,
  //   method: 'get'
  // })
  
  // 临时返回示例数据
  return Promise.resolve({
    code: 200,
    data: {
      id: 1,
      name: '示例工作流',
      stages: [
        {
          id: 1,
          name: '项目投资确认',
          startTime: '2024-03-01',
          endTime: '2024-03-06',
          duration: 6,
          tasks: [
            {
              id: 1,
              name: '签定投资发展协议',
              description: '与投资方签订正式的投资发展协议',
              startTime: '2024-03-01',
              duration: 2,
              endTime: '2024-03-02',
              assignee: '杨运昊',
              stageId: 1,
              predecessorTasks: [],
              successorTasks: [2],
              position: { x: 20, y: 80 }
            },
            {
              id: 2,
              name: '投资保证金缴纳',
              description: '按照协议要求缴纳投资保证金',
              startTime: '2024-03-03',
              duration: 2,
              endTime: '2024-03-04',
              assignee: '杨运昊',
              stageId: 1,
              predecessorTasks: [1],
              successorTasks: [3],
              position: { x: 20, y: 200 }
            },
            {
              id: 3,
              name: '确定挂牌时间',
              description: '确定项目挂牌的具体时间',
              startTime: '2024-03-05',
              duration: 2,
              endTime: '2024-03-06',
              assignee: '杨运昊',
              stageId: 1,
              predecessorTasks: [2],
              successorTasks: [],
              position: { x: 20, y: 320 }
            }
          ],
          predecessorStages: [],
          successorStages: [2],
          position: { x: 50, y: 50, width: 400, height: 450 }
        },
        {
          id: 2,
          name: '招拍挂手续',
          startTime: '2024-03-07',
          endTime: '2024-03-11',
          duration: 5,
          tasks: [
            {
              id: 4,
              name: '规划指标确认',
              description: '确认项目规划指标',
              startTime: '2024-03-07',
              duration: 2,
              endTime: '2024-03-08',
              assignee: '杨运昊',
              stageId: 2,
              predecessorTasks: [],
              successorTasks: [5],
              position: { x: 20, y: 80 }
            },
            {
              id: 5,
              name: '报名、报价、摘牌、成交确认书、土地出让合同',
              description: '完成土地招拍挂相关手续',
              startTime: '2024-03-09',
              duration: 3,
              endTime: '2024-03-11',
              assignee: '乐贺祥',
              stageId: 2,
              predecessorTasks: [4],
              successorTasks: [6, 7, 8, 9, 10],
              position: { x: 20, y: 200 }
            }
          ],
          predecessorStages: [1],
          successorStages: [],
          position: { x: 500, y: 50, width: 500, height: 350 }
        }
      ]
    }
  })
}

// 根据项目ID保存工作流数据
export function saveWorkflowDataByProjectId(projectId, workflowData) {
  apiLog('API调用: saveWorkflowDataByProjectId', { projectId, workflowData })
  // TODO: 后端完成后替换为真实请求
  // return request({
  //   url: `/workflow/project/${projectId}`,
  //   method: 'put',
  //   data: workflowData
  // })
  
  // 保存到pinia store
  return new Promise((resolve) => {
    import('@/views/workbench/routine/task-configuration/stores/workflowDataStore').then(({ useWorkflowDataStore }) => {
      const workflowDataStore = useWorkflowDataStore()
      workflowDataStore.setWorkflowData(projectId, {
        ...workflowData,
        projectId: projectId
      })
      
      resolve({
        code: 200,
        message: '保存成功'
      })
    })
  })
}

// 保存工作流数据(保留原方法,可能其他地方还在使用)
export function saveWorkflowData(workflowId, workflowData) {
  apiLog('API调用: saveWorkflowData', { workflowId, workflowData })
  // TODO: 后端完成后替换为真实请求
  // return request({
  //   url: `/workflow/${workflowId}`,
  //   method: 'put',
  //   data: workflowData
  // })
  
  // 临时返回成功响应
  return Promise.resolve({
    code: 200,
    message: '保存成功'
  })
}

// 保存草稿
export function saveWorkflowDraft(workflowId, workflowData) {
  apiLog('API调用: saveWorkflowDraft', { workflowId, workflowData })
  // TODO: 后端完成后替换为真实请求
  // return request({
  //   url: `/workflow/${workflowId}/draft`,
  //   method: 'post',
  //   data: workflowData
  // })
  
  return Promise.resolve({
    code: 200,
    message: '草稿保存成功'
  })
}

// 保存任务配置
// @param {Object} taskConfigData - 任务配置数据，包含 projectId, stages, tasks
// @returns {Promise} 返回后端响应数据
export function saveTaskConfig(taskConfigData) {
  apiLog('API调用: saveTaskConfig', { taskConfigData })
  return request({
    url: '/task/save',
    method: 'post',
    data: taskConfigData,
    headers: {
      skipAutoError: true  // 跳过拦截器的自动错误提示，由调用方自定义处理
    }
  })
}

// 保存任务配置并生成
// @param {Object} taskConfigData - 任务配置数据，包含 projectId, stages, tasks
// @returns {Promise} 返回后端响应数据
export function saveTaskConfigAndGenerate(taskConfigData) {
  apiLog('API调用: saveTaskConfigAndGenerate', { taskConfigData })
  return request({
    url: '/task/save-and-generate',
    method: 'post',
    data: taskConfigData,
    headers: {
      skipAutoError: true  // 跳过拦截器的自动错误提示，由调用方自定义处理
    }
  })
}
