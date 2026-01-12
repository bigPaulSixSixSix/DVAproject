// composables/useCanvasZoomControls.js
import { computed } from 'vue'

/**
 * 画布缩放控制相关功能
 * 包括缩放选项、缩放命令处理等
 */
export const useCanvasZoomControls = (zoomLevel, resetZoom, zoomTo, canvasRef) => {
  // 缩放百分比显示
  const zoomPercentage = computed(() => Math.round((zoomLevel.value || 1) * 100))

  // 缩放选项
  const zoomOptions = computed(() => {
    const current = zoomPercentage.value
    const options = []
    for (let percent = 200; percent >= 20; percent -= 10) {
      options.push({
        label: `${percent}%`,
        command: (percent / 100).toFixed(2),
        disabled: current === percent
      })
    }
    return options
  })

  // 处理缩放命令
  const handleZoomCommand = (command) => {
    if (command === 'reset') {
      resetZoom(canvasRef.value)
      return
    }
    const zoomValue = parseFloat(command)
    if (!Number.isNaN(zoomValue)) {
      zoomTo(canvasRef.value, zoomValue)
    }
  }

  return {
    zoomPercentage,
    zoomOptions,
    handleZoomCommand
  }
}

