-- ============================================
-- 任务配置表扩展 - 添加审批相关字段
-- 执行日期：2025-01-17
-- ============================================

-- ----------------------------
-- MySQL版本
-- ----------------------------
-- 添加审批模式字段
ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL COMMENT '审批模式（specified-指定编制审批，sequential-逐级审批）';

-- 添加审批层级字段
ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL COMMENT '审批层级数组（JSON格式，存储岗位编制ID列表）';

-- 更新assignee字段注释（从"用户ID或用户名"改为"负责人工号"）
ALTER TABLE proj_task MODIFY COLUMN assignee VARCHAR(64) NULL COMMENT '负责人工号';

-- ----------------------------
-- PostgreSQL版本
-- ----------------------------
-- 添加审批模式字段
-- ALTER TABLE proj_task ADD COLUMN approval_type VARCHAR(32) NULL;
-- COMMENT ON COLUMN proj_task.approval_type IS '审批模式（specified-指定编制审批，sequential-逐级审批）';

-- 添加审批层级字段
-- ALTER TABLE proj_task ADD COLUMN approval_levels TEXT NULL;
-- COMMENT ON COLUMN proj_task.approval_levels IS '审批层级数组（JSON格式，存储岗位编制ID列表）';

-- 更新assignee字段注释（从"用户ID或用户名"改为"负责人工号"）
-- COMMENT ON COLUMN proj_task.assignee IS '负责人工号';
