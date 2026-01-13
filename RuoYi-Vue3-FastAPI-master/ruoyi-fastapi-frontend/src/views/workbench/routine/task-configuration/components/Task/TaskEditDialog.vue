<template>
  <el-dialog
    v-model="dialogVisible"
    width="1500px"
    append-to-body
    title=""
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="task-edit-dialog"
    @close="handleClose"
  >
    <template #header>
      <TaskEditTabs
        v-if="taskTabs && taskTabs.length"
        :tabs="taskTabs"
        :active-tab-id="activeTabId"
        :get-user-nick-name="getUserNickName"
        :find-task-by-id="findTaskById"
        @select="handleTabSelect"
        @close="handleTabClose"
      />
    </template>
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="dynamicRules" 
      label-width="100px"
    >
      <!-- 上半部分：基本信息 -->
      <el-row :gutter="20">
        <!-- 左列：任务名称、任务描述 -->
        <el-col :span="12">
          <el-form-item label="任务名称" prop="name">
            <el-input 
              v-model="form.name" 
              placeholder="请输入任务名称"
              :disabled="!isEditable"
            />
          </el-form-item>
          <el-form-item label="任务描述">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入任务描述（可选）" 
              :disabled="!isEditable"
            />
          </el-form-item>
        </el-col>
        <!-- 右列：时间信息、负责人 -->
        <el-col :span="12">
          <el-form-item label="时间信息" required>
            <div class="time-info-container">
              <el-form-item 
                prop="startTime" 
                :class="['time-info-item', { 'time-info-item--time-warning': timeIssueDetails.startTimeIssue }]"
              >
                <el-date-picker
                  v-model="form.startTime"
                  type="date"
                  placeholder="开始时间"
                  format="YYYY/MM/DD"
                  value-format="YYYY/MM/DD"
                  clearable
                  :disabled="!isEditable"
                  @change="() => handleTimeFieldChange('startTime')"
                />
                <div v-if="startTimeWarningMessage" class="time-warning-error">
                  {{ startTimeWarningMessage }}
                </div>
              </el-form-item>
              <el-form-item prop="duration" class="time-info-item">
                <el-input-number
                  v-model="form.duration"
                  :min="1"
                  :precision="0"
                  placeholder="持续时间"
                  :disabled="!isEditable"
                  @change="() => handleTimeFieldChange('duration')"
                />
              </el-form-item>
              <el-form-item 
                prop="endTime" 
                :class="['time-info-item', { 'time-info-item--time-warning': timeIssueDetails.endTimeIssue }]"
              >
                <el-date-picker
                  v-model="form.endTime"
                  type="date"
                  placeholder="结束时间"
                  format="YYYY/MM/DD"
                  value-format="YYYY/MM/DD"
                  clearable
                  :disabled="!isEditable"
                  @change="() => handleTimeFieldChange('endTime')"
                />
                <div v-if="endTimeWarningMessage" class="time-warning-error">
                  {{ endTimeWarningMessage }}
                </div>
              </el-form-item>
            </div>
          </el-form-item>
          <el-form-item label="负责人" prop="jobNumber">
            <el-select
              v-model="form.jobNumber"
              placeholder="请选择负责人"
              filterable
              :disabled="!isEditable"
              style="width: 100%"
            >
              <el-option
                v-for="option in employeeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="审批层级" prop="approvalLevel">
            <div style="display: flex; gap: 8px; width: 100%;">
              <!-- 第一个选项框：审批类型 -->
              <el-select
                v-model="form.approvalType"
                placeholder="请选择审批类型"
                :disabled="!isEditable"
                style="width: 220px; flex-shrink: 0;"
              >
                <el-option
                  label="逐级审批"
                  value="sequential"
                />
                <el-option
                  label="指定编制审批"
                  value="specified"
                />
                <el-option
                  label="无需审批"
                  value="none"
                />
              </el-select>
              <!-- 第二个选项框：审批层级树形选择（单选） -->
              <el-tree-select
                :model-value="form.approvalLevel"
                @update:model-value="(val) => form.approvalLevel = val === null ? undefined : val"
                :data="approvalLevelTree"
                :props="{ label: 'label', children: 'children', value: 'id' }"
                placeholder="请选择审批层级"
                :disabled="!isEditable || form.approvalType === 'none' || (form.jobNumber && approvalLevelTree.length === 0)"
                style="flex: 1 1 auto; min-width: 200px;"
                clearable
                check-strictly
                default-expand-all
              />
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 分隔线 -->
      <el-divider />

      <!-- 下半部分：前置任务和后置任务 -->
      <el-row :gutter="20">
        <!-- 左列：前置任务 -->
        <el-col :span="12">
          <div style="font-weight: bold; margin-bottom: 10px;">前置任务</div>
          <el-table
            :data="predecessorTaskList"
            border
            class="relation-table"
            :class="{ 'relation-table--empty': !hasPredecessorTasks }"
            style="width: 100%"
            :max-height="TABLE_MAX_HEIGHT"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="任务名称" min-width="120">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'name') }">
                  {{ row.name || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="开始时间" width="100">
              <template #default="{ row }">
                <span :class="{ 
                  'time-cell-warning-bg': getTaskTimeIssueDetails(row, true).startTimeIssue,
                  'missing-field': isFieldMissing(row, 'startTime')
                }">
                  {{ row.startTime ? formatDate(row.startTime) : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="时长" width="60">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'duration') }">
                  {{ row.duration || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="结束时间" width="100">
              <template #default="{ row }">
                <span :class="{ 
                  'time-cell-warning-bg': getTaskTimeIssueDetails(row, true).endTimeIssue,
                  'missing-field': isFieldMissing(row, 'endTime')
                }">
                  {{ row.endTime ? formatDate(row.endTime) : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="负责人" width="100">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'jobNumber') }">
                  {{ getUserNickName(row.jobNumber || row.assignee) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right" :resizable="false">
              <template #default="{ row }">
                <div class="relation-action-buttons">
                  <!-- 如果当前任务不可编辑：前置任务只显示查看按钮 -->
                  <template v-if="!isEditable">
                    <el-tooltip content="查看详情" placement="top">
                      <el-button 
                        size="small" 
                        type="info" 
                        plain 
                        @click="handlePredecessorTaskEdit(row)"
                      >
                        <el-icon><MoreFilled /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </template>
                  <!-- 如果当前任务可编辑：根据前置任务是否可编辑显示不同按钮 -->
                  <template v-else>
                    <!-- 如果前置任务可编辑：显示三个按钮 -->
                    <template v-if="isTaskEditable(row)">
                  <el-tooltip content="编辑" placement="top">
                        <el-button 
                          size="small" 
                          type="primary" 
                          plain 
                          @click="handlePredecessorTaskEdit(row)"
                        >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="取消关联" placement="top">
                        <el-button 
                          size="small" 
                          type="info" 
                          plain 
                          @click="handlePredecessorTaskUnlink(row)"
                        >
                      <el-icon><Link /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                        <el-button 
                          size="small" 
                          type="danger" 
                          plain 
                          @click="handlePredecessorTaskDelete(row)"
                        >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                    </template>
                    <!-- 如果前置任务不可编辑：显示两个按钮（查看、删除关联） -->
                    <template v-else>
                      <el-tooltip content="查看详情" placement="top">
                        <el-button 
                          size="small" 
                          type="info" 
                          plain 
                          @click="handlePredecessorTaskEdit(row)"
                        >
                          <el-icon><MoreFilled /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip content="取消关联" placement="top">
                        <el-button 
                          size="small" 
                          type="info" 
                          plain 
                          @click="handlePredecessorTaskUnlink(row)"
                        >
                          <el-icon><Link /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </template>
                  </template>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <!-- 右列：后置任务 -->
        <el-col :span="12">
          <div style="font-weight: bold; margin-bottom: 10px;">后置任务</div>
          <el-table
            :data="successorTaskList"
            border
            class="relation-table"
            :class="{ 'relation-table--empty': !hasSuccessorTasks }"
            style="width: 100%"
            :max-height="TABLE_MAX_HEIGHT"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="任务名称" min-width="120">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'name') }">
                  {{ row.name || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="开始时间" width="100">
              <template #default="{ row }">
                <span :class="{ 
                  'time-cell-warning-bg': getTaskTimeIssueDetails(row, false).startTimeIssue,
                  'missing-field': isFieldMissing(row, 'startTime')
                }">
                  {{ row.startTime ? formatDate(row.startTime) : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="时长" width="60">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'duration') }">
                  {{ row.duration || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="结束时间" width="100">
              <template #default="{ row }">
                <span :class="{ 
                  'time-cell-warning-bg': getTaskTimeIssueDetails(row, false).endTimeIssue,
                  'missing-field': isFieldMissing(row, 'endTime')
                }">
                  {{ row.endTime ? formatDate(row.endTime) : '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="负责人" width="100">
              <template #default="{ row }">
                <span :class="{ 'missing-field': isFieldMissing(row, 'jobNumber') }">
                  {{ getUserNickName(row.jobNumber || row.assignee) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right" :resizable="false">
              <template #default="{ row }">
                <div class="relation-action-buttons">
                  <!-- 如果当前任务不可编辑：根据后置任务是否可编辑显示不同按钮 -->
                  <template v-if="!isEditable">
                    <!-- 如果后置任务可编辑：显示三个按钮 -->
                    <template v-if="isTaskEditable(row)">
                      <el-tooltip content="编辑" placement="top">
                        <el-button 
                          size="small" 
                          type="primary" 
                          plain 
                          @click="handleSuccessorTaskEdit(row)"
                        >
                          <el-icon><Edit /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip content="取消关联" placement="top">
                        <el-button 
                          size="small" 
                          type="info" 
                          plain 
                          @click="handleSuccessorTaskUnlink(row)"
                        >
                          <el-icon><Link /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip content="删除" placement="top">
                        <el-button 
                          size="small" 
                          type="danger" 
                          plain 
                          @click="handleSuccessorTaskDelete(row)"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </template>
                    <!-- 如果后置任务不可编辑：只显示查看按钮 -->
                    <template v-else>
                      <el-tooltip content="查看详情" placement="top">
                        <el-button 
                          size="small" 
                          type="info" 
                          plain 
                          @click="handleSuccessorTaskEdit(row)"
                        >
                          <el-icon><MoreFilled /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </template>
                  </template>
                  <!-- 如果当前任务可编辑：后置任务都是可编辑的，显示三个按钮 -->
                  <template v-else>
                  <el-tooltip content="编辑" placement="top">
                      <el-button 
                        size="small" 
                        type="primary" 
                        plain 
                        @click="handleSuccessorTaskEdit(row)"
                      >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="取消关联" placement="top">
                      <el-button 
                        size="small" 
                        type="info" 
                        plain 
                        @click="handleSuccessorTaskUnlink(row)"
                      >
                      <el-icon><Link /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="删除" placement="top">
                      <el-button 
                        size="small" 
                        type="danger" 
                        plain 
                        @click="handleSuccessorTaskDelete(row)"
                      >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                  </template>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button 
          v-if="isEditable"
          type="danger" 
          @click="handleDelete"
        >
          删除
        </el-button>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm">确认</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElDialog, ElForm, ElFormItem, ElInput, ElButton, ElTable, ElTableColumn, ElDivider, ElSelect, ElOption, ElDatePicker, ElInputNumber, ElTooltip, ElTreeSelect } from 'element-plus'
import { Edit, Delete, Link, MoreFilled } from '@element-plus/icons-vue'
import TaskEditTabs from './EditTabs/TaskEditTabs.vue'
import { useDialogKeyboardHandler } from '../../composables/utils/useDialogKeyboardHandler'
import { useTaskEditTimeValidation } from '../../composables/task/useTaskEditTimeValidation'
import { isTaskFieldMissing } from '../../composables/utils/useUtils'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  form: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    required: true
  },
  employeeOptions: {
    type: Array,
    default: () => []
  },
  approvalLevelTree: {
    type: Array,
    default: () => []
  },
  updateApprovalLevelTree: {
    type: Function,
    default: null
  },
  currentEditingTask: {
    type: Object,
    default: null
  },
  taskTabs: {
    type: Array,
    default: () => []
  },
  activeTabId: {
    type: [String, Number, null],
    default: null
  },
  predecessorTaskList: {
    type: Array,
    default: () => []
  },
  successorTaskList: {
    type: Array,
    default: () => []
  },
  getUserNickName: {
    type: Function,
    required: true
  },
  handleTimeFieldChange: {
    type: Function,
    required: true
  },
  findTaskById: {
    type: Function,
    default: null
  }
})

const emit = defineEmits([
  'update:visible',
  'close',
  'confirm',
  'cancel',
  'delete',
  'tab-select',
  'tab-close',
  'predecessor-task-edit',
  'predecessor-task-unlink',
  'predecessor-task-delete',
  'successor-task-edit',
  'successor-task-unlink',
  'successor-task-delete',
  'enter-key',
  'esc-key'
])

const formRef = ref(null)

// 计算当前任务是否可编辑
const isEditable = computed(() => {
  return props.currentEditingTask?.isEditable !== false
})

// 检查任务是否可编辑
const isTaskEditable = (task) => {
  return task?.isEditable !== false
}

// 检查后置任务是否可编辑（用于后置任务操作按钮）
const isSuccessorTaskEditable = (task) => {
  // 如果当前任务不可编辑，只能编辑未生成的后置任务
  if (!isEditable.value) {
    return task.isEditable !== false
  }
  return true
}

// 任务编辑时间验证
const {
  timeIssueDetails,
  startTimeWarningMessage,
  endTimeWarningMessage,
  getTaskTimeIssueDetails,
  getDynamicRules
} = useTaskEditTimeValidation({
  currentEditingTask: computed(() => props.currentEditingTask),
  form: computed(() => props.form),
  findTaskById: props.findTaskById
})

// 动态验证规则：当结束时间有冲突时，不显示"请选择结束时间"的验证提示
const dynamicRules = computed(() => {
  return getDynamicRules(props.rules)
})

// 监听审批类型变化，当选择"无需审批"时清空审批层级
watch(() => props.form.approvalType, (newValue) => {
  if (newValue === 'none') {
    // 使用 nextTick 确保在 v-model 更新后再清空审批层级
    nextTick(() => {
      form.approvalLevel = undefined
    })
  }
}, { immediate: false })

// 键盘事件处理函数（emit 事件给父组件）
const handleFormEnter = (event) => {
  emit('enter-key')
}

const handleFormEsc = (event) => {
  emit('esc-key')
}

// 使用弹窗键盘事件处理 composable
const { setup: setupKeyboardHandler, cleanup: cleanupKeyboardHandler } = useDialogKeyboardHandler({
  dialogSelector: () => {
    const allDialogs = document.querySelectorAll('.el-dialog')
    return Array.from(allDialogs).find(dialog => 
      dialog.classList.contains('task-edit-dialog') || 
      dialog.querySelector('.task-edit-dialog') !== null
    )
  },
  onEnter: handleFormEnter,
  onEsc: handleFormEsc,
  isMessageBoxShowing: () => {
    // 检查是否有 ElMessageBox 正在显示（通过 DOM 检查）
    return document.querySelector('.el-message-box') !== null
  },
  debug: false // 生产环境可以设为 false
})

// 监听弹窗打开/关闭，设置/清理键盘事件监听和触发表单验证
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    // 等待 DOM 更新完成
    await nextTick()
    await nextTick()
    // 手动触发验证，显示必填字段的错误提示
    if (formRef.value) {
      formRef.value.validateField(['startTime', 'endTime', 'jobNumber', 'approvalLevel']).catch(() => {
        // 验证失败是预期的，用于显示错误提示
      })
    }
    // 设置键盘事件监听
    setupKeyboardHandler()
  } else {
    // 清理键盘事件监听
    cleanupKeyboardHandler()
  }
})

// 监听负责人变化，更新审批层级树
watch(() => props.form.jobNumber, (newJobNumber, oldJobNumber) => {
  if (newJobNumber !== oldJobNumber && props.updateApprovalLevelTree) {
    // 使用 nextTick 确保数据已更新
    nextTick(() => {
      props.updateApprovalLevelTree()
    })
  }
}, { immediate: false })

// 暴露 formRef 供父组件使用
defineExpose({
  formRef
})

// 计算是否有数据
const hasPredecessorTasks = computed(() => props.predecessorTaskList && props.predecessorTaskList.length > 0)
const hasSuccessorTasks = computed(() => props.successorTaskList && props.successorTaskList.length > 0)

// 表格区域最大高度
const TABLE_MAX_HEIGHT = 600

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 格式化日期显示
const formatDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}/${month}/${day}`
}


// 使用工具函数检查任务字段是否缺失
const isFieldMissing = isTaskFieldMissing

const handleClose = () => {
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}

const handleDelete = () => {
  emit('delete')
}

const handleTabSelect = (taskId) => {
  emit('tab-select', taskId)
}

const handleTabClose = (taskId) => {
  emit('tab-close', taskId)
}

const handlePredecessorTaskEdit = (task) => {
  emit('predecessor-task-edit', task)
}

const handlePredecessorTaskUnlink = (task) => {
  emit('predecessor-task-unlink', task)
}

const handlePredecessorTaskDelete = (task) => {
  emit('predecessor-task-delete', task)
}

const handleSuccessorTaskEdit = (task) => {
  emit('successor-task-edit', task)
}

const handleSuccessorTaskUnlink = (task) => {
  emit('successor-task-unlink', task)
}

const handleSuccessorTaskDelete = (task) => {
  emit('successor-task-delete', task)
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 0;
  padding: 0;
}

.dialog-footer :deep(.el-button + .el-button) {
  margin-left: 0;
}

.relation-action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex-wrap: nowrap;
}

.relation-action-buttons .el-button {
  white-space: nowrap;
  padding: 0;
  margin: 0;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.relation-table--empty :deep(.el-table__body-wrapper) {
  /* 确保空表格的表体区域正确显示，不产生滚动条 */
  overflow: hidden !important;
}

.relation-table--empty :deep(.el-table__empty-block) {
  padding: 0 !important;
  margin: 0 !important;
  height: 41px !important; /* 固定高度为一行的高度，避免出现60px */
  min-height: 41px !important;
  max-height: 41px !important;
  display: flex !important;
  align-items: flex-start !important; /* 顶部对齐，而非垂直居中 */
  justify-content: center !important;
}

.relation-table--empty :deep(.el-table__empty-text) {
  line-height: 41px !important; /* 与数据行行高一致（实际测量为41px） */
  margin: 0 !important;
  padding: 0 !important;
  display: block !important; /* 改为 block，确保顶部对齐 */
}

/* 隐藏空表格时的固定列边框 */
.relation-table--empty :deep(.el-table__fixed-right) {
  display: none !important;
}

.relation-table--empty :deep(.el-table__fixed-right-patch) {
  display: none !important;
}


/* 对话框样式调整 */
.task-edit-dialog :deep(.el-dialog) {
  display: flex;
  flex-direction: column;
}

.task-edit-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-x: hidden;
}

/* 时间字段警告样式 - 统一黄色状态 */
.time-info-item--time-warning :deep(.el-input__wrapper) {
  border-color: var(--el-color-warning) !important;
  background-color: var(--el-color-warning-light-9);
  box-shadow: 0 0 0 1px var(--el-color-warning) inset;
}

.time-info-item--time-warning :deep(.el-input__wrapper:hover) {
  border-color: var(--el-color-warning) !important;
}

.time-info-item--time-warning :deep(.el-input__wrapper.is-focus) {
  border-color: var(--el-color-warning) !important;
  box-shadow: 0 0 0 1px var(--el-color-warning) inset;
}

.time-warning-error {
  font-size: 12px;
  color: var(--el-color-warning);
  margin-top: -16px;
  line-height: 1.2;
  position: absolute;
  right: 0;
}

/* 表格中时间单元格警告样式 - 通过 :has() 选择器给父级单元格设置背景色 */
.relation-table :deep(td:has(.time-cell-warning-bg)),
.relation-table :deep(td:has(.time-cell-warning-bg) .cell),
.relation-table :deep(tbody tr:hover td:has(.time-cell-warning-bg)),
.relation-table :deep(tbody tr:hover td:has(.time-cell-warning-bg) .cell) {
  background-color: var(--el-color-warning-light-9) !important;
}

/* 表格中缺失字段样式 - 通过 :has() 选择器给父级单元格设置红色背景 */
.relation-table :deep(td:has(.missing-field)),
.relation-table :deep(td:has(.missing-field) .cell),
.relation-table :deep(tbody tr:hover td:has(.missing-field)),
.relation-table :deep(tbody tr:hover td:has(.missing-field) .cell) {
  background-color: var(--el-color-danger-light-9) !important;
}

/* 如果同时有时间警告和缺失字段，优先显示红色（缺失字段优先级更高） */
.relation-table :deep(td:has(.missing-field.time-cell-warning-bg)),
.relation-table :deep(td:has(.missing-field.time-cell-warning-bg) .cell),
.relation-table :deep(tbody tr:hover td:has(.missing-field.time-cell-warning-bg)),
.relation-table :deep(tbody tr:hover td:has(.missing-field.time-cell-warning-bg) .cell) {
  background-color: var(--el-color-danger-light-9) !important;
}

/* 时间信息行样式 - 使用 flex 布局，padding 为 0，间距 8px */
.time-info-container {
  display: flex;
  gap: 8px;
  padding: 0;
  margin: 0;
}

.time-info-item {
  flex: 1;
  margin: 0 !important;
  padding: 0 !important;
}

.time-info-item :deep(.el-form-item__content) {
  margin: 0 !important;
  padding: 0 !important;
  position: relative;
  overflow: visible;
}

.time-warning-error {
  font-size: 12px;
  color: var(--el-color-warning);
  line-height: 1.4;
  position: absolute;
  left: 0;
  top: calc(100% + 16px);
  pointer-events: none;
}

.time-info-item :deep(.el-date-picker),
.time-info-item :deep(.el-input-number) {
  width: 100% !important;
}

/* 确保日期选择器的清除按钮不会导致宽度跳动 */
.time-info-item :deep(.el-date-picker .el-input__wrapper) {
  padding-right: 30px !important;
}

.time-info-item :deep(.el-date-picker .el-input__suffix) {
  width: 30px !important;
  right: 0 !important;
}
</style>

