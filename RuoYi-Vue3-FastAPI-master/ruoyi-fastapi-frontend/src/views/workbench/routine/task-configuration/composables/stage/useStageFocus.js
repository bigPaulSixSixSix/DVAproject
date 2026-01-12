// composables/stage/useStageFocus.js
import { ElMessage } from 'element-plus'

/**
 * 阶段定位功能
 * 用于定位和聚焦到特定阶段
 */
export const useStageFocus = (findStageById, zoomTo, canvasRef) => {
  /**
   * 定位到指定阶段
   * @param {string|number} stageId - 阶段ID
   */
  const focusOnStage = (stageId) => {
    const stage = findStageById(stageId)
    if (!stage || !stage.position) {
      ElMessage.warning('无法定位该阶段')
      return
    }

    // 定位到阶段的中心，缩放为100%
    const STAGE_HEADER_HEIGHT = 60
    const centerX = stage.position.x + stage.position.width / 2
    const centerY = stage.position.y + STAGE_HEADER_HEIGHT / 2

    // 使用平滑滚动动画定位到阶段中心，缩放为100%
    zoomTo(canvasRef.value, 1, { x: centerX, y: centerY }, { animate: true, duration: 600 })
  }

  return {
    focusOnStage
  }
}

