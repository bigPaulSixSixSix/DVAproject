// composables/connection/config/testConfig.js
// 连接相关测试功能开关配置
// 用于聚合所有与连接相关的测试功能开关

/**
 * ============================================
 * 1. 前端验证开关
 * ============================================
 * 
 * 是否启用前端验证
 * 
 * 设置为 true 时，将启用所有前端验证（打开验证模式），如果操作非法，会予以阻拦，包括：
 * - 循环依赖检测（回环检测）
 * - 阶段外任务连接限制
 * - 跨阶段任务关系限制
 * - 保存前的所有验证
 * 
 * 设置为 false 时，将跳过所有前端验证（关闭验证模式），如果操作非法，不阻拦，允许执行
 * 用于测试后端验证功能
 * 
 * 注意：测试后端验证时，请将此值设置为 false，以关闭前端验证
 */
export const ENABLE_FRONTEND_VALIDATION = true


/**
 * ============================================
 * 2. 连接日志下载开关
 * ============================================
 * 
 * 是否启用连接操作日志自动下载功能
 * 
 * 设置为 true 时，在以下操作时会自动生成并下载日志文件：
 * - 连接创建成功时
 * - 连接创建失败时
 * - 回环检测失败时
 * 
 * 设置为 false 时，不生成日志文件，只显示普通提示消息
 * 
 * 注意：此功能用于调试和测试，生产环境建议关闭
 */
export const ENABLE_CONNECTION_LOGGING = false



/**
 * 检查是否应该跳过验证
 * @returns {boolean} true表示跳过验证（关闭验证模式，允许所有操作），false表示执行验证（打开验证模式，阻拦非法操作）
 * 
 * 逻辑说明：
 * - ENABLE_FRONTEND_VALIDATION = true -> shouldSkipValidation() = false -> 执行验证（打开验证模式，阻拦非法操作）
 * - ENABLE_FRONTEND_VALIDATION = false -> shouldSkipValidation() = true -> 跳过验证（关闭验证模式，允许所有操作）
 */
export const shouldSkipValidation = () => {
  return !ENABLE_FRONTEND_VALIDATION
}

/**
 * 检查是否应该启用连接日志下载
 * @returns {boolean} true表示启用日志下载，false表示禁用日志下载
 */
export const shouldEnableConnectionLogging = () => {
  return ENABLE_CONNECTION_LOGGING
}

