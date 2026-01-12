-- ============================================
-- 清理测试数据脚本
-- 用于测试准备：清空任务执行和审批相关表
-- ============================================
-- 
-- 说明：
-- 1. 保留配置表：proj_task, proj_stage（任务配置数据）
-- 2. 清空执行表：todo_task, todo_stage（任务执行数据）
-- 3. 清空审批表：apply_primary, apply_rules, apply_log, todo_task_apply（审批流程数据）
-- 
-- 注意：本项目中所有表都没有外键约束，通过代码逻辑管理关系
-- ============================================

-- 1. 清理审批日志表（最底层依赖表）
TRUNCATE TABLE apply_log;

-- 2. 清理审批规则表
TRUNCATE TABLE apply_rules;

-- 3. 清理申请单主表
TRUNCATE TABLE apply_primary;

-- 4. 清理任务申请详情表
TRUNCATE TABLE todo_task_apply;

-- 5. 清理任务执行表
TRUNCATE TABLE todo_task;

-- 6. 清理阶段执行表
TRUNCATE TABLE todo_stage;

-- ============================================
-- 验证清理结果（可选，用于确认）
-- ============================================
-- SELECT COUNT(*) as todo_task_count FROM todo_task;
-- SELECT COUNT(*) as todo_stage_count FROM todo_stage;
-- SELECT COUNT(*) as todo_task_apply_count FROM todo_task_apply;
-- SELECT COUNT(*) as apply_primary_count FROM apply_primary;
-- SELECT COUNT(*) as apply_rules_count FROM apply_rules;
-- SELECT COUNT(*) as apply_log_count FROM apply_log;
-- 
-- SELECT COUNT(*) as proj_task_count FROM proj_task;
-- SELECT COUNT(*) as proj_stage_count FROM proj_stage;
