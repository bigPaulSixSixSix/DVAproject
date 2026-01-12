// composables/useDebug.js
// 轻量日志工具：通过 localStorage.setItem('wf_debug','1') 开启，removeItem 关闭

export const createDebug = (namespace = 'wf') => {
  // 直接开启调试输出（调试结束后整块删除）
  const isEnabled = () => true

  const prefix = `[${namespace}]`

  const group = (...args) => {
    if (!isEnabled()) return
    // eslint-disable-next-line no-console
    console.groupCollapsed(prefix, ...args)
  }

  const groupEnd = () => {
    if (!isEnabled()) return
    // eslint-disable-next-line no-console
    console.groupEnd()
  }

  const log = (...args) => {
    if (!isEnabled()) return
    // 控制台输出已禁用
  }

  const warn = (...args) => {
    if (!isEnabled()) return
    // 控制台输出已禁用
  }

  return { log, warn, group, groupEnd }
}


