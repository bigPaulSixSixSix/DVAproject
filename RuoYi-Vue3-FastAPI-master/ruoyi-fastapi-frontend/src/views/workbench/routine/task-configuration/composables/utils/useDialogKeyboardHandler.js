/**
 * 弹窗键盘事件处理 composable
 * 用于处理弹窗的 Enter 和 Esc 键事件，即使弹窗失焦也能正常工作
 */

import { ref, onUnmounted } from 'vue'

/**
 * 检查事件目标是否是输入元素
 * @param {HTMLElement} target - 事件目标元素
 * @returns {Object} { isInputElement, isContentEditable, isButton }
 */
const checkInputElement = (target) => {
  const isInputElement = target.tagName === 'INPUT' || 
                         target.tagName === 'TEXTAREA' || 
                         target.tagName === 'SELECT'
  const isContentEditable = target.isContentEditable
  const isButton = target.tagName === 'BUTTON' || target.closest('button') !== null
  
  return { isInputElement, isContentEditable, isButton }
}

/**
 * 检查是否有 ElMessageBox 正在显示
 * @param {HTMLElement} target - 事件目标元素
 * @returns {boolean}
 */
const isMessageBoxActive = (target) => {
  return target.closest('.el-message-box') !== null
}

/**
 * 查找指定的弹窗元素
 * @param {string|Function} dialogSelector - 弹窗选择器或查找函数
 * @returns {HTMLElement|null}
 */
const findDialogElement = (dialogSelector) => {
  if (typeof dialogSelector === 'function') {
    return dialogSelector()
  }
  
  const allDialogs = document.querySelectorAll('.el-dialog')
  if (typeof dialogSelector === 'string') {
    return Array.from(allDialogs).find(dialog => 
      dialog.classList.contains(dialogSelector) || 
      dialog.querySelector(dialogSelector) !== null
    )
  }
  
  return null
}

/**
 * 检查弹窗是否可见
 * @param {HTMLElement} dialogElement - 弹窗元素
 * @returns {boolean}
 */
const isDialogVisible = (dialogElement) => {
  if (!dialogElement) return false
  const style = window.getComputedStyle(dialogElement)
  return style.display !== 'none' && style.visibility !== 'hidden'
}

/**
 * 检查是否有其他弹窗在上层
 * @param {HTMLElement} dialogElement - 当前弹窗元素
 * @returns {boolean}
 */
const hasUpperDialog = (dialogElement) => {
  if (!dialogElement) return false
  
  // 找到包含当前 dialog 的 overlay
  const currentOverlay = dialogElement.closest('.el-overlay')
  if (!currentOverlay) return false
  
  const currentOverlayZIndex = parseInt(window.getComputedStyle(currentOverlay).zIndex) || 0
  
  // 检查是否有其他 overlay 在上层（排除当前 overlay）
  const allOverlays = document.querySelectorAll('.el-overlay')
  return Array.from(allOverlays).some(overlay => {
    if (overlay === currentOverlay) {
      return false // 跳过当前 overlay
    }
    const overlayZIndex = parseInt(window.getComputedStyle(overlay).zIndex) || 0
    return overlayZIndex > currentOverlayZIndex
  })
}

/**
 * 检查事件是否应该被处理
 * @param {KeyboardEvent} event - 键盘事件
 * @param {HTMLElement} dialogElement - 弹窗元素
 * @param {boolean} isMessageBoxShowing - 是否有 ElMessageBox 正在显示（标志位）
 * @returns {Object} { shouldHandle: boolean, reason?: string }
 */
