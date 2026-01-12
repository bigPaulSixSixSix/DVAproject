// composables/useCanvasDrag.js
import { ref } from 'vue'

export const useCanvasDrag = () => {
  const isDragging = ref(false)
  const isSpaceDown = ref(false)
  const startPosition = ref({ x: 0, y: 0 })
  const startScroll = ref({ x: 0, y: 0 })
  const canvasElement = ref(null)
  
  const handleKeyDown = (event) => {
    if (event.code === 'Space') {
      event.preventDefault()
      isSpaceDown.value = true
    }
  }
  
  const handleKeyUp = (event) => {
    if (event.code === 'Space') {
      isSpaceDown.value = false
    }
  }
  
  const handleMouseDown = (event) => {
    // 空格键按下时，优先执行画布拖拽
    if (!isSpaceDown.value) return
    
    // 阻止事件传播，确保优先级最高
    event.stopPropagation()
    event.preventDefault()
    
    isDragging.value = true
    startPosition.value = {
      x: event.clientX,
      y: event.clientY
    }
    
    if (canvasElement.value) {
      startScroll.value = {
        x: canvasElement.value.scrollLeft,
        y: canvasElement.value.scrollTop
      }
    }
    
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }
  
  const handleMouseMove = (event) => {
    if (!isDragging.value || !canvasElement.value) return
    
    // 阻止事件传播，确保拖拽过程不受干扰
    event.stopPropagation()
    event.preventDefault()
    
    const deltaX = startPosition.value.x - event.clientX
    const deltaY = startPosition.value.y - event.clientY
    
    canvasElement.value.scrollLeft = startScroll.value.x + deltaX
    canvasElement.value.scrollTop = startScroll.value.y + deltaY
  }
  
  const handleMouseUp = () => {
    if (isDragging.value) {
      isDragging.value = false
      if (canvasElement.value) {
      }
    }
    
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  const initCanvasDrag = (canvasRef) => {
    canvasElement.value = canvasRef
    
    if (canvasRef) {
      // 使用 capture 模式，确保在子元素事件之前捕获
      canvasRef.addEventListener('mousedown', handleMouseDown, true)
    }
    
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('keyup', handleKeyUp)
  }
  
  const cleanupCanvasDrag = () => {
    if (canvasElement.value) {
      canvasElement.value.removeEventListener('mousedown', handleMouseDown, true)
    }
    
    document.removeEventListener('keydown', handleKeyDown)
    document.removeEventListener('keyup', handleKeyUp)
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  return {
    isDragging,
    isSpaceDown,
    initCanvasDrag,
    cleanupCanvasDrag,
    handleKeyDown,
    handleKeyUp
  }
}
