<template>
  <div class="app-container">
    <el-table
      v-loading="loading"
      :data="projectList"
      border
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="code" label="序号" width="120" align="center" />
      <el-table-column prop="name" label="项目名称" min-width="120" />
      <el-table-column prop="projectStatus" label="项目状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getProjectStatusType(row.projectStatus)">
            {{ row.projectStatus || '-' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="missingInfoCount" label="信息缺失数" width="150" align="center" />
      <el-table-column prop="timeRelationErrorCount" label="时间异常数" width="150" align="center" />
      <el-table-column prop="unassignedStageCount" label="未分配到阶段数" width="150" align="center" />
      <el-table-column prop="stageCount" label="阶段数量" width="150" align="center" />
      <el-table-column prop="taskCount" label="任务数量" width="150" align="center" />
      <el-table-column prop="createTime" label="创建时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="updateTime" label="修改时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.updateTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="tasksGenerated" label="任务状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.tasksGenerated ? 'success' : 'info'">
            {{ row.tasksGenerated ? '已生成' : '未生成' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="生成任务" width="120" align="center">
        <template #default="{ row }">
          <!-- 已生成任务的项目不显示按钮 -->
          <span v-if="row.tasksGenerated">-</span>
          <!-- 未生成任务的项目显示按钮 -->
          <template v-else>
            <el-tooltip
              v-if="row.projectStatus !== '正常'"
              content="当前项目状态异常，请完善所有任务后再生成"
              placement="top"
            >
              <span style="display: inline-block;">
                <el-button
                  :disabled="true"
                  type="primary"
                  size="small"
                  @click.stop="handleGenerateTasks(row)"
                >
                  生成任务
                </el-button>
              </span>
            </el-tooltip>
            <el-button
              v-else
              :loading="generatingTasks.has(row.id)"
              :disabled="generatingTasks.has(row.id)"
              type="primary"
              size="small"
              @click.stop="handleGenerateTasks(row)"
            >
              生成任务
            </el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElTag, ElButton, ElTooltip } from 'element-plus'
import { fetchTaskProjectList } from '@/api/workflow'
import { generateTasks } from '@/api/todo'

defineOptions({
  name: 'ProjectList'
})

const router = useRouter()

const loading = ref(false)
const projectList = ref([])
const generatingTasks = ref(new Set()) // 记录正在生成任务的项目ID

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取项目状态的标签类型
const getProjectStatusType = (status) => {
  if (!status) return 'info'
  if (status === '正常') return 'success'
  if (status === '异常') return 'danger'
  return 'warning'
}

// 加载项目列表
const loadProjectList = async () => {
  loading.value = true
  try {
    const response = await fetchTaskProjectList()
    const rawList = Array.isArray(response?.data?.data)
      ? response.data.data
      : Array.isArray(response?.data)
        ? response.data
        : Array.isArray(response)
          ? response
          : []
    projectList.value = rawList.map(item => ({
      id: item.projectId,
      code: item.projectId,
      name: item.projectName || item.projectLabel || `项目${item.projectId}`,
      stageCount: item.stageCount ?? 0,
      taskCount: item.taskCount ?? 0,
      missingInfoCount: item.missingInfoCount ?? 0,
      timeRelationErrorCount: item.timeRelationErrorCount ?? 0,
      unassignedStageCount: item.unassignedStageCount ?? 0,
      projectStatus: item.projectStatus || '正常',
      tasksGenerated: item.tasksGenerated ?? false,
      createTime: item.createTime || null,
      updateTime: item.updateTime || null
    }))
  } catch (error) {
    ElMessage.error('加载项目列表失败: ' + (error.message || '未知错误'))
    projectList.value = []
  } finally {
    loading.value = false
  }
}

// 点击行跳转到任务配置页面
const handleRowClick = (row) => {
  router.push({
    path: `/workbench/routine/task-configuration/${row.id}`
  })
}

// 生成任务
const handleGenerateTasks = async (row) => {
  if (row.projectStatus !== '正常') {
    ElMessage.warning('当前项目状态异常，请完善所有任务后再生成')
    return
  }

  // 如果正在生成，直接返回
  if (generatingTasks.value.has(row.id)) {
    return
  }

  generatingTasks.value.add(row.id)
  try {
    const response = await generateTasks(row.id)
    if (response.code === 200) {
      ElMessage.success(response.msg || '任务生成成功')
      // 更新当前行的任务状态
      row.tasksGenerated = true
      // 重新加载列表以获取最新数据
      await loadProjectList()
    } else {
      ElMessage.error(response.msg || '任务生成失败')
    }
  } catch (error) {
    ElMessage.error('任务生成失败: ' + (error.message || '未知错误'))
  } finally {
    generatingTasks.value.delete(row.id)
  }
}

onMounted(() => {
  loadProjectList()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
  background: transparent;
}

:deep(.el-table) {
  cursor: pointer;
  background: transparent;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: var(--el-table-row-hover-bg-color);
}
</style>

