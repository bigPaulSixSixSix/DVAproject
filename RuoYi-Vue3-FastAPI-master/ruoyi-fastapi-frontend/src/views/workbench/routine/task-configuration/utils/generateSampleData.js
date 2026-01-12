// utils/generateSampleData.js
/**
 * 生成示例工作流数据
 */

/**
 * 格式化日期为 YYYY/MM/DD
 */
function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}/${month}/${day}`
}

/**
 * 计算结束日期
 */
function calculateEndDate(startDate, duration) {
  const endDate = new Date(startDate)
  endDate.setDate(endDate.getDate() + duration - 1)
  return endDate
}

/**
 * 随机选择数组中的元素
 */
function randomChoice(array) {
  return array[Math.floor(Math.random() * array.length)]
}

/**
 * 生成示例工作流数据
 * @param {string} projectId - 项目ID
 * @param {string} projectName - 项目名称
 * @param {Array} employees - 员工列表 [{ userId, nickName, userName }]
 * @returns {Object} 工作流数据
 */
export function generateSampleWorkflowData(projectId, projectName, employees) {
  if (!employees || employees.length === 0) {
    console.warn('员工列表为空，无法生成示例数据')
    return {
      projectId,
      name: `${projectName}的工作流`,
      stages: []
    }
  }
  
  // 过滤掉超级管理员（用户名包含admin的用户）
  const validEmployees = employees.filter(emp => {
    const userName = (emp.userName || '').toLowerCase()
    return !userName.includes('admin')
  })
  
  if (validEmployees.length === 0) {
    console.warn('没有可用的员工（已过滤超级管理员），无法生成示例数据')
    return {
      projectId,
      name: `${projectName}的工作流`,
      stages: []
    }
  }
  
  // 获取员工ID列表（排除超级管理员）
  // 不再需要 employeeIds，直接使用 employees 数组
  
  // 生成阶段数量（3-5个）
  const stageCount = 3 + Math.floor(Math.random() * 3) // 3-5
  
  // 基础日期（从今天开始）
  const baseDate = new Date()
  baseDate.setHours(0, 0, 0, 0)
  
  const stages = []
  let currentDate = new Date(baseDate)
  
  // 使用项目ID作为前缀，确保任务ID全局唯一
  // 例如：项目ID为"1"，任务ID从1001开始；项目ID为"2"，任务ID从2001开始
  const projectIdNum = parseInt(projectId) || 1
  const stageIdBase = projectIdNum * 1000
  const taskIdBase = projectIdNum * 10000
  
  let stageId = stageIdBase + 1
  let taskId = taskIdBase + 1
  
  // 阶段名称模板
  const stageTemplates = [
    '项目立项',
    '规划设计',
    '招投标',
    '施工准备',
    '施工阶段',
    '验收交付'
  ]
  
  for (let i = 0; i < stageCount; i++) {
    const stageName = stageTemplates[i] || `阶段${i + 1}`
    
    // 生成任务数量（2-6个）
    const taskCount = 2 + Math.floor(Math.random() * 5) // 2-6
    
    // 阶段开始时间
    const stageStartDate = new Date(currentDate)
    
    // 生成任务
    const tasks = []
    let taskStartDate = new Date(stageStartDate)
    
    // 任务名称模板
    const taskTemplates = [
      '需求调研',
      '方案设计',
      '技术评审',
      '预算编制',
      '合同签订',
      '材料采购',
      '现场施工',
      '质量检查',
      '进度汇报',
      '验收测试',
      '文档整理',
      '培训交付'
    ]
    
    for (let j = 0; j < taskCount; j++) {
      const taskName = taskTemplates[j] || `任务${j + 1}`
      
      // 任务持续时间（1-5天）
      const taskDuration = 1 + Math.floor(Math.random() * 5)
      
      // 任务结束时间
      const taskEndDate = calculateEndDate(taskStartDate, taskDuration)
      
      // 随机选择负责人（获取工号）
      const selectedEmployee = randomChoice(employees)
      const jobNumber = selectedEmployee ? selectedEmployee.jobNumber : null
      
      // 当前任务ID
      const currentTaskId = taskId
      taskId++ // 递增任务ID
      
      // 前置任务ID（前一个任务的ID）
      const predecessorTaskId = j > 0 ? tasks[j - 1].id : null
      
      // 创建任务
      const task = {
        id: currentTaskId,
        name: `${taskName}`,
        description: `${projectName} - ${stageName} - ${taskName}`,
        startTime: formatDate(taskStartDate),
        duration: taskDuration,
        endTime: formatDate(taskEndDate),
        jobNumber: jobNumber,
        stageId: stageId,
        predecessorTasks: predecessorTaskId ? [predecessorTaskId] : [],
        successorTasks: [], // 后置任务将在下一个任务创建时设置
        position: {
          x: 20,
          y: 80 + j * 120
        },
        projectId: projectId,
        approvalType: 'sequential', // 默认逐级审批
        approvalNodes: [] // 默认空数组
      }
      
      // 如果前一个任务存在，将当前任务添加到前一个任务的后置任务列表
      if (predecessorTaskId) {
        const prevTask = tasks[j - 1]
        prevTask.successorTasks.push(currentTaskId)
      }
      
      tasks.push(task)
      
      // 下一个任务开始时间（当前任务结束后1天）
      taskStartDate = new Date(taskEndDate)
      taskStartDate.setDate(taskStartDate.getDate() + 1)
    }
    
    // 阶段结束时间（最后一个任务的结束时间）
    const stageEndDate = tasks.length > 0 
      ? new Date(tasks[tasks.length - 1].endTime)
      : new Date(stageStartDate)
    
    // 阶段持续时间
    const stageDuration = Math.ceil(
      (stageEndDate - stageStartDate) / (1000 * 60 * 60 * 24)
    ) + 1
    
    // 创建阶段
    const stage = {
      id: stageId++,
      name: stageName,
      startTime: formatDate(stageStartDate),
      endTime: formatDate(stageEndDate),
      duration: stageDuration,
      tasks: tasks,
      predecessorStages: i > 0 ? [stageId - 2] : [],
      successorStages: i < stageCount - 1 ? [stageId] : [],
      position: {
        x: 50 + i * 450,
        y: 50,
        width: 400,
        height: Math.max(250, tasks.length * 120 + 100)
      },
      projectId: projectId
    }
    
    stages.push(stage)
    
    // 下一个阶段开始时间（当前阶段结束后1天）
    currentDate = new Date(stageEndDate)
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  return {
    projectId,
    name: `${projectName}的工作流`,
    stages
  }
}

/**
 * 初始化示例数据
 * @param {Array} projectDicts - 项目字典列表 [{ dictValue, dictLabel }]
 * @param {Array} employees - 员工列表
 */
export async function initSampleData(projectDicts, employees) {
  const { useWorkflowDataStore } = await import('../stores/workflowDataStore')
  const workflowDataStore = useWorkflowDataStore()
  
  // 需要生成数据的项目名称
  const targetProjects = ['丹北', '周铁']
  
  for (const projectDict of projectDicts) {
    const projectName = projectDict.dictLabel
    const projectId = projectDict.dictValue
    
    // 只为指定的项目生成数据
    if (targetProjects.includes(projectName)) {
      // 检查是否已有数据
      if (!workflowDataStore.hasWorkflowData(projectId)) {
        const workflowData = generateSampleWorkflowData(projectId, projectName, employees)
        workflowDataStore.setWorkflowData(projectId, workflowData)
        console.log(`已为项目"${projectName}"生成示例数据`, workflowData)
      }
    }
  }
}

