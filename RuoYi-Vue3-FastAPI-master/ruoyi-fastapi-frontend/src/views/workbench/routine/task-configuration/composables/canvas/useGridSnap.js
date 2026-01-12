// composables/useGridSnap.js
import { ref } from 'vue'

export const useGridSnap = () => {
  const gridSize = 8 // 网格大小
  
  const snapToGrid = (position) => {
    const result = {}
    
    if (position.x !== undefined) {
      result.x = Math.round(position.x / gridSize) * gridSize
    }
    if (position.y !== undefined) {
      result.y = Math.round(position.y / gridSize) * gridSize
    }
    if (position.width !== undefined) {
      result.width = Math.round(position.width / gridSize) * gridSize
    }
    if (position.height !== undefined) {
      result.height = Math.round(position.height / gridSize) * gridSize
    }
    
    return result
  }
  
  const isSnappedToGrid = (position) => {
    return position.x % gridSize === 0 && position.y % gridSize === 0
  }
  
  return {
    gridSize,
    snapToGrid,
    isSnappedToGrid
  }
}
