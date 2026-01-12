<template>
  <svg class="connection-line-preview" viewBox="0 0 20000 20000" preserveAspectRatio="none">
    <path
      :d="pathData"
      class="connection-line-preview--active"
      stroke-width="4"
      fill="none"
    />
  </svg>
</template>

<script setup>
import { computed } from 'vue'
import { useConnectionLine } from '../../composables/connection/useConnection'

const props = defineProps({
  fromPoint: {
    type: Object,
    required: true
  },
  toPoint: {
    type: Object,
    required: true
  }
})

const { calculateBezierPath } = useConnectionLine()

const pathData = computed(() => {
  if (!props.fromPoint || !props.toPoint) {
    return ''
  }
  
  return calculateBezierPath(props.fromPoint, props.toPoint)
})
</script>

<style scoped>
.connection-line-preview {
  position: absolute;
  top: 0;
  left: 0;
  width: 20000px;
  height: 20000px;
  pointer-events: none;
  z-index: 7; /* 在正常连接线之上 */
  overflow: visible;
}

.connection-line-preview--active {
  stroke: var(--el-color-primary); /* 蓝色，和连接点激活时一样 */
}
</style>

