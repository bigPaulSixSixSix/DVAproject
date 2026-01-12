// composables/useCanvasZoom.js
import { ref } from 'vue'

const clampZoom = (value, minZoom, maxZoom) => {
  return Math.max(minZoom, Math.min(maxZoom, value))
}

export const useCanvasZoom = () => {
  const zoomLevel = ref(1)
  const minZoom = 0.2
  const maxZoom = 3
  
  const handleWheel = (event, canvasElement) => {
    event.preventDefault()
    
    if (!canvasElement) return
    
    const delta = event.deltaY > 0 ? -0.1 : 0.1
    const oldZoom = zoomLevel.value
    const newZoom = clampZoom(oldZoom + delta, minZoom, maxZoom)
    
    // 如果缩放级别没有变化，直接返回
    if (oldZoom === newZoom) return
    
    // 获取鼠标相对于 canvas 容器的位置
    const canvasRect = canvasElement.getBoundingClientRect()
    const mouseX = event.clientX - canvasRect.left
    const mouseY = event.clientY - canvasRect.top
    
    // 获取当前的滚动位置
    const oldScrollLeft = canvasElement.scrollLeft
    const oldScrollTop = canvasElement.scrollTop
    
    // 计算鼠标在画布内容（未缩放坐标系）上的位置
    // 鼠标在画布内容上的位置 = (鼠标相对于 canvas 的位置 + scroll) / 当前缩放
    const contentX = (mouseX + oldScrollLeft) / oldZoom
    const contentY = (mouseY + oldScrollTop) / oldZoom
    
    // 更新缩放级别
    zoomLevel.value = newZoom
    
    // 计算新的滚动位置，使鼠标下的点在缩放后仍然在鼠标下
    // 新 scroll = 鼠标在画布内容上的位置 * 新缩放 - 鼠标相对于 canvas 的位置
    const newScrollLeft = contentX * newZoom - mouseX
    const newScrollTop = contentY * newZoom - mouseY
    
    // 应用新的滚动位置
    canvasElement.scrollLeft = newScrollLeft
    canvasElement.scrollTop = newScrollTop
  }
  
  const resetZoom = (canvasElement) => {
    if (!canvasElement) {
      zoomLevel.value = 1
      return
    }
    
    const oldZoom = zoomLevel.value
    const newZoom = 1
    
    // 如果已经是 1，直接返回
    if (oldZoom === newZoom) return
    
    // 获取 canvas 中心位置
    const canvasRect = canvasElement.getBoundingClientRect()
    const mouseX = canvasRect.width / 2
    const mouseY = canvasRect.height / 2
    
    // 获取当前的滚动位置
    const oldScrollLeft = canvasElement.scrollLeft
    const oldScrollTop = canvasElement.scrollTop
    
    // 计算鼠标在画布内容上的位置
    const contentX = (mouseX + oldScrollLeft) / oldZoom
    const contentY = (mouseY + oldScrollTop) / oldZoom
    
    // 更新缩放级别
    zoomLevel.value = newZoom
    
    // 计算新的滚动位置
    const newScrollLeft = contentX * newZoom - mouseX
    const newScrollTop = contentY * newZoom - mouseY
    
    // 应用新的滚动位置
    canvasElement.scrollLeft = newScrollLeft
    canvasElement.scrollTop = newScrollTop
  }
  
  /**
   * 平滑滚动动画函数
   * @param {HTMLElement} element - 要滚动的元素
   * @param {number} startScrollLeft - 起始滚动位置 X
   * @param {number} startScrollTop - 起始滚动位置 Y
   * @param {number} targetScrollLeft - 目标滚动位置 X
   * @param {number} targetScrollTop - 目标滚动位置 Y
   * @param {number} duration - 动画时长（毫秒）
   */
  const smoothScroll = (element, startScrollLeft, startScrollTop, targetScrollLeft, targetScrollTop, duration) => {
    const startTime = performance.now()
    const deltaX = targetScrollLeft - startScrollLeft
    const deltaY = targetScrollTop - startScrollTop

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用 easeInOutCubic 缓动函数
      const easeProgress = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2

      const currentScrollLeft = startScrollLeft + deltaX * easeProgress
      const currentScrollTop = startScrollTop + deltaY * easeProgress

      element.scrollLeft = currentScrollLeft
      element.scrollTop = currentScrollTop

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }

  const zoomTo = (canvasElement, targetZoom, focusPoint = null, options = {}) => {
    const { animate = false, duration = 600, align = 'center' } = options
    const oldZoom = zoomLevel.value
    const newZoom = clampZoom(targetZoom, minZoom, maxZoom)
    
    if (!canvasElement) {
      zoomLevel.value = newZoom
      return
    }

    const viewportWidth = canvasElement.clientWidth
    const viewportHeight = canvasElement.clientHeight

    let contentX
    let contentY

    if (focusPoint && typeof focusPoint.x === 'number' && typeof focusPoint.y === 'number') {
      contentX = focusPoint.x
      contentY = focusPoint.y
    } else {
      // 默认使用当前视口中心
      const mouseX = viewportWidth / 2
      const mouseY = viewportHeight / 2
      const oldScrollLeft = canvasElement.scrollLeft
      const oldScrollTop = canvasElement.scrollTop
      contentX = (mouseX + oldScrollLeft) / (oldZoom || 1)
      contentY = (mouseY + oldScrollTop) / (oldZoom || 1)
    }

    // 根据对齐方式计算滚动位置
    let newScrollLeft, newScrollTop
    if (align === 'top-left') {
      // 将 focusPoint 对齐到视口左上角
      newScrollLeft = contentX * newZoom
      newScrollTop = contentY * newZoom
    } else {
      // 默认：将 focusPoint 对齐到视口中心
      newScrollLeft = contentX * newZoom - viewportWidth / 2
      newScrollTop = contentY * newZoom - viewportHeight / 2
    }

    const maxScrollLeft = canvasElement.scrollWidth - viewportWidth
    const maxScrollTop = canvasElement.scrollHeight - viewportHeight

    const finalScrollLeft = Math.max(0, Math.min(newScrollLeft, maxScrollLeft))
    const finalScrollTop = Math.max(0, Math.min(newScrollTop, maxScrollTop))

    // 更新缩放级别
    zoomLevel.value = newZoom

    // 如果启用动画，使用平滑滚动
    if (animate) {
      const startScrollLeft = canvasElement.scrollLeft
      const startScrollTop = canvasElement.scrollTop
      smoothScroll(canvasElement, startScrollLeft, startScrollTop, finalScrollLeft, finalScrollTop, duration)
    } else {
      // 否则直接设置滚动位置
      canvasElement.scrollLeft = finalScrollLeft
      canvasElement.scrollTop = finalScrollTop
    }
  }

  return {
    zoomLevel,
    handleWheel,
    resetZoom,
    zoomTo
  }
}