const shouldHandleKeyboardEvent = (event, dialogElement, isMessageBoxShowing = false) => {
  const target = event.target
  
  // 检查标志位
  if (isMessageBoxShowing) {
    return { shouldHandle: false, reason: 'ElMessageBox 正在显示（标志位）' }
  }
  
  // 检查是否有 ElMessageBox 正在显示
  if (isMessageBoxActive(target)) {
    return { shouldHandle: false, reason: '事件在 ElMessageBox 内' }
  }
  
  // 检查弹窗是否存在
  if (!dialogElement) {
    return { shouldHandle: false, reason: '找不到弹窗元素' }
  }
  
  // 检查弹窗是否可见
  if (!isDialogVisible(dialogElement)) {
    return { shouldHandle: false, reason: '弹窗不可见' }
  }
  
  // 检查是否有其他弹窗在上层
  if (hasUpperDialog(dialogElement)) {
    return { shouldHandle: false, reason: '有其他弹窗在上层' }
  }
  
  // 检查是否是输入元素
  const { isInputElement, isContentEditable, isButton } = checkInputElement(target)
  
  // 检查事件是否发生在弹窗内
  const isInDialog = dialogElement.contains(target) || target.closest('.task-edit-dialog') !== null
  
  // 如果焦点在输入元素上，且不在弹窗内，不处理（可能是其他输入框）
  if (isInputElement && !isInDialog) {
    return { shouldHandle: false, reason: '焦点在输入元素上且不在弹窗内' }
  }
  
  return { 
    shouldHandle: true, 
    isInputElement, 
    isContentEditable, 
    isButton,
    isInDialog
  }
}

/**
 * 创建弹窗键盘事件处理器
 * @param {Object} options
 * @param {string|Function} options.dialogSelector - 弹窗选择器或查找函数
 * @param {Function} options.onEnter - Enter 键处理函数
 * @param {Function} options.onEsc - Esc 键处理函数
 * @param {Function} options.isMessageBoxShowing - 获取 ElMessageBox 显示状态的函数（可选）
 * @param {boolean} options.debug - 是否输出调试信息（默认 false）
 * @returns {Object} { setup, cleanup }
 */
export const useDialogKeyboardHandler = (options) => {
  const { dialogSelector, onEnter, onEsc, isMessageBoxShowing, debug = false } = options
  
  let documentKeydownHandler = null
  
  const log = (message, ...args) => {
    if (debug) {
      console.log(`[调试] ${message}`, ...args)
    }
  }
  
  /**
   * 创建键盘事件处理函数
   */
  const createKeyboardHandler = () => {
    return (event) => {
      log('document 级别捕获到 keydown 事件:', event.key, event.target)
      
      // 获取 ElMessageBox 显示状态
      const messageBoxShowing = isMessageBoxShowing ? isMessageBoxShowing() : false
      
      // 查找弹窗元素
      const dialogElement = findDialogElement(dialogSelector)
      log('找到弹窗元素:', dialogElement)
      
      // 检查是否应该处理事件
      const checkResult = shouldHandleKeyboardEvent(event, dialogElement, messageBoxShowing)
      if (!checkResult.shouldHandle) {
        log('不处理事件，原因:', checkResult.reason)
        return
      }
      
      const { isInputElement, isContentEditable, isButton } = checkResult
      
      // 处理 Enter 键
      if (event.key === 'Enter' && !isInputElement && !isContentEditable && !isButton) {
        log('document 级别处理 Enter 键')
        event.preventDefault()
        event.stopPropagation()
        onEnter(event)
      }
      // 处理 Esc 键
      else if (event.key === 'Escape' || event.keyCode === 27) {
        if (!isContentEditable) {
          log('document 级别处理 Esc 键')
          event.preventDefault()
          event.stopPropagation()
          onEsc(event)
        }
      }
    }
  }
  
  /**
   * 设置键盘事件监听
   */
  const setup = () => {
    if (!documentKeydownHandler) {
      documentKeydownHandler = createKeyboardHandler()
      document.addEventListener('keydown', documentKeydownHandler, true)
      log('已添加 document 级别的键盘事件监听')
    } else {
      log('document 级别的键盘事件监听器已存在，跳过添加')
    }
  }
  
  /**
   * 清理键盘事件监听
   */
  const cleanup = () => {
    if (documentKeydownHandler) {
      document.removeEventListener('keydown', documentKeydownHandler, true)
      documentKeydownHandler = null
      log('已移除 document 级别的键盘事件监听')
    }
  }
  
  // 组件卸载时自动清理
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    setup,
    cleanup
  }
}

