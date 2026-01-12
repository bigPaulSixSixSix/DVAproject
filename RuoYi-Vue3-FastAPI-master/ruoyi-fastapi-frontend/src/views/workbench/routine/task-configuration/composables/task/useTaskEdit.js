// composables/useTaskEdit.js
// 任务编辑相关逻辑

import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { listUser, deptTreeSelect } from '@/api/system/user'
import { updateTaskAndRelatedTasksTimeIssueFlags } from './useTaskTimeValidation'
import { updateStageAndRelatedStagesTimeIssueFlags } from '../stage/useStageTimeValidation'
import { useStageTime } from '../stage/useStageTime'

export const useTaskEdit = () => {
  // 任务编辑弹窗状态
  const taskEditDialogVisible = ref(false)
  const taskEditFormRef = ref(null)
  const currentEditingTask = ref(null)
  const taskEditForm = ref({
    name: '',
    description: '',
    startTime: null,
    endTime: null,
    duration: 1,
    jobNumber: null, // 负责人工号
    approvalType: 'sequential', // 审批类型：'sequential'（逐级审批）或 'specified'（指定编制审批）
    approvalLevel: undefined // 审批层级：单选，存储选中的编制ID（使用 undefined 而不是 null，因为 ElTreeSelect 不接受 null）
  })

  // 员工列表
  const employeeList = ref([])
  const employeeOptions = ref([])
  
  // 编制树和审批人选项
  const deptTree = ref([]) // 完整的编制树
  const approvalLevelTree = ref([]) // 审批层级树（只显示负责人向上的编制）

  const MAX_TAB_COUNT = 10
  const taskEditTabs = ref([])
  const activeTaskTabId = ref(null)
  const isProgrammaticFormSync = ref(false)

  // 任务编辑表单验证规则
  const taskEditRules = {
    name: [
      { required: true, message: '请输入任务名称', trigger: 'blur' },
      { min: 1, max: 100, message: '任务名称长度在 1 到 100 个字符', trigger: 'blur' }
    ],
    startTime: [
      { required: true, message: '请选择开始时间', trigger: ['blur', 'change'] }
    ],
    endTime: [
      { required: true, message: '请选择结束时间', trigger: ['blur', 'change'] }
    ],
    duration: [
      { required: true, message: '请输入持续时间', trigger: 'blur' },
      { type: 'number', min: 1, message: '持续时间必须大于0', trigger: 'blur' }
    ],
    jobNumber: [
      { required: true, message: '请选择负责人', trigger: 'change' }
    ],
    approvalLevel: [
      { required: true, message: '请选择审批层级', trigger: 'change' }
    ]
  }

  /**
   * 加载员工列表
   */
  const loadEmployeeList = async () => {
    try {
      const response = await listUser({ pageNum: 1, pageSize: 1000 }) // 获取所有员工
      if (response && response.rows) {
        employeeList.value = response.rows
        employeeOptions.value = response.rows.map(user => ({
          value: user.jobNumber, // 使用 jobNumber（工号）作为值
          label: `${user.employeeName || user.jobNumber}[${user.jobNumber}]` // 显示：员工姓名[工号]，例如：许亮[000008]
        }))
      }
    } catch (error) {
      console.error('加载员工列表失败:', error)
      ElMessage.error('加载员工列表失败')
    }
  }

  /**
   * 加载编制树结构
   */
  const loadDeptTree = async () => {
    try {
      const deptTreeResponse = await deptTreeSelect()
      deptTree.value = deptTreeResponse?.data || []
    } catch (error) {
      console.error('加载编制树失败:', error)
      ElMessage.error('加载编制树失败')
      deptTree.value = []
    }
  }

  /**
   * 根据负责人构建审批层级树（只显示负责人向上的编制）
   * @param {string} jobNumber - 负责人工号
   * @returns {Array} 审批层级树
   */
  const buildApprovalLevelTree = (jobNumber) => {
    if (!jobNumber || !deptTree.value || deptTree.value.length === 0) {
      return []
    }

    // 找到负责人的编制
    const assignee = employeeList.value.find(u => 
      u.jobNumber === jobNumber || String(u.jobNumber) === String(jobNumber)
    )
    
    if (!assignee) {
      return []
    }

    const assigneeDeptId = assignee.dept?.deptId || assignee.deptId || assignee.dept?.id
    if (!assigneeDeptId) {
      return []
    }

    // 在编制树中找到负责人所在的编制节点及其所有父级节点
    // 返回从根节点到目标节点的路径
    const findNodePath = (nodes, targetId, path = []) => {
      for (const node of nodes) {
        const currentPath = [...path, node]
        if (String(node.id) === String(targetId)) {
          return currentPath
        }
        if (node.children && node.children.length > 0) {
          const found = findNodePath(node.children, targetId, currentPath)
          if (found) return found
        }
      }
      return null
    }

    const path = findNodePath(deptTree.value, assigneeDeptId)
    if (!path || path.length === 0) {
      return []
    }

    // 排除负责人所在的编制（最后一个节点），只保留父级编制
    // path 是从根到负责人编制的路径，所以需要排除最后一个
    const parentPath = path.slice(0, -1)
    if (parentPath.length === 0) {
      // 负责人编制就是根节点，没有父级编制
      return []
    }

    // 构建树形结构，只包含父级编制
    // 递归函数：从原始树中提取指定路径上的节点，构建新的树
    const buildTreeFromPath = (sourceNodes, targetPath, currentLevel = 0) => {
      if (currentLevel >= targetPath.length) {
        return []
      }

      const targetNode = targetPath[currentLevel]
      const result = []

      // 在当前层级查找目标节点
      for (const sourceNode of sourceNodes) {
        if (String(sourceNode.id) === String(targetNode.id)) {
          // 找到目标节点，构建标签
          // 格式：编制名级别名 员工名[工号]
          // 找到该编制下的员工（同一编制下只有一个员工）
          const deptUsers = employeeList.value.filter(user => {
            const userDeptId = user.dept?.deptId || user.deptId || user.dept?.id
            return userDeptId && String(userDeptId) === String(sourceNode.id)
          })

          let label = sourceNode.label // 默认使用编制名
          if (deptUsers.length > 0) {
            const user = deptUsers[0] // 同一编制下只有一个员工
            const rankName = user.rankName || '' // 级别名
            const employeeName = user.employeeName || user.jobNumber || '' // 员工名
            const jobNumber = user.jobNumber || '' // 工号
            
            // 格式：编制名级别名 员工名[工号]
            // 如果级别名为空，则不显示级别名
            if (rankName) {
              label = `${sourceNode.label}${rankName} ${employeeName}[${jobNumber}]`
            } else {
              label = `${sourceNode.label} ${employeeName}[${jobNumber}]`
            }
          } else {
            // 编制下没有员工，显示：编制名-空岗
            label = `${sourceNode.label}-空岗`
          }

          const treeNode = {
            id: sourceNode.id,
            label: label,
            children: []
          }

          // 如果还有下一级，递归构建子节点
          if (currentLevel + 1 < targetPath.length && sourceNode.children) {
            treeNode.children = buildTreeFromPath(sourceNode.children, targetPath, currentLevel + 1)
          }

          result.push(treeNode)
          break
        }
      }

      return result
    }

    // 从根节点开始构建树
    const tree = buildTreeFromPath(deptTree.value, parentPath, 0)
    return tree
  }

  /**
   * 更新审批层级树（当负责人改变时调用）
   */
  const updateApprovalLevelTree = () => {
    if (!taskEditForm.value.jobNumber) {
      approvalLevelTree.value = []
      taskEditForm.value.approvalLevel = undefined
      return
    }
    
    // 确保编制树已加载
    if (!deptTree.value || deptTree.value.length === 0) {
      approvalLevelTree.value = []
      taskEditForm.value.approvalLevel = undefined
      return
    }
    
    // 确保员工列表已加载
    if (!employeeList.value || employeeList.value.length === 0) {
      approvalLevelTree.value = []
      taskEditForm.value.approvalLevel = undefined
      return
    }
    
    approvalLevelTree.value = buildApprovalLevelTree(taskEditForm.value.jobNumber)
    // 如果审批层级树为空，清空已选择的审批层级
    if (approvalLevelTree.value.length === 0) {
      taskEditForm.value.approvalLevel = undefined
    }
  }

  /**
   * 在编制树中查找从根节点到指定节点的路径
   * @param {Array} nodes - 编制树节点数组
   * @param {number|string} targetId - 目标编制ID
   * @param {Array} path - 当前路径
   * @returns {Array|null} 从根节点到目标节点的路径（包含目标节点）
   */
  const findPathFromRoot = (nodes, targetId, path = []) => {
    for (const node of nodes) {
      const currentPath = [...path, node]
      if (String(node.id) === String(targetId)) {
        return currentPath
      }
      if (node.children && node.children.length > 0) {
        const found = findPathFromRoot(node.children, targetId, currentPath)
        if (found) return found
      }
    }
    return null
  }

  /**
   * 根据选中的审批层级和审批类型，计算最终的审批节点数组
   * @param {number|string} approvalLevel - 选中的审批层级（编制ID）
   * @param {string} approvalType - 审批类型
   * @returns {Array} 审批节点数组
   */
  const calculateApprovalNodes = (approvalLevel, approvalType) => {
    if (!approvalLevel) {
      return []
    }

    if (approvalType === 'specified') {
      // 指定编制审批：只返回选中的编制ID
      return [Number(approvalLevel)]
    } else if (approvalType === 'sequential') {
      // 逐级审批：从负责人编制开始，一直向上找父级编制，直到选中的编制
      const jobNumber = taskEditForm.value.jobNumber
      if (!jobNumber) {
        return []
      }

      const assignee = employeeList.value.find(u => 
        u.jobNumber === jobNumber || String(u.jobNumber) === String(jobNumber)
      )
      
      if (!assignee) {
        return []
      }

      const assigneeDeptId = assignee.dept?.deptId || assignee.deptId || assignee.dept?.id
      if (!assigneeDeptId) {
        return []
      }

      // 如果负责人编制和选中编制相同，只返回选中编制
      if (String(assigneeDeptId) === String(approvalLevel)) {
        return [Number(approvalLevel)]
      }

      // 找到从根节点到负责人编制的路径
      const assigneePath = findPathFromRoot(deptTree.value, assigneeDeptId)
      // 找到从根节点到选中编制的路径
      const targetPath = findPathFromRoot(deptTree.value, approvalLevel)

      if (!assigneePath || !targetPath) {
        return [Number(approvalLevel)]
      }

      // 路径是从根到目标节点的顺序：[根, ..., 目标]
      // 需要找到负责人编制在选中编制路径中的位置
      const assigneeIndex = targetPath.findIndex(node => String(node.id) === String(assigneeDeptId))
      
      if (assigneeIndex === -1) {
        // 负责人编制不在选中编制的路径中
        // 这说明选中编制不在负责人编制的父级路径上
        // 但是根据业务逻辑，审批层级树只显示负责人向上的编制，所以选中编制应该在负责人编制的父级路径上
        // 如果找不到，可能是路径查找有问题，尝试反向查找：在负责人路径中查找选中编制
        const targetIndex = assigneePath.findIndex(node => String(node.id) === String(approvalLevel))
        if (targetIndex === -1) {
          // 选中编制也不在负责人编制的路径中，说明它们不在同一条路径上
          return [Number(approvalLevel)]
        }
        
        // 选中编制在负责人编制的路径中，说明选中编制是负责人编制的祖先
        // assigneePath是从根到负责人编制的路径：[根, ..., 选中编制, ..., 负责人编制]
        // targetIndex是选中编制在路径中的位置
        // 需要从负责人编制的上一级开始（不包括负责人编制），向上到选中编制
        // 负责人编制是路径的最后一个元素（index = assigneePath.length - 1）
        // 需要从 assigneePath.length - 2 开始，向上到 targetIndex
        const approvalNodes = []
        for (let i = assigneePath.length - 2; i >= targetIndex; i--) {
          approvalNodes.push(Number(assigneePath[i].id))
        }
        return approvalNodes
      }

      // 负责人编制在选中编制的路径中，说明选中编制是负责人编制的祖先
      // targetPath是从根到选中编制的路径：[根, ..., 负责人编制, ..., 选中编制]
      // assigneeIndex是负责人编制在路径中的位置
      // 需要从负责人编制的下一级开始（不包括负责人编制），到选中编制
      // 这些编制ID需要按照从负责人向上到选中编制的顺序存储
      const approvalNodes = []
      for (let i = assigneeIndex + 1; i < targetPath.length; i++) {
        approvalNodes.push(Number(targetPath[i].id))
        if (String(targetPath[i].id) === String(approvalLevel)) {
          break
        }
      }

      // 如果循环结束后还没有找到选中编制，说明选中编制不在负责人编制的路径上
      // 这种情况下，只返回选中编制
      if (approvalNodes.length === 0 || String(approvalNodes[approvalNodes.length - 1]) !== String(approvalLevel)) {
        return [Number(approvalLevel)]
      }

      return approvalNodes
    }

    return []
  }

  /**
   * 根据 jobNumber 获取用户显示名称（用于下拉框，显示：用户昵称[工号]）
   * @param {string} jobNumber - 工号
   * @returns {string} 显示名称，格式：用户昵称[工号]
   */
  const getUserDisplayName = (jobNumber) => {
    if (!jobNumber) return ''
    const user = employeeList.value.find(u => u.jobNumber === jobNumber || String(u.jobNumber) === String(jobNumber))
    if (user) {
      return `${user.employeeName || user.jobNumber}[${user.jobNumber}]`
    }
    return String(jobNumber) // 如果找不到用户，返回工号字符串
  }

  /**
   * 根据 jobNumber 获取用户昵称（用于任务面板显示，只显示人名）
   * @param {string} jobNumber - 工号
   * @returns {string} 用户昵称
   */
  const getUserNickName = (jobNumber) => {
    if (!jobNumber) return ''
    const user = employeeList.value.find(u => u.jobNumber === jobNumber || String(u.jobNumber) === String(jobNumber))
    if (user) {
      return user.employeeName || user.jobNumber || String(jobNumber)
    }
    return String(jobNumber) // 如果找不到用户，返回工号字符串
  }

  /**
   * 格式化日期为 YYYY/MM/DD 格式
   * @param {Date|string} date - 日期对象或日期字符串
   * @returns {string|null} 格式化后的日期字符串
   */
  const formatDateFull = (date) => {
    if (!date) return null
    if (typeof date === 'string') {
      if (/^\d{4}\/\d{2}\/\d{2}$/.test(date)) {
        return date
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        return date.replace(/-/g, '/')
      }
    }
    const d = new Date(date)
    if (Number.isNaN(d.getTime())) {
      return null
    }
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}/${month}/${day}`
  }

  /**
   * 解析日期字符串为 Date 对象
   * @param {string} dateStr - 日期字符串 (YYYY/MM/DD)
   * @returns {Date|null} Date 对象或 null
   */
  const parseDate = (dateStr) => {
    if (!dateStr) return null
    const parts = dateStr.split('/')
    if (parts.length !== 3) return null
    const year = parseInt(parts[0], 10)
    const month = parseInt(parts[1], 10) - 1
    const day = parseInt(parts[2], 10)
    return new Date(year, month, day)
  }

  /**
   * 根据开始时间和持续时间计算结束时间
   * @param {Date} startTime - 开始时间
   * @param {number} duration - 持续时间（天数）
   * @returns {Date} 结束时间
   */
  const calculateEndTime = (startTime, duration) => {
    if (!startTime || !duration) return null
    const endTime = new Date(startTime)
    endTime.setDate(endTime.getDate() + duration - 1) // 包含首尾，所以减1
    return endTime
  }

  /**
   * 根据结束时间和持续时间计算开始时间
   * @param {Date} endTime - 结束时间
   * @param {number} duration - 持续时间（天数）
   * @returns {Date} 开始时间
   */
  const calculateStartTime = (endTime, duration) => {
    if (!endTime || !duration) return null
    const startTime = new Date(endTime)
    startTime.setDate(startTime.getDate() - duration + 1) // 包含首尾，所以加1
    return startTime
  }

  /**
   * 根据开始时间和结束时间计算持续时间
   * @param {Date} startTime - 开始时间
   * @param {Date} endTime - 结束时间
   * @returns {number} 持续时间（天数）
   */
  const calculateDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return null
    const diffTime = endTime - startTime
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1 // 包含首尾
    return diffDays > 0 ? diffDays : 1
  }

  /**
   * 处理时间字段的自动计算逻辑
   * 规则：
   * (1) 如果有开始时间但没有结束时间，则填写或修改持续时间后，结束时间自动计算
   * (2) 如果没有开始时间但有结束时间，则填写或修改持续时间后，开始时间自动计算
   * (3) 如果既有开始时间也有结束时间，则按规则(1)进行（以开始时间为基准）
   * (4) 如果开始时间和结束时间都没有，则只填入持续时间。但当后续又填写了开始时间或结束时间中的一项，则另一项自动计算
   * (5) 如果开始时间、结束时间、持续时间都有，但是修改了开始或结束时间，则另一个端点的时间不变，更改持续时间
   * @param {string} changedField - 改变的字段名 ('startTime' | 'endTime' | 'duration')
   */
  const handleTimeFieldChange = (changedField) => {
    const form = taskEditForm.value
    const startTime = form.startTime ? parseDate(form.startTime) : null
    const endTime = form.endTime ? parseDate(form.endTime) : null
    const duration = form.duration || null

    // 规则(1): 如果有开始时间但没有结束时间，则填写或修改持续时间后，结束时间自动计算
    if (startTime && !endTime && duration) {
      if (changedField === 'duration' || changedField === 'startTime') {
        const calculatedEndTime = calculateEndTime(startTime, duration)
        if (calculatedEndTime) {
          form.endTime = formatDateFull(calculatedEndTime)
        }
      }
    }
    // 规则(2): 如果没有开始时间但有结束时间，则填写或修改持续时间后，开始时间自动计算
    else if (!startTime && endTime && duration) {
      if (changedField === 'duration' || changedField === 'endTime') {
        const calculatedStartTime = calculateStartTime(endTime, duration)
        if (calculatedStartTime) {
          form.startTime = formatDateFull(calculatedStartTime)
        }
      }
    }
    // 规则(3)和(5): 如果既有开始时间也有结束时间
    else if (startTime && endTime) {
      if (duration) {
        // 规则(5): 如果开始时间、结束时间、持续时间都有，但是修改了开始或结束时间，则另一个端点的时间不变，更改持续时间
        if (changedField === 'startTime') {
          // 修改开始时间，结束时间不变，重新计算持续时间
          // 如果开始时间晚于结束时间，允许保存但持续时间设为1（会被标记为时间异常）
          const calculatedDuration = calculateDuration(startTime, endTime)
          if (calculatedDuration) {
            form.duration = calculatedDuration
          }
        } else if (changedField === 'endTime') {
          // 修改结束时间，开始时间不变，重新计算持续时间
          // 如果开始时间晚于结束时间，允许保存但持续时间设为1（会被标记为时间异常）
          const calculatedDuration = calculateDuration(startTime, endTime)
          if (calculatedDuration) {
            form.duration = calculatedDuration
          }
        }
        // 规则(3): 如果既有开始时间也有结束时间，修改持续时间时，按规则(1)进行（以开始时间为基准）
        else if (changedField === 'duration') {
          // 修改持续时间，以开始时间为基准，重新计算结束时间
          const calculatedEndTime = calculateEndTime(startTime, duration)
          if (calculatedEndTime) {
            form.endTime = formatDateFull(calculatedEndTime)
          }
        }
      } else {
        // 如果只有开始时间和结束时间，没有持续时间，计算持续时间
        const calculatedDuration = calculateDuration(startTime, endTime)
        if (calculatedDuration) {
          form.duration = calculatedDuration
        }
      }
    }
    // 规则(4): 如果开始时间和结束时间都没有，则只填入持续时间
    // 当后续又填写了开始时间或结束时间中的一项，则另一项自动计算
    else if (!startTime && !endTime && duration) {
      // 这种情况只填入持续时间，不自动计算
      // 当后续填写了开始时间或结束时间时，会触发相应的规则
    }
    // 规则(4的后续): 当后续填写了开始时间或结束时间中的一项
    else if (!startTime && endTime && duration && changedField === 'endTime') {
      // 填写了结束时间，如果有持续时间，计算开始时间
      const calculatedStartTime = calculateStartTime(endTime, duration)
      if (calculatedStartTime) {
        form.startTime = formatDateFull(calculatedStartTime)
      }
    }
    else if (startTime && !endTime && duration && changedField === 'startTime') {
      // 填写了开始时间，如果有持续时间，计算结束时间
      const calculatedEndTime = calculateEndTime(startTime, duration)
      if (calculatedEndTime) {
        form.endTime = formatDateFull(calculatedEndTime)
      }
    }
  }

  const deepClone = (obj) => {
    return JSON.parse(JSON.stringify(obj))
  }

  const createFormStateFromTask = (task) => {
    // 从审批节点数组中提取最后一个作为选中的审批层级（用于显示）
    // 如果是逐级审批，数组包含从负责人向上到选中编制的所有编制
    // 如果是指定编制审批，数组只包含一个编制ID
    const approvalNodes = Array.isArray(task.approvalNodes) ? task.approvalNodes : []
    const approvalLevel = approvalNodes.length > 0 ? approvalNodes[approvalNodes.length - 1] : undefined

    // 兼容旧数据：如果 task.assignee 存在，尝试转换为 jobNumber
    // 如果 task.jobNumber 存在，直接使用
    let jobNumber = task.jobNumber || null
    if (!jobNumber && task.assignee) {
      // 尝试通过 assignee（可能是 userId）查找对应的 jobNumber
      const user = employeeList.value.find(u => 
        u.userId === task.assignee || String(u.userId) === String(task.assignee)
      )
      if (user) {
        jobNumber = user.jobNumber
      } else {
        // 如果找不到，可能是旧数据，assignee 本身就是 jobNumber
        jobNumber = String(task.assignee)
      }
    }

    return {
      name: task.name || '',
      description: task.description || '',
      startTime: task.startTime ? formatDateFull(task.startTime) : null,
      endTime: task.endTime ? formatDateFull(task.endTime) : null,
      duration: task.duration || 1,
      jobNumber: jobNumber,
      approvalType: task.approvalType || 'sequential', // 默认逐级审批
      approvalLevel: approvalLevel ? Number(approvalLevel) : undefined
    }
  }

  const areFormStatesEqual = (a, b) => {
    return JSON.stringify(a) === JSON.stringify(b)
  }

  const findTabIndex = (taskId) => taskEditTabs.value.findIndex(tab => String(tab.taskId) === String(taskId))
  const findTabById = (taskId) => taskEditTabs.value.find(tab => String(tab.taskId) === String(taskId))

  const syncFormWithActiveTab = async () => {
    const activeTab = findTabById(activeTaskTabId.value)
    if (!activeTab) return
    isProgrammaticFormSync.value = true
    taskEditForm.value = deepClone(activeTab.formState)
    await nextTick()
    isProgrammaticFormSync.value = false
    await nextTick()
    taskEditFormRef.value?.clearValidate?.()
  }

  const updateCurrentEditingTask = (taskId, findTaskByIdFn) => {
    if (!taskId) {
      currentEditingTask.value = null
      return
    }
    const taskInfo = findTaskByIdFn(taskId)
    currentEditingTask.value = taskInfo ? taskInfo.task : null
  }

  /**
   * 打开或激活任务编辑选项卡
   * @param {Object} task - 任务对象
   * @param {Function} findTaskById - 查找任务函数
   */
  const openTaskEditDialog = async (task, findTaskById) => {
    if (!task) return
    
    await ensureEmployeeListLoaded()
    await loadDeptTree()
    
    const taskInfo = findTaskById(task.id)
    const currentTask = taskInfo ? taskInfo.task : task
    
    const existingIndex = findTabIndex(currentTask.id)
    if (existingIndex !== -1) {
      activeTaskTabId.value = currentTask.id
      updateCurrentEditingTask(currentTask.id, findTaskById)
      await syncFormWithActiveTab()
      // 在表单数据同步后，更新审批层级树
      if (taskEditForm.value.jobNumber) {
        updateApprovalLevelTree()
      }
      taskEditDialogVisible.value = true
      return
    }

    if (taskEditTabs.value.length >= MAX_TAB_COUNT) {
      ElMessage.warning(`最多同时打开 ${MAX_TAB_COUNT} 个任务`)
      return
    }

    const newTab = {
      taskId: currentTask.id,
      formState: createFormStateFromTask(currentTask),
      initialFormState: createFormStateFromTask(currentTask),
      dirty: false
    }

    let insertIndex = taskEditTabs.value.length
    const activeIndex = findTabIndex(activeTaskTabId.value)
    if (activeIndex !== -1) {
      insertIndex = activeIndex + 1
    }
    taskEditTabs.value.splice(insertIndex, 0, newTab)
    activeTaskTabId.value = currentTask.id
    updateCurrentEditingTask(currentTask.id, findTaskById)
    await syncFormWithActiveTab()
    // 在表单数据同步后，更新审批层级树
    if (taskEditForm.value.jobNumber) {
      updateApprovalLevelTree()
    }
    taskEditDialogVisible.value = true
  }

  const setActiveTaskTab = async (taskId, findTaskByIdFn) => {
    if (!taskId) return
    const tab = findTabById(taskId)
    if (!tab) return
    activeTaskTabId.value = taskId
    updateCurrentEditingTask(taskId, findTaskByIdFn)
    await syncFormWithActiveTab()
  }

  const closeTaskTab = async (taskId, findTaskByIdFn = null) => {
    const index = findTabIndex(taskId)
    if (index === -1) return
    taskEditTabs.value.splice(index, 1)
    const wasActive = activeTaskTabId.value === taskId
    if (wasActive) {
      const nextTab = taskEditTabs.value[index - 1] || taskEditTabs.value[index] || null
      activeTaskTabId.value = nextTab ? nextTab.taskId : null
      if (activeTaskTabId.value && findTaskByIdFn) {
        updateCurrentEditingTask(activeTaskTabId.value, findTaskByIdFn)
        await syncFormWithActiveTab()
      }
    }
    if (!activeTaskTabId.value) {
      currentEditingTask.value = null
      resetFormState()
      taskEditDialogVisible.value = false
    }
  }

  const getActiveTaskTab = () => findTabById(activeTaskTabId.value)

  const isTaskTabDirty = (taskId) => {
    const tab = findTabById(taskId)
    return tab ? !!tab.dirty : false
  }

  const markTaskTabAsSaved = (taskId) => {
    const tab = findTabById(taskId)
    if (!tab) return
    tab.initialFormState = deepClone(tab.formState)
    tab.dirty = false
  }

  const resetFormState = () => {
    taskEditForm.value = {
      name: '',
      description: '',
      startTime: null,
      endTime: null,
      duration: 1,
      jobNumber: null,
      approvalType: 'sequential',
      approvalLevel: undefined
    }
    approvalLevelTree.value = []
    taskEditFormRef.value?.resetFields?.()
  }

  /**
   * 关闭任务编辑弹窗
   */
  const closeTaskEditDialog = (resetTabs = true) => {
    currentEditingTask.value = null
    activeTaskTabId.value = null
    resetFormState()
    if (resetTabs) {
      taskEditTabs.value = []
    }
    taskEditDialogVisible.value = false
  }

  /**
   * 获取当前编辑的任务ID
   * @returns {string|number|null} 任务ID
   */
  const getCurrentEditingTaskId = () => {
    return currentEditingTask.value?.id || null
  }

  /**
   * 获取任务的前置任务数量
   * @param {Object} task - 任务对象
   * @returns {number} 前置任务数量
   */
  const getPredecessorTaskCount = (task) => {
    if (!task || !task.predecessorTasks) return 0
    return Array.isArray(task.predecessorTasks) ? task.predecessorTasks.length : 0
  }

  /**
   * 获取任务的后置任务数量
   * @param {Object} task - 任务对象
   * @returns {number} 后置任务数量
   */
  const getSuccessorTaskCount = (task) => {
    if (!task || !task.successorTasks) return 0
    return Array.isArray(task.successorTasks) ? task.successorTasks.length : 0
  }

  /**
   * 获取前置任务列表
   * @param {Object} task - 任务对象
   * @param {Function} findTaskById - 查找任务函数
   * @returns {Array} 前置任务列表
   */
  const getPredecessorTaskList = (task, findTaskById) => {
    if (!task || !task.predecessorTasks || !Array.isArray(task.predecessorTasks)) return []
    return task.predecessorTasks
      .map(taskId => {
        const taskInfo = findTaskById(taskId)
        return taskInfo ? taskInfo.task : null
      })
      .filter(t => t != null)
  }

  /**
   * 获取后置任务列表
   * @param {Object} task - 任务对象
   * @param {Function} findTaskById - 查找任务函数
   * @returns {Array} 后置任务列表
   */
  const getSuccessorTaskList = (task, findTaskById) => {
    if (!task || !task.successorTasks || !Array.isArray(task.successorTasks)) return []
    return task.successorTasks
      .map(taskId => {
        const taskInfo = findTaskById(taskId)
        return taskInfo ? taskInfo.task : null
      })
      .filter(t => t != null)
  }

  /**
   * 获取任务所属阶段名称
   * @param {Object} task - 任务对象
   * @param {Function} findTaskById - 查找任务函数
   * @returns {string} 阶段名称
   */
  const getTaskStageName = (task, findTaskById) => {
    if (!task) return '未分配'
    const taskInfo = findTaskById(task.id)
    if (taskInfo && taskInfo.stage) {
      return taskInfo.stage.name || '未命名阶段'
    }
    return '未分配'
  }

  /**
   * 确认任务编辑
   * @param {Function} findTaskById - 查找任务函数
   * @param {Object} workflowStore - 工作流store
   * @param {Object} formRef - 表单引用（可选，如果提供则使用提供的引用）
   * @returns {Promise<boolean>} 是否成功保存
   */
  const confirmTaskEdit = async (findTaskById, workflowStore, formRef = null, workflowData = null) => {
    const formRefToUse = formRef || taskEditFormRef.value
    if (!formRefToUse) return false
    
    // 1. 触发表单验证以显示样式（红色边框等），但不阻止保存
    // 即使验证失败也允许保存，因为实际场景中可能先填写部分信息
    formRefToUse.validate().catch(() => {
      // 验证失败不影响保存流程，仅用于显示样式
    })
    
    if (!currentEditingTask.value) return false
    
    // 2. 准备任务数据（转换日期格式）
    // 根据审批类型和选中的审批层级，计算最终的审批节点数组
    const approvalLevel = taskEditForm.value.approvalLevel
    const approvalNodes = approvalLevel !== undefined && approvalLevel !== null
      ? calculateApprovalNodes(approvalLevel, taskEditForm.value.approvalType)
      : []
    
    const taskData = {
      name: taskEditForm.value.name,
      description: taskEditForm.value.description || '',
      startTime: taskEditForm.value.startTime ? parseDate(taskEditForm.value.startTime) : null,
      endTime: taskEditForm.value.endTime ? parseDate(taskEditForm.value.endTime) : null,
      duration: taskEditForm.value.duration || 1,
      jobNumber: taskEditForm.value.jobNumber || null, // jobNumber 是工号（字符串）
      approvalType: taskEditForm.value.approvalType || 'sequential',
      approvalNodes: approvalNodes // 计算后的审批节点数组
    }
    
    // 3. 查找任务并更新数据
    const taskInfo = findTaskById(currentEditingTask.value.id)
    if (!taskInfo || !taskInfo.task) {
      ElMessage.error('未找到任务')
      return false
    }
    
    // 更新任务数据
    taskInfo.task.name = taskData.name
    taskInfo.task.description = taskData.description
    taskInfo.task.startTime = taskData.startTime
    taskInfo.task.endTime = taskData.endTime
    taskInfo.task.duration = taskData.duration
    // jobNumber 保存为工号（字符串）
    taskInfo.task.jobNumber = taskData.jobNumber
    // 审批节点相关字段
    taskInfo.task.approvalType = taskData.approvalType
    taskInfo.task.approvalNodes = taskData.approvalNodes
    
    // 4. 任务对象已经直接更新，不需要额外操作 workflowStore
    // 因为 taskInfo.task 就是主数据源中的任务对象引用
    
    // 5. 如果任务在阶段内，更新阶段的时间（因为阶段时间是根据阶段内所有任务的时间计算的）
    // 优先使用传入的 workflowData，如果没有则尝试从 workflowStore 获取
    let workflowDataValue = null
    if (workflowData) {
      workflowDataValue = workflowData.value
    } else if (workflowStore?.workflowDataRef?.value) {
      workflowDataValue = workflowStore.workflowDataRef.value.value
    }
    
    if (taskInfo.stage && workflowDataValue && workflowDataValue.stages) {
      const { updateStageTime } = useStageTime()
      const stage = workflowDataValue.stages.find(s => s.id === taskInfo.stage.id)
      
      if (stage) {
        // 更新阶段的时间（重新计算阶段内所有任务的时间范围）
        const updatedStage = updateStageTime(stage)
        // 使用 Object.assign 确保响应式更新
        Object.assign(stage, {
          startTime: updatedStage.startTime,
          endTime: updatedStage.endTime,
          duration: updatedStage.duration
        })
        
        // 阶段时间更新后，立即校验并更新阶段的时间异常标记
        // 创建 findStageById 函数
        const findStageById = (stageId) => {
          return workflowDataValue.stages.find(s => s.id === stageId) || null
        }
        // 立即更新阶段及其相关阶段的时间异常标记
        updateStageAndRelatedStagesTimeIssueFlags(stage.id, findStageById, workflowStore, workflowData)
      }
    }
    
    // 6. 检查任务及其相关任务（前置和后置）的时间问题（需要在更新数据后调用）
    // 因为修改任务时间可能影响前置任务和后置任务的时间状态
    // 注意：阶段的时间异常标记已经在步骤5中更新了，这里传入 workflowData 以避免重复调用
    // 但 updateTaskAndRelatedTasksTimeIssueFlags 内部会检查，如果已经更新过则不会重复更新
    updateTaskAndRelatedTasksTimeIssueFlags(taskInfo.task.id, findTaskById, workflowStore, workflowDataValue ? workflowData : null)
    
    ElMessage.success('任务已更新')
    return true
  }

  watch(taskEditForm, (newVal) => {
    if (isProgrammaticFormSync.value) return
    const activeTab = findTabById(activeTaskTabId.value)
    if (!activeTab) return
    const clonedForm = deepClone(newVal)
    activeTab.formState = clonedForm
    activeTab.dirty = !areFormStatesEqual(activeTab.initialFormState, clonedForm)
  }, { deep: true })

  // 在打开弹窗时加载员工列表（如果还未加载）
  const ensureEmployeeListLoaded = async () => {
    if (employeeList.value.length === 0) {
      await loadEmployeeList()
    }
  }

  // 监听负责人变化，更新审批层级树并清空已选择的审批层级
  watch(() => taskEditForm.value.jobNumber, (newJobNumber, oldJobNumber) => {
    if (newJobNumber !== oldJobNumber) {
      updateApprovalLevelTree()
    }
  })

  return {
    // 状态
    taskEditDialogVisible,
    taskEditFormRef,
    currentEditingTask,
    taskEditForm,
    taskEditRules,
    employeeOptions,
    taskEditTabs,
    activeTaskTabId,
    MAX_TAB_COUNT,
    // 方法
    openTaskEditDialog,
    closeTaskEditDialog,
    confirmTaskEdit,
    setActiveTaskTab,
    closeTaskTab,
    findTabById,
    areFormStatesEqual,
    getActiveTaskTab,
    isTaskTabDirty,
    markTaskTabAsSaved,
    getCurrentEditingTaskId,
    getPredecessorTaskCount,
    getSuccessorTaskCount,
    getPredecessorTaskList,
    getSuccessorTaskList,
    getTaskStageName,
    handleTimeFieldChange,
    formatDateFull,
    parseDate,
    loadEmployeeList,
    getUserDisplayName,
    getUserNickName,
    employeeList, // 导出 employeeList 供外部使用
    approvalLevelTree, // 导出审批层级树
    updateApprovalLevelTree, // 导出更新审批层级树函数
    loadDeptTree // 导出加载编制树函数
  }
}

