<template>
  <SummaryCard
    title="我的任务"
    :description="taskDescription"
    :badge-text="totalCount"
    badge-type="primary"
    icon-name="List"
    icon-color="primary"
    :on-click="handleClick"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SummaryCard from './index.vue'
import { getWorkbenchTaskStats } from '@/api/todo'

const router = useRouter()

// 统计数据
const stats = ref({
  pendingSubmit: 0,  // 待提交数量
  pendingApprove: 0, // 待审批数量
  rejected: 0        // 被驳回数量
})

// 计算总数
const totalCount = computed(() => {
  return String(stats.value.pendingSubmit + stats.value.pendingApprove + stats.value.rejected)
})

// 计算描述文本
const taskDescription = computed(() => {
  const parts = []
  if (stats.value.pendingSubmit > 0) {
    parts.push(`${stats.value.pendingSubmit}项待提交`)
  }
  if (stats.value.pendingApprove > 0) {
    parts.push(`${stats.value.pendingApprove}项待审批`)
  }
  if (stats.value.rejected > 0) {
    parts.push(`${stats.value.rejected}项被驳回`)
  }
  return parts.length > 0 ? parts.join(' ') : '暂无任务'
})

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getWorkbenchTaskStats()
    if (res.code === 200 && res.data) {
      stats.value = {
        pendingSubmit: res.data.pendingSubmit || 0,
        pendingApprove: res.data.pendingApprove || 0,
        rejected: res.data.rejected || 0
      }
    }
  } catch (error) {
    console.error('加载任务统计失败:', error)
    // 失败时使用默认值
    stats.value = {
      pendingSubmit: 0,
      pendingApprove: 0,
      rejected: 0
    }
  }
}

const handleClick = () => {
  router.push('/workbench/todo')
}

onMounted(() => {
  loadStats()
})
</script>
