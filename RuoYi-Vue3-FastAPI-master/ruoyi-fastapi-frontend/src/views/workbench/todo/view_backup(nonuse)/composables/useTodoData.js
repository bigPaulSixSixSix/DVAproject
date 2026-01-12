import { ref, reactive } from 'vue'
import { getMyTaskCategories, getMyTaskList, getTaskDetail } from '@/api/todo'

/**
 * 我的任务数据管理
 */
export function useTodoData() {
  // 分类统计数据
  const categories = ref({
    project: { total: 0, items: [] },
    department: { total: 0, items: [] },
    status: { total: 0, items: [] }
  })

  // 筛选状态
  const filterState = reactive({
    projectId: null,
    deptId: null,
    taskStatus: null
  })

  // 任务列表
  const taskList = ref([])
  const taskListLoading = ref(false)
  const taskListTotal = ref(0)
  const taskListQuery = reactive({
    pageNum: 1,
    pageSize: 10
  })

  // 当前选中的任务
  const selectedTask = ref(null)
  const taskDetail = ref(null)
  const taskDetailLoading = ref(false)

  // 加载分类统计
  const loadCategories = async () => {
    try {
      const res = await getMyTaskCategories()
      if (res.code === 200 && res.data) {
        categories.value = res.data
      }
    } catch (error) {
      console.error('加载分类统计失败:', error)
    }
  }

  // 加载任务列表
  const loadTaskList = async () => {
    taskListLoading.value = true
    try {
      const params = {
        ...taskListQuery,
        projectId: filterState.projectId || undefined,
        deptId: filterState.deptId || undefined,
        taskStatus: filterState.taskStatus || undefined
      }
      const res = await getMyTaskList(params)
      if (res.code === 200 && res.data) {
        taskList.value = res.data.rows || []
        taskListTotal.value = res.data.total || 0
      }
    } catch (error) {
      console.error('加载任务列表失败:', error)
      taskList.value = []
      taskListTotal.value = 0
    } finally {
      taskListLoading.value = false
    }
  }

  // 加载任务详情
  const loadTaskDetail = async (taskId) => {
    if (!taskId) {
      taskDetail.value = null
      return
    }
    taskDetailLoading.value = true
    try {
      const res = await getTaskDetail(taskId)
      if (res.code === 200 && res.data) {
        taskDetail.value = res.data
      }
    } catch (error) {
      console.error('加载任务详情失败:', error)
      taskDetail.value = null
    } finally {
      taskDetailLoading.value = false
    }
  }

  // 选择分类
  const selectCategory = (type, value) => {
    if (type === 'project') {
      filterState.projectId = value
    } else if (type === 'department') {
      filterState.deptId = value
    } else if (type === 'status') {
      filterState.taskStatus = value
    }
    // 重置分页
    taskListQuery.pageNum = 1
    // 重新加载任务列表
    loadTaskList()
    // 清空选中任务
    selectedTask.value = null
    taskDetail.value = null
  }

  // 选择任务
  const selectTask = async (task) => {
    selectedTask.value = task
    await loadTaskDetail(task.taskId)
  }

  // 重置筛选
  const resetFilter = () => {
    filterState.projectId = null
    filterState.deptId = null
    filterState.taskStatus = null
    taskListQuery.pageNum = 1
    loadTaskList()
    selectedTask.value = null
    taskDetail.value = null
  }

  return {
    // 数据
    categories,
    filterState,
    taskList,
    taskListLoading,
    taskListTotal,
    taskListQuery,
    selectedTask,
    taskDetail,
    taskDetailLoading,
    // 方法
    loadCategories,
    loadTaskList,
    loadTaskDetail,
    selectCategory,
    selectTask,
    resetFilter
  }
}
