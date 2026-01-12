<template>
  <div class="task-edit-tabs">
    <button
      v-if="showLeftArrow"
      class="tab-scroll-button left"
      type="button"
      @click="scrollTabs('left')"
    >
      <el-icon><ArrowLeft /></el-icon>
    </button>
    <div class="tabs-scroll-wrapper" ref="scrollWrapper" @scroll="handleScroll">
      <div class="tabs-inner" ref="tabsInner">
        <TaskEditTabItem
          v-for="tab in tabs"
          :key="tab.taskId"
          :tab="tab"
          :active="String(tab.taskId) === String(activeTabId)"
          :get-user-nick-name="getUserNickName"
          :find-task-by-id="findTaskById"
          @select="handleSelect"
          @close="handleClose"
        />
      </div>
    </div>
    <button
      v-if="showRightArrow"
      class="tab-scroll-button right"
      type="button"
      @click="scrollTabs('right')"
    >
      <el-icon><ArrowRight /></el-icon>
    </button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import TaskEditTabItem from './TaskEditTabItem.vue'

const props = defineProps({
  tabs: {
    type: Array,
    default: () => []
  },
  activeTabId: {
    type: [String, Number, null],
    default: null
  },
  getUserNickName: {
    type: Function,
    required: true
  },
  findTaskById: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['select', 'close'])

const scrollWrapper = ref(null)
const tabsInner = ref(null)
const showLeftArrow = ref(false)
const showRightArrow = ref(false)

const updateArrowVisibility = () => {
  const wrapper = scrollWrapper.value
  if (!wrapper) return
  const { scrollLeft, scrollWidth, clientWidth } = wrapper
  showLeftArrow.value = scrollLeft > 2
  showRightArrow.value = scrollLeft + clientWidth < scrollWidth - 2
}

const ensureActiveTabVisible = () => {
  const wrapper = scrollWrapper.value
  if (!wrapper) return
  const activeEl = wrapper.querySelector('.task-edit-tab-item.active')
  if (!activeEl) return
  const wrapperRect = wrapper.getBoundingClientRect()
  const activeRect = activeEl.getBoundingClientRect()
  if (activeRect.left < wrapperRect.left) {
    wrapper.scrollBy({
      left: activeRect.left - wrapperRect.left - 16,
      behavior: 'smooth'
    })
  } else if (activeRect.right > wrapperRect.right) {
    wrapper.scrollBy({
      left: activeRect.right - wrapperRect.right + 16,
      behavior: 'smooth'
    })
  }
}

const getAverageTabWidth = () => {
  const items = tabsInner.value?.querySelectorAll('.task-edit-tab-item')
  if (items && items.length) {
    const first = items[0]
    return first.offsetWidth + 12
  }
  return 240
}

const scrollTabs = (direction) => {
  const wrapper = scrollWrapper.value
  if (!wrapper) return
  const distance = getAverageTabWidth() * 3
  wrapper.scrollBy({
    left: direction === 'left' ? -distance : distance,
    behavior: 'smooth'
  })
}

const handleScroll = () => {
  updateArrowVisibility()
}

const handleSelect = (taskId) => {
  emit('select', taskId)
}

const handleClose = (taskId) => {
  emit('close', taskId)
}

const handleResize = () => {
  updateArrowVisibility()
}

onMounted(() => {
  updateArrowVisibility()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

watch(
  () => props.tabs.length,
  async () => {
    await nextTick()
    updateArrowVisibility()
    ensureActiveTabVisible()
  }
)

watch(
  () => props.activeTabId,
  async () => {
    await nextTick()
    ensureActiveTabVisible()
  }
)
</script>

<style scoped>
.task-edit-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0 12px;
}

.tabs-scroll-wrapper {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
}

.tabs-scroll-wrapper::-webkit-scrollbar {
  height: 0;
}

.tabs-inner {
  display: flex;
  gap: 12px;
  overflow: visible;
  padding: 0 4px;
}

.tab-scroll-button {
  width: 32px;
  height: 32px;
  border: 1px solid var(--el-border-color);
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--el-text-color-regular);
  flex-shrink: 0;
}

.tab-scroll-button:hover {
  color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.tab-scroll-button :deep(svg) {
  width: 16px;
  height: 16px;
}
</style>

